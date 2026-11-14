from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from barrot_agent.evolution.paired_block_bootstrap import (
    PairedBootstrapError,
    evaluate_paired_block_bootstrap,
)

BASE = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _rows(*, origins=60, source_clusters=5):
    rows = []
    for index in range(origins):
        origin_id = f"origin-{index:04d}"
        stamp = (BASE + timedelta(hours=index)).isoformat().replace("+00:00", "Z")
        group_id = f"independent-source-{index % source_clusters}"
        naive_brier = 0.30 + (index % 3) * 0.001
        naive_log = 0.80 + (index % 4) * 0.002
        rows.extend([
            {
                "origin_id": origin_id,
                "origin_time_utc": stamp,
                "source_group_id": group_id,
                "model_id": "naive_class_prior",
                "brier_loss": naive_brier,
                "log_loss": naive_log,
            },
            {
                "origin_id": origin_id,
                "origin_time_utc": stamp,
                "source_group_id": group_id,
                "model_id": "momentum_sign",
                "brier_loss": naive_brier - 0.05,
                "log_loss": naive_log - 0.10,
            },
        ])
    return rows


def test_paired_temporal_and_source_bootstrap_is_deterministic_and_paired():
    rows = _rows()
    source_cadence = {f"independent-source-{index}": 18_000 for index in range(5)}
    first = evaluate_paired_block_bootstrap(rows, bootstrap_replicates=300, expected_cadence_seconds=3600, expected_source_cadence_seconds_by_group=source_cadence)
    second = evaluate_paired_block_bootstrap(rows, bootstrap_replicates=300, expected_cadence_seconds=3600, expected_source_cadence_seconds_by_group=source_cadence)

    comparison = first["comparisons"]["momentum_sign"]
    assert comparison["paired_origin_count"] == 60
    assert comparison["mean_brier_difference_vs_benchmark"] == pytest.approx(-0.05)
    assert comparison["mean_log_loss_difference_vs_benchmark"] == pytest.approx(-0.10)
    assert comparison["temporal_moving_block_bootstrap"]["status"] == "ESTIMATED"
    assert comparison["source_clustered_moving_block_bootstrap"]["status"] == "ESTIMATED"
    assert comparison["source_clustered_moving_block_bootstrap"]["source_cluster_count"] == 5
    assert comparison["source_clustered_moving_block_bootstrap"]["source_group_ids"] == [
        "independent-source-0", "independent-source-1", "independent-source-2",
        "independent-source-3", "independent-source-4",
    ]
    temporal_diagnostics = comparison["temporal_moving_block_bootstrap"]["sampling_diagnostics"]
    assert temporal_diagnostics["cadence_source"] == "declared"
    source_diagnostics = comparison["source_clustered_moving_block_bootstrap"]["brier_sampling_diagnostics"]["per_cluster"]
    assert set(source_diagnostics) == set(comparison["source_clustered_moving_block_bootstrap"]["source_group_ids"])
    assert all(item["cadence_source"] == "declared" for item in source_diagnostics.values())
    assert comparison["temporal_moving_block_bootstrap"]["brier_difference_ci_95"] == pytest.approx([-0.05, -0.05])
    assert comparison["source_clustered_moving_block_bootstrap"]["log_loss_difference_ci_95"] == pytest.approx([-0.10, -0.10])
    assert first == second


def test_single_source_does_not_produce_a_source_clustered_confidence_interval():
    result = evaluate_paired_block_bootstrap(
        _rows(origins=40, source_clusters=1),
        bootstrap_replicates=200,
    )
    comparison = result["comparisons"]["momentum_sign"]
    assert comparison["temporal_moving_block_bootstrap"]["status"] == "ESTIMATED"
    source = comparison["source_clustered_moving_block_bootstrap"]
    assert source["status"] == "INSUFFICIENT_SOURCE_CLUSTERS"
    assert source["source_cluster_count"] == 1
    assert source["brier_difference_ci_95"] is None


def test_adjusted_confidence_level_is_reported():
    rows = _rows()
    result = evaluate_paired_block_bootstrap(
        rows, bootstrap_replicates=10000, confidence_level=0.99375
    )
    temporal = result["comparisons"]["momentum_sign"]["temporal_moving_block_bootstrap"]
    assert result["confidence_level"] == pytest.approx(0.99375)
    assert temporal["confidence_level"] == pytest.approx(0.99375)
    assert len(temporal["brier_difference_ci"]) == 2


def test_invalid_confidence_level_is_rejected():
    with pytest.raises(PairedBootstrapError, match="confidence_level"):
        evaluate_paired_block_bootstrap(_rows(), confidence_level=1.0)


def test_source_cluster_minimum_must_cover_block_length():
    with pytest.raises(
        PairedBootstrapError,
        match="minimum_origins_per_source_cluster must be at least block_length_origins",
    ):
        evaluate_paired_block_bootstrap(
            _rows(),
            bootstrap_replicates=200,
            block_length_origins=5,
            minimum_origins_per_source_cluster=4,
        )


def test_duplicate_origin_model_pair_is_rejected():
    rows = _rows(origins=30, source_clusters=5)
    rows.append(dict(rows[0]))
    with pytest.raises(PairedBootstrapError, match="duplicate"):
        evaluate_paired_block_bootstrap(rows, bootstrap_replicates=200)


def test_model_without_benchmark_match_is_not_paired():
    rows = _rows(origins=30, source_clusters=5)
    rows = [row for row in rows if not (
        row["origin_id"] == "origin-0000" and row["model_id"] == "naive_class_prior"
    )]
    result = evaluate_paired_block_bootstrap(rows, bootstrap_replicates=200)
    assert result["comparisons"]["momentum_sign"]["paired_origin_count"] == 29
    assert result["comparisons"]["momentum_sign"]["temporal_moving_block_bootstrap"]["status"] == "INSUFFICIENT_ORIGINS"


def test_temporal_bootstrap_refuses_to_bridge_large_timestamp_gaps():
    rows = []
    indexes = [0, 1, 2, 3, 20, 21, 22, 23]
    for position, hour in enumerate(indexes):
        stamp = (BASE + timedelta(hours=hour)).isoformat().replace("+00:00", "Z")
        group_id = "single-independent-source"
        naive_brier = 0.30 + (position % 3) * 0.001
        naive_log = 0.80 + (position % 4) * 0.002
        rows.extend([
            {
                "origin_id": f"gap-origin-{position:04d}",
                "origin_time_utc": stamp,
                "source_group_id": group_id,
                "model_id": "naive_class_prior",
                "brier_loss": naive_brier,
                "log_loss": naive_log,
            },
            {
                "origin_id": f"gap-origin-{position:04d}",
                "origin_time_utc": stamp,
                "source_group_id": group_id,
                "model_id": "momentum_sign",
                "brier_loss": naive_brier - 0.05,
                "log_loss": naive_log - 0.10,
            },
        ])

    result = evaluate_paired_block_bootstrap(
        rows,
        block_length_origins=5,
        bootstrap_replicates=200,
        minimum_origins=5,
        minimum_source_clusters=5,
        expected_cadence_seconds=3600,
    )
    comparison = result["comparisons"]["momentum_sign"]
    temporal = comparison["temporal_moving_block_bootstrap"]

    assert comparison["paired_origin_count"] == 8
    assert temporal["status"] == "INSUFFICIENT_CONTIGUOUS_BLOCKS"
    assert temporal["brier_difference_ci"] is None
    assert temporal["sampling_diagnostics"]["contiguous_segment_count"] == 2
    assert temporal["sampling_diagnostics"]["contiguous_segment_lengths"] == [4, 4]
    assert temporal["sampling_diagnostics"]["valid_block_window_count"] == 0


def _candidate_rows(*, origins=100, start=BASE):
    rows = []
    baseline_levels = {
        "naive_class_prior": (0.30, 0.80),
        "momentum_sign": (0.29, 0.75),
        "mean_reversion_sign": (0.28, 0.70),
        "volatility_normal": (0.27, 0.65),
    }
    for index in range(origins):
        origin_id = f"candidate-origin-{index:04d}"
        stamp = (start + timedelta(hours=index)).isoformat().replace("+00:00", "Z")
        group_id = f"independent-source-{index % 5}"
        brier_variation = (index % 3) * 0.001
        log_variation = (index % 4) * 0.002
        rows.append({
            "origin_id": origin_id,
            "origin_time_utc": stamp,
            "source_group_id": group_id,
            "model_id": "xrp-candidate-v1",
            "brier_loss": 0.20 + brier_variation,
            "log_loss": 0.40 + log_variation,
        })
        for model_id, (brier_base, log_base) in baseline_levels.items():
            rows.append({
                "origin_id": origin_id,
                "origin_time_utc": stamp,
                "source_group_id": group_id,
                "model_id": model_id,
                "brier_loss": brier_base + brier_variation,
                "log_loss": log_base + log_variation,
            })
    return rows


def test_candidate_readiness_uncertainty_compares_all_baselines_in_both_windows():
    from barrot_agent.evolution.paired_block_bootstrap import evaluate_candidate_readiness_uncertainty

    source_cadence = {f"independent-source-{index}": 18_000 for index in range(5)}
    result = evaluate_candidate_readiness_uncertainty(
        _candidate_rows(),
        _candidate_rows(start=BASE + timedelta(days=10)),
        candidate_model_id="xrp-candidate-v1",
        expected_cadence_seconds=3600,
        expected_source_cadence_seconds_by_group=source_cadence,
    )

    assert result["status"] == "PASS"
    assert result["familywise_comparison_count"] == 8
    assert result["individual_confidence_level"] == pytest.approx(0.99375)
    for window_name in ("out_of_sample", "shadow_evaluation"):
        window = result[window_name]
        assert window["status"] == "PASS"
        assert set(window["comparisons"]) == {
            "naive_class_prior",
            "momentum_sign",
            "mean_reversion_sign",
            "volatility_normal",
        }
        for comparison in window["comparisons"].values():
            assert comparison["status"] == "PASS"
            assert comparison["paired_origin_count"] == 100
            assert comparison["temporal_moving_block_bootstrap"]["confidence_level"] == pytest.approx(0.99375)
            assert comparison["source_clustered_moving_block_bootstrap"]["source_cluster_count"] == 5


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("bootstrap_replicates", 9_999, "bootstrap_replicates"),
        ("minimum_paired_origins", 99, "minimum_paired_origins"),
        ("minimum_source_clusters", 4, "minimum_source_clusters"),
    ],
)
def test_candidate_readiness_uncertainty_rejects_below_policy_floors(field, value, message):
    from barrot_agent.evolution.paired_block_bootstrap import evaluate_candidate_readiness_uncertainty

    kwargs = {
        "candidate_model_id": "xrp-candidate-v1",
        "expected_cadence_seconds": 3600,
        "expected_source_cadence_seconds_by_group": {
            f"independent-source-{index}": 18_000 for index in range(5)
        },
        field: value,
    }
    with pytest.raises(PairedBootstrapError, match=message):
        evaluate_candidate_readiness_uncertainty([], [], **kwargs)
