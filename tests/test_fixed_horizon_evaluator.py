"""Synthetic-only tests for the fixed-horizon diagnostic."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fh_eval_test", ROOT / "scripts" / "fixed_horizon_evaluator.py")
evaluator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = evaluator
spec.loader.exec_module(evaluator)


def entry(ts, price, score=70, **extra):
    row = {
        "generated_at_unix": ts,
        "timestamp": datetime.fromtimestamp(ts, timezone.utc).isoformat(),
        "price_at_emission": price,
        "score": score,
        "source": "test:model",
        "model_available": True,
        "signal_status": "model_only",
        "score_basis": "model",
    }
    row.update(extra)
    return row


def test_fixed_horizon_matches_and_computes_return():
    rows = [entry(1000, 1.0, 75), entry(1000 + 24*3600 + 60, 1.02, 50)]
    report = evaluator.build_report(rows, generated_at_utc="fixed")
    assert report["all_matched_samples"] == 1
    assert report["samples"][0]["forward_return_pct"] == 2.0
    assert report["samples"][0]["actual_label"] == "bullish"
    assert report["production_gate"]["passed"] is False


def test_observation_outside_tolerance_is_rejected():
    rows = [entry(1000, 1.0, 70), entry(1000 + 24*3600 + 46*60, 1.02, None)]
    report = evaluator.build_report(rows, tolerance_minutes=45, generated_at_utc="fixed")
    assert report["all_matched_samples"] == 0
    assert report["input"]["matching_counts"]["unmatched_horizon"] == 1


def test_only_future_observation_near_target_can_match():
    rows = [entry(1000, 1.0), entry(1000 + 23*3600, 1.1, None), entry(1000 + 25*3600, 1.01, None)]
    report = evaluator.build_report(rows, tolerance_minutes=45, generated_at_utc="fixed")
    assert report["all_matched_samples"] == 0


def test_news_only_excluded_but_its_price_can_be_outcome_observation():
    rows = [
        entry(1000, 1.0, signal_status="news_only", score_basis="news_only", model_available=False),
        entry(1000 + 24*3600, 1.02, score=50),
    ]
    report = evaluator.build_report(rows, generated_at_utc="fixed")
    assert report["input"]["matching_counts"]["excluded_news_only"] == 1
    assert report["input"]["price_observations"] == 2
    assert report["all_matched_samples"] == 0


def test_legacy_provider_failure_excluded():
    rows = [
        entry(1000, 1.0, 44, source="sentiment unavailable (github_failed; groq_failed)+news(11)"),
        entry(1000 + 24*3600, 1.01, 50),
    ]
    report = evaluator.build_report(rows, generated_at_utc="fixed")
    assert report["input"]["matching_counts"]["excluded_legacy_provider_failure"] == 1
    assert report["all_matched_samples"] == 0


def test_future_price_observation_not_reused():
    rows = [
        entry(1000, 1.0, 70),
        entry(1010, 1.0, 70),
        entry(1000 + 24*3600 + 5, 1.02, 50),
    ]
    report = evaluator.build_report(rows, generated_at_utc="fixed")
    assert report["all_matched_samples"] == 1
    assert report["input"]["matching_counts"]["outcome_observation_already_used"] == 1


def test_strict_thresholds_and_neutral_band():
    assert evaluator.label_return(0.5, 0.5) == "flat"
    assert evaluator.label_return(0.51, 0.5) == "bullish"
    assert evaluator.label_return(-0.51, 0.5) == "bearish"
    assert evaluator.label_score(40, 40, 60) == "flat"
    assert evaluator.label_score(60, 40, 60) == "flat"
    assert evaluator.label_score(39.9, 40, 60) == "bearish"
    assert evaluator.label_score(60.1, 40, 60) == "bullish"


def test_holdout_baselines_and_calibration_caveat():
    start = 1_800_000_000
    signals = [entry(start + i*3600, 1.0 + (0.01 if i % 2 == 0 else -0.01), 70 if i%2 == 0 else 30) for i in range(12)]
    outcomes = [entry(start + i*3600 + 24*3600, signals[i]["price_at_emission"] * (1.01 if i%2 == 0 else 0.99), 50) for i in range(12)]
    report = evaluator.build_report(signals + outcomes, generated_at_utc="fixed")
    assert report["chronological_holdout"]["always_flat_baseline"]["n"] > 0
    assert report["chronological_holdout"]["expanding_matured_label_majority_baseline"]["n"] > 0
    assert report["chronological_holdout"]["sample_size_warning"] is True
    assert report["calibration"]["status"] == "not_computed"


def test_invalid_prices_and_duplicate_timestamps_counted():
    rows = [
        entry(1000, 1.0),
        entry(1000, 1.05),
        entry(2000, 0),
        {"generated_at_unix": "bad", "price_at_emission": 1.0, "score": 50},
    ]
    report = evaluator.build_report(rows, generated_at_utc="fixed")
    assert report["input"]["quality_counts"]["duplicate_timestamps"] == 1
    assert report["input"]["quality_counts"]["invalid_timestamp_or_price"] == 2


def test_invalid_configuration_rejected():
    with pytest.raises(ValueError):
        evaluator.build_report([], horizon_hours=0)
    with pytest.raises(ValueError):
        evaluator.build_report([], bearish_threshold=70, bullish_threshold=60)
