from datetime import datetime, timedelta, timezone
import pytest

from barrot_agent.evolution.forecast_ledger import (
    ForecastAlreadyResolvedError,
    ForecastLedger,
    ForecastLedgerError,
)

CUTOFF = "2026-11-03T16:00:00Z"
ISSUED = "2026-11-03T16:01:00Z"
TARGET = "2026-11-03T17:00:00Z"
OUTCOME_TIME = "2026-11-03T17:00:30Z"
RESOLVED = "2026-11-03T17:01:00Z"


def forecast(**overrides):
    value = {
        "asset": "XRP",
        "venue": "kraken:XRP/USD",
        "target_definition": "XRP/USD mid-price return at exact target timestamp; three-class thresholded outcome",
        "reference_price_usd": 1.27,
        "data_cutoff_utc": CUTOFF,
        "issued_at_utc": ISSUED,
        "target_time_utc": TARGET,
        "horizon_seconds": 3600,
        "model_version": "xrp-test-v1",
        "baseline_model_version": "naive-frequency-v1",
        "probabilities": {"down": 0.2, "flat": 0.3, "up": 0.5},
        "baseline_probabilities": {"down": 0.3, "flat": 0.4, "up": 0.3},
        "flat_band_bps": 25.0,
        "outcome_tolerance_seconds": 60,
        "feature_max_timestamp_utc": "2026-11-03T15:59:00Z",
        "feature_snapshot_ids": ["snapshot-001"],
        "source_ids": ["kraken-001", "macro-001"],
        "assumptions": ["No venue outage during horizon"],
        "alternatives": ["Derivatives deleveraging overwhelms spot demand"],
        "fee_bps": 10.0,
        "slippage_bps": 5.0,
    }
    value.update(overrides)
    return value


def test_record_is_idempotent_and_append_only(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    first = ledger.record_forecast(forecast())
    second = ledger.record_forecast(forecast())
    assert first == second
    assert len(ledger.events(first)) == 1
    assert ledger.get_forecast(first)["forecast_id"] == first


def test_rejects_unsupported_horizon(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="horizon_seconds"):
        ledger.record_forecast(forecast(horizon_seconds=7200))


def test_rejects_naive_timestamp(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="UTC timezone"):
        ledger.record_forecast(forecast(data_cutoff_utc="2026-11-03T16:00:00"))


def test_rejects_feature_lookahead(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="look-ahead"):
        ledger.record_forecast(forecast(feature_max_timestamp_utc="2026-11-03T16:00:01Z"))


def test_rejects_target_time_mismatch(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="target_time_utc"):
        ledger.record_forecast(forecast(target_time_utc="2026-11-03T17:01:00Z"))


def test_rejects_probabilities_that_do_not_sum_to_one(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="sum to 1"):
        ledger.record_forecast(forecast(probabilities={"down": 0.2, "flat": 0.2, "up": 0.2}))


def test_rejects_missing_alternative(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="alternatives"):
        ledger.record_forecast(forecast(alternatives=[]))


def test_rejects_resolution_before_target(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="precedes target"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T16:59:59Z",
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:00:00Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_scored_outcome_records_brier_and_baseline(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    outcome = ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    assert outcome["status"] == "scored"
    assert outcome["actual_class"] == "up"
    assert outcome["directional_correct"] is True
    assert outcome["brier_score"] < outcome["baseline_brier_score"]
    assert len(ledger.events(forecast_id)) == 2
    summary = ledger.summary()
    assert summary["scored"] == 1
    assert summary["unresolved"] == 0
    assert summary["mean_brier_score"] == outcome["brier_score"]
    assert summary["brier_improvement_vs_baseline"] > 0


def test_rejects_cross_venue_without_normalization(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="cross-venue"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc=OUTCOME_TIME,
            outcome_venue="coinbase:XRP-USD",
            outcome_source_ids=["coinbase-outcome-001"],
        )


def test_cross_venue_requires_explicit_normalization(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    outcome = ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="coinbase:XRP-USD",
        outcome_source_ids=["coinbase-outcome-001"],
        cross_venue_normalization="USD spot mid-price; same UTC target timestamp; no FX conversion",
    )
    assert outcome["status"] == "scored"
    assert outcome["cross_venue_normalization"]


def test_missing_outcome_is_unscorable_not_a_miss(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    outcome = ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc="2026-11-03T17:05:00Z",
        outcome_price_usd=None,
        unscorable_reason="No venue price available within the predeclared target tolerance",
    )
    assert outcome["status"] == "unscorable"
    assert outcome["actual_class"] is None
    assert outcome["directional_correct"] is None
    summary = ledger.summary()
    assert summary["unscorable"] == 1
    assert summary["scored"] == 0
    assert summary["directional_accuracy"] is None


def test_outcome_is_immutable(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    with pytest.raises(ForecastAlreadyResolvedError):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.25,
            outcome_price_timestamp_utc=OUTCOME_TIME,
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-002"],
        )
    assert len(ledger.events(forecast_id)) == 2


def test_rejects_outcome_timestamp_outside_tolerance(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="tolerance"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:05:00Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_calibration_bins_are_reported(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    summary = ledger.summary()
    assert summary["calibration_bins"][0]["count"] == 1
    assert summary["weighted_calibration_error"] is not None


def test_database_rejects_mutation_of_ledger_records(tmp_path):
    import sqlite3

    db_path = tmp_path / "forecasts.sqlite3"
    ledger = ForecastLedger(db_path)
    forecast_id = ledger.record_forecast(forecast())
    connection = sqlite3.connect(db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE forecasts SET venue = 'other' WHERE forecast_id = ?",
                (forecast_id,),
            )
        connection.rollback()
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM events WHERE forecast_id = ?",
                (forecast_id,),
            )
        connection.rollback()
    finally:
        connection.close()


def test_rejects_boolean_probability(tmp_path):
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="not boolean"):
        ledger.record_forecast(
            forecast(probabilities={"down": True, "flat": 0.0, "up": 0.0})
        )
