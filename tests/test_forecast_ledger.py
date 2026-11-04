from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from barrot_agent.evolution.forecast_ledger import (
    ForecastAlreadyResolvedError,
    ForecastLedger,
    ForecastLedgerError,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

CUTOFF = "2026-11-03T16:00:00Z"
ISSUED = "2026-11-03T16:01:00Z"
TARGET = "2026-11-03T17:00:00Z"
OUTCOME_TIME = "2026-11-03T17:00:30Z"
RESOLVED = "2026-11-03T17:01:00Z"
TEST_NOW = datetime(2026, 11, 3, 16, 1, 30, tzinfo=timezone.utc)


class MutableClock:
    def __init__(self, current):
        self.current = current

    def __call__(self):
        return self.current

    def set(self, current):
        self.current = current


def make_ledger(path, *, now=TEST_NOW):
    clock = MutableClock(now)
    ledger = ForecastLedger(path, clock=clock)
    ledger._test_clock = clock
    return ledger


def set_ledger_time(ledger, value):
    ledger._test_clock.set(datetime.fromisoformat(value.replace("Z", "+00:00")))


def forecast(**overrides):
    value = {
        "asset": "XRP",
        "venue": "kraken:XRP/USD",
        "target_definition": "XRP/USD mid-price return at exact target timestamp; three-class thresholded outcome",
        "reference_price_usd": 1.27,
        "reference_price_timestamp_utc": CUTOFF,
        "reference_price_source_id": "kraken-001",
        "reference_price_max_age_seconds": 60,
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
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    first = ledger.record_forecast(forecast())
    second = ledger.record_forecast(forecast())
    assert first == second
    assert len(ledger.events(first)) == 1
    assert ledger.get_forecast(first)["forecast_id"] == first


def test_live_shadow_issue_event_records_actual_ledger_receipt_time(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    event = ledger.events(forecast_id)[0]
    assert event["recorded_at_utc"] == "2026-11-03T16:01:30.000000Z"
    assert event["recording_mode"] == "live_shadow"


def test_live_shadow_ledger_rejects_backdated_forecast_after_target(tmp_path):
    now = datetime(2026, 11, 4, 3, 30, tzinfo=timezone.utc)
    ledger = make_ledger(tmp_path / "forecasts.sqlite3", now=now)
    with pytest.raises(ForecastLedgerError, match="target_time_utc must be after actual ledger recording time"):
        ledger.record_forecast(forecast())


def test_live_shadow_ledger_rejects_backdated_issue_before_future_target(tmp_path):
    now = datetime(2026, 11, 3, 16, 10, tzinfo=timezone.utc)
    ledger = make_ledger(tmp_path / "forecasts.sqlite3", now=now)
    with pytest.raises(ForecastLedgerError, match="older than the five-minute live recording window"):
        ledger.record_forecast(forecast())


def test_live_shadow_ledger_rejects_future_issue_timestamp(tmp_path):
    now = datetime(2026, 11, 3, 16, 0, 30, tzinfo=timezone.utc)
    ledger = make_ledger(tmp_path / "forecasts.sqlite3", now=now)
    with pytest.raises(ForecastLedgerError, match="cannot be later than actual ledger recording time"):
        ledger.record_forecast(forecast())


def test_rejects_unsupported_horizon(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="horizon_seconds"):
        ledger.record_forecast(forecast(horizon_seconds=7200))


def test_rejects_naive_timestamp(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="UTC timezone"):
        ledger.record_forecast(forecast(data_cutoff_utc="2026-11-03T16:00:00"))


def test_rejects_feature_lookahead(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="look-ahead"):
        ledger.record_forecast(forecast(feature_max_timestamp_utc="2026-11-03T16:00:01Z"))


def test_rejects_reference_price_after_cutoff(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="reference_price_timestamp_utc exceeds data cutoff"):
        ledger.record_forecast(forecast(reference_price_timestamp_utc="2026-11-03T16:00:01Z"))


def test_rejects_stale_reference_price(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="older than the declared maximum age"):
        ledger.record_forecast(forecast(reference_price_timestamp_utc="2026-11-03T15:58:59Z"))


def test_reference_price_source_must_be_in_source_manifest(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="included in source_ids"):
        ledger.record_forecast(forecast(reference_price_source_id="unregistered-reference-source"))


def test_rejects_target_time_mismatch(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="target_time_utc"):
        ledger.record_forecast(forecast(target_time_utc="2026-11-03T17:01:00Z"))


def test_rejects_probabilities_that_do_not_sum_to_one(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="sum to 1"):
        ledger.record_forecast(forecast(probabilities={"down": 0.2, "flat": 0.2, "up": 0.2}))


def test_rejects_missing_alternative(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="alternatives"):
        ledger.record_forecast(forecast(alternatives=[]))


def test_rejects_resolution_before_target(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="precedes target"):
        set_ledger_time(ledger, "2026-11-03T17:00:00Z")
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T16:59:59Z",
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:00:00Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_scored_outcome_records_brier_and_baseline(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
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
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="cross-venue"):
        set_ledger_time(ledger, "2026-11-03T17:01:00Z")
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc=OUTCOME_TIME,
            outcome_venue="coinbase:XRP-USD",
            outcome_source_ids=["coinbase-outcome-001"],
        )


def test_cross_venue_requires_explicit_normalization(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
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
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
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
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    with pytest.raises(ForecastAlreadyResolvedError):
        set_ledger_time(ledger, "2026-11-03T17:01:00Z")
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
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="tolerance"):
        set_ledger_time(ledger, "2026-11-03T17:05:00Z")
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:05:00Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_calibration_bins_are_reported(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
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


def test_summary_does_not_pool_different_horizons(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    one_hour_id = ledger.record_forecast(forecast())
    four_hour_id = ledger.record_forecast(
        forecast(
            target_time_utc="2026-11-03T20:00:00Z",
            horizon_seconds=14400,
        )
    )
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    ledger.resolve_forecast(
        one_hour_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    set_ledger_time(ledger, "2026-11-03T20:01:00Z")
    ledger.resolve_forecast(
        four_hour_id,
        resolved_at_utc="2026-11-03T20:01:00Z",
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc="2026-11-03T20:00:30Z",
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-004h"],
    )

    summary = ledger.summary()
    assert summary["scored"] == 2
    assert summary["directional_accuracy"] is None
    assert summary["top_class_accuracy"] is None
    assert summary["mean_brier_score"] is None
    assert len(summary["cohort_summaries"]) == 2
    assert {item["horizon_seconds"] for item in summary["cohort_summaries"]} == {3600, 14400}
    assert all(item["scored"] == 1 for item in summary["cohort_summaries"])


def test_database_rejects_mutation_of_ledger_records(tmp_path):
    import sqlite3

    db_path = tmp_path / "forecasts.sqlite3"
    ledger = make_ledger(db_path)
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
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="not boolean"):
        ledger.record_forecast(
            forecast(probabilities={"down": True, "flat": 0.0, "up": 0.0})
        )



def test_default_forecast_ledger_database_and_sidecars_are_gitignored() -> None:
    ignored = set((REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())
    assert {
        "data/xrp_intelligence/forecast_ledger.sqlite3",
        "data/xrp_intelligence/forecast_ledger.sqlite3-wal",
        "data/xrp_intelligence/forecast_ledger.sqlite3-shm",
        "data/xrp_intelligence/forecast_ledger.sqlite3-journal",
    }.issubset(ignored)


def test_resolve_rejects_future_resolution_timestamp(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T16:30:00Z")
    with pytest.raises(ForecastLedgerError, match="cannot be later than actual ledger recording time"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc=OUTCOME_TIME,
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_resolve_rejects_future_outcome_price_timestamp(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:00:15Z")
    with pytest.raises(ForecastLedgerError, match="outcome_price_timestamp_utc cannot be later than actual ledger recording time"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T17:00:15Z",
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:00:30Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_unscorable_outcome_waits_until_tolerance_window_closes(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:00:30Z")
    with pytest.raises(ForecastLedgerError, match="tolerance_seconds window closes"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T17:00:30Z",
            outcome_price_usd=None,
            unscorable_reason="No price within the predeclared target tolerance",
        )
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    outcome = ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc="2026-11-03T17:01:00Z",
        outcome_price_usd=None,
        unscorable_reason="No price within the predeclared target tolerance",
    )
    assert outcome["status"] == "unscorable"
    assert outcome["recorded_at_utc"] == "2026-11-03T17:01:00.000000Z"
    assert ledger.events(forecast_id)[-1]["recorded_at_utc"] == "2026-11-03T17:01:00.000000Z"
