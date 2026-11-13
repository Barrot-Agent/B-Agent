"""Paired temporal and source-clustered uncertainty for walk-forward losses."""
from __future__ import annotations

import math
import random
import statistics
from collections import defaultdict
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any


class PairedBootstrapError(ValueError):
    """A paired bootstrap input violates its provenance or scoring contract."""


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise PairedBootstrapError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise PairedBootstrapError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PairedBootstrapError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _loss(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PairedBootstrapError(f"{field} must be a finite non-negative number")
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise PairedBootstrapError(f"{field} must be a finite non-negative number")
    return result


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise PairedBootstrapError("percentile requires observations")
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _moving_block_sample(values: list[float], block_length: int, rng: random.Random) -> list[float]:
    """Circular moving-block resample with the original sample length."""
    if not values:
        return []
    size = len(values)
    width = min(block_length, size)
    sample: list[float] = []
    while len(sample) < size:
        start = rng.randrange(size)
        for offset in range(width):
            sample.append(values[(start + offset) % size])
            if len(sample) == size:
                break
    return sample


def _temporal_interval(
    values: list[float], *, block_length: int, replicates: int, seed: int
) -> list[float]:
    rng = random.Random(seed)
    means = [
        statistics.fmean(_moving_block_sample(values, block_length, rng))
        for _ in range(replicates)
    ]
    return [_percentile(means, 0.025), _percentile(means, 0.975)]


def _source_cluster_interval(
    clusters: Mapping[str, list[tuple[datetime, float]]],
    *,
    block_length: int,
    replicates: int,
    seed: int,
) -> tuple[list[float], float]:
    """Resample source groups, then contiguous time blocks within each group."""
    cluster_ids = sorted(clusters)
    point_estimate = statistics.fmean(
        statistics.fmean(value for _, value in clusters[group_id])
        for group_id in cluster_ids
    )
    rng = random.Random(seed)
    means: list[float] = []
    for _ in range(replicates):
        selected_cluster_means = []
        for _ in cluster_ids:
            group_id = rng.choice(cluster_ids)
            values = [
                value
                for _, value in sorted(clusters[group_id], key=lambda item: item[0])
            ]
            sampled = _moving_block_sample(values, min(block_length, len(values)), rng)
            selected_cluster_means.append(statistics.fmean(sampled))
        means.append(statistics.fmean(selected_cluster_means))
    return [_percentile(means, 0.025), _percentile(means, 0.975)], point_estimate


def evaluate_paired_block_bootstrap(
    observations: Iterable[Mapping[str, Any]],
    *,
    benchmark_model_id: str = "naive_class_prior",
    block_length_origins: int = 5,
    bootstrap_replicates: int = 1000,
    minimum_origins: int = 30,
    minimum_source_clusters: int = 5,
    minimum_origins_per_source_cluster: int = 2,
    random_seed: int = 20261113,
) -> dict[str, Any]:
    """Compare each model with a benchmark using paired temporal/source resampling.

    A source_group_id must come from the source registry's independence_group.
    Candidate and benchmark losses are paired only at the same origin. If their
    source groups differ, that origin is excluded from source-clustered analysis.
    """
    if not isinstance(benchmark_model_id, str) or not benchmark_model_id.strip():
        raise PairedBootstrapError("benchmark_model_id is required")
    benchmark_model_id = benchmark_model_id.strip()
    for value, field, minimum in (
        (block_length_origins, "block_length_origins", 1),
        (bootstrap_replicates, "bootstrap_replicates", 100),
        (minimum_origins, "minimum_origins", 2),
        (minimum_source_clusters, "minimum_source_clusters", 2),
        (minimum_origins_per_source_cluster, "minimum_origins_per_source_cluster", 2),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise PairedBootstrapError(f"{field} must be an integer of at least {minimum}")
    if isinstance(random_seed, bool) or not isinstance(random_seed, int):
        raise PairedBootstrapError("random_seed must be an integer")

    by_origin: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    origin_times: dict[str, datetime] = {}
    for index, row in enumerate(observations):
        if not isinstance(row, Mapping):
            raise PairedBootstrapError("observations must contain mapping objects")
        origin_id, model_id = row.get("origin_id"), row.get("model_id")
        if not isinstance(origin_id, str) or not origin_id.strip():
            raise PairedBootstrapError(f"observations[{index}].origin_id is required")
        if not isinstance(model_id, str) or not model_id.strip():
            raise PairedBootstrapError(f"observations[{index}].model_id is required")
        origin_id, model_id = origin_id.strip(), model_id.strip()
        event_time = _timestamp(row.get("origin_time_utc"), "origin_time_utc")
        if origin_id in origin_times and origin_times[origin_id] != event_time:
            raise PairedBootstrapError("one origin_id cannot map to multiple timestamps")
        origin_times[origin_id] = event_time
        if model_id in by_origin[origin_id]:
            raise PairedBootstrapError("duplicate (origin_id, model_id) observation")
        group_id = row.get("source_group_id")
        if group_id is not None and (
            not isinstance(group_id, str) or not group_id.strip()
        ):
            raise PairedBootstrapError("source_group_id must be a non-empty string or null")
        by_origin[origin_id][model_id] = {
            "source_group_id": group_id.strip() if isinstance(group_id, str) else None,
            "brier_loss": _loss(row.get("brier_loss"), "brier_loss"),
            "log_loss": _loss(row.get("log_loss"), "log_loss"),
        }

    model_ids = sorted({
        model_id for models in by_origin.values() for model_id in models
        if model_id != benchmark_model_id
    })
    comparisons: dict[str, Any] = {}
    for model_index, model_id in enumerate(model_ids):
        paired = []
        for origin_id, models in by_origin.items():
            candidate, benchmark = models.get(model_id), models.get(benchmark_model_id)
            if candidate is None or benchmark is None:
                continue
            group_id = candidate["source_group_id"]
            if group_id != benchmark["source_group_id"]:
                group_id = None
            paired.append({
                "origin_id": origin_id,
                "origin_time": origin_times[origin_id],
                "source_group_id": group_id,
                "brier_difference": candidate["brier_loss"] - benchmark["brier_loss"],
                "log_loss_difference": candidate["log_loss"] - benchmark["log_loss"],
            })
        paired.sort(key=lambda item: (item["origin_time"], item["origin_id"]))
        count = len(paired)
        brier = [item["brier_difference"] for item in paired]
        log_loss = [item["log_loss_difference"] for item in paired]

        if count >= minimum_origins:
            temporal = {
                "status": "ESTIMATED",
                "confidence_level": 0.95,
                "brier_difference_ci_95": _temporal_interval(
                    brier, block_length=block_length_origins,
                    replicates=bootstrap_replicates, seed=random_seed + model_index * 10 + 1,
                ),
                "log_loss_difference_ci_95": _temporal_interval(
                    log_loss, block_length=block_length_origins,
                    replicates=bootstrap_replicates, seed=random_seed + model_index * 10 + 2,
                ),
            }
        else:
            temporal = {
                "status": "INSUFFICIENT_ORIGINS",
                "required_origins": minimum_origins,
                "observed_origins": count,
                "brier_difference_ci_95": None,
                "log_loss_difference_ci_95": None,
            }

        brier_clusters: dict[str, list[tuple[datetime, float]]] = defaultdict(list)
        log_clusters: dict[str, list[tuple[datetime, float]]] = defaultdict(list)
        for item in paired:
            group_id = item["source_group_id"]
            if group_id is None:
                continue
            brier_clusters[group_id].append((item["origin_time"], item["brier_difference"]))
            log_clusters[group_id].append((item["origin_time"], item["log_loss_difference"]))
        cluster_sizes = [len(values) for values in brier_clusters.values()]
        cluster_count = len(brier_clusters)
        enough_clusters = (
            cluster_count >= minimum_source_clusters
            and bool(cluster_sizes)
            and min(cluster_sizes) >= minimum_origins_per_source_cluster
        )
        if enough_clusters:
            brier_ci, brier_cluster_mean = _source_cluster_interval(
                brier_clusters, block_length=block_length_origins,
                replicates=bootstrap_replicates, seed=random_seed + model_index * 10 + 3,
            )
            log_ci, log_cluster_mean = _source_cluster_interval(
                log_clusters, block_length=block_length_origins,
                replicates=bootstrap_replicates, seed=random_seed + model_index * 10 + 4,
            )
            source_clustered = {
                "status": "ESTIMATED",
                "confidence_level": 0.95,
                "source_cluster_count": cluster_count,
                "minimum_origins_per_source_cluster": minimum_origins_per_source_cluster,
                "equal_cluster_weighted_mean_brier_difference": brier_cluster_mean,
                "equal_cluster_weighted_mean_log_loss_difference": log_cluster_mean,
                "brier_difference_ci_95": brier_ci,
                "log_loss_difference_ci_95": log_ci,
            }
        else:
            source_clustered = {
                "status": "INSUFFICIENT_SOURCE_CLUSTERS",
                "source_cluster_count": cluster_count,
                "required_source_clusters": minimum_source_clusters,
                "minimum_origins_per_source_cluster": minimum_origins_per_source_cluster,
                "observed_minimum_origins_per_source_cluster": min(cluster_sizes) if cluster_sizes else 0,
                "brier_difference_ci_95": None,
                "log_loss_difference_ci_95": None,
            }

        comparisons[model_id] = {
            "paired_origin_count": count,
            "mean_brier_difference_vs_benchmark": statistics.fmean(brier) if paired else None,
            "mean_log_loss_difference_vs_benchmark": statistics.fmean(log_loss) if paired else None,
            "temporal_moving_block_bootstrap": temporal,
            "source_clustered_moving_block_bootstrap": source_clustered,
        }

    return {
        "method": "paired_temporal_and_source_clustered_moving_block_bootstrap_v1",
        "benchmark_model_id": benchmark_model_id,
        "block_length_origins": block_length_origins,
        "bootstrap_replicates": bootstrap_replicates,
        "minimum_origins": minimum_origins,
        "minimum_source_clusters": minimum_source_clusters,
        "minimum_origins_per_source_cluster": minimum_origins_per_source_cluster,
        "random_seed": random_seed,
        "interpretation": (
            "Loss differences are model minus benchmark; negative values favor the model. "
            "Temporal intervals resample contiguous origin blocks. Source-clustered intervals "
            "resample registry independence groups and then temporal blocks within each group. "
            "Too few independent source groups yields no source-clustered CI. These diagnostics "
            "do not authorize a live forecast."
        ),
        "comparisons": comparisons,
    }
