from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import pytest

from barrot_agent.evolution.feature_store import HistoricalFeatureStore
from barrot_agent.evolution.point_in_time_features import FeatureSnapshotError
from barrot_agent.evolution.research_eligibility import (
    ResearchEligibilityError,
    build_feature_snapshot_with_research_overlay,
    git_blob_sha1,
)

SOURCE_PATH = "research/xrp_intelligence/source.json"
OVERLAY_PATH = "research/xrp_intelligence/overlay.json"
CUTOFF = "2026-11-04T12:00:00.000000Z"
CAPTURED = "2026-11-04T12:01:00.000000Z"
RAW_RECEIPT_BYTES = b'{"asset":"XRP","price_usd":1.25,"venue":"primary-provider"}'
RAW_RECEIPT_SHA256 = hashlib.sha256(RAW_RECEIPT_BYTES).hexdigest()


def _bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


RAW_RECEIPT_PAYLOAD = {
    "source_id": "primary-provider",
    "source_uri": "https://example.com/xrp",
    "captured_at_utc": "2026-11-04T11:59:02Z",
    "source_data_as_of_utc": "2026-11-04T11:59:00Z",
    "source_http_date": None,
    "raw_content_sha256": RAW_RECEIPT_SHA256,
    "payload_size_bytes": len(RAW_RECEIPT_BYTES),
    "raw_payload_path": f"raw/sha256/{RAW_RECEIPT_SHA256}.json",
    "model_eligible_source": True,
    "raw_only_reason": "",
}
RAW_RECEIPT_ID = hashlib.sha256(_bytes(RAW_RECEIPT_PAYLOAD)).hexdigest()
RAW_RECEIPT = {**RAW_RECEIPT_PAYLOAD, "receipt_id": RAW_RECEIPT_ID}


def _documents(corrections=None):
    source = {
        "schema_version": 1,
        "model_eligible": True,
        "quality_status": "verified",
        "source_registry": [
            {
                "source_id": "primary-provider",
                "raw_receipt_id": RAW_RECEIPT_ID,
                "raw_receipt": RAW_RECEIPT,
                "raw_content_sha256": RAW_RECEIPT_SHA256,
                "raw_capture_status": "byte_complete",
                "independence_group": "primary-provider",
                "source_uri": "https://example.com/xrp",
                "source_data_as_of_utc": "2026-11-04T11:59:00Z",
                "captured_at_utc": "2026-11-04T11:59:02Z",
            }
        ],
        "observations": [
            {
                "observation_id": "blocked-observation",
                "model_eligible": True,
                "quality_status": "verified",
                "source_ids": ["primary-provider"],
                "source_independence_groups": ["primary-provider"],
                "event_time_utc": "2026-11-04T11:59:00Z",
                "known_at_utc": "2026-11-04T11:59:01Z",
                "source_data_as_of_utc": "2026-11-04T11:59:00Z",
            },
            {
                "observation_id": "eligible-observation",
                "model_eligible": True,
                "quality_status": "verified",
                "source_ids": ["primary-provider"],
                "source_independence_groups": ["primary-provider"],
                "event_time_utc": "2026-11-04T11:59:00Z",
                "known_at_utc": "2026-11-04T11:59:01Z",
                "source_data_as_of_utc": "2026-11-04T11:59:00Z",
            },
        ],
    }
    source_bytes = _bytes(source)
    overlay = {
        "schema_version": "barrot.xrp.research-correction.v1",
        "artifact_id": "eligibility-overlay-test",
        "artifact_type": "append_only_observation_eligibility_correction",
        "source_artifact": SOURCE_PATH,
        "source_artifact_blob_sha": git_blob_sha1(source_bytes),
        "preservation": {
            "source_artifact_modified": False,
            "raw_source_receipts_modified": False,
            "correction_mode": "append_only_observation_overlay",
            "forecast_issued": False,
            "consumer_application_status": "NOT_EXECUTED",
        },
        "correction": {
            "observations": corrections if corrections is not None else [
                {
                    "observation_id": "blocked-observation",
                    "model_eligible": False,
                    "reason": "Secondary observation has no synchronized primary-source receipt.",
                }
            ]
        },
    }
    return source_bytes, overlay, _bytes(overlay)


def _feature(observation_id, source_sha, **updates):
    record = {
        "research_observation_id": observation_id,
        "source_artifact_path": SOURCE_PATH,
        "source_artifact_blob_sha": source_sha,
        "record_id": f"record:{observation_id}",
        "feature_id": f"xrp.research.{observation_id}",
        "feature_version": 1,
        "asset": "XRP",
        "feature_name": "research_observation",
        "value": 1.25,
        "unit": "USD",
        "event_time_utc": "2026-11-04T11:59:00Z",
        "known_at_utc": "2026-11-04T11:59:01Z",
        "source_data_as_of_utc": "2026-11-04T11:59:00Z",
        "ingested_at_utc": "2026-11-04T11:59:02Z",
        "revision_available_at_utc": "2026-11-04T11:59:01Z",
        "sources": [
            {
                "source_id": "primary-provider",
                "independence_group": "primary-provider",
                "source_uri": "https://example.com/xrp",
                "raw_content_sha256": RAW_RECEIPT_SHA256,
            }
        ],
        "quality_status": "verified",
        "model_eligible": True,
        "eligibility_reason": "",
        "revision_status": "original",
        "supersedes_record_id": None,
        "adapter_version": "research-adapter-v1",
        "parser_version": "research-parser-v1",
        "limitations": [],
        "disconfirming_evidence_ids": [],
    }
    record.update(updates)
    return record


def _build(records, source_bytes, overlay, overlay_bytes, raw_receipt_bytes=None):
    return build_feature_snapshot_with_research_overlay(
        records,
        overlay=overlay,
        source_artifact_path=SOURCE_PATH,
        source_artifact_bytes=source_bytes,
        overlay_artifact_path=OVERLAY_PATH,
        overlay_artifact_bytes=overlay_bytes,
        raw_receipt_bytes=(
            {RAW_RECEIPT_ID: RAW_RECEIPT_BYTES}
            if raw_receipt_bytes is None
            else raw_receipt_bytes
        ),
        cutoff_utc=CUTOFF,
        captured_at_utc=CAPTURED,
        asset_scope=["XRP"],
    )


def test_overlay_downgrades_exact_observation_and_snapshot_commits_overlay_provenance(tmp_path):
    source_bytes, overlay, overlay_bytes = _documents()
    source_sha = git_blob_sha1(source_bytes)
    snapshot = _build(
        [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
        source_bytes,
        overlay,
        overlay_bytes,
    )

    assert snapshot["input_record_count"] == 2
    assert snapshot["eligible_record_count"] == 1
    assert [record["record_id"] for record in snapshot["records"]] == ["record:eligible-observation"]
    assert snapshot["excluded_records"] == [
        {"record_id": "record:blocked-observation", "reasons": ["record_marked_ineligible"]}
    ]
    applied = snapshot["research_eligibility_overlays"][0]
    assert applied["application_status"] == "APPLIED_BEFORE_POINT_IN_TIME_VALIDATION"
    assert applied["corrections"][0]["observation_id"] == "blocked-observation"
    assert applied["corrections"][0]["model_eligible"] is False
    assert applied["corrections"][0]["reason"].startswith("Secondary observation")
    assert snapshot["research_source_receipts"] == [
        {
            "source_id": "primary-provider",
            "raw_receipt_id": RAW_RECEIPT_ID,
            "raw_content_sha256": RAW_RECEIPT_SHA256,
            "raw_capture_status": "byte_complete",
            "raw_receipt_sha256_verified": True,
            "independence_group": "primary-provider",
            "source_uri": "https://example.com/xrp",
            "source_data_as_of_utc": "2026-11-04T11:59:00Z",
            "captured_at_utc": "2026-11-04T11:59:02Z",
        }
    ]

    store = HistoricalFeatureStore(
        tmp_path / "features.sqlite3",
        clock=lambda: datetime(2026, 11, 4, 12, 2, tzinfo=timezone.utc),
    )
    receipt = store.append_snapshot(snapshot)
    assert receipt["created"] is True
    assert store.verify_snapshot(snapshot["snapshot_id"])["valid"] is True


def test_all_corrected_records_fail_closed_without_a_model_facing_snapshot():
    source_bytes, overlay, _ = _documents([
        {"observation_id": "blocked-observation", "model_eligible": False, "reason": "No receipt."},
        {"observation_id": "eligible-observation", "model_eligible": False, "reason": "No primary reconciliation."},
    ])
    overlay_bytes = _bytes(overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(FeatureSnapshotError, match="no point-in-time eligible records"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes,
            overlay,
            overlay_bytes,
        )


def test_overlay_rejects_a_mismatched_source_blob_sha():
    source_bytes, overlay, _ = _documents()
    overlay["source_artifact_blob_sha"] = "0" * 40
    overlay_bytes = _bytes(overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="does not match exact source bytes"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes,
            overlay,
            overlay_bytes,
        )


def test_overlay_cannot_promote_an_observation_to_model_eligible():
    source_bytes, overlay, _ = _documents([
        {"observation_id": "blocked-observation", "model_eligible": True, "reason": "Attempted promotion."}
    ])
    overlay_bytes = _bytes(overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="downgrade eligibility only"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes,
            overlay,
            overlay_bytes,
        )


def test_overlay_rejects_unknown_or_unmapped_observation_ids():
    source_bytes, overlay, _ = _documents([
        {"observation_id": "not-in-source", "model_eligible": False, "reason": "Unknown."}
    ])
    overlay_bytes = _bytes(overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="unknown source observation"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes,
            overlay,
            overlay_bytes,
        )

    source_bytes, overlay, _ = _documents()
    overlay_bytes = _bytes(overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="lack exactly mapped feature records"):
        _build([_feature("eligible-observation", source_sha)], source_bytes, overlay, overlay_bytes)


def test_overlay_rejects_mutated_source_preservation_declarations():
    source_bytes, overlay, _ = _documents()
    overlay["preservation"]["source_artifact_modified"] = True
    overlay_bytes = _bytes(overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="preserve the original source artifact"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes,
            overlay,
            overlay_bytes,
        )


def test_feature_records_must_bind_to_exact_source_artifact_and_blob():
    source_bytes, overlay, overlay_bytes = _documents()
    source_sha = git_blob_sha1(source_bytes)
    wrong = _feature("blocked-observation", "f" * 40)
    with pytest.raises(ResearchEligibilityError, match="not bound to the exact source blob"):
        _build([wrong, _feature("eligible-observation", source_sha)], source_bytes, overlay, overlay_bytes)


def test_overlay_bytes_must_match_the_supplied_overlay_mapping():
    source_bytes, overlay, overlay_bytes = _documents()
    changed_bytes = overlay_bytes.replace(b"Secondary observation", b"Altered observation")
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="mapping does not match"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes,
            overlay,
            changed_bytes,
        )


def _rebind_source_document(source, overlay):
    source_bytes = _bytes(source)
    overlay["source_artifact_blob_sha"] = git_blob_sha1(source_bytes)
    return source_bytes, overlay, _bytes(overlay)


def test_source_artifact_must_be_explicitly_eligible_and_verified():
    source_bytes, overlay, _ = _documents()
    source = json.loads(source_bytes)
    source["model_eligible"] = False
    source_bytes, overlay, overlay_bytes = _rebind_source_document(source, overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="not explicitly model eligible"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes, overlay, overlay_bytes
        )

    source = json.loads(source_bytes)
    source["model_eligible"] = True
    source["quality_status"] = "provisional"
    source_bytes, overlay, overlay_bytes = _rebind_source_document(source, overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="quality_status must be verified"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes, overlay, overlay_bytes
        )


def test_source_observation_must_be_explicitly_eligible_and_verified():
    source_bytes, overlay, _ = _documents()
    source = json.loads(source_bytes)
    source["observations"][0]["model_eligible"] = False
    source_bytes, overlay, overlay_bytes = _rebind_source_document(source, overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="not explicitly model eligible"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes, overlay, overlay_bytes
        )

    source["observations"][0]["model_eligible"] = True
    source["observations"][0]["quality_status"] = "unverified"
    source_bytes, overlay, overlay_bytes = _rebind_source_document(source, overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="quality_status must be verified"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes, overlay, overlay_bytes
        )


def test_source_receipt_must_be_byte_complete_and_feature_lineage_must_match():
    source_bytes, overlay, _ = _documents()
    source = json.loads(source_bytes)
    source["source_registry"][0]["raw_capture_status"] = "web_rendered_extract_only"
    source_bytes, overlay, overlay_bytes = _rebind_source_document(source, overlay)
    source_sha = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="must be byte_complete"):
        _build(
            [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)],
            source_bytes, overlay, overlay_bytes
        )

    source_bytes, overlay, overlay_bytes = _documents()
    source_sha = git_blob_sha1(source_bytes)
    mismatched = _feature(
        "blocked-observation",
        source_sha,
        sources=[{
            "source_id": "primary-provider",
            "independence_group": "primary-provider",
            "source_uri": "https://example.com/other",
            "raw_content_sha256": RAW_RECEIPT_SHA256,
        }],
    )
    with pytest.raises(ResearchEligibilityError, match="source URI does not match receipt"):
        _build(
            [mismatched, _feature("eligible-observation", source_sha)],
            source_bytes, overlay, overlay_bytes
        )


def test_feature_record_event_and_source_cutoff_must_match_observation():
    source_bytes, overlay, overlay_bytes = _documents()
    source_sha = git_blob_sha1(source_bytes)
    mismatched = _feature(
        "blocked-observation",
        source_sha,
        event_time_utc="2026-11-04T11:58:00Z",
    )
    with pytest.raises(ResearchEligibilityError, match="event time does not match"):
        _build(
            [mismatched, _feature("eligible-observation", source_sha)],
            source_bytes, overlay, overlay_bytes
        )


def test_raw_receipt_bytes_are_required_and_must_match_sha256():
    source_bytes, overlay, overlay_bytes = _documents()
    source_sha = git_blob_sha1(source_bytes)
    records = [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)]

    with pytest.raises(ResearchEligibilityError, match="raw receipt bytes are missing"):
        _build(records, source_bytes, overlay, overlay_bytes, raw_receipt_bytes={})

    with pytest.raises(ResearchEligibilityError, match="do not match raw_content_sha256"):
        _build(
            records,
            source_bytes,
            overlay,
            overlay_bytes,
            raw_receipt_bytes={RAW_RECEIPT_ID: b'{"asset":"XRP","price_usd":0.0}'},
        )



def test_raw_receipt_id_is_recomputed_from_complete_canonical_metadata():
    source_bytes, overlay, _ = _documents()
    source = json.loads(source_bytes)
    source["source_registry"][0]["raw_receipt"]["receipt_id"] = "0" * 64
    source_bytes, overlay, overlay_bytes = _rebind_source_document(source, overlay)
    source_sha = git_blob_sha1(source_bytes)
    records = [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)]

    with pytest.raises(ResearchEligibilityError, match="canonical receipt metadata"):
        _build(records, source_bytes, overlay, overlay_bytes)


def test_raw_receipt_registry_metadata_must_match_canonical_receipt():
    source_bytes, overlay, _ = _documents()
    source = json.loads(source_bytes)
    source["source_registry"][0]["source_uri"] = "https://example.com/other"
    source_bytes, overlay, overlay_bytes = _rebind_source_document(source, overlay)
    source_sha = git_blob_sha1(source_bytes)
    records = [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)]

    with pytest.raises(ResearchEligibilityError, match="source_uri does not match its canonical receipt"):
        _build(records, source_bytes, overlay, overlay_bytes)


def test_raw_receipt_path_must_be_content_addressed_to_verified_payload():
    source_bytes, overlay, _ = _documents()
    source = json.loads(source_bytes)
    receipt = source["source_registry"][0]["raw_receipt"]
    receipt_payload = {key: value for key, value in receipt.items() if key != "receipt_id"}
    receipt_payload["raw_payload_path"] = "raw/sha256/" + ("0" * 64) + ".json"
    receipt["raw_payload_path"] = receipt_payload["raw_payload_path"]
    receipt_id = hashlib.sha256(_bytes(receipt_payload)).hexdigest()
    receipt["receipt_id"] = receipt_id
    source["source_registry"][0]["raw_receipt_id"] = receipt_id
    source_bytes, overlay, overlay_bytes = _rebind_source_document(source, overlay)
    source_sha = git_blob_sha1(source_bytes)
    records = [_feature("blocked-observation", source_sha), _feature("eligible-observation", source_sha)]

    with pytest.raises(ResearchEligibilityError, match="not bound to the content-addressed payload"):
        _build(
            records,
            source_bytes,
            overlay,
            overlay_bytes,
            raw_receipt_bytes={receipt_id: RAW_RECEIPT_BYTES},
        )
