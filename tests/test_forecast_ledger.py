import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from barrot_agent.evolution.feature_store import HistoricalFeatureStore
from barrot_agent.evolution.forecast_ledger import (
    ForecastAlreadyResolvedError,
    ForecastLedger,
    ForecastLedgerError,
    _validate_readiness_report,
)
from barrot_agent.evolution.point_in_time_features import build_feature_snapshot

REPO_ROOT = Path(__file__).resolve().parents[1]

CUTOFF = "2026-11-03T16:00:00Z"
ISSUED = "2026-11-03T16:01:00Z"
TARGET = "2026-11-03T17:00:00Z"
OUTCOME_TIME = "2026-11-03T17:00:30Z"
RESOLVED = "2026-11-03T17:01:00Z"
TEST_NOW = datetime(2026, 11, 3, 16, 1, 30, tzinfo=timezone.utc)


FEATURE_CUTOFF = "2026-11-03T15:59:30Z"
FEATURE_CAPTURED = "2026-11-03T15:59:35Z"
STORE_RECEIPT = datetime(2026, 11, 3, 15, 59, 40, tzinfo=timezone.utc)
FEATURE_RECORD = {
    "record_id": "xrp:spot:mid:2026-11-03T15:59:30Z:v1",
    "feature_id": "xrp.spot.mid_price",
    "feature_version": 1,
    "asset": "XRP",
    "feature_name": "spot_mid_price",
    "value": 1.27,
    "unit": "USD/XRP",
    "event_time_utc": FEATURE_CUTOFF,
    "known_at_utc": FEATURE_CUTOFF,
    "source_data_as_of_utc": FEATURE_CUTOFF,
    "ingested_at_utc": FEATURE_CUTOFF,
    "revision_available_at_utc": FEATURE_CUTOFF,
    "sources": [
        {
            "source_id": "kraken-001",
            "independence_group": "kraken.com",
            "source_uri": "https://api.kraken.com/0/public/Ticker?pair=XRPUSD",
            "raw_content_sha256": "a" * 64,
        },
        {
            "source_id": "macro-001",
            "independence_group": "fred.stlouisfed.org",
            "source_uri": "https://api.stlouisfed.org/fred/series/observations",
            "raw_content_sha256": "b" * 64,
        },
    ],
    "quality_status": "verified",
    "model_eligible": True,
    "eligibility_reason": "",
    "revision_status": "original",
    "supersedes_record_id": None,
    "adapter_version": "test-adapter-v1",
    "parser_version": "test-parser-v1",
    "limitations": [],
    "disconfirming_evidence_ids": [],
}
FEATURE_SNAPSHOT = build_feature_snapshot(
    [FEATURE_RECORD],
    cutoff_utc=FEATURE_CUTOFF,
    captured_at_utc=FEATURE_CAPTURED,
)


def _readiness_fixture(asset, horizon_seconds, source_ids=None):
    """Synthetic test-only evidence; never represents real XRP model readiness."""
    source_ids = source_ids or ["kraken-001", "macro-001"]
    source_details = {
        "kraken-001": (
            "kraken.com",
            "https://api.kraken.com/0/public/Ticker?pair=XRPUSD",
            b'{"pair":"XRP/USD","mid":1.27}',
        ),
        "macro-001": (
            "fred.stlouisfed.org",
            "https://api.stlouisfed.org/fred/series/observations",
            b'{"series":"DFF","value":"4.00"}',
        ),
        "unregistered": (
            "unregistered.example",
            "https://example.com/receipt",
            b'{"source":"unregistered-test-only"}',
        ),
    }
    raw_receipt_bytes = {}
    receipts = []
    for source_id in source_ids:
        group, source_uri, raw_bytes = source_details[source_id]
        receipt_id = f"receipt-{source_id}"
        raw_receipt_bytes[receipt_id] = raw_bytes
        receipts.append(
            {
                "source_id": source_id,
                "receipt_id": receipt_id,
                "raw_content_sha256": hashlib.sha256(raw_bytes).hexdigest(),
                "raw_capture_status": "byte_complete",
                "raw_receipt_sha256_verified": True,
                "independence_group": group,
                "source_uri": source_uri,
                "source_data_as_of_utc": FEATURE_CUTOFF,
                "captured_at_utc": FEATURE_CAPTURED,
            }
        )
    independence_groups = sorted({source_details[source_id][0] for source_id in source_ids})
    dataset_manifest = {
        "model_eligible": True,
        "quality_status": "verified",
        "asset": asset,
        "venue": "kraken:XRP/USD",
        "feature_ids": ["xrp.spot.mid_price"],
        "feature_snapshot_ids": [FEATURE_SNAPSHOT["snapshot_id"]],
        "source_ids": source_ids,
        "source_independence_groups": independence_groups,
        "raw_source_receipts": receipts,
        "data_cutoff_utc": FEATURE_CUTOFF,
    }
    canonical_dataset = json.dumps(
        dataset_manifest,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    report = {
        "schema_version": "barrot.xrp.model-readiness.v1",
        "evaluation_type": "chronological_walk_forward_model_evaluation",
        "status": "PASS",
        "policy_id": "xrp_forecast_readiness_v1",
        "evaluation_id": f"test-evaluation-{asset.lower()}-{horizon_seconds}-{'-'.join(source_ids)}",
        "model_version": "xrp-test-v1",
        "baseline_model_version": "naive-frequency-v1",
        "asset": asset,
        "venue": "kraken:XRP/USD",
        "horizon_seconds": horizon_seconds,
        "dataset_receipt_id": f"test-dataset-receipt-{asset.lower()}-{horizon_seconds}",
        "dataset_sha256": hashlib.sha256(canonical_dataset).hexdigest(),
        "dataset_manifest": dataset_manifest,
        "source_independence_group_count": len(independence_groups),
        "training_sample_count": 1000,
        "out_of_sample_sample_count": 200,
        "shadow_evaluation_sample_count": 200,
        "out_of_sample_start_utc": "2026-10-01T00:00:00Z",
        "out_of_sample_end_utc": "2026-10-20T00:00:00Z",
        "shadow_evaluation_start_utc": "2026-10-20T00:00:00Z",
        "shadow_evaluation_end_utc": "2026-11-03T15:00:00Z",
        "leakage_check_status": "PASS",
        "calibration_status": "PASS",
        "drift_status": "STABLE",
        "shadow_evaluation_status": "PASS",
        "weighted_calibration_error": 0.02,
        "model_metrics": {"mean_brier_score": 0.15, "mean_log_loss": 0.42},
        "baseline_metrics": {
            "naive_class_prior": {"mean_brier_score": 0.24, "mean_log_loss": 0.65},
            "momentum_sign": {"mean_brier_score": 0.22, "mean_log_loss": 0.61},
            "mean_reversion_sign": {"mean_brier_score": 0.23, "mean_log_loss": 0.63},
            "volatility_normal": {"mean_brier_score": 0.21, "mean_log_loss": 0.59},
        },
        "evaluation_data_cutoff_utc": FEATURE_CUTOFF,
        "evaluation_completed_at_utc": "2026-11-03T16:00:30Z",
    }
    report_bytes = json.dumps(
        report,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    receipt_id = f"test-readiness-receipt-{asset.lower()}-{horizon_seconds}-{'-'.join(source_ids)}"
    report_sha256 = hashlib.sha256(report_bytes).hexdigest()
    return {
        "report_bytes": report_bytes,
        "receipt_id": receipt_id,
        "raw_receipt_bytes": raw_receipt_bytes,
        "certificate": {
            "report_sha256": report_sha256,
            "receipt_id": receipt_id,
            "policy_id": "xrp_forecast_readiness_v1",
            "status": "PASS",
        },
    }


READINESS_FIXTURES = {
    ("XRP", 3600): _readiness_fixture("XRP", 3600),
    ("XRP", 14400): _readiness_fixture("XRP", 14400),
    ("BTC", 3600): _readiness_fixture("BTC", 3600),
    ("XRP", 3600, "source_mismatch"): _readiness_fixture(
        "XRP", 3600, ["kraken-001", "macro-001", "unregistered"]
    ),
}
def _register_readiness_fixtures(ledger):
    for fixture in READINESS_FIXTURES.values():
        ledger.register_readiness_report(
            fixture["report_bytes"],
            receipt_id=fixture["receipt_id"],
            raw_receipt_bytes=fixture["raw_receipt_bytes"],
        )


class MutableClock:
    def __init__(self, current):
        self.current = current

    def __call__(self):
        return self.current

    def set(self, current):
        self.current = current


def make_ledger(path, *, now=TEST_NOW, store_clock=STORE_RECEIPT, snapshot=FEATURE_SNAPSHOT):
    # Readiness evidence must be registered before the forecast issue timestamp.
    clock = MutableClock(datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc))
    store = HistoricalFeatureStore(
        Path(path).parent / "feature_store.sqlite3",
        clock=lambda: store_clock,
    )
    store.append_snapshot(snapshot)
    ledger = ForecastLedger(path, clock=clock, feature_store=store)
    _register_readiness_fixtures(ledger)
    clock.set(now)
    ledger._test_clock = clock
    ledger._test_feature_store = store
    ledger._test_snapshot_id = snapshot["snapshot_id"]
    return ledger


def set_ledger_time(ledger, value):
    ledger._test_clock.set(datetime.fromisoformat(value.replace("Z", "+00:00")))


def forecast(**overrides):
    value = {
        "asset": "XRP",
        "venue": "kraken:XRP/USD",
        "target_definition": "XRP/USD mid-price return at exact target timestamp; three-class thresholded outcome",
        "reference_price_usd": 1.27,
        "reference_price_timestamp_utc": FEATURE_CUTOFF,
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
        "feature_max_timestamp_utc": FEATURE_CUTOFF,
        "feature_snapshot_ids": [FEATURE_SNAPSHOT["snapshot_id"]],
        "source_ids": ["kraken-001", "macro-001"],
        "assumptions": ["No venue outage during horizon"],
        "alternatives": ["Derivatives deleveraging overwhelms spot demand"],
        "fee_bps": 10.0,
        "slippage_bps": 5.0,
    }
    value.update(overrides)
    if "readiness_certificate" not in value:
        fixture_key = (str(value["asset"]).strip().upper(), value["horizon_seconds"])
        if "unregistered" in value["source_ids"]:
            fixture_key = (*fixture_key, "source_mismatch")
        fixture = READINESS_FIXTURES.get(fixture_key, READINESS_FIXTURES[("XRP", 3600)])
        value["readiness_certificate"] = fixture["certificate"]
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
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
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
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
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
    set_ledger_time(ledger, "2026-11-03T17:05:00Z")
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


def test_forecast_recording_requires_a_verified_feature_store(tmp_path):
    clock = MutableClock(datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc))
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3", clock=clock)
    _register_readiness_fixtures(ledger)
    clock.set(TEST_NOW)
    with pytest.raises(ForecastLedgerError, match="verified HistoricalFeatureStore"):
        ledger.record_forecast(forecast())


def test_readiness_requires_candidate_to_beat_every_baseline():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["baseline_metrics"]["momentum_sign"]["mean_brier_score"] = 0.14
    report["baseline_metrics"]["momentum_sign"]["mean_log_loss"] = 0.40
    with pytest.raises(ForecastLedgerError, match="momentum_sign"):
        _validate_readiness_report(report)


def test_rejects_unknown_or_non_sha256_feature_snapshot(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="SHA-256 snapshot IDs"):
        ledger.record_forecast(forecast(feature_snapshot_ids=["snapshot-001"]))
    with pytest.raises(ForecastLedgerError, match="unavailable or failed integrity"):
        ledger.record_forecast(forecast(feature_snapshot_ids=["f" * 64]))


def test_rejects_feature_snapshot_for_another_asset(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="does not cover asset BTC"):
        ledger.record_forecast(forecast(asset="BTC"))


def test_rejects_forecast_source_manifest_that_differs_from_snapshot_lineage(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="do not exactly match referenced feature lineage"):
        ledger.record_forecast(forecast(source_ids=["kraken-001", "macro-001", "unregistered"]))


def test_rejects_underreported_feature_information_timestamp(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="must equal the maximum feature information"):
        ledger.record_forecast(forecast(feature_max_timestamp_utc="2026-11-03T15:59:29Z"))


def test_rejects_feature_snapshot_received_after_forecast_cutoff(tmp_path):
    late_store_receipt = datetime(2026, 11, 3, 16, 0, 1, tzinfo=timezone.utc)
    ledger = make_ledger(
        tmp_path / "forecasts.sqlite3",
        store_clock=late_store_receipt,
    )
    with pytest.raises(ForecastLedgerError, match="not captured and stored by the forecast cutoff"):
        ledger.record_forecast(forecast())


def test_rejects_feature_snapshot_data_cutoff_after_forecast_cutoff(tmp_path):
    later_snapshot = build_feature_snapshot(
        [FEATURE_RECORD],
        cutoff_utc="2026-11-03T16:00:01Z",
        captured_at_utc="2026-11-03T16:00:02Z",
    )
    ledger = make_ledger(
        tmp_path / "forecasts.sqlite3",
        store_clock=datetime(2026, 11, 3, 16, 0, 3, tzinfo=timezone.utc),
        snapshot=later_snapshot,
    )
    with pytest.raises(ForecastLedgerError, match="data cutoff exceeds forecast cutoff"):
        ledger.record_forecast(
            forecast(feature_snapshot_ids=[later_snapshot["snapshot_id"]])
        )


