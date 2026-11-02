from pathlib import Path

import pytest

from barrot_agent.analysis.xrp_telemetry_matrix import (
    EvidenceError,
    render_report,
    validate_snapshot,
    write_report,
)


def not_issued():
    return {
        "schema_version": "1.0",
        "snapshot_id": "xrp-not-issued",
        "captured_at_utc": "2026-11-02T14:00:00Z",
        "data_cutoff_utc": "2026-11-02T13:59:00Z",
        "sources": [],
        "market_observations": [],
        "forecast": {
            "status": "NOT_ISSUED",
            "reason": "Independent evaluation attestation is not available.",
        },
    }


def self_attested_issued():
    snapshot = not_issued()
    snapshot["snapshot_id"] = "xrp-self-attested"
    snapshot["sources"] = [
        {
            "source_id": "a",
            "publisher": "Publisher A",
            "url": "https://a.example/feed",
            "retrieved_at_utc": "2026-11-02T13:58:00Z",
            "independence_group": "group-a",
            "evidence_class": "market",
        },
        {
            "source_id": "b",
            "publisher": "Publisher B",
            "url": "https://b.example/feed",
            "retrieved_at_utc": "2026-11-02T13:58:20Z",
            "independence_group": "group-b",
            "evidence_class": "market",
        },
    ]
    snapshot["market_observations"] = [
        {
            "symbol": "XRP/USD",
            "venue": "Venue A",
            "price": 1.20,
            "timestamp_utc": "2026-11-02T13:58:00Z",
            "source_id": "a",
        },
        {
            "symbol": "XRP/USD",
            "venue": "Venue B",
            "price": 1.19,
            "timestamp_utc": "2026-11-02T13:58:20Z",
            "source_id": "b",
        },
    ]
    snapshot["forecast"] = {
        "status": "ISSUED",
        "target": "XRP/USD return over one hour",
        "horizon": "1h",
        "horizon_seconds": 3600,
        "issued_at_utc": "2026-11-02T14:00:01Z",
        "data_cutoff_utc": "2026-11-02T13:59:00Z",
        "probability": 0.65,
        "confidence": 0.70,
        "model_version": "unverified-test-v1",
        "assumptions": ["The supplied observations are valid."],
        "alternatives": ["The move reverses."],
        "evaluation": {
            "walk_forward_samples": 30,
            "out_of_sample": True,
            "leakage_check": "passed",
            "drift_status": "stable",
            "model_brier_score": 0.18,
            "baseline_brier_score": 0.22,
            "model_log_loss": 0.50,
            "baseline_log_loss": 0.62,
            "calibration_error": 0.05,
            "calibration_tolerance": 0.10,
            "evaluation_artifact_id": "invented-eval-id",
            "evaluation_run_url": "https://github.com/Barrot-Agent/B-Agent/actions/runs/1",
        },
        "outcome": {"status": "PENDING"},
    }
    return snapshot


def test_not_issued_report_contains_no_direction_or_recommendation():
    report = render_report(not_issued())
    assert "Forecast status: NOT_ISSUED" in report
    assert "No directional forecast" in report
    assert "BUY" not in report
    assert "SELL" not in report


def test_self_attested_metrics_and_run_url_cannot_issue_forecast():
    snapshot = self_attested_issued()
    with pytest.raises(EvidenceError, match="independently verifiable evaluation-attestation"):
        validate_snapshot(snapshot)


def test_self_asserted_attestation_fields_do_not_bypass_issuance_block():
    snapshot = self_attested_issued()
    snapshot["forecast"]["evaluation"]["attestation"] = {
        "verified": True,
        "signature": "not-a-real-signature",
        "repository": "Barrot-Agent/B-Agent",
        "workflow": "XRP Evidence Gate",
    }
    with pytest.raises(EvidenceError, match="self-asserted"):
        render_report(snapshot)


def test_unknown_forecast_status_is_rejected():
    snapshot = not_issued()
    snapshot["forecast"]["status"] = "MAYBE"
    with pytest.raises(EvidenceError, match="forecast status"):
        validate_snapshot(snapshot)


def test_writer_never_overwrites_existing_report(tmp_path):
    destination = tmp_path / "report.md"
    destination.write_text("preserve existing report", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_report("replacement", destination)
    assert destination.read_text(encoding="utf-8") == "preserve existing report"


def test_naive_capture_timestamp_is_rejected():
    snapshot = not_issued()
    snapshot["captured_at_utc"] = "2026-11-02T14:00:00"
    with pytest.raises(EvidenceError, match="UTC timezone"):
        validate_snapshot(snapshot)


def test_not_issued_payload_does_not_render_untrusted_forecast_fields():
    snapshot = not_issued()
    snapshot["forecast"].update(
        {
            "target": "XRP/USD return over one hour",
            "horizon": "1h",
            "probability": 0.99,
            "confidence": 0.99,
            "model_version": "unverified",
            "evaluation": {"walk_forward_samples": 9999, "out_of_sample": True},
        }
    )
    report = render_report(snapshot)
    assert "Forecast status: NOT_ISSUED" in report
    assert "0.99" not in report
    assert "9999" not in report
    assert "unverified" not in report
