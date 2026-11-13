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
    first = evaluate_paired_block_bootstrap(rows, bootstrap_replicates=300)
    second = evaluate_paired_block_bootstrap(rows, bootstrap_replicates=300)

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
