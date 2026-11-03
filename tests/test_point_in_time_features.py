from __future__ import annotations

import pytest

from barrot_agent.evolution.point_in_time_features import (
    FeatureSnapshotError,
    build_feature_snapshot,
    independent_source_groups,
    validate_feature_record,
)

CUTOFF = "2026-11-03T16:00:00Z"
CAPTURED = "2026-11-03T16:05:00Z"
HASH_A = "a" * 64
HASH_B = "b" * 64


def source(source_id="provider-a", group="exchange-a", digest=HASH_A):
    return {
        "source_id": source_id,
        "independence_group": group,
        "source_uri": "https://example.com/public-data",
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
