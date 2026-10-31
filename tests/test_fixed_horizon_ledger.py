import math

import pytest

from barrot_agent.research.fixed_horizon import ForecastLedger


def forecast_payload(**overrides):
    payload = {
        "forecast_id": "xrp-forecast-001",
        "asset_pair": "XRP/USD",
        "issued_at_utc": "2026-10-31T00:00:00Z",
        "data_cutoff_utc": "2026-10-30T23:59:00Z",
        "horizon_seconds": 3600,
        "target": {
            "name": "xrp_usd_return_class_v1",
            "up_threshold_pct": 0.5,
            "down_threshold_pct": -0.5,
        },
        "probabilities": {"up": 0.6, "flat": 0.25, "down": 0.15},
        "assumptions": ["The point-in-time feature snapshot is complete."],
        "alternatives": ["The market remains range-bound."],
        "model": {"name": "barrot-xrp", "version": "0.1.0"},
        "feature_snapshot": {
            "snapshot_id": "features-001",
            "sha256": "a" * 64,
            "captured_at_utc": "2026-10-30T23:58:00Z",
        },
        "baseline": {
            "id": "uniform-v1",
            "trained_through_utc": "2026-10-30T23:59:00Z",
            "computed_at_utc": "2026-10-30T23:59:00Z",
            "probabilities": {"up": 1 / 3, "flat": 1 / 3, "down": 1 / 3},
        },
        "source_ids": ["SRC-MARKET-001"],
        "price_at_issue_usd": 1.25,
        "price_at_issue_source_id": "SRC-MARKET-001",
        "price_at_issue_observed_at_utc": "2026-10-30T23:59:00Z",
    }
    payload.update(overrides)
    return payload


def test_forecast_is_appended_with_fixed_target_and_computed_confidence(tmp_path):
    ledger = ForecastLedger(tmp_path)
    record = ledger.append_forecast(forecast_payload())
    assert record["record_type"] == "xrp_forecast"
    assert record["horizon_seconds"] == 3600
    assert record["target_end_at_utc"] == "2026-10-31T01:00:00Z"
    assert record["confidence"] == pytest.approx(0.6)
    assert record["status"] == "OPEN"
    assert len(ledger.forecasts()) == 1
    assert ledger.outcomes() == []


def test_forecast_rejects_data_cutoff_after_issue_time(tmp_path):
    ledger = ForecastLedger(tmp_path)
    with pytest.raises(ValueError, match="data_cutoff_utc"):
        ledger.append_forecast(forecast_payload(data_cutoff_utc="2026-10-31T00:01:00Z"))


def test_forecast_rejects_feature_snapshot_after_data_cutoff(tmp_path):
    ledger = ForecastLedger(tmp_path)
    payload = forecast_payload()
    payload["feature_snapshot"]["captured_at_utc"] = "2026-10-31T00:00:01Z"
    with pytest.raises(ValueError, match="feature snapshot"):
        ledger.append_forecast(payload)


def test_forecast_rejects_baseline_trained_after_data_cutoff(tmp_path):
    ledger = ForecastLedger(tmp_path)
    payload = forecast_payload()
    payload["baseline"]["trained_through_utc"] = "2026-10-31T00:00:01Z"
    with pytest.raises(ValueError, match="baseline"):
        ledger.append_forecast(payload)


def test_forecast_rejects_baseline_computed_after_issue_time(tmp_path):
    ledger = ForecastLedger(tmp_path)
    payload = forecast_payload()
    payload["baseline"]["computed_at_utc"] = "2026-10-31T00:00:01Z"
    with pytest.raises(ValueError, match="baseline must be computed"):
        ledger.append_forecast(payload)


def test_forecast_rejects_issue_price_observed_after_cutoff(tmp_path):
    ledger = ForecastLedger(tmp_path)
    payload = forecast_payload(price_at_issue_observed_at_utc="2026-10-31T00:00:01Z")
    with pytest.raises(ValueError, match="issue price observation"):
        ledger.append_forecast(payload)


def test_forecast_requires_issue_price_source_in_source_registry(tmp_path):
    ledger = ForecastLedger(tmp_path)
    payload = forecast_payload(price_at_issue_source_id="SRC-UNREGISTERED")
    with pytest.raises(ValueError, match="included in source_ids"):
        ledger.append_forecast(payload)


def test_observation_lag_must_be_an_integer(tmp_path):
    with pytest.raises(ValueError, match="positive integer"):
        ForecastLedger(tmp_path, max_observation_lag_seconds=1.5)


def test_forecast_rejects_invalid_probability_distribution(tmp_path):
    ledger = ForecastLedger(tmp_path)
    payload = forecast_payload(probabilities={"up": 0.6, "flat": 0.2, "down": 0.1})
    with pytest.raises(ValueError, match="sum to one"):
        ledger.append_forecast(payload)


def test_forecast_rejects_timezone_naive_timestamps(tmp_path):
    ledger = ForecastLedger(tmp_path)
    with pytest.raises(ValueError, match="timezone"):
        ledger.append_forecast(forecast_payload(issued_at_utc="2026-10-31T00:00:00"))


def test_forecast_rejects_duplicate_ids(tmp_path):
    ledger = ForecastLedger(tmp_path)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="already exists"):
        ledger.append_forecast(forecast_payload())


def test_outcome_cannot_be_recorded_before_fixed_horizon(tmp_path):
    ledger = ForecastLedger(tmp_path)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="cannot precede"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-31T00:59:59Z",
            "2026-10-31T01:00:10Z", "SRC-PRICE-001"
        )


def test_outcome_rejects_price_observation_outside_lag_window(tmp_path):
    ledger = ForecastLedger(tmp_path, max_observation_lag_seconds=60)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="observation lag"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-31T01:02:00Z",
            "2026-10-31T01:03:00Z", "SRC-PRICE-001"
        )


def test_outcome_is_separate_and_does_not_mutate_forecast(tmp_path):
    ledger = ForecastLedger(tmp_path)
    ledger.append_forecast(forecast_payload())
    original_forecasts = ledger.forecasts_path.read_bytes()
    outcome = ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T01:00:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    assert outcome["realized_class"] == "up"
    assert outcome["realized_return_pct"] == pytest.approx(1.6)
    assert ledger.forecasts_path.read_bytes() == original_forecasts
    assert len(ledger.outcomes()) == 1


def test_duplicate_outcome_is_rejected(tmp_path):
    ledger = ForecastLedger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T01:00:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    with pytest.raises(ValueError, match="already exists"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.28, "2026-10-31T01:00:40Z",
            "2026-10-31T01:02:00Z", "SRC-PRICE-002"
        )


def test_metrics_report_brier_log_loss_baseline_and_calibration(tmp_path):
    ledger = ForecastLedger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T01:00:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    metrics = ledger.metrics()
    assert metrics["resolved_count"] == 1
    assert metrics["pending_count"] == 0
    assert metrics["accuracy"] == 1.0
    assert metrics["mean_brier_score"] == pytest.approx(0.245)
    assert metrics["mean_log_loss"] == pytest.approx(-math.log(0.6))
    assert metrics["mean_baseline_brier_score"] == pytest.approx(2 / 3)
    assert metrics["brier_skill_score"] > 0
    assert metrics["top_label_calibration_bins"][0]["count"] == 1
    assert metrics["performance_claim_status"] == "DESCRIPTIVE_ONLY_NO_MODEL_SKILL_CLAIM"
    assert metrics["walk_forward_baseline_status"] == "NOT_IMPLEMENTED_STORED_BASELINE_CUTOFF_CHECKED"


def test_metrics_do_not_claim_skill_without_resolved_outcomes(tmp_path):
    ledger = ForecastLedger(tmp_path)
    ledger.append_forecast(forecast_payload())
    metrics = ledger.metrics()
    assert metrics["resolved_count"] == 0
    assert metrics["pending_count"] == 1
    assert metrics["mean_brier_score"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED"


def test_invalid_feature_snapshot_hash_is_rejected(tmp_path):
    ledger = ForecastLedger(tmp_path)
    payload = forecast_payload()
    payload["feature_snapshot"]["sha256"] = "not-a-hash"
    with pytest.raises(ValueError, match="SHA-256"):
        ledger.append_forecast(payload)


def test_outcome_requires_a_price_source_id(tmp_path):
    ledger = ForecastLedger(tmp_path)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="price_source_id"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-31T01:00:30Z",
            "2026-10-31T01:01:00Z", ""
        )
