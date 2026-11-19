from __future__ import annotations

import json
import sqlite3

import pytest

from barrot_agent.evolution.feature_store import (
    FeatureStoreError,
    HistoricalFeatureStore,
    _canonical,
    _sha256,
)
from barrot_agent.evolution.point_in_time_features import (
    FeatureSnapshotError,
    build_feature_snapshot,
    independent_source_groups,
    validate_feature_record,
)
from barrot_agent.evolution.research_artifact_clock import (
    ResearchArtifactClockError,
    validate_capture_before_commit,
)

CUTOFF = "2026-11-03T16:00:00Z"
CAPTURED = "2026-11-03T16:05:00Z"
HASH_A = "a" * 64
HASH_B = "b" * 64


def source(source_id="provider-a", group="exchange-a", digest=HASH_A):
    return {
        "source_id": source_id,
        "independence_group": group,
        "source_uri": f"https://{source_id}.example/public-data",
        "raw_content_sha256": digest,
    }


def feature(**updates):
    item = {
        "record_id": "xrp:spot:mid:2026-11-03T15:59:00Z:v1",
        "feature_id": "xrp.spot.mid_price",
        "feature_version": 1,
        "asset": "XRP",
        "feature_name": "spot_mid_price",
        "value": 1.27,
        "unit": "USD/XRP",
        "event_time_utc": "2026-11-03T15:59:00Z",
        "known_at_utc": "2026-11-03T15:59:02Z",
        "source_data_as_of_utc": "2026-11-03T15:59:00Z",
        "ingested_at_utc": "2026-11-03T15:59:04Z",
        "revision_available_at_utc": "2026-11-03T15:59:02Z",
        "sources": [source()],
        "quality_status": "verified",
        "model_eligible": True,
        "eligibility_reason": "",
        "revision_status": "original",
        "supersedes_record_id": None,
        "adapter_version": "public-market-v1",
        "parser_version": "xrp-features-v1",
        "limitations": ["Single venue observation"],
        "disconfirming_evidence_ids": [],
    }
    item.update(updates)
    return item


def test_valid_record_normalizes_timezone_and_future_event_can_be_known():
    result = validate_feature_record(
        feature(event_time_utc="2026-11-04T14:46:00Z"), CUTOFF, captured_at_utc=CAPTURED
    )
    assert result["eligible"] is True
    assert result["record"]["asset"] == "XRP"
    assert result["record"]["event_time_utc"] == "2026-11-04T14:46:00.000000Z"


def test_future_known_record_is_excluded_without_exposing_its_value():
    late = feature(
        record_id="future", known_at_utc="2026-11-03T16:00:01Z",
        revision_available_at_utc="2026-11-03T16:00:01Z",
        ingested_at_utc="2026-11-03T16:00:02Z", value="future-secret",
    )
    snapshot = build_feature_snapshot([feature(), late], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED)
    assert snapshot["eligible_record_count"] == 1
    assert "future-secret" not in str(snapshot["records"])
    assert "future-secret" not in str(snapshot["excluded_records"])
    assert "not_public_by_cutoff" in snapshot["excluded_records"][0]["reasons"]


def test_source_data_after_cutoff_is_excluded():
    result = validate_feature_record(
        feature(source_data_as_of_utc="2026-11-03T16:00:01Z", revision_available_at_utc="2026-11-03T16:00:02Z", ingested_at_utc="2026-11-03T16:00:03Z"),
        CUTOFF, captured_at_utc=CAPTURED,
    )
    assert "source_data_after_cutoff" in result["exclusion_reasons"]


def test_late_ingestion_is_never_backdated_in_schema_v1():
    result = validate_feature_record(feature(ingested_at_utc="2026-11-03T16:00:01Z"), CUTOFF, captured_at_utc=CAPTURED)
    assert result["eligible"] is False
    assert "ingested_after_cutoff" in result["exclusion_reasons"]


def test_missing_source_as_of_and_naive_timestamps_are_rejected():
    item = feature()
    del item["source_data_as_of_utc"]
    with pytest.raises(FeatureSnapshotError, match="source_data_as_of_utc"):
        validate_feature_record(item, CUTOFF, captured_at_utc=CAPTURED)
    with pytest.raises(FeatureSnapshotError, match="include a timezone"):
        validate_feature_record(feature(known_at_utc="2026-11-03T15:59:02"), CUTOFF, captured_at_utc=CAPTURED)


def test_non_finite_numeric_value_and_boolean_version_are_rejected():
    with pytest.raises(FeatureSnapshotError, match="finite"):
        validate_feature_record(feature(value=float("nan")), CUTOFF, captured_at_utc=CAPTURED)
    with pytest.raises(FeatureSnapshotError, match="positive integer"):
        validate_feature_record(feature(feature_version=True), CUTOFF, captured_at_utc=CAPTURED)


def test_provisional_quality_cannot_be_model_eligible():
    with pytest.raises(FeatureSnapshotError, match="quality_status=verified"):
        validate_feature_record(feature(quality_status="provisional"), CUTOFF, captured_at_utc=CAPTURED)
    result = validate_feature_record(
        feature(quality_status="provisional", model_eligible=False, eligibility_reason="Provisional issuer row"),
        CUTOFF, captured_at_utc=CAPTURED,
    )
    assert "quality_provisional" in result["exclusion_reasons"]


def test_superseded_and_malformed_revision_records_are_rejected():
    with pytest.raises(FeatureSnapshotError, match="cannot be model eligible"):
        validate_feature_record(feature(revision_status="superseded"), CUTOFF, captured_at_utc=CAPTURED)
    with pytest.raises(FeatureSnapshotError, match="require a different supersedes_record_id"):
        validate_feature_record(feature(revision_status="revised"), CUTOFF, captured_at_utc=CAPTURED)


def test_stale_source_is_excluded_by_feature_specific_age_limit():
    result = validate_feature_record(
        feature(known_at_utc="2026-11-03T15:00:02Z", source_data_as_of_utc="2026-11-03T15:00:00Z", revision_available_at_utc="2026-11-03T15:00:02Z", ingested_at_utc="2026-11-03T15:00:04Z"),
        CUTOFF, captured_at_utc=CAPTURED, max_source_age_seconds=3000,
    )
    assert "source_data_stale_at_cutoff" in result["exclusion_reasons"]


def test_independence_groups_deduplicate_syndicated_sources():
    result = validate_feature_record(
        feature(sources=[source("feed-a", "same-wire", HASH_A), source("feed-b", "same-wire", HASH_B), source("exchange-c", "exchange-c", "c" * 64)]),
        CUTOFF, captured_at_utc=CAPTURED,
    )
    assert independent_source_groups(result["record"]) == ["exchange-c", "same-wire"]
    assert result["record"]["independent_source_group_count"] == 2


def test_same_publisher_different_labels_count_as_one_source_group():
    result = validate_feature_record(
        feature(
            sources=[
                {
                    **source("api-feed", "api-label", HASH_A),
                    "source_uri": "https://api.example.com/market",
                },
                {
                    **source("www-feed", "www-label", HASH_B),
                    "source_uri": "https://www.example.com/market",
                },
            ]
        ),
        CUTOFF,
        captured_at_utc=CAPTURED,
    )
    assert result["record"]["source_independence_groups"] == ["publisher:example.com"]
    assert result["record"]["independent_source_group_count"] == 1


def test_snapshot_id_is_deterministic_and_order_independent():
    a = feature()
    b = feature(record_id="spread-v1", feature_id="xrp.spot.spread", feature_name="spot_spread", value=0.0001)
    first = build_feature_snapshot([a, b], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED)
    second = build_feature_snapshot([b, a], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED)
    assert first["snapshot_id"] == second["snapshot_id"]
    assert len(first["snapshot_id"]) == 64


def test_duplicate_record_and_source_ids_are_rejected():
    with pytest.raises(FeatureSnapshotError, match="duplicate record_id"):
        build_feature_snapshot([feature(), feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED)
    with pytest.raises(FeatureSnapshotError, match="duplicate source_id"):
        validate_feature_record(feature(sources=[source("same", "a"), source("same", "b", HASH_B)]), CUTOFF, captured_at_utc=CAPTURED)


def test_capture_before_cutoff_and_empty_eligible_snapshot_are_rejected():
    with pytest.raises(FeatureSnapshotError, match="cannot precede"):
        build_feature_snapshot([feature()], cutoff_utc=CUTOFF, captured_at_utc="2026-11-03T15:59:59Z")
    future = feature(known_at_utc="2026-11-03T16:00:01Z", revision_available_at_utc="2026-11-03T16:00:01Z", ingested_at_utc="2026-11-03T16:00:02Z")
    with pytest.raises(FeatureSnapshotError, match="no point-in-time eligible records"):
        build_feature_snapshot([future], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED)


def test_asset_scope_must_cover_eligible_records():
    with pytest.raises(FeatureSnapshotError, match="outside declared asset_scope"):
        build_feature_snapshot([feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED, asset_scope=["BTC"])


def test_source_uri_hash_timestamp_order_and_age_arguments_are_validated():
    with pytest.raises(FeatureSnapshotError, match=r"HTTP\(S\) URL"):
        validate_feature_record(feature(sources=[{**source(), "source_uri": "file:///tmp/data"}]), CUTOFF, captured_at_utc=CAPTURED)
    with pytest.raises(FeatureSnapshotError, match="SHA-256"):
        validate_feature_record(feature(sources=[{**source(), "raw_content_sha256": "bad"}]), CUTOFF, captured_at_utc=CAPTURED)
    with pytest.raises(FeatureSnapshotError, match="cannot precede known_at"):
        validate_feature_record(feature(revision_available_at_utc="2026-11-03T15:59:01Z"), CUTOFF, captured_at_utc=CAPTURED)
    with pytest.raises(FeatureSnapshotError, match="non-negative integer"):
        validate_feature_record(feature(), CUTOFF, captured_at_utc=CAPTURED, max_source_age_seconds=True)


def test_normalized_hash_and_market_dimensions_are_recorded():
    result = validate_feature_record(
        feature(venue="kraken", instrument="XRP/USD", currency_pair="XRP/USD", market_type="spot", aggregation_window="1m"),
        CUTOFF, captured_at_utc=CAPTURED,
    )
    assert len(result["record"]["normalized_content_sha256"]) == 64
    assert result["record"]["venue"] == "kraken"
    assert result["record"]["market_type"] == "spot"


def test_future_values_never_enter_model_facing_snapshot():
    late = feature(record_id="late", known_at_utc="2026-11-03T16:01:00Z", revision_available_at_utc="2026-11-03T16:01:00Z", ingested_at_utc="2026-11-03T16:02:00Z", value="future-secret")
    snapshot = build_feature_snapshot([feature(), late], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED)
    assert "future-secret" not in str(snapshot["records"])
    assert "future-secret" not in str(snapshot["excluded_records"])



def test_snapshot_uses_only_latest_eligible_revision_for_a_feature():
    original = feature(record_id="v1", feature_version=1, value=1.25)
    revised = feature(
        record_id="v2",
        feature_version=2,
        value=1.28,
        known_at_utc="2026-11-03T16:00:00Z",
        source_data_as_of_utc="2026-11-03T16:00:00Z",
        ingested_at_utc="2026-11-03T16:00:00Z",
        revision_available_at_utc="2026-11-03T16:00:00Z",
        revision_status="revised",
        supersedes_record_id="v1",
    )
    snapshot = build_feature_snapshot(
        [original, revised], cutoff_utc="2026-11-03T16:00:00Z", captured_at_utc="2026-11-03T16:05:00Z"
    )
    assert [record["record_id"] for record in snapshot["records"]] == ["v2"]
    assert snapshot["excluded_records"] == [
        {"record_id": "v1", "reasons": ["superseded_by_revision"]}
    ]


def test_revision_must_match_predecessor_feature_and_asset():
    original = feature(record_id="v1", feature_version=1)
    revised = feature(
        record_id="v2",
        feature_version=2,
        feature_id="xrp.spot.spread",
        revision_status="revised",
        supersedes_record_id="v1",
    )
    with pytest.raises(FeatureSnapshotError, match="same feature and asset"):
        build_feature_snapshot(
            [original, revised], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
        )


def test_revision_version_must_exceed_present_predecessor():
    original = feature(record_id="v1", feature_version=2)
    revised = feature(
        record_id="v2",
        feature_version=2,
        revision_status="revised",
        supersedes_record_id="v1",
    )
    with pytest.raises(FeatureSnapshotError, match="must exceed its predecessor"):
        build_feature_snapshot(
            [original, revised], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
        )


def test_conflicting_revisions_cannot_supersede_the_same_predecessor():
    original = feature(record_id="v1", feature_version=1)
    revised_a = feature(
        record_id="v2a", feature_version=2, revision_status="revised", supersedes_record_id="v1"
    )
    revised_b = feature(
        record_id="v2b", feature_version=3, revision_status="revised", supersedes_record_id="v1"
    )
    with pytest.raises(FeatureSnapshotError, match="multiple eligible revisions"):
        build_feature_snapshot(
            [original, revised_a, revised_b], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
        )


def test_artifact_capture_must_not_follow_introducing_commit():
    result = validate_capture_before_commit(
        "2026-11-03T22:00:00Z", "2026-11-03T22:00:01Z"
    )
    assert result["chronology"] == "valid"
    with pytest.raises(ResearchArtifactClockError, match="cannot be later"):
        validate_capture_before_commit(
            "2026-11-03T22:00:02Z", "2026-11-03T22:00:01Z"
        )


def test_artifact_clock_rejects_naive_or_malformed_timestamps():
    with pytest.raises(ResearchArtifactClockError, match="include a timezone"):
        validate_capture_before_commit(
            "2026-11-03T22:00:00", "2026-11-03T22:00:01Z"
        )
    with pytest.raises(ResearchArtifactClockError, match="not valid ISO-8601"):
        validate_capture_before_commit(
            "not-a-time", "2026-11-03T22:00:01Z"
        )


def test_historical_feature_store_is_idempotent_and_preserves_lineage(tmp_path):
    snapshot = build_feature_snapshot(
        [feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
    )
    store = HistoricalFeatureStore(tmp_path / "feature_store.sqlite3")

    first = store.append_snapshot(snapshot)
    second = store.append_snapshot(snapshot)

    assert first["created"] is True
    assert second["created"] is False
    assert first["snapshot_id"] == snapshot["snapshot_id"]
    assert first["stored_at_utc"] == second["stored_at_utc"]

    future_as_of = "2030-01-01T00:00:00Z"
    stored = store.snapshot_as_of("XRP", future_as_of)
    assert stored is not None
    assert stored["snapshot_id"] == snapshot["snapshot_id"]
    assert store.features_as_of("XRP", future_as_of)[0]["value"] == 1.27

    lineage = store.source_lineage(snapshot["snapshot_id"])
    assert len(lineage) == 1
    assert lineage[0]["source_id"] == "provider-a"
    assert lineage[0]["raw_content_sha256"] == HASH_A
    assert "raw_content" not in lineage[0]

    verified = store.verify_snapshot(snapshot["snapshot_id"])
    assert verified["valid"] is True
    assert verified["snapshot_columns_ok"] is True
    assert verified["sqlite_integrity"] == "ok"

    exact = store.verified_snapshot(snapshot["snapshot_id"])
    assert exact["snapshot_id"] == snapshot["snapshot_id"]
    assert exact["asset_scope"] == ["XRP"]
    assert exact["manifest"]["snapshot_id"] == snapshot["snapshot_id"]
    assert exact["verification"]["valid"] is True


def test_historical_feature_store_hides_backfilled_snapshot_before_store_receipt(tmp_path):
    snapshot = build_feature_snapshot(
        [feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
    )
    store = HistoricalFeatureStore(tmp_path / "feature_store.sqlite3")
    saved = store.append_snapshot(snapshot)

    # The source data is old, but the store did not receive this snapshot until now.
    assert saved["stored_at_utc"] > CAPTURED
    assert store.snapshot_as_of("XRP", CAPTURED) is None
    assert store.features_as_of("XRP", CAPTURED) == []
    assert store.snapshot_as_of("BTC", "2030-01-01T00:00:00Z") is None


def test_historical_feature_store_rejects_tampered_manifest_and_append_mutation(tmp_path):
    snapshot = build_feature_snapshot(
        [feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
    )
    store = HistoricalFeatureStore(tmp_path / "feature_store.sqlite3")
    store.append_snapshot(snapshot)

    tampered = dict(snapshot)
    tampered["records"] = [dict(snapshot["records"][0], value=9.99)]
    with pytest.raises(FeatureStoreError, match="snapshot_id does not match"):
        store.append_snapshot(tampered)

    connection = sqlite3.connect(tmp_path / "feature_store.sqlite3")
    try:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE snapshots SET manifest_json = '{}' WHERE snapshot_id = ?",
                (snapshot["snapshot_id"],),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM feature_records WHERE snapshot_id = ?",
                (snapshot["snapshot_id"],),
            )
    finally:
        connection.close()


def test_historical_feature_store_rejects_unknown_schema_and_unknown_snapshot(tmp_path):
    database = tmp_path / "feature_store.sqlite3"
    store = HistoricalFeatureStore(database)
    with pytest.raises(FeatureStoreError, match="unknown snapshot_id"):
        store.verify_snapshot("f" * 64)

    connection = sqlite3.connect(database)
    connection.execute("PRAGMA user_version = 99")
    connection.close()
    with pytest.raises(FeatureStoreError, match="unsupported feature-store schema"):
        HistoricalFeatureStore(database)



def test_historical_feature_store_rejects_capture_time_after_store_receipt(tmp_path):
    from datetime import datetime, timedelta, timezone

    future_capture = (
        datetime.now(timezone.utc) + timedelta(seconds=30)
    ).isoformat(timespec="microseconds").replace("+00:00", "Z")
    snapshot = build_feature_snapshot(
        [feature()],
        cutoff_utc="2026-11-04T06:00:00Z",
        captured_at_utc=future_capture,
    )
    store = HistoricalFeatureStore(tmp_path / "future-capture.sqlite3")

    with pytest.raises(FeatureStoreError, match="cannot be later than store receipt"):
        store.append_snapshot(snapshot)


def test_historical_feature_store_verify_detects_record_tampering_after_trigger_removal(tmp_path):
    snapshot = build_feature_snapshot(
        [feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
    )
    database = tmp_path / "tampered-record.sqlite3"
    store = HistoricalFeatureStore(database)
    store.append_snapshot(snapshot)

    connection = sqlite3.connect(database)
    try:
        connection.execute("DROP TRIGGER feature_records_no_update")
        row = connection.execute(
            "SELECT record_json FROM feature_records WHERE snapshot_id = ?",
            (snapshot["snapshot_id"],),
        ).fetchone()
        record = json.loads(row[0])
        record["value"] = 9.99
        connection.execute(
            "UPDATE feature_records SET record_json = ? WHERE snapshot_id = ?",
            (json.dumps(record, sort_keys=True, separators=(",", ":")), snapshot["snapshot_id"]),
        )
        connection.commit()
    finally:
        connection.close()

    verified = store.verify_snapshot(snapshot["snapshot_id"])
    assert verified["valid"] is False
    assert verified["records_ok"] is False
    assert verified["lineage_ok"] is True


def test_historical_feature_store_verify_detects_source_lineage_tampering(tmp_path):
    snapshot = build_feature_snapshot(
        [feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
    )
    database = tmp_path / "tampered-lineage.sqlite3"
    store = HistoricalFeatureStore(database)
    store.append_snapshot(snapshot)

    connection = sqlite3.connect(database)
    try:
        connection.execute("DROP TRIGGER source_snapshots_no_update")
        connection.execute(
            "UPDATE source_snapshots SET raw_content_sha256 = ? WHERE snapshot_id = ?",
            ("c" * 64, snapshot["snapshot_id"]),
        )
        connection.commit()
    finally:
        connection.close()

    verified = store.verify_snapshot(snapshot["snapshot_id"])
    assert verified["valid"] is False
    assert verified["records_ok"] is True
    assert verified["lineage_ok"] is False


@pytest.mark.parametrize(
    ("column", "tampered_value"),
    [
        ("data_cutoff_utc", "2026-11-03T15:00:00.000000Z"),
        ("captured_at_utc", "2026-11-03T16:06:00.000000Z"),
        ("stored_at_utc", "2026-11-03T16:04:00.000000Z"),
        ("asset_scope_json", '["BTC"]'),
    ],
)
def test_historical_feature_store_verify_detects_snapshot_metadata_tampering(
    tmp_path, column, tampered_value
):
    snapshot = build_feature_snapshot(
        [feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
    )
    database = tmp_path / f"tampered-snapshot-{column}.sqlite3"
    store = HistoricalFeatureStore(database)
    store.append_snapshot(snapshot)

    connection = sqlite3.connect(database)
    try:
        connection.execute("DROP TRIGGER snapshots_no_update")
        connection.execute(
            f"UPDATE snapshots SET {column} = ? WHERE snapshot_id = ?",
            (tampered_value, snapshot["snapshot_id"]),
        )
        connection.commit()
    finally:
        connection.close()

    verified = store.verify_snapshot(snapshot["snapshot_id"])
    assert verified["valid"] is False
    assert verified["snapshot_columns_ok"] is False
    assert verified["records_ok"] is True
    assert verified["lineage_ok"] is True


def test_historical_feature_store_as_of_refuses_unverified_manifest_tampering(tmp_path):
    snapshot = build_feature_snapshot(
        [feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
    )
    database = tmp_path / "tampered-manifest-read.sqlite3"
    store = HistoricalFeatureStore(database)
    store.append_snapshot(snapshot)

    connection = sqlite3.connect(database)
    try:
        connection.execute("DROP TRIGGER snapshots_no_update")
        row = connection.execute(
            "SELECT manifest_json FROM snapshots WHERE snapshot_id = ?",
            (snapshot["snapshot_id"],),
        ).fetchone()
        manifest = json.loads(row[0])
        manifest["records"][0]["value"] = 9.99
        connection.execute(
            "UPDATE snapshots SET manifest_json = ? WHERE snapshot_id = ?",
            (
                json.dumps(manifest, sort_keys=True, separators=(",", ":")),
                snapshot["snapshot_id"],
            ),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(FeatureStoreError, match="snapshot integrity verification failed"):
        store.snapshot_as_of("XRP", "2030-01-01T00:00:00Z")
    with pytest.raises(FeatureStoreError, match="snapshot integrity verification failed"):
        store.features_as_of("XRP", "2030-01-01T00:00:00Z")
    with pytest.raises(FeatureStoreError, match="snapshot integrity verification failed"):
        store.source_lineage(snapshot["snapshot_id"])


def test_historical_feature_store_rejects_noncanonical_manifest_record_before_normalizing(tmp_path):
    snapshot = build_feature_snapshot(
        [feature()], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED
    )
    tampered = json.loads(json.dumps(snapshot))
    tampered["records"][0]["asset"] = "xrp"
    manifest_without_id = dict(tampered)
    manifest_without_id.pop("snapshot_id")
    tampered["snapshot_id"] = _sha256(_canonical(manifest_without_id))

    store = HistoricalFeatureStore(tmp_path / "noncanonical-record.sqlite3")
    with pytest.raises(FeatureStoreError, match="canonical normalized form"):
        store.append_snapshot(tampered)


@pytest.mark.parametrize(
    "identity_change",
    [
        {"event_time_utc": "2026-11-03T15:58:00Z"},
        {"feature_name": "perpetual_open_interest"},
        {"unit": "USD/BTC"},
        {"venue": "binance"},
        {"instrument": "XRP-USDT-SWAP"},
        {"currency_pair": "XRP/USDT"},
        {"market_type": "perpetual"},
        {"aggregation_window": "5m"},
    ],
)
def test_revision_cannot_supersede_a_different_event_or_market_identity(identity_change):
    dimensions = {
        "venue": "kraken",
        "instrument": "XRP/USD",
        "currency_pair": "XRP/USD",
        "market_type": "spot",
        "aggregation_window": "1m",
    }
    original = feature(record_id="v1", feature_version=1, **dimensions)
    revised_dimensions = {**dimensions, **identity_change}
    revised = feature(
        record_id="v2",
        feature_version=2,
        revision_status="revised",
        supersedes_record_id="v1",
        **revised_dimensions,
    )
    with pytest.raises(FeatureSnapshotError, match="same feature and asset at the same event time"):
        build_feature_snapshot([original, revised], cutoff_utc=CUTOFF, captured_at_utc=CAPTURED)


def test_historical_feature_store_reconstructs_revisions_at_actual_store_receipt_time(tmp_path):
    from datetime import datetime, timezone

    clock = [datetime.fromisoformat("2026-11-03T16:06:00+00:00")]
    store = HistoricalFeatureStore(
        tmp_path / "cross-run-history.sqlite3",
        clock=lambda: clock[0],
    )
    first = build_feature_snapshot(
        [feature()],
        cutoff_utc=CUTOFF,
        captured_at_utc=CAPTURED,
    )
    store.append_snapshot(first)

    second_record = feature(
        value=1.28,
        source_data_as_of_utc="2026-11-03T16:10:00Z",
        known_at_utc="2026-11-03T16:10:00Z",
        ingested_at_utc="2026-11-03T16:10:02Z",
        revision_available_at_utc="2026-11-03T16:10:02Z",
        sources=[source(digest=HASH_B)],
    )
    second = build_feature_snapshot(
        [second_record],
        cutoff_utc="2026-11-03T16:15:00Z",
        captured_at_utc="2026-11-03T16:15:00Z",
    )
    clock[0] = datetime.fromisoformat("2026-11-03T16:16:00+00:00")
    store.append_snapshot(second)

    before_store_receipt = store.records_through("XRP", "2026-11-03T16:15:59Z")
    assert len(before_store_receipt) == 1
    assert before_store_receipt[0]["value"] == 1.27
    assert store.features_as_of("XRP", "2026-11-03T16:15:59Z")[0]["value"] == 1.27

    complete_history = store.records_through("XRP", "2026-11-03T16:20:00Z")
    assert len(complete_history) == 2
    original = next(item for item in complete_history if item["revision_status"] == "original")
    revised = next(item for item in complete_history if item["revision_status"] == "revised")
    assert original["record_id"] == "xrp:spot:mid:2026-11-03T15:59:00Z:v1"
    assert revised["record_id"] == "xrp:spot:mid:2026-11-03T15:59:00Z:v2"
    assert revised["feature_version"] == 2
    assert revised["supersedes_record_id"] == original["record_id"]
    assert revised["value"] == 1.28
    assert revised["ingested_at_utc"] == "2026-11-03T16:16:00.000000Z"

    as_of_features = store.features_as_of("XRP", "2026-11-03T16:20:00Z")
    assert len(as_of_features) == 1
    assert as_of_features[0]["record_id"] == revised["record_id"]
    assert as_of_features[0]["value"] == 1.28

    assert store.verify_all_snapshots()["valid"] is True
    assert store.snapshot_count() == 2
    assert store.checkpoint()["valid"] is True


def test_future_issuer_row_cannot_be_backdated_to_aggregator_observation_date():
    with pytest.raises(
        FeatureSnapshotError,
        match="source_data_as_of_utc cannot follow revision_available_at_utc",
    ):
        validate_feature_record(
            feature(
                record_id="xrpc:nov6:future-issuer-row",
                feature_id="xrp.etf.xrpc.holdings_delta",
                feature_name="xrpc_holdings_delta",
                value=-752_048,
                unit="XRP",
                event_time_utc="2026-11-06T00:00:00Z",
                known_at_utc="2026-11-07T16:16:09Z",
                source_data_as_of_utc="2026-11-09T00:00:00Z",
                ingested_at_utc="2026-11-07T16:16:10Z",
                revision_available_at_utc="2026-11-07T16:16:09Z",
            ),
            "2026-11-07T17:00:00Z",
            captured_at_utc="2026-11-07T17:05:00Z",
        )
