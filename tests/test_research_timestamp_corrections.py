from __future__ import annotations

import json

import pytest

from barrot_agent.evolution.research_eligibility import ResearchEligibilityError, git_blob_sha1
from barrot_agent.evolution.research_timestamp_corrections import apply_source_timestamp_correction_overlay


def _bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _documents():
    source = {
        "schema_version": "barrot.xrp.market_snapshot.v1",
        "artifact_id": "timestamp-correction-source-fixture",
        "source_registry": [
            {
                "source_id": "xrp-insights",
                "source_event_time_utc": "2026-11-04T21:00:00Z",
                "raw_response_text_sha256": "a" * 64,
                "model_eligible": False,
            },
            {
                "source_id": "cryptokeyhole",
                "page_checked_at_utc": "2026-11-05T03:04:00Z",
                "raw_response_text_sha256": "b" * 64,
                "model_eligible": False,
            },
        ],
        "market_snapshot": {"spot": {"last_usd": 1.23363}, "etf_flows": [{"flow_xrp": -64826}]},
        "admission": {"model_eligible": False, "forecast_eligible": False},
        "forecast": {"issued": False, "directional": False},
    }
    source_bytes = _bytes(source)
    overlay = {
        "schema_version": "barrot.xrp.research-correction.v1",
        "artifact_id": "timestamp-correction-overlay-fixture",
        "artifact_type": "append_only_source_timestamp_semantics_correction",
        "target_artifact": "research/xrp_intelligence/source-market-snapshot.json",
        "target_artifact_blob_sha": git_blob_sha1(source_bytes),
        "model_eligible": False,
        "forecast_issued": False,
        "preservation": {
            "target_artifact_modified": False,
            "raw_source_text_hashes_modified": False,
            "correction_mode": "append_only_field_overlay",
            "forecast_issued": False,
            "model_eligible": False,
        },
        "field_corrections": [
            {
                "source_id": "xrp-insights",
                "target_field": "source_event_time_utc",
                "expected_original_value": "2026-11-04T21:00:00Z",
                "replacement_value": None,
                "canonical_field": "source_event_date",
                "canonical_field_value": "2026-11-04",
                "reason": "The publisher supplies a trading date, not an exact event time.",
                "model_eligible": False,
            },
            {
                "source_id": "cryptokeyhole",
                "target_field": "page_checked_at_utc",
                "expected_original_value": "2026-11-05T03:04:00Z",
                "replacement_value": None,
                "canonical_field": "issuer_file_timestamps_utc",
                "canonical_field_value": {
                    "XRP": "2026-11-05T03:04:00Z",
                    "XRPZ": {
                        "start": "2026-11-04T23:42:00Z",
                        "end": "2026-11-04T23:47:00Z",
                    },
                },
                "reason": "The timestamp belongs to one issuer file, not the page retrieval.",
                "model_eligible": False,
            },
        ],
    }
    return source_bytes, overlay, _bytes(overlay)


def _apply(source_bytes, overlay_bytes, source_path="research/xrp_intelligence/source-market-snapshot.json"):
    return apply_source_timestamp_correction_overlay(
        source_artifact_path=source_path,
        source_artifact_bytes=source_bytes,
        overlay_artifact_path="research/xrp_intelligence/source-market-snapshot-correction.json",
        overlay_artifact_bytes=overlay_bytes,
    )


def test_overlay_applies_only_preimage_bound_date_and_issuer_timestamp_corrections():
    source_bytes, _, overlay_bytes = _documents()
    result = _apply(source_bytes, overlay_bytes)
    corrected = result["corrected_document"]
    sources = {item["source_id"]: item for item in corrected["source_registry"]}
    assert sources["xrp-insights"]["source_event_time_utc"] is None
    assert sources["xrp-insights"]["source_event_date"] == "2026-11-04"
    assert sources["cryptokeyhole"]["page_checked_at_utc"] is None
    assert sources["cryptokeyhole"]["issuer_file_timestamps_utc"]["XRP"] == "2026-11-05T03:04:00Z"
    assert sources["cryptokeyhole"]["issuer_file_timestamps_utc"]["XRPZ"]["start"] == "2026-11-04T23:42:00Z"
    assert corrected["market_snapshot"] == json.loads(source_bytes)["market_snapshot"]
    assert result["source_artifact_preserved"] is True
    assert result["model_eligible"] is False
    assert result["forecast_issued"] is False
    assert corrected["admission"]["model_eligible"] is False
    assert corrected["forecast"]["issued"] is False
    assert result["application_manifest"]["application_status"] == "APPLIED_TO_IN_MEMORY_RESEARCH_VIEW_ONLY"
    assert result["application_manifest"]["target_git_blob_sha1"] == git_blob_sha1(source_bytes)
    assert json.loads(source_bytes)["source_registry"][0]["source_event_time_utc"] == "2026-11-04T21:00:00Z"


def test_overlay_rejects_a_different_target_preimage():
    source_bytes, _, overlay_bytes = _documents()
    changed = json.loads(source_bytes)
    changed["market_snapshot"]["spot"]["last_usd"] = 9.99
    with pytest.raises(ResearchEligibilityError, match="does not match exact source bytes"):
        _apply(_bytes(changed), overlay_bytes)


def test_overlay_rejects_expected_original_value_mismatch():
    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"][0]["expected_original_value"] = "2026-11-04T20:00:00Z"
    with pytest.raises(ResearchEligibilityError, match="does not match the declared preimage"):
        _apply(source_bytes, _bytes(overlay))


def test_overlay_rejects_unknown_source_ids_and_duplicate_targets():
    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"][0]["source_id"] = "unknown-source"
    with pytest.raises(ResearchEligibilityError, match="unknown source_id"):
        _apply(source_bytes, _bytes(overlay))

    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"].append(dict(overlay["field_corrections"][0]))
    with pytest.raises(ResearchEligibilityError, match="duplicate source/field"):
        _apply(source_bytes, _bytes(overlay))


def test_overlay_rejects_non_timestamp_fields_and_timestamp_promotion():
    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"][0]["target_field"] = "last_usd"
    with pytest.raises(ResearchEligibilityError, match="non-allowlisted"):
        _apply(source_bytes, _bytes(overlay))

    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"][0]["replacement_value"] = "2026-11-04T21:00:00Z"
    with pytest.raises(ResearchEligibilityError, match="only remove unsupported"):
        _apply(source_bytes, _bytes(overlay))

    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"][0]["model_eligible"] = True
    with pytest.raises(ResearchEligibilityError, match="may not promote"):
        _apply(source_bytes, _bytes(overlay))


def test_overlay_rejects_invalid_calendar_dates_and_unanchored_issuer_times():
    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"][0]["canonical_field_value"] = "2026-11-05"
    with pytest.raises(ResearchEligibilityError, match="must match the removed timestamp"):
        _apply(source_bytes, _bytes(overlay))

    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"][0]["canonical_field_value"] = "2026-02-30"
    with pytest.raises(ResearchEligibilityError, match="ISO calendar date"):
        _apply(source_bytes, _bytes(overlay))

    source_bytes, overlay, _ = _documents()
    overlay["field_corrections"][1]["canonical_field_value"]["XRPZ"]["start"] = "2026-11-04T23:42:00"
    with pytest.raises(ResearchEligibilityError, match="include a timezone"):
        _apply(source_bytes, _bytes(overlay))


def test_overlay_requires_explicitly_ineligible_no_forecast_source():
    source_bytes, overlay, _ = _documents()
    source = json.loads(source_bytes)
    source["admission"]["model_eligible"] = True
    source_bytes = _bytes(source)
    overlay["target_artifact_blob_sha"] = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="model-eligible"):
        _apply(source_bytes, _bytes(overlay))

    source_bytes, overlay, _ = _documents()
    source = json.loads(source_bytes)
    source["forecast"]["issued"] = True
    source_bytes = _bytes(source)
    overlay["target_artifact_blob_sha"] = git_blob_sha1(source_bytes)
    with pytest.raises(ResearchEligibilityError, match="no forecast was issued"):
        _apply(source_bytes, _bytes(overlay))


def test_overlay_rejects_reapplication_to_a_changed_copy_and_invalid_preservation_flags():
    source_bytes, overlay, overlay_bytes = _documents()
    result = _apply(source_bytes, overlay_bytes)
    corrected_bytes = _bytes(result["corrected_document"])
    with pytest.raises(ResearchEligibilityError, match="does not match exact source bytes"):
        _apply(corrected_bytes, overlay_bytes)

    source_bytes, overlay, _ = _documents()
    overlay["preservation"]["raw_source_text_hashes_modified"] = True
    with pytest.raises(ResearchEligibilityError, match="must preserve source, raw hashes"):
        _apply(source_bytes, _bytes(overlay))
