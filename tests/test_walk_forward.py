from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import pytest

from barrot_agent.evolution.walk_forward import (
    WalkForwardEvaluationError,
    evaluate_chronological_walk_forward,
)

FEATURE_ID = "xrp.spot.kraken.1h.close_usd"
BASE = datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc)


def _stamp(value):
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def _bar(index, price, *, capture_at=None, venue="kraken", source_group="kraken"):
    event = BASE + timedelta(hours=index)
    capture = capture_at or event + timedelta(seconds=3)
    return {
        "record_id": f"xrp:kraken:1h:{index}:v1",
        "feature_id": FEATURE_ID,
        "feature_version": 1,
        "asset": "XRP",
        "feature_name": "spot_close_price",
        "value": price,
        "unit": "USD/XRP",
        "event_time_utc": _stamp(event),
        "known_at_utc": _stamp(capture - timedelta(seconds=2)),
        "source_data_as_of_utc": _stamp(event),
        "ingested_at_utc": _stamp(capture),
        "revision_available_at_utc": _stamp(capture - timedelta(seconds=1)),
        "sources": [
            {
                "source_id": f"{source_group}-public-api",
                "independence_group": source_group,
                "source_uri": (
                    "https://api.kraken.com/0/public/OHLC?pair=XRPUSD&interval=60"
                    if source_group == "kraken"
                    else f"https://api.{source_group}.example/public/OHLC?pair=XRPUSD&interval=60"
                ),
                "raw_content_sha256": f"{index + 1:064x}",
            }
        ],
        "quality_status": "verified",
        "model_eligible": True,
        "eligibility_reason": "",
        "revision_status": "original",
        "supersedes_record_id": None,
        "adapter_version": "kraken-ohlc-v1",
        "parser_version": "xrp-bars-v1",
        "limitations": ["Single-venue close-price observation"],
        "disconfirming_evidence_ids": [],
        "venue": venue,
        "instrument": "XRP/USD",
        "currency_pair": "XRP/USD",
        "market_type": "spot",
        "aggregation_window": "1h",
    }


def _series(count=30, *, source_groups=None):
    prices = [1.0]
    changes = [0.001, 0.002, -0.001, 0.0002, -0.002, 0.0015, 0.0001]
    for index in range(1, count):
        prices.append(prices[-1] * (1.0 + changes[(index - 1) % len(changes)]))
    return [
        _bar(index, price, source_group=(source_groups[index % len(source_groups)] if source_groups else "kraken"))
        for index, price in enumerate(prices)
    ]


def test_walk_forward_emits_only_chronological_backtest_baselines_with_metrics():
    records = _series()
    evaluation_as_of = _stamp(BASE + timedelta(hours=29, seconds=3))
    result = evaluate_chronological_walk_forward(
        records,
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=evaluation_as_of,
        horizon_seconds=3600,
        min_train_samples=5,
        min_out_of_sample_samples=1,
        flat_band_bps=5,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )

    assert result["status"] == "SCORED"
    assert result["live_forecast_issued"] is False
    assert result["paper_trade_executed"] is False
    assert result["forecast_count"] > 0
    assert result["out_of_sample_effective_sample_size"] == result["out_of_sample_origin_count"]
    assert result["effective_sample_size_method"] == "greedy_non_overlapping_target_intervals_v1"
    assert set(result["metrics"]) == {
        "naive_class_prior",
        "momentum_sign",
        "mean_reversion_sign",
        "volatility_normal",
    }
    for model_id, metrics in result["metrics"].items():
        assert metrics["forecast_count"] > 0
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert math.isfinite(metrics["mean_brier_score"])
        assert math.isfinite(metrics["mean_log_loss"])
        assert metrics["overlap_adjusted_effective_sample_size"] == metrics["forecast_count"]
        assert metrics["calibration"]["recalibration_applied"] is False
    for forecast in result["forecasts"]:
        assert forecast["forecast_type"] == "historical_backtest_only"
        assert forecast["live_forecast_issued"] is False
        assert forecast["paper_trade_executed"] is False
        assert forecast["data_cutoff_utc"] < forecast["target_time_utc"]
        assert set(forecast["probabilities"]) == {"down", "flat", "up"}
        assert sum(forecast["probabilities"].values()) == pytest.approx(1.0)
        assert len(forecast["alternative_scenarios"]) == 3
        assert forecast["outcome"]["outcome_event_time_utc"] > forecast["data_cutoff_utc"]


def test_backfilled_history_supports_training_only_at_or_after_its_capture_time():
    capture = BASE + timedelta(hours=23, seconds=3)
    records = [
        _bar(index, 1.0 + index * 0.001, capture_at=capture)
        for index in range(24)
    ]
    records.append(_bar(24, 1.025, capture_at=capture + timedelta(hours=1)))
    result = evaluate_chronological_walk_forward(
        records,
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=_stamp(capture + timedelta(hours=1)),
        horizon_seconds=3600,
        min_train_samples=5,
        min_out_of_sample_samples=1,
        min_effective_out_of_sample_samples=1,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )
    assert result["status"] == "SCORED"
    assert result["forecast_count"] == 4
    parsed_cutoffs = {
        datetime.fromisoformat(item["data_cutoff_utc"].replace("Z", "+00:00"))
        for item in result["forecasts"]
    }
    assert parsed_cutoffs == {capture}
    assert all(item["assumptions"]["training_example_count"] == 23 for item in result["forecasts"])
    parsed_outcomes = {
        datetime.fromisoformat(item["outcome"]["outcome_event_time_utc"].replace("Z", "+00:00"))
        for item in result["forecasts"]
    }
    assert parsed_outcomes == {BASE + timedelta(hours=24)}
    assert all(item["live_forecast_issued"] is False for item in result["forecasts"])


def test_walk_forward_requires_minimum_distinct_out_of_sample_origins():
    records = _series(30)
    result = evaluate_chronological_walk_forward(
        records,
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=_stamp(BASE + timedelta(hours=29, seconds=3)),
        horizon_seconds=3600,
        min_train_samples=5,
        min_out_of_sample_samples=100,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )

    assert result["status"] == "INSUFFICIENT_HISTORY"
    assert result["min_train_samples"] == 5
    assert result["min_out_of_sample_samples"] == 100
    assert 0 < result["out_of_sample_origin_count"] < 100
    assert result["forecast_count"] == result["out_of_sample_origin_count"] * 4
    assert result["insufficient_history_reason"].startswith("insufficient_out_of_sample_origins:")
    assert result["live_forecast_issued"] is False
    assert result["paper_trade_executed"] is False


def test_walk_forward_rejects_non_positive_out_of_sample_minimum():
    with pytest.raises(WalkForwardEvaluationError, match="min_out_of_sample_samples must be a positive integer"):
        evaluate_chronological_walk_forward(
            _series(12),
            feature_id=FEATURE_ID,
            evaluation_as_of_utc=_stamp(BASE + timedelta(hours=11, seconds=3)),
            horizon_seconds=3600,
            min_train_samples=3,
            min_out_of_sample_samples=0,
            target_tolerance_seconds=5,
            venue="kraken",
            currency_pair="XRP/USD",
        )


def test_future_price_record_cannot_be_available_before_its_event_time():
    records = _series(12)
    future = records[-1]
    event = _stamp(BASE + timedelta(hours=11))
    early = _stamp(BASE + timedelta(hours=10, seconds=30))
    future["known_at_utc"] = early
    future["source_data_as_of_utc"] = early
    future["revision_available_at_utc"] = early
    future["ingested_at_utc"] = early
    with pytest.raises(WalkForwardEvaluationError, match="available before its event time"):
        evaluate_chronological_walk_forward(
            records,
            feature_id=FEATURE_ID,
            evaluation_as_of_utc=_stamp(BASE + timedelta(hours=12)),
            horizon_seconds=3600,
            min_train_samples=3,
            target_tolerance_seconds=5,
            venue="kraken",
            currency_pair="XRP/USD",
        )


def test_mixed_venues_and_currency_pairs_are_not_aggregated_implicitly():
    records = _series(12)
    records.append(_bar(12, 1.02, venue="binance"))
    with pytest.raises(WalkForwardEvaluationError, match="select one venue"):
        evaluate_chronological_walk_forward(
            records,
            feature_id=FEATURE_ID,
            evaluation_as_of_utc=_stamp(BASE + timedelta(hours=13)),
            horizon_seconds=3600,
            min_train_samples=3,
            target_tolerance_seconds=5,
        )


def test_insufficient_future_outcomes_never_create_unscored_directional_forecasts():
    records = _series(10)
    result = evaluate_chronological_walk_forward(
        records[:7],
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=_stamp(BASE + timedelta(hours=1, seconds=2)),
        horizon_seconds=3600,
        min_train_samples=3,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )
    assert result["forecast_count"] == 0
    assert result["live_forecast_issued"] is False
    assert all(item["reason"] == "future_target_not_available_by_evaluation_cutoff" for item in result["skipped_origins"])


def test_walk_forward_embargo_excludes_training_labels_inside_buffer():
    records = _series(40)
    evaluation_as_of = _stamp(BASE + timedelta(hours=39, seconds=3))
    common = {
        "feature_id": FEATURE_ID,
        "evaluation_as_of_utc": evaluation_as_of,
        "horizon_seconds": 3600,
        "min_train_samples": 5,
        "min_out_of_sample_samples": 1,
        "target_tolerance_seconds": 5,
        "venue": "kraken",
        "currency_pair": "XRP/USD",
    }
    unembargoed = evaluate_chronological_walk_forward(records, **common)
    embargoed = evaluate_chronological_walk_forward(records, embargo_seconds=3600, **common)

    assert embargoed["embargo_seconds"] == 3600
    assert embargoed["purge_policy"] == "training_start_and_outcome_available_by_cutoff_minus_embargo"
    unembargoed_by_cutoff = {
        item["data_cutoff_utc"]: item
        for item in unembargoed["forecasts"]
        if item["model_id"] == "naive_class_prior"
    }
    embargoed_forecasts = [
        item for item in embargoed["forecasts"]
        if item["model_id"] == "naive_class_prior"
    ]
    assert embargoed_forecasts
    common_cutoffs = set(unembargoed_by_cutoff).intersection(
        item["data_cutoff_utc"] for item in embargoed_forecasts
    )
    assert common_cutoffs
    for item in embargoed_forecasts:
        cutoff = datetime.fromisoformat(item["data_cutoff_utc"].replace("Z", "+00:00"))
        training_cutoff = datetime.fromisoformat(item["training_cutoff_utc"].replace("Z", "+00:00"))
        assumptions = item["assumptions"]
        latest_outcome = datetime.fromisoformat(
            assumptions["training_latest_outcome_event_time_utc"].replace("Z", "+00:00")
        )
        latest_available = datetime.fromisoformat(
            assumptions["training_latest_outcome_available_at_utc"].replace("Z", "+00:00")
        )
        assert training_cutoff == cutoff - timedelta(hours=1)
        assert latest_outcome <= training_cutoff
        assert latest_available <= training_cutoff
        if item["data_cutoff_utc"] in common_cutoffs:
            assert assumptions["training_example_count"] <= unembargoed_by_cutoff[item["data_cutoff_utc"]]["assumptions"]["training_example_count"]


@pytest.mark.parametrize("value", [-1, True, 1.5])
def test_walk_forward_rejects_invalid_embargo_seconds(value):
    with pytest.raises(WalkForwardEvaluationError, match="embargo_seconds must be a non-negative integer"):
        evaluate_chronological_walk_forward(
            _series(12),
            feature_id=FEATURE_ID,
            evaluation_as_of_utc=_stamp(BASE + timedelta(hours=11, seconds=3)),
            horizon_seconds=3600,
            min_train_samples=3,
            min_out_of_sample_samples=1,
            target_tolerance_seconds=5,
            embargo_seconds=value,
            venue="kraken",
            currency_pair="XRP/USD",
        )

def test_walk_forward_calibration_uses_only_prior_resolved_oos_forecasts():
    records = _series(120)
    result = evaluate_chronological_walk_forward(
        records,
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=_stamp(BASE + timedelta(hours=119, seconds=3)),
        horizon_seconds=3600,
        min_train_samples=5,
        min_out_of_sample_samples=1,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )

    assert result["calibration_is_diagnostic_only"] is False
    assert result["calibration_method"] == "rolling_temporal_temperature_scaling_v1"
    assert result["min_calibration_samples"] == 50
    assert result["forecast_count"] > 100
    for forecast in result["forecasts"]:
        calibration = forecast["calibration"]
        assert calibration["fit_cutoff_utc"] == forecast["training_cutoff_utc"]
        assert calibration["calibration_sample_count"] <= result["calibration_max_history"]
        if calibration["calibration_sample_count"]:
            assert calibration["history_max_data_cutoff_utc"] < calibration["fit_cutoff_utc"]
            assert (
                calibration["history_max_outcome_event_time_utc"]
                <= calibration["fit_cutoff_utc"]
            )
            assert (
                calibration["history_max_outcome_available_at_utc"]
                <= calibration["fit_cutoff_utc"]
            )
        assert forecast["raw_scoring"]["brier_score"] >= 0
        assert sum(forecast["raw_probabilities"].values()) == pytest.approx(1.0)
        assert sum(forecast["probabilities"].values()) == pytest.approx(1.0)

    assert max(
        forecast["calibration"]["calibration_sample_count"]
        for forecast in result["forecasts"]
    ) >= 50
    for metrics in result["metrics"].values():
        assert "raw_mean_brier_score" in metrics
        assert "raw_mean_log_loss" in metrics
        assert metrics["calibration"]["method"] == "rolling_temporal_temperature_scaling_v1"


def test_walk_forward_overlap_adjusted_effective_sample_size_gates_longer_horizons():
    result = evaluate_chronological_walk_forward(
        _series(120),
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=_stamp(BASE + timedelta(hours=119, seconds=3)),
        horizon_seconds=4 * 3600,
        min_train_samples=5,
        min_out_of_sample_samples=100,
        min_effective_out_of_sample_samples=30,
        embargo_seconds=4 * 3600,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )

    assert result["out_of_sample_origin_count"] >= 100
    assert result["out_of_sample_effective_sample_size"] < 30
    assert result["out_of_sample_effective_sample_size"] < result["out_of_sample_origin_count"]
    assert result["out_of_sample_overlap_adjustment_factor"] > 3.0
    assert result["status"] == "INSUFFICIENT_EFFECTIVE_HISTORY"
    assert result["insufficient_history_reason"].startswith(
        "insufficient_overlap_adjusted_effective_sample_size:"
    )
    assert result["live_forecast_issued"] is False
    assert result["paper_trade_executed"] is False


def test_walk_forward_rejects_non_positive_effective_sample_minimum():
    with pytest.raises(
        WalkForwardEvaluationError,
        match="min_effective_out_of_sample_samples must be a positive integer",
    ):
        evaluate_chronological_walk_forward(
            _series(12),
            feature_id=FEATURE_ID,
            evaluation_as_of_utc=_stamp(BASE + timedelta(hours=11, seconds=3)),
            horizon_seconds=3600,
            min_train_samples=3,
            min_effective_out_of_sample_samples=0,
            target_tolerance_seconds=5,
            venue="kraken",
            currency_pair="XRP/USD",
        )


def test_walk_forward_clusters_each_origin_by_its_observed_target_publisher():
    records = _series(60, source_groups=[f"venue-{index}" for index in range(5)])
    result = evaluate_chronological_walk_forward(
        records,
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=_stamp(BASE + timedelta(hours=59, seconds=3)),
        horizon_seconds=3600,
        min_train_samples=5,
        min_out_of_sample_samples=1,
        min_effective_out_of_sample_samples=1,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )
    comparison = result["paired_uncertainty"]["comparisons"]["momentum_sign"]
    source = comparison["source_clustered_moving_block_bootstrap"]
    assert source["status"] == "ESTIMATED"
    assert source["source_cluster_count"] == 5
    assert source["observed_minimum_origins_per_source_cluster"] >= 2
    assert all(
        item["assumptions"]["outcome_source_group_resolution_status"] == "RESOLVED"
        and len(item["assumptions"]["outcome_source_independence_groups"]) == 1
        for item in result["forecasts"]
    )


def test_walk_forward_does_not_force_multi_publisher_target_into_one_cluster():
    records = _series(60)
    for index, record in enumerate(records):
        record["sources"].append({
            "source_id": f"secondary-{index}",
            "independence_group": "secondary-publisher",
            "source_uri": f"https://api.secondary-publisher.example/xrp/{index}",
            "raw_content_sha256": f"{index + 1000:064x}",
        })
    result = evaluate_chronological_walk_forward(
        records,
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=_stamp(BASE + timedelta(hours=59, seconds=3)),
        horizon_seconds=3600,
        min_train_samples=5,
        min_out_of_sample_samples=1,
        min_effective_out_of_sample_samples=1,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )
    comparison = result["paired_uncertainty"]["comparisons"]["momentum_sign"]
    source = comparison["source_clustered_moving_block_bootstrap"]
    assert source["status"] == "INSUFFICIENT_SOURCE_CLUSTERS"
    assert source["source_cluster_count"] == 0
    assert all(
        item["assumptions"]["outcome_source_group_resolution_status"] == "MULTIPLE_OUTCOME_SOURCE_GROUPS"
        and item["assumptions"]["outcome_source_cluster_id"] is None
        for item in result["forecasts"]
    )


def test_walk_forward_reports_paired_bootstrap_and_fails_closed_on_one_source_group():
    records = _series(50)
    result = evaluate_chronological_walk_forward(
        records,
        feature_id=FEATURE_ID,
        evaluation_as_of_utc=_stamp(BASE + timedelta(hours=49, seconds=3)),
        horizon_seconds=3600,
        min_train_samples=5,
        min_out_of_sample_samples=1,
        min_effective_out_of_sample_samples=1,
        target_tolerance_seconds=5,
        venue="kraken",
        currency_pair="XRP/USD",
    )

    assert result["paired_uncertainty"]["method"] == "paired_temporal_and_source_clustered_moving_block_bootstrap_v1"
    comparison = result["paired_uncertainty"]["comparisons"]["momentum_sign"]
    assert comparison["paired_origin_count"] == result["out_of_sample_origin_count"]
    assert comparison["temporal_moving_block_bootstrap"]["status"] == "ESTIMATED"
    source = comparison["source_clustered_moving_block_bootstrap"]
    assert source["status"] == "INSUFFICIENT_SOURCE_CLUSTERS"
    assert source["source_cluster_count"] == 1
    assert all(
        item["assumptions"]["source_independence_groups"] == ["kraken"]
        for item in result["forecasts"]
    )
