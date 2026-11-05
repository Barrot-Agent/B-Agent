from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from barrot_agent.evolution.research_eligibility import ResearchEligibilityError, git_blob_sha1
from barrot_agent.evolution.research_timestamp_corrections import (
    apply_capture_time_interval_correction_overlay,
    apply_research_timestamp_correction_overlays,
)


RUN = "2026-11-05T22:04:37Z"
UPPER = "2026-11-05T22:08:06Z"
PERP_UPDATE = "2026-11-05T21:49:00Z"
TRADRADAR_UPDATE = "2026-11-05T21:10:00Z"


def _bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _legacy_documents():
    raw_text = '{"error":[],"result":{"XRPUSD":{"c":["1.22180000"]}}}'
    raw_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    source = {
        "schema_version": "barrot.xrp.market_snapshot.v1",
        "artifact_id": "legacy-capture-source",
        "captured_at_utc": RUN,
        "data_cutoff_utc": RUN,
        "market_snapshot": {
            "kraken_spot": {
                "url": "https://api.kraken.com/0/public/Ticker?pair=XRPUSD",
                "retrieved_at_utc": RUN,
                "raw_response_body_text": raw_text,
                "raw_response_body_text_sha256": raw_hash,
                "market": {"last_trade_usd": 1.2218, "rolling_24h_volume_xrp": 39037780.8669},
            },
            "kraken_perpetuals": {
                "url": "https://www.kraken.com/features/futures/xrp",
                "observed_at_utc": PERP_UPDATE,
                "mark_price_usd": 1.22,
            },
            "tradradar_aggregate": {
                "url": "https://tradradar.io/markets/xrp",
                "observed_at_utc": TRADRADAR_UPDATE,
                "open_interest_usd": 1940000000,
            },
        },
        "etf_flow_reconciliation": {
            "observations": [
                {"source_id": "XRP_INSIGHTS_ETF_20261105", "data_as_of": "2026-11-04", "retrieved_during_run": True, "net_flow_xrp": -259701},
                {"source_id": "ALPHA_FINANCE_XRP_ETF_20261105", "data_through": "2026-11-04", "retrieved_during_run": True, "seven_session_net_flow_usd": 4800000},
            ]
        },
        "sources": [
            {"id": "KRAKEN_XRPUSD_TICKER_20261105T220437Z", "retrieval_time_utc": RUN, "url": "https://api.kraken.com/0/public/Ticker?pair=XRPUSD"},
            {"id": "KRAKEN_XRP_PERP_PAGE_20261105T214900Z", "retrieval_time_utc": RUN, "provider_update_time_utc": PERP_UPDATE, "url": "https://www.kraken.com/features/futures/xrp"},
            {"id": "TRADRADAR_XRP_PERPS_20261105T211000Z", "retrieval_time_utc": RUN, "provider_update_time_utc": TRADRADAR_UPDATE, "url": "https://tradradar.io/markets/xrp"},
            {"id": "XRP_INSIGHTS_ETF_20261105", "retrieval_time_utc": RUN, "data_as_of": "2026-11-04", "url": "https://xrp-insights.com/data"},
            {"id": "ALPHA_FINANCE_XRP_ETF_20261105", "retrieval_time_utc": RUN, "data_through": "2026-11-04", "url": "https://alphafinance.io/etf/xrp/"},
        ],
        "model_admission": {"status": "RESEARCH_ONLY_MODEL_INELIGIBLE", "eligible": False, "directional_forecast_issued": False},
        "preservation": {
            "original_artifacts_modified": False,
            "directional_forecast_issued": False,
            "paper_trade_executed": False,
            "real_money_action": False,
            "external_mutation": False,
        },
    }
    source_bytes = _bytes(source)
    overlay = {
        "schema_version": 1,
        "correction_id": "XRP_CAPTURE_TIME_INTERVAL_20261105T220437Z",
        "artifact_type": "append_only_xrp_research_timestamp_correction",
        "source_artifact_path": "research/xrp_intelligence/legacy-source.json",
        "source_artifact_blob_sha": git_blob_sha1(source_bytes),
        "source_artifact_commit_sha": "b" * 40,
        "original_claimed_captured_at_utc": RUN,
        "run_started_at_utc": RUN,
        "artifact_committed_at_utc": UPPER,
        "exact_retrieval_time_utc": None,
        "retrieval_time_lower_bound_utc": RUN,
        "retrieval_time_upper_bound_utc": UPPER,
        "conservative_known_at_utc": UPPER,
        "superseded_fields": {
            "captured_at_utc": {"old_value": RUN, "corrected_value": None},
            "data_cutoff_utc": {"old_value": RUN, "corrected_value": UPPER},
            "market_snapshot": {
                "kraken_spot": {"retrieved_at_utc": {"old_value": RUN, "corrected_value": None}, "known_at_upper_bound_utc": UPPER},
                "kraken_perpetuals": {"retrieved_at_utc": {"old_value": RUN, "corrected_value": None}, "provider_update_time_utc": PERP_UPDATE},
                "tradradar_aggregate": {"retrieved_at_utc": {"old_value": RUN, "corrected_value": None}, "provider_update_time_utc": TRADRADAR_UPDATE},
            },
            "etf_flow_reconciliation": {
                "XRP_INSIGHTS_ETF_20261105": {"retrieval_time_utc": {"old_value": RUN, "corrected_value": None}, "data_as_of": "2026-11-04"},
                "ALPHA_FINANCE_XRP_ETF_20261105": {"retrieval_time_utc": {"old_value": RUN, "corrected_value": None}, "data_through": "2026-11-04"},
            },
            "sources_retrieval_times": {"all_source_records": "Exact retrieval time unknown; do not interpret run-start timestamp as retrieval time."},
        },
        "preserved_facts": {
            "kraken_response_body_sha256": raw_hash,
            "kraken_response_body_text_preserved": True,
            "provider_event_timestamp_for_kraken_spot": None,
            "kraken_futures_provider_update_time_utc": PERP_UPDATE,
            "tradradar_provider_update_time_utc": TRADRADAR_UPDATE,
            "etf_data_as_of_dates_preserved": True,
            "numeric_market_values_changed": False,
            "source_urls_changed": False,
        },
        "point_in_time_policy": {
            "use_exact_retrieval_time": False,
            "conservative_availability_cutoff_utc": UPPER,
            "may_be_used_for_earlier_cutoffs": False,
            "model_eligible": False,
        },
        "correction_application": {
            "original_artifact_modified": False,
            "append_only_overlay_created": True,
            "automatic_overlay_consumer_present_on_research_branch": False,
            "must_be_reconciled_with_timestamp_consumer_before_any_model_admission": True,
        },
        "directional_forecast_issued": False,
    }
    return source_bytes, overlay, _bytes(overlay)


def _canonical_documents():
    source = {
        "schema_version": "barrot.xrp.market_snapshot.v1",
        "artifact_id": "canonical-correction-source",
        "source_registry": [
            {"source_id": "xrp-insights", "source_event_time_utc": "2026-11-04T21:00:00Z", "raw_response_text_sha256": "a" * 64, "model_eligible": False}
        ],
        "market_snapshot": {"spot": {"last_usd": 1.22}},
        "admission": {"model_eligible": False},
        "forecast": {"issued": False},
    }
    source_bytes = _bytes(source)
    overlay = {
        "schema_version": "barrot.xrp.research-correction.v1",
        "artifact_id": "canonical-timestamp-overlay",
        "artifact_type": "append_only_source_timestamp_semantics_correction",
        "target_artifact": "research/xrp_intelligence/canonical-source.json",
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
            }
        ],
    }
    return source_bytes, _bytes(overlay)


def test_capture_time_overlay_removes_only_synthetic_run_start_and_preserves_provider_data():
    source_bytes, _, overlay_bytes = _legacy_documents()
    result = apply_capture_time_interval_correction_overlay(
        source_artifact_path="research/xrp_intelligence/legacy-source.json",
        source_artifact_bytes=source_bytes,
        overlay_artifact_path="research/xrp_intelligence/legacy-correction.json",
        overlay_artifact_bytes=overlay_bytes,
    )
    corrected = result["corrected_document"]
    assert corrected["captured_at_utc"] is None
    assert corrected["data_cutoff_utc"] == UPPER
    spot = corrected["market_snapshot"]["kraken_spot"]
    assert spot["retrieved_at_utc"] is None
    assert spot["known_at_upper_bound_utc"] == UPPER
    assert spot["raw_response_body_text"] == json.loads(source_bytes)["market_snapshot"]["kraken_spot"]["raw_response_body_text"]
    assert corrected["market_snapshot"]["kraken_perpetuals"]["observed_at_utc"] == PERP_UPDATE
    assert corrected["market_snapshot"]["tradradar_aggregate"]["observed_at_utc"] == TRADRADAR_UPDATE
    assert all(item["retrieval_time_utc"] is None for item in corrected["sources"])
    assert corrected["etf_flow_reconciliation"]["observations"][0]["data_as_of"] == "2026-11-04"
    assert corrected["etf_flow_reconciliation"]["observations"][1]["data_through"] == "2026-11-04"
    assert corrected["market_snapshot"]["kraken_spot"]["market"] == json.loads(source_bytes)["market_snapshot"]["kraken_spot"]["market"]
    assert result["source_artifact_preserved"] is True
    assert result["model_eligible"] is False
    assert result["forecast_issued"] is False
    assert json.loads(source_bytes)["captured_at_utc"] == RUN
    assert result["application_manifest"]["application_status"] == "APPLIED_TO_IN_MEMORY_RESEARCH_VIEW_ONLY"


def test_capture_time_overlay_rejects_wrong_preimage_and_source_retrieval_disagreement():
    source_bytes, overlay, overlay_bytes = _legacy_documents()
    changed = json.loads(source_bytes)
    changed["market_snapshot"]["kraken_spot"]["market"]["last_trade_usd"] = 9.99
    with pytest.raises(ResearchEligibilityError, match="does not match exact source bytes"):
        apply_capture_time_interval_correction_overlay(
            source_artifact_path="research/xrp_intelligence/legacy-source.json",
            source_artifact_bytes=_bytes(changed),
            overlay_artifact_path="research/xrp_intelligence/legacy-correction.json",
            overlay_artifact_bytes=overlay_bytes,
        )
    changed = json.loads(source_bytes)
    changed["sources"][0]["retrieval_time_utc"] = "2026-11-05T22:05:00Z"
    changed_bytes = _bytes(changed)
    overlay["source_artifact_blob_sha"] = git_blob_sha1(changed_bytes)
    with pytest.raises(ResearchEligibilityError, match="retrieval time does not match"):
        apply_capture_time_interval_correction_overlay(
            source_artifact_path="research/xrp_intelligence/legacy-source.json",
            source_artifact_bytes=changed_bytes,
            overlay_artifact_path="research/xrp_intelligence/legacy-correction.json",
            overlay_artifact_bytes=_bytes(overlay),
        )


def test_archive_consumer_applies_both_supported_formats_without_writing_sources(tmp_path):
    archive = tmp_path / "research" / "xrp_intelligence"
    archive.mkdir(parents=True)
    legacy_source, _, legacy_overlay = _legacy_documents()
    canonical_source, canonical_overlay = _canonical_documents()
    (archive / "legacy-source.json").write_bytes(legacy_source)
    (archive / "legacy-correction.json").write_bytes(legacy_overlay)
    (archive / "canonical-source.json").write_bytes(canonical_source)
    (archive / "canonical-correction.json").write_bytes(canonical_overlay)

    result = apply_research_timestamp_correction_overlays(tmp_path)

    assert result["overlay_count"] == 2
    assert result["source_artifacts_modified"] is False
    assert result["model_eligible"] is False
    assert result["forecast_issued"] is False
    assert result["corrected_artifacts"]["research/xrp_intelligence/legacy-source.json"]["captured_at_utc"] is None
    canonical = result["corrected_artifacts"]["research/xrp_intelligence/canonical-source.json"]
    assert canonical["source_registry"][0]["source_event_time_utc"] is None
    assert canonical["source_registry"][0]["source_event_date"] == "2026-11-04"
    assert (archive / "legacy-source.json").read_bytes() == legacy_source
    assert (archive / "canonical-source.json").read_bytes() == canonical_source


def test_archive_consumer_fails_closed_on_missing_target_duplicate_target_and_unknown_schema(tmp_path):
    archive = tmp_path / "research" / "xrp_intelligence"
    archive.mkdir(parents=True)
    legacy_source, _, legacy_overlay = _legacy_documents()
    overlay = json.loads(legacy_overlay)
    overlay["source_artifact_path"] = "research/xrp_intelligence/missing-source.json"
    (archive / "missing-correction.json").write_bytes(_bytes(overlay))
    with pytest.raises(ResearchEligibilityError, match="missing or escapes"):
        apply_research_timestamp_correction_overlays(tmp_path)

    (archive / "missing-correction.json").unlink()
    (archive / "legacy-source.json").write_bytes(legacy_source)
    overlay["source_artifact_path"] = "research/xrp_intelligence/legacy-source.json"
    overlay["source_artifact_blob_sha"] = git_blob_sha1(legacy_source)
    (archive / "correction-a.json").write_bytes(_bytes(overlay))
    duplicate_overlay = dict(overlay)
    duplicate_overlay["correction_id"] = "XRP_CAPTURE_TIME_INTERVAL_DUPLICATE"
    (archive / "correction-b.json").write_bytes(_bytes(duplicate_overlay))
    with pytest.raises(ResearchEligibilityError, match="multiple timestamp overlays"):
        apply_research_timestamp_correction_overlays(tmp_path)

    (archive / "correction-a.json").unlink()
    (archive / "correction-b.json").unlink()
    (archive / "unknown-timestamp-correction.json").write_bytes(
        _bytes({"schema_version": 2, "artifact_type": "xrp_timestamp_correction_v2"})
    )
    with pytest.raises(ResearchEligibilityError, match="unsupported timestamp correction schema"):
        apply_research_timestamp_correction_overlays(tmp_path)
