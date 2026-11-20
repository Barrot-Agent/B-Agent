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


def _contiguous_block_windows(
    values: list[float],
    times: list[datetime],
    *,
    block_length: int,
    max_gap_multiple: float,
    expected_cadence_seconds: float | None = None,
) -> tuple[list[tuple[float, ...]], dict[str, Any]]:
    """Build non-circular blocks that never cross an observed timestamp gap."""
    if len(values) != len(times):
        raise PairedBootstrapError("block values and timestamps must have equal lengths")
    if not values or len(values) < block_length:
        return [], {
            "cadence_seconds": expected_cadence_seconds,
            "cadence_source": "declared" if expected_cadence_seconds is not None else "unavailable",
            "max_gap_multiple": max_gap_multiple,
            "contiguous_segment_count": 0,
            "contiguous_segment_lengths": [],
            "largest_contiguous_segment": 0,
            "valid_block_window_count": 0,
            "sample_origin_count": len(values),
            "sampling_policy": "non_circular_contiguous_time_blocks_v1",
        }

    deltas = [
        (times[index] - times[index - 1]).total_seconds()
        for index in range(1, len(times))
    ]
    positive_deltas = [delta for delta in deltas if delta > 0]
    if expected_cadence_seconds is None:
        cadence = statistics.median(positive_deltas) if positive_deltas else None
        cadence_source = "median_observed_interval"
    else:
        cadence = float(expected_cadence_seconds)
        cadence_source = "declared"

    if cadence is None or not math.isfinite(float(cadence)) or cadence <= 0:
        return [], {
            "cadence_seconds": None,
            "cadence_source": cadence_source,
            "max_gap_multiple": max_gap_multiple,
            "contiguous_segment_count": 0,
            "contiguous_segment_lengths": [],
            "largest_contiguous_segment": 0,
            "valid_block_window_count": 0,
            "sample_origin_count": len(values),
            "sampling_policy": "non_circular_contiguous_time_blocks_v1",
        }

    segments: list[tuple[int, int]] = []
    segment_start = 0
    for index, delta in enumerate(deltas, start=1):
        if delta <= 0 or delta > cadence * max_gap_multiple:
            segments.append((segment_start, index))
            segment_start = index
    segments.append((segment_start, len(values)))

    segment_lengths = [end - start for start, end in segments]
    windows: list[tuple[float, ...]] = []
    for start, end in segments:
        for window_start in range(start, end - block_length + 1):
            windows.append(tuple(values[window_start:window_start + block_length]))

    return windows, {
        "cadence_seconds": float(cadence),
        "cadence_source": cadence_source,
        "max_gap_multiple": float(max_gap_multiple),
        "contiguous_segment_count": len(segments),
        "contiguous_segment_lengths": segment_lengths,
        "largest_contiguous_segment": max(segment_lengths, default=0),
        "valid_block_window_count": len(windows),
        "sample_origin_count": len(values),
        "sampling_policy": "non_circular_contiguous_time_blocks_v1",
    }


def _moving_block_sample(
    windows: list[tuple[float, ...]],
    sample_size: int,
    rng: random.Random,
) -> list[float] | None:
    """Sample fixed-length blocks without circular wrap or gap bridging."""
    if not windows:
        return None
    sample: list[float] = []
    while len(sample) < sample_size:
        block = rng.choice(windows)
        sample.extend(block[:sample_size - len(sample)])
    return sample


def _temporal_interval(
    values: list[float],
    times: list[datetime],
    *,
    block_length: int,
    replicates: int,
    seed: int,
    confidence_level: float,
    max_gap_multiple: float,
    expected_cadence_seconds: float | None = None,
) -> tuple[list[float] | None, dict[str, Any]]:
    windows, diagnostics = _contiguous_block_windows(
        values,
        times,
        block_length=block_length,
        max_gap_multiple=max_gap_multiple,
        expected_cadence_seconds=expected_cadence_seconds,
    )
    if not windows:
        return None, diagnostics
    rng = random.Random(seed)
    means = []
    for _ in range(replicates):
        sampled = _moving_block_sample(windows, len(values), rng)
        if sampled is None:
            return None, diagnostics
        means.append(statistics.fmean(sampled))
    tail = (1.0 - confidence_level) / 2.0
    return [_percentile(means, tail), _percentile(means, 1.0 - tail)], diagnostics


def _source_cluster_interval(
    clusters: Mapping[str, list[tuple[datetime, float]]],
    *,
    block_length: int,
    replicates: int,
    seed: int,
    confidence_level: float,
    max_gap_multiple: float,
    expected_cadence_seconds_by_group: Mapping[str, float] | None,
) -> tuple[list[float] | None, float, dict[str, Any]]:
    """Resample independent source groups and contiguous time blocks within each."""
    cluster_ids = sorted(clusters)
    point_estimate = statistics.fmean(
        statistics.fmean(value for _, value in clusters[group_id])
        for group_id in cluster_ids
    )
    cluster_windows: dict[str, list[tuple[float, ...]]] = {}
    cluster_diagnostics: dict[str, dict[str, Any]] = {}
    for group_id in cluster_ids:
        ordered = sorted(clusters[group_id], key=lambda item: item[0])
        times = [timestamp for timestamp, _ in ordered]
        values = [value for _, value in ordered]
        windows, diagnostics = _contiguous_block_windows(
            values,
            times,
            block_length=block_length,
            max_gap_multiple=max_gap_multiple,
            expected_cadence_seconds=(expected_cadence_seconds_by_group or {}).get(group_id),
        )
        cluster_windows[group_id] = windows
        cluster_diagnostics[group_id] = diagnostics
        if not windows:
            return None, point_estimate, {
                "status": "INSUFFICIENT_CONTIGUOUS_BLOCKS",
                "source_cluster_count": len(cluster_ids),
                "source_group_ids": cluster_ids,
                "per_cluster": cluster_diagnostics,
            }

    rng = random.Random(seed)
    means: list[float] = []
    for _ in range(replicates):
        selected_cluster_means = []
        for _ in cluster_ids:
            group_id = rng.choice(cluster_ids)
            sample = _moving_block_sample(
                cluster_windows[group_id],
                len(clusters[group_id]),
                rng,
            )
            if sample is None:
                return None, point_estimate, {
                    "status": "INSUFFICIENT_CONTIGUOUS_BLOCKS",
                    "source_cluster_count": len(cluster_ids),
                    "source_group_ids": cluster_ids,
                    "per_cluster": cluster_diagnostics,
                }
            selected_cluster_means.append(statistics.fmean(sample))
        means.append(statistics.fmean(selected_cluster_means))
    tail = (1.0 - confidence_level) / 2.0
    return (
        [_percentile(means, tail), _percentile(means, 1.0 - tail)],
        point_estimate,
        {
            "status": "ESTIMATED",
            "source_cluster_count": len(cluster_ids),
            "source_group_ids": cluster_ids,
            "per_cluster": cluster_diagnostics,
        },
    )


def evaluate_paired_block_bootstrap(
    observations: Iterable[Mapping[str, Any]],
    *,
    benchmark_model_id: str = "naive_class_prior",
    block_length_origins: int = 5,
    bootstrap_replicates: int = 1000,
    minimum_origins: int = 30,
    minimum_source_clusters: int = 5,
    minimum_origins_per_source_cluster: int = 5,
    random_seed: int = 20261113,
    confidence_level: float = 0.95,
    max_gap_multiple: float = 1.5,
    expected_cadence_seconds: float | None = None,
    expected_source_cadence_seconds_by_group: Mapping[str, float] | None = None,
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
    if (
        isinstance(confidence_level, bool)
        or not isinstance(confidence_level, (int, float))
        or not math.isfinite(float(confidence_level))
        or not 0.0 < float(confidence_level) < 1.0
    ):
        raise PairedBootstrapError("confidence_level must be finite and strictly between zero and one")
    confidence_level = float(confidence_level)
    if (
        isinstance(max_gap_multiple, bool)
        or not isinstance(max_gap_multiple, (int, float))
        or not math.isfinite(float(max_gap_multiple))
        or float(max_gap_multiple) < 1.0
    ):
        raise PairedBootstrapError("max_gap_multiple must be finite and at least one")
    max_gap_multiple = float(max_gap_multiple)
    if expected_cadence_seconds is not None and (
        isinstance(expected_cadence_seconds, bool)
        or not isinstance(expected_cadence_seconds, (int, float))
        or not math.isfinite(float(expected_cadence_seconds))
        or float(expected_cadence_seconds) <= 0
    ):
        raise PairedBootstrapError("expected_cadence_seconds must be finite and positive")
    if expected_source_cadence_seconds_by_group is not None:
        if not isinstance(expected_source_cadence_seconds_by_group, Mapping):
            raise PairedBootstrapError("expected_source_cadence_seconds_by_group must be a mapping")
        for group_id, cadence in expected_source_cadence_seconds_by_group.items():
            if not isinstance(group_id, str) or not group_id.strip():
                raise PairedBootstrapError("source cadence group IDs must be non-empty strings")
            if (
                isinstance(cadence, bool)
                or not isinstance(cadence, (int, float))
                or not math.isfinite(float(cadence))
                or float(cadence) <= 0
            ):
                raise PairedBootstrapError("source-group cadence values must be finite and positive")
    if minimum_origins_per_source_cluster < block_length_origins:
        raise PairedBootstrapError(
            "minimum_origins_per_source_cluster must be at least block_length_origins"
        )

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

        origin_times_for_pairing = [item["origin_time"] for item in paired]
        temporal_brier_ci, temporal_brier_diagnostics = _temporal_interval(
            brier,
            origin_times_for_pairing,
            block_length=block_length_origins,
            replicates=bootstrap_replicates,
            seed=random_seed + model_index * 10 + 1,
            confidence_level=confidence_level,
            max_gap_multiple=max_gap_multiple,
            expected_cadence_seconds=expected_cadence_seconds,
        )
        temporal_log_ci, temporal_log_diagnostics = _temporal_interval(
            log_loss,
            origin_times_for_pairing,
            block_length=block_length_origins,
            replicates=bootstrap_replicates,
            seed=random_seed + model_index * 10 + 2,
            confidence_level=confidence_level,
            max_gap_multiple=max_gap_multiple,
            expected_cadence_seconds=expected_cadence_seconds,
        )
        if count < minimum_origins:
            temporal = {
                "status": "INSUFFICIENT_ORIGINS",
                "required_origins": minimum_origins,
                "observed_origins": count,
                "brier_difference_ci": None,
                "log_loss_difference_ci": None,
                "sampling_diagnostics": temporal_brier_diagnostics,
            }
        elif temporal_brier_ci is None or temporal_log_ci is None:
            temporal = {
                "status": "INSUFFICIENT_CONTIGUOUS_BLOCKS",
                "required_block_length_origins": block_length_origins,
                "brier_difference_ci": None,
                "log_loss_difference_ci": None,
                "sampling_diagnostics": temporal_brier_diagnostics,
                "log_loss_sampling_diagnostics": temporal_log_diagnostics,
            }
        else:
            temporal = {
                "status": "ESTIMATED",
                "confidence_level": confidence_level,
                "brier_difference_ci": temporal_brier_ci,
                "log_loss_difference_ci": temporal_log_ci,
                "sampling_diagnostics": temporal_brier_diagnostics,
                "log_loss_sampling_diagnostics": temporal_log_diagnostics,
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
            brier_ci, brier_cluster_mean, brier_diagnostics = _source_cluster_interval(
                brier_clusters,
                block_length=block_length_origins,
                replicates=bootstrap_replicates,
                seed=random_seed + model_index * 10 + 3,
                confidence_level=confidence_level,
                max_gap_multiple=max_gap_multiple,
                expected_cadence_seconds_by_group=expected_source_cadence_seconds_by_group,
            )
            log_ci, log_cluster_mean, log_diagnostics = _source_cluster_interval(
                log_clusters,
                block_length=block_length_origins,
                replicates=bootstrap_replicates,
                seed=random_seed + model_index * 10 + 4,
                confidence_level=confidence_level,
                max_gap_multiple=max_gap_multiple,
                expected_cadence_seconds_by_group=expected_source_cadence_seconds_by_group,
            )
            if brier_ci is None or log_ci is None:
                source_clustered = {
                    "status": "INSUFFICIENT_CONTIGUOUS_BLOCKS",
                    "source_cluster_count": cluster_count,
                    "source_group_ids": sorted(brier_clusters),
                    "required_block_length_origins": block_length_origins,
                    "brier_sampling_diagnostics": brier_diagnostics,
                    "log_loss_sampling_diagnostics": log_diagnostics,
                    "brier_difference_ci": None,
                    "log_loss_difference_ci": None,
                }
            else:
                source_clustered = {
                    "status": "ESTIMATED",
                    "confidence_level": confidence_level,
                    "source_cluster_count": cluster_count,
                    "source_group_ids": sorted(brier_clusters),
                    "minimum_origins_per_source_cluster": minimum_origins_per_source_cluster,
                    "observed_minimum_origins_per_source_cluster": min(cluster_sizes),
                    "equal_cluster_weighted_mean_brier_difference": brier_cluster_mean,
                    "equal_cluster_weighted_mean_log_loss_difference": log_cluster_mean,
                    "brier_difference_ci": brier_ci,
                    "log_loss_difference_ci": log_ci,
                    "brier_sampling_diagnostics": brier_diagnostics,
                    "log_loss_sampling_diagnostics": log_diagnostics,
                }
        else:
            source_clustered = {
                "status": "INSUFFICIENT_SOURCE_CLUSTERS",
                "source_cluster_count": cluster_count,
                "source_group_ids": sorted(brier_clusters),
                "required_source_clusters": minimum_source_clusters,
                "minimum_origins_per_source_cluster": minimum_origins_per_source_cluster,
                "observed_minimum_origins_per_source_cluster": min(cluster_sizes) if cluster_sizes else 0,
                "brier_difference_ci": None,
                "log_loss_difference_ci": None,
            }

        if math.isclose(confidence_level, 0.95, rel_tol=0.0, abs_tol=1e-12):
            temporal["brier_difference_ci_95"] = temporal.get("brier_difference_ci")
            temporal["log_loss_difference_ci_95"] = temporal.get("log_loss_difference_ci")
            source_clustered["brier_difference_ci_95"] = source_clustered.get("brier_difference_ci")
            source_clustered["log_loss_difference_ci_95"] = source_clustered.get("log_loss_difference_ci")

        comparisons[model_id] = {
            "paired_origin_count": count,
            "mean_brier_difference_vs_benchmark": statistics.fmean(brier) if paired else None,
            "mean_log_loss_difference_vs_benchmark": statistics.fmean(log_loss) if paired else None,
            "temporal_moving_block_bootstrap": temporal,
            "source_clustered_moving_block_bootstrap": source_clustered,
        }

    return {
        "method": "paired_temporal_and_source_clustered_moving_block_bootstrap_v1",
        "sampling_policy": "non_circular_contiguous_time_blocks_v1",
        "max_gap_multiple": max_gap_multiple,
        "expected_cadence_seconds": expected_cadence_seconds,
        "benchmark_model_id": benchmark_model_id,
        "block_length_origins": block_length_origins,
        "bootstrap_replicates": bootstrap_replicates,
        "minimum_origins": minimum_origins,
        "minimum_source_clusters": minimum_source_clusters,
        "minimum_origins_per_source_cluster": minimum_origins_per_source_cluster,
        "random_seed": random_seed,
        "confidence_level": confidence_level,
        "interpretation": (
            "Loss differences are model minus benchmark; negative values favor the model. "
            "Temporal and source-clustered intervals use non-circular blocks drawn only from "
            "contiguous timestamp segments. Gaps larger than max_gap_multiple times the declared "
            "or median-observed cadence split segments; no block crosses a segment boundary. "
            "Per-cluster cadence is inferred separately unless a future source-specific cadence "
            "contract is supplied. Too few valid blocks or independent source groups yields no CI. "
            "These diagnostics do not authorize a live forecast."
        ),
        "comparisons": comparisons,
    }


_REQUIRED_CANDIDATE_BASELINES = (
    "naive_class_prior",
    "momentum_sign",
    "mean_reversion_sign",
    "volatility_normal",
)


def evaluate_candidate_readiness_uncertainty(
    out_of_sample_observations: Iterable[Mapping[str, Any]],
    shadow_observations: Iterable[Mapping[str, Any]],
    *,
    candidate_model_id: str,
    expected_cadence_seconds: float,
    expected_source_cadence_seconds_by_group: Mapping[str, float],
    familywise_confidence_level: float = 0.95,
    bootstrap_replicates: int = 10_000,
    minimum_paired_origins: int = 100,
    block_length_origins: int = 5,
    minimum_source_clusters: int = 5,
    minimum_origins_per_source_cluster: int = 5,
    max_gap_multiple: float = 1.5,
    random_seed: int = 20261114,
) -> dict[str, Any]:
    """Build policy-v6 paired uncertainty for a candidate versus all four baselines.

    The returned object has the paired_uncertainty shape consumed by the
    forecast-readiness ledger. It evaluates the candidate separately against
    every required baseline in both the independent out-of-sample and later
    shadow windows. It does not train a model, validate dataset receipts,
    attest an evaluator, or authorize forecast issuance; the ledger performs
    those independent checks.

    Policy floors are enforced here rather than silently accepting the
    diagnostic defaults of the lower-level bootstrap.
    """
    if not isinstance(candidate_model_id, str) or not candidate_model_id.strip():
        raise PairedBootstrapError("candidate_model_id is required")
    candidate_model_id = candidate_model_id.strip()
    if candidate_model_id in _REQUIRED_CANDIDATE_BASELINES:
        raise PairedBootstrapError("candidate_model_id must be distinct from all required baselines")

    for value, field, minimum in (
        (bootstrap_replicates, "bootstrap_replicates", 10_000),
        (minimum_paired_origins, "minimum_paired_origins", 100),
        (block_length_origins, "block_length_origins", 2),
        (minimum_source_clusters, "minimum_source_clusters", 5),
        (minimum_origins_per_source_cluster, "minimum_origins_per_source_cluster", block_length_origins),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise PairedBootstrapError(f"{field} must be an integer of at least {minimum}")
    if isinstance(random_seed, bool) or not isinstance(random_seed, int):
        raise PairedBootstrapError("random_seed must be an integer")
    if (
        isinstance(familywise_confidence_level, bool)
        or not isinstance(familywise_confidence_level, (int, float))
        or not math.isfinite(float(familywise_confidence_level))
        or not 0.95 <= float(familywise_confidence_level) < 1.0
    ):
        raise PairedBootstrapError("familywise_confidence_level must be in [0.95, 1)")
    if (
        isinstance(expected_cadence_seconds, bool)
        or not isinstance(expected_cadence_seconds, (int, float))
        or not math.isfinite(float(expected_cadence_seconds))
        or float(expected_cadence_seconds) <= 0
    ):
        raise PairedBootstrapError("expected_cadence_seconds must be finite and positive")
    if not isinstance(expected_source_cadence_seconds_by_group, Mapping) or not expected_source_cadence_seconds_by_group:
        raise PairedBootstrapError("declared source-group cadence mapping is required")
    for group_id, cadence in expected_source_cadence_seconds_by_group.items():
        if not isinstance(group_id, str) or not group_id.strip():
            raise PairedBootstrapError("source cadence group IDs must be non-empty strings")
        if (
            isinstance(cadence, bool)
            or not isinstance(cadence, (int, float))
            or not math.isfinite(float(cadence))
            or float(cadence) <= 0
        ):
            raise PairedBootstrapError("source-group cadence values must be finite and positive")
    if (
        isinstance(max_gap_multiple, bool)
        or not isinstance(max_gap_multiple, (int, float))
        or not math.isfinite(float(max_gap_multiple))
        or float(max_gap_multiple) < 1.0
    ):
        raise PairedBootstrapError("max_gap_multiple must be finite and at least one")

    comparison_count = len(_REQUIRED_CANDIDATE_BASELINES) * 2
    individual_confidence_level = 1.0 - (
        (1.0 - float(familywise_confidence_level)) / comparison_count
    )

    def negative_interval(value: Any) -> bool:
        if not isinstance(value, list) or len(value) != 2:
            return False
        lower, upper = value
        if (
            isinstance(lower, bool)
            or isinstance(upper, bool)
            or not isinstance(lower, (int, float))
            or not isinstance(upper, (int, float))
            or not math.isfinite(float(lower))
            or not math.isfinite(float(upper))
        ):
            return False
        return float(lower) <= float(upper) and float(upper) < 0.0

    def declared_cadence(diagnostics: Any) -> bool:
        if not isinstance(diagnostics, Mapping) or diagnostics.get("cadence_source") != "declared":
            return False
        cadence = diagnostics.get("cadence_seconds")
        windows = diagnostics.get("valid_block_window_count")
        segments = diagnostics.get("contiguous_segment_count")
        return (
            isinstance(cadence, (int, float))
            and not isinstance(cadence, bool)
            and math.isfinite(float(cadence))
            and float(cadence) > 0
            and isinstance(windows, int)
            and not isinstance(windows, bool)
            and windows > 0
            and isinstance(segments, int)
            and not isinstance(segments, bool)
            and segments > 0
        )

    def evaluate_window(
        observations: Iterable[Mapping[str, Any]],
        *,
        window_name: str,
        seed_offset: int,
    ) -> dict[str, Any]:
        rows = list(observations)
        failures: list[str] = []
        comparisons: dict[str, Any] = {}
        if not rows:
            return {
                "status": "FAIL",
                "comparisons": {},
                "failure_reasons": [f"{window_name}: observations are empty"],
            }

        for baseline_index, baseline_model_id in enumerate(_REQUIRED_CANDIDATE_BASELINES):
            try:
                result = evaluate_paired_block_bootstrap(
                    rows,
                    benchmark_model_id=baseline_model_id,
                    block_length_origins=block_length_origins,
                    bootstrap_replicates=bootstrap_replicates,
                    minimum_origins=minimum_paired_origins,
                    minimum_source_clusters=minimum_source_clusters,
                    minimum_origins_per_source_cluster=minimum_origins_per_source_cluster,
                    random_seed=random_seed + seed_offset + baseline_index * 101,
                    confidence_level=individual_confidence_level,
                    max_gap_multiple=float(max_gap_multiple),
                    expected_cadence_seconds=float(expected_cadence_seconds),
                    expected_source_cadence_seconds_by_group={
                        key: float(value)
                        for key, value in expected_source_cadence_seconds_by_group.items()
                    },
                )
                comparison = result["comparisons"].get(candidate_model_id)
            except (PairedBootstrapError, KeyError, TypeError, ValueError) as exc:
                comparison = None
                failures.append(f"{window_name}.{baseline_model_id}: bootstrap failed: {exc}")

            if not isinstance(comparison, Mapping):
                comparisons[baseline_model_id] = {
                    "status": "FAIL",
                    "failure_reasons": [f"candidate or baseline has no paired observations for {baseline_model_id}"],
                }
                if not any(item.startswith(f"{window_name}.{baseline_model_id}:") for item in failures):
                    failures.append(f"{window_name}.{baseline_model_id}: comparison is missing")
                continue

            comparison = dict(comparison)
            local_failures: list[str] = []
            paired_count = comparison.get("paired_origin_count")
            if (
                isinstance(paired_count, bool)
                or not isinstance(paired_count, int)
                or paired_count < minimum_paired_origins
            ):
                local_failures.append(
                    f"paired origins below policy minimum {minimum_paired_origins}"
                )

            for metric in ("brier", "log_loss"):
                mean_difference = comparison.get(f"mean_{metric}_difference_vs_benchmark")
                if (
                    isinstance(mean_difference, bool)
                    or not isinstance(mean_difference, (int, float))
                    or not math.isfinite(float(mean_difference))
                    or float(mean_difference) >= 0.0
                ):
                    local_failures.append(f"mean {metric} difference does not favor the candidate")

            temporal = comparison.get("temporal_moving_block_bootstrap")
            if not isinstance(temporal, Mapping) or temporal.get("status") != "ESTIMATED":
                local_failures.append("temporal moving-block interval is not estimated")
            else:
                level = temporal.get("confidence_level")
                if (
                    isinstance(level, bool)
                    or not isinstance(level, (int, float))
                    or not math.isfinite(float(level))
                    or float(level) + 1e-12 < individual_confidence_level
                ):
                    local_failures.append("temporal interval is below the Bonferroni-adjusted confidence level")
                if not negative_interval(temporal.get("brier_difference_ci")):
                    local_failures.append("temporal Brier interval does not establish candidate superiority")
                if not negative_interval(temporal.get("log_loss_difference_ci")):
                    local_failures.append("temporal log-loss interval does not establish candidate superiority")
                if not declared_cadence(temporal.get("sampling_diagnostics")):
                    local_failures.append("temporal Brier sampling lacks declared cadence or valid blocks")
                if not declared_cadence(temporal.get("log_loss_sampling_diagnostics")):
                    local_failures.append("temporal log-loss sampling lacks declared cadence or valid blocks")

            source = comparison.get("source_clustered_moving_block_bootstrap")
            if not isinstance(source, Mapping) or source.get("status") != "ESTIMATED":
                local_failures.append("source-clustered interval is not estimated")
            else:
                level = source.get("confidence_level")
                if (
                    isinstance(level, bool)
                    or not isinstance(level, (int, float))
                    or not math.isfinite(float(level))
                    or float(level) + 1e-12 < individual_confidence_level
                ):
                    local_failures.append("source-clustered interval is below the Bonferroni-adjusted confidence level")
                cluster_count = source.get("source_cluster_count")
                group_ids = source.get("source_group_ids")
                if (
                    isinstance(cluster_count, bool)
                    or not isinstance(cluster_count, int)
                    or cluster_count < minimum_source_clusters
                    or not isinstance(group_ids, list)
                    or len(group_ids) != cluster_count
                    or len(set(group_ids)) != len(group_ids)
                    or any(not isinstance(group_id, str) or not group_id.strip() for group_id in group_ids)
                ):
                    local_failures.append("source-cluster count or IDs do not satisfy policy")
                    group_ids = []
                observed_minimum = source.get("observed_minimum_origins_per_source_cluster")
                declared_minimum = source.get("minimum_origins_per_source_cluster")
                if (
                    isinstance(observed_minimum, bool)
                    or not isinstance(observed_minimum, int)
                    or observed_minimum < minimum_origins_per_source_cluster
                    or isinstance(declared_minimum, bool)
                    or not isinstance(declared_minimum, int)
                    or declared_minimum < minimum_origins_per_source_cluster
                ):
                    local_failures.append("source clusters do not meet the per-cluster origin minimum")
                for metric in ("brier", "log_loss"):
                    cluster_mean = source.get(f"equal_cluster_weighted_mean_{metric}_difference")
                    if (
                        isinstance(cluster_mean, bool)
                        or not isinstance(cluster_mean, (int, float))
                        or not math.isfinite(float(cluster_mean))
                        or float(cluster_mean) >= 0.0
                    ):
                        local_failures.append(f"equal-cluster mean {metric} difference does not favor the candidate")
                    if not negative_interval(source.get(f"{metric}_difference_ci")):
                        local_failures.append(f"source-clustered {metric} interval does not establish candidate superiority")
                for field in ("brier_sampling_diagnostics", "log_loss_sampling_diagnostics"):
                    diagnostics = source.get(field)
                    per_cluster = diagnostics.get("per_cluster") if isinstance(diagnostics, Mapping) else None
                    if (
                        not isinstance(per_cluster, Mapping)
                        or set(per_cluster) != set(group_ids)
                        or not all(declared_cadence(item) for item in per_cluster.values())
                    ):
                        local_failures.append(f"source-clustered {field} lacks declared cadence for every admitted group")

            comparison["baseline_model_id"] = baseline_model_id
            comparison["status"] = "PASS" if not local_failures else "FAIL"
            comparison["failure_reasons"] = local_failures
            comparisons[baseline_model_id] = comparison
            failures.extend(
                f"{window_name}.{baseline_model_id}: {reason}"
                for reason in local_failures
            )

        return {
            "status": "PASS" if not failures and set(comparisons) == set(_REQUIRED_CANDIDATE_BASELINES) else "FAIL",
            "comparisons": comparisons,
            "failure_reasons": failures,
        }

    out_of_sample = evaluate_window(
        out_of_sample_observations,
        window_name="out_of_sample",
        seed_offset=0,
    )
    shadow_evaluation = evaluate_window(
        shadow_observations,
        window_name="shadow_evaluation",
        seed_offset=10_000,
    )
    overall_status = (
        "PASS"
        if out_of_sample["status"] == "PASS" and shadow_evaluation["status"] == "PASS"
        else "FAIL"
    )
    return {
        "status": overall_status,
        "method": "paired_temporal_and_source_clustered_moving_block_bootstrap_v1",
        "sampling_policy": "non_circular_contiguous_time_blocks_v1",
        "candidate_model_id": candidate_model_id,
        "multiplicity_method": "bonferroni",
        "familywise_confidence_level": float(familywise_confidence_level),
        "familywise_comparison_count": comparison_count,
        "individual_confidence_level": individual_confidence_level,
        "bootstrap_replicates": bootstrap_replicates,
        "block_length_origins": block_length_origins,
        "minimum_paired_origins": minimum_paired_origins,
        "minimum_source_clusters": minimum_source_clusters,
        "minimum_origins_per_source_cluster": minimum_origins_per_source_cluster,
        "expected_cadence_seconds": float(expected_cadence_seconds),
        "expected_source_cadence_seconds_by_group": {
            key: float(value)
            for key, value in expected_source_cadence_seconds_by_group.items()
        },
        "max_gap_multiple": float(max_gap_multiple),
        "out_of_sample": out_of_sample,
        "shadow_evaluation": shadow_evaluation,
        "interpretation": (
            "The candidate is compared separately with all four required baselines in both "
            "chronological evaluation windows. Confidence is Bonferroni-adjusted across four "
            "baselines and two loss metrics. Temporal and source-clustered intervals must both "
            "show negative candidate-minus-baseline Brier and log-loss differences. Every "
            "sampling cadence must be declared; inferred cadence cannot pass this gate. This "
            "artifact does not train a model, validate raw-source receipts, attest an evaluator, "
            "or authorize forecast issuance."
        ),
    }
