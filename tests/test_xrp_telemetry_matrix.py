import pytest

from barrot_agent.analysis.xrp_telemetry_matrix import (
    SnapshotValidationError, render_report, validate_snapshot, write_report,
)


def not_issued_snapshot():
    return {
        "schema_version": "1.0", "snapshot_id": "xrp-not-issued-001",
        "captured_at_utc": "2026-11-02T14:00:00Z", "data_cutoff_utc": "2026-11-02T13:59:00Z",
        "sources": [], "market_observations": [],
        "forecast": {"status": "NOT_ISSUED", "reason": "Synchronized post-event observations and validated model evidence are missing."},
    }


def issued_snapshot():
    snapshot = not_issued_snapshot()
    snapshot["snapshot_id"] = "xrp-issued-test-001"
    snapshot["sources"] = [
        {"source_id": "venue-a", "publisher": "Venue A", "url": "https://a.example/market", "retrieved_at_utc": "2026-11-02T13:58:00Z", "independence_group": "exchange-a", "evidence_class": "market_data"},
        {"source_id": "venue-b", "publisher": "Venue B", "url": "https://b.example/market", "retrieved_at_utc": "2026-11-02T13:58:20Z", "independence_group": "exchange-b", "evidence_class": "market_data"},
    ]
    snapshot["market_observations"] = [
        {"symbol": "XRP/USD", "venue": "Venue A", "price": 1.2, "timestamp_utc": "2026-11-02T13:58:00Z", "source_id": "venue-a"},
        {"symbol": "XRP/USD", "venue": "Venue B", "price": 1.19, "timestamp_utc": "2026-11-02T13:58:20Z", "source_id": "venue-b"},
    ]
    snapshot["forecast"] = {
        "status": "ISSUED", "target": "XRP/USD return over the next one-hour horizon", "horizon": "1h",
        "data_cutoff_utc": "2026-11-02T13:59:00Z", "probability": 0.65, "confidence": 0.7,
        "model_version": "test-model-v1", "assumptions": ["Both venue observations are valid and synchronized."],
        "alternatives": ["The move reverses after the cutoff."],
        "evaluation": {"walk_forward_samples": 30, "out_of_sample": True, "leakage_check": "passed", "drift_status": "stable", "model_brier_score": 0.18, "baseline_brier_score": 0.22, "model_log_loss": 0.5, "baseline_log_loss": 0.62, "calibration_error": 0.05, "calibration_tolerance": 0.1, "evaluation_artifact_id": "walk-forward-eval-001", "evaluation_run_url": "https://github.com/Barrot-Agent/B-Agent/actions/runs/1"},
        "outcome": {"status": "PENDING"},
    }
    return snapshot


def test_not_issued_report_has_no_hardcoded_price_or_directional_signal():
    report = render_report(not_issued_snapshot())
    assert "Forecast status: NOT_ISSUED" in report
    assert "Synchronized post-event observations" in report
    assert "No directional forecast or trading recommendation was issued." in report
    assert "Market Price" not in report and "BUY" not in report and "SELL" not in report


def test_issued_forecast_requires_two_independent_source_groups():
    snapshot = issued_snapshot()
    snapshot["sources"][1]["independence_group"] = "exchange-a"
    with pytest.raises(SnapshotValidationError, match="two independent source groups"):
        validate_snapshot(snapshot)


def test_issued_forecast_requires_synchronized_venues():
    snapshot = issued_snapshot()
    snapshot["market_observations"][0]["timestamp_utc"] = "2026-11-02T13:57:00Z"
    snapshot["market_observations"][1]["timestamp_utc"] = "2026-11-02T13:58:30Z"
    with pytest.raises(SnapshotValidationError, match="synchronization window"):
        validate_snapshot(snapshot)


def test_issued_forecast_requires_out_of_sample_baseline_improvement():
    snapshot = issued_snapshot()
    snapshot["forecast"]["evaluation"]["model_brier_score"] = 0.25
    with pytest.raises(SnapshotValidationError, match="Brier score must beat"):
        validate_snapshot(snapshot)


def test_issued_forecast_requires_pending_or_resolved_outcome():
    snapshot = issued_snapshot()
    snapshot["forecast"]["outcome"] = {}
    with pytest.raises(SnapshotValidationError, match="outcome.status"):
        validate_snapshot(snapshot)


def test_valid_issued_forecast_is_labeled_research_only():
    report = render_report(issued_snapshot())
    assert "Research-only forecast. Not a trading instruction." in report
    assert "Outcome: PENDING" in report
    assert "Assumptions" in report and "Alternatives" in report


def test_report_writer_refuses_to_overwrite_existing_file(tmp_path):
    output = tmp_path / "report.md"
    output.write_text("preserve me", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_report("new content", output)
    assert output.read_text(encoding="utf-8") == "preserve me"


def test_naive_timestamp_is_rejected():
    snapshot = not_issued_snapshot()
    snapshot["captured_at_utc"] = "2026-11-02T14:00:00"
    with pytest.raises(SnapshotValidationError, match="UTC timezone"):
        validate_snapshot(snapshot)