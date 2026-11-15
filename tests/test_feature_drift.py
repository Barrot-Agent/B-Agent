from __future__ import annotations

import hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest

from barrot_agent.evolution.feature_drift import (
    FeatureDriftError,
    monitor_feature_drift,
)
from barrot_agent.evolution.xrp_public_ingestion import run_ingestion


ROOT = Path(__file__).resolve().parents[1]
CUTOFF = datetime(2026, 11, 6, 0, 0, tzinfo=timezone.utc)


def _stamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _record(index, value, event_time, *, group="kraken", ingested_at=None, feature_id="xrp.spot.mid_price"):
    ingested = ingested_at or event_time + timedelta(minutes=1)
    raw = f"{group}:{index}".encode()
    return {
        "record_id": f"{feature_id}:{index}",
        "feature_id": feature_id,
        "feature_version": 1,
        "asset": "XRP",
        "feature_name": "spot_mid_price",
        "value": value,
        "unit": "USD/XRP",
        "event_time_utc": _stamp(event_time),
        "known_at_utc": _stamp(event_time),
        "source_data_as_of_utc": _stamp(event_time),
        "ingested_at_utc": _stamp(ingested),
        "revision_available_at_utc": _stamp(ingested),
        "sources": [{
            "source_id": f"{group}-{index}",
            "independence_group": group,
            "source_uri": f"https://{group}.example/xrp",
            "raw_content_sha256": hashlib.sha256(raw).hexdigest(),
        }],
        "quality_status": "verified",
        "model_eligible": True,
        "eligibility_reason": "",
        "revision_status": "original",
        "supersedes_record_id": None,
        "adapter_version": "test-v1",
        "parser_version": "test-v1",
        "limitations": [],
        "disconfirming_evidence_ids": [],
        "venue": "composite",
        "currency_pair": "XRP/USD",
        "market_type": "spot",
        "aggregation_window": "1h",
    }


def _windows(reference_values=None, current_values=None, *, reference_group="kraken", current_group="kraken"):
    reference_values = reference_values or [1.0 + (index % 3 - 1) * 0.01 for index in range(30)]
    current_values = current_values or [1.0 + (index % 3 - 1) * 0.01 for index in range(30)]
    reference_end = CUTOFF - timedelta(days=7)
    reference_start = reference_end - timedelta(days=30)
    records = []
    for index, value in enumerate(reference_values):
        event = reference_start + timedelta(days=index)
        records.append(_record(index, value, event, group=reference_group))
    for index, value in enumerate(current_values):
        event = reference_end + timedelta(hours=index * 5)
        records.append(_record(100 + index, value, event, group=current_group))
    return records, reference_end


def test_stable_distribution_returns_diagnostic_only_stable_report():
    records, _ = _windows()
    report = monitor_feature_drift(records, cutoff_utc=_stamp(CUTOFF))
    assert report["status"] == "STABLE"
    assert report["evaluated_feature_count"] == 1
    assert report["feature_results"][0]["reference_sample_count"] == 30
    assert report["feature_results"][0]["current_sample_count"] == 30
    assert report["model_eligible"] is False
    assert report["forecast_issuance_allowed"] is False
    assert len(report["report_sha256"]) == 64


def test_large_distribution_shift_triggers_drift():
    records, _ = _windows(current_values=[2.0 + index * 0.001 for index in range(30)])
    report = monitor_feature_drift(records, cutoff_utc=_stamp(CUTOFF))
    assert report["status"] == "DRIFT"
    assert report["feature_results"][0]["psi"] >= 0.25
    assert report["forecast_issuance_allowed"] is False


def test_source_mix_shift_is_reported_separately_from_value_psi():
    records, _ = _windows(reference_group="kraken", current_group="coinbase")
    report = monitor_feature_drift(records, cutoff_utc=_stamp(CUTOFF))
    result = report["feature_results"][0]
    assert result["source_mix_psi"] is not None
    assert result["source_mix_psi"] >= 0.25
    assert result["status"] == "DRIFT"


def test_late_backfilled_reference_records_are_excluded_not_backdated():
    records, reference_end = _windows()
    records[0]["ingested_at_utc"] = _stamp(reference_end + timedelta(minutes=1))
    records[0]["revision_available_at_utc"] = records[0]["ingested_at_utc"]
    report = monitor_feature_drift(
        records,
        cutoff_utc=_stamp(CUTOFF),
        min_samples_per_window=30,
    )
    result = report["feature_results"][0]
    assert result["reference_sample_count"] == 29
    assert report["late_reference_record_exclusion_count"] == 1
    assert report["status"] == "INSUFFICIENT_DATA"
    assert report["forecast_issuance_allowed"] is False


def test_records_not_available_by_current_cutoff_are_excluded():
    records, _ = _windows()
    records[-1]["ingested_at_utc"] = _stamp(CUTOFF + timedelta(minutes=1))
    records[-1]["revision_available_at_utc"] = records[-1]["ingested_at_utc"]
    report = monitor_feature_drift(records, cutoff_utc=_stamp(CUTOFF))
    assert report["excluded_ineligible_record_count"] == 1
    assert report["feature_results"][0]["current_sample_count"] == 29
    assert report["status"] == "INSUFFICIENT_DATA"


def test_empty_history_fails_closed_as_insufficient_data():
    report = monitor_feature_drift([], cutoff_utc=_stamp(CUTOFF))
    assert report["status"] == "INSUFFICIENT_DATA"
    assert report["feature_results"] == []
    assert report["forecast_issuance_allowed"] is False


def test_invalid_cutoffs_and_thresholds_are_rejected():
    with pytest.raises(FeatureDriftError, match="timezone-aware"):
        monitor_feature_drift([], cutoff_utc="2026-11-06T00:00:00")
    with pytest.raises(FeatureDriftError, match="warning_psi"):
        monitor_feature_drift([], cutoff_utc=_stamp(CUTOFF), warning_psi=0.3, drift_psi=0.2)


def test_scheduled_ingestion_writes_a_read_only_drift_report(tmp_path):
    def unavailable(_source_id, _url):
        raise OSError("test-only provider unavailable")

    summary = run_ingestion(
        tmp_path,
        fetcher=unavailable,
        now=CUTOFF,
    )
    report_path = tmp_path / "drift_report.json"
    assert report_path.exists()
    report = __import__("json").loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "INSUFFICIENT_DATA"
    assert report["forecast_issuance_allowed"] is False
    assert summary["drift_status"] == "INSUFFICIENT_DATA"
    assert summary["drift_report_retention_days"] == 90
    assert summary["drift_report_sha256"] == report["report_sha256"]
    assert summary["forecast_status"] == "NOT_ISSUED"


def test_drift_report_is_uploaded_with_ninety_day_retention():
    workflow = (ROOT / ".github" / "workflows" / "xrp-public-ingestion.yml").read_text(encoding="utf-8")
    assert "artifacts/xrp_ingestion/drift_report.json" in workflow
    assert "retention-days: 90" in workflow
