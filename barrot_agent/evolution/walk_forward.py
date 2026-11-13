"""Leakage-safe chronological evaluation of deterministic XRP price baselines."""
from __future__ import annotations

import hashlib
import json
from bisect import bisect_left
import math
import statistics
from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta, timezone
from typing import Any

from .point_in_time_features import FeatureSnapshotError, build_feature_snapshot
from .probability_calibration import apply_temporal_temperature_calibration
from .paired_block_bootstrap import evaluate_paired_block_bootstrap

_CLASSES = ("down", "flat", "up")
_BASELINES = ("naive_class_prior", "momentum_sign", "mean_reversion_sign", "volatility_normal")
_EFFECTIVE_SAMPLE_SIZE_METHOD = "greedy_non_overlapping_target_intervals_v1"


class WalkForwardEvaluationError(ValueError):
    """A chronological evaluation input violates its point-in-time contract."""


def _utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise WalkForwardEvaluationError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise WalkForwardEvaluationError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise WalkForwardEvaluationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _format(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _available_at(record: Mapping[str, Any]) -> datetime:
    fields = (
        "known_at_utc",
        "source_data_as_of_utc",
        "ingested_at_utc",
        "revision_available_at_utc",
    )
    return max(_utc(record.get(field), field) for field in fields)


def _price(record: Mapping[str, Any]) -> float:
    value = record.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WalkForwardEvaluationError("spot close feature value must be numeric")
    if not math.isfinite(float(value)) or float(value) <= 0:
        raise WalkForwardEvaluationError("spot close feature value must be finite and positive")
    return float(value)


def _classify(value: float, flat_band: float) -> str:
    if value > flat_band:
        return "up"
    if value < -flat_band:
        return "down"
    return "flat"


def _normalize_probabilities(values: Mapping[str, float]) -> dict[str, float]:
    if set(values) != set(_CLASSES):
        raise WalkForwardEvaluationError("baseline must provide down, flat and up probabilities")
    cleaned = {}
    for label in _CLASSES:
        value = values[label]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise WalkForwardEvaluationError("baseline probabilities must be finite numbers")
        if float(value) < 0:
            raise WalkForwardEvaluationError("baseline probabilities cannot be negative")
        cleaned[label] = max(float(value), 1e-12)
    total = sum(cleaned.values())
    return {label: cleaned[label] / total for label in _CLASSES}


def _class_prior(returns: list[float], flat_band: float, alpha: float) -> dict[str, float]:
    counts = {label: alpha for label in _CLASSES}
    for value in returns:
        counts[_classify(value, flat_band)] += 1
    return _normalize_probabilities(counts)


def _directional_baseline(
    trailing_class: str | None,
    *,
    direction: str,
    prior: Mapping[str, float],
    directional_confidence: float,
    flat_probability: float,
) -> dict[str, float]:
    if trailing_class not in {"down", "up"}:
        return dict(prior)
    same = trailing_class
    opposite = "down" if same == "up" else "up"
    favored = same if direction == "momentum" else opposite
    other = opposite if favored == same else same
    return _normalize_probabilities(
        {favored: directional_confidence, "flat": flat_probability, other: 1.0 - directional_confidence - flat_probability}
    )


def _normal_probabilities(
    returns: list[float],
    flat_band: float,
    fallback: Mapping[str, float],
) -> dict[str, float]:
    if len(returns) < 2:
        return dict(fallback)
    mean = statistics.fmean(returns)
    deviation = statistics.pstdev(returns)
    if not math.isfinite(deviation) or deviation <= 1e-12:
        return dict(fallback)

    def cdf(value: float) -> float:
        return 0.5 * (1.0 + math.erf((value - mean) / (deviation * math.sqrt(2.0))))

    lower = cdf(-flat_band)
    upper = cdf(flat_band)
    return _normalize_probabilities(
        {"down": lower, "flat": max(0.0, upper - lower), "up": max(0.0, 1.0 - upper)}
    )


def _nearest_record(
    records: list[dict[str, Any]],
    target_time: datetime,
    tolerance_seconds: int,
) -> dict[str, Any] | None:
    """Find the nearest event in a list already sorted by event_time_utc."""
    if not records:
        return None
    index = bisect_left(
        records,
        target_time,
        key=lambda item: _utc(item["event_time_utc"], "event_time_utc"),
    )
    candidates = []
    for candidate_index in (index - 1, index):
        if 0 <= candidate_index < len(records):
            record = records[candidate_index]
            event_time = _utc(record["event_time_utc"], "event_time_utc")
            difference = abs((event_time - target_time).total_seconds())
            if difference <= tolerance_seconds:
                candidates.append((difference, event_time, record))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        raise WalkForwardEvaluationError("target matching is ambiguous within the configured tolerance")
    return candidates[0][2]


def _score(probabilities: Mapping[str, float], actual: str) -> dict[str, Any]:
    predicted = max(_CLASSES, key=lambda label: (probabilities[label], label == "flat"))
    brier = sum((probabilities[label] - (1.0 if label == actual else 0.0)) ** 2 for label in _CLASSES) / 3.0
    log_loss = -math.log(max(probabilities[actual], 1e-15))
    return {
        "predicted_class": predicted,
        "actual_class": actual,
        "correct": predicted == actual,
        "brier_score": brier,
        "log_loss": log_loss,
    }



def _overlap_adjusted_effective_sample_size(forecasts: list[dict[str, Any]]) -> dict[str, Any]:
    """Count the maximum non-overlapping fixed-horizon target intervals.

    This is a conservative overlap-only effective sample size. It does not
    correct residual serial dependence between disjoint windows or shared-source
    correlation; those require separate uncertainty analysis.
    """
    intervals = set()
    for forecast in forecasts:
        start = _utc(forecast.get("data_cutoff_utc"), "data_cutoff_utc")
        end_value = forecast.get("observed_target_event_time_utc") or forecast.get("target_time_utc")
        end = _utc(end_value, "target_time_utc")
        if end <= start:
            raise WalkForwardEvaluationError("target interval must end after its forecast cutoff")
        intervals.add((start, end))

    ordered = sorted(intervals, key=lambda interval: (interval[1], interval[0]))
    effective = 0
    last_end: datetime | None = None
    for start, end in ordered:
        # Target windows are treated as half-open [cutoff, outcome), so
        # adjacent windows that meet exactly do not overlap.
        if last_end is None or start >= last_end:
            effective += 1
            last_end = end

    raw_count = len(ordered)
    return {
        "raw_sample_count": raw_count,
        "overlap_adjusted_effective_sample_size": effective,
        "overlap_adjustment_factor": raw_count / effective if effective else None,
        "effective_sample_size_method": _EFFECTIVE_SAMPLE_SIZE_METHOD,
    }


def _metrics(forecasts: list[dict[str, Any]], bin_count: int) -> dict[str, Any]:
    if not forecasts:
        return {"forecast_count": 0}
    count = len(forecasts)
    overlap_metrics = _overlap_adjusted_effective_sample_size(forecasts)
    bins: dict[str, list[dict[str, float]]] = {
        label: [
            {"count": 0, "predicted_sum": 0.0, "observed_sum": 0.0}
            for _ in range(bin_count)
        ]
        for label in _CLASSES
    }
    for forecast in forecasts:
        actual = forecast["outcome"]["actual_class"]
        for label in _CLASSES:
            probability = forecast["probabilities"][label]
            index = min(int(probability * bin_count), bin_count - 1)
            bucket = bins[label][index]
            bucket["count"] += 1
            bucket["predicted_sum"] += probability
            bucket["observed_sum"] += 1.0 if actual == label else 0.0

    calibration_bins = {}
    weighted_error = 0.0
    total_cells = count * len(_CLASSES)
    for label in _CLASSES:
        populated = []
        for index, bucket in enumerate(bins[label]):
            if not bucket["count"]:
                continue
            avg_predicted = bucket["predicted_sum"] / bucket["count"]
            observed = bucket["observed_sum"] / bucket["count"]
            weighted_error += (bucket["count"] / total_cells) * abs(avg_predicted - observed)
            populated.append(
                {
                    "bin": index,
                    "count": bucket["count"],
                    "mean_predicted_probability": avg_predicted,
                    "observed_frequency": observed,
                }
            )
        calibration_bins[label] = populated

    directional = [
        item for item in forecasts
        if item["outcome"]["actual_class"] in {"down", "up"}
    ]
    directional_correct = [
        item for item in directional
        if item["scoring"]["predicted_class"] in {"down", "up"}
        and item["scoring"]["predicted_class"] == item["outcome"]["actual_class"]
    ]
    recalibrated = [
        item for item in forecasts if item["calibration"]["recalibration_applied"]
    ]
    return {
        "forecast_count": count,
        **overlap_metrics,
        "accuracy": sum(item["scoring"]["correct"] for item in forecasts) / count,
        "mean_brier_score": statistics.fmean(item["scoring"]["brier_score"] for item in forecasts),
        "mean_log_loss": statistics.fmean(item["scoring"]["log_loss"] for item in forecasts),
        "raw_mean_brier_score": statistics.fmean(item["raw_scoring"]["brier_score"] for item in forecasts),
        "raw_mean_log_loss": statistics.fmean(item["raw_scoring"]["log_loss"] for item in forecasts),
        "directional_outcome_count": len(directional),
        "directional_accuracy": (
            len(directional_correct) / len(directional) if directional else None
        ),
        "calibration": {
            "method": "rolling_temporal_temperature_scaling_v1",
            "weighted_calibration_error": weighted_error,
            "bin_count": bin_count,
            "bins": calibration_bins,
            "recalibration_applied": bool(recalibrated),
            "recalibrated_forecast_count": len(recalibrated),
            "maximum_prior_calibration_samples": max(
                item["calibration"]["calibration_sample_count"] for item in forecasts
            ),
        },
    }


def evaluate_chronological_walk_forward(
    records: Iterable[Mapping[str, Any]],
    *,
    feature_id: str,
    evaluation_as_of_utc: str,
    horizon_seconds: int,
    asset: str = "XRP",
    venue: str | None = None,
    currency_pair: str | None = None,
    min_train_samples: int = 100,
    min_out_of_sample_samples: int = 100,
    min_effective_out_of_sample_samples: int = 10,
    flat_band_bps: float = 5.0,
    target_tolerance_seconds: int = 60,
    embargo_seconds: int = 0,
    max_origin_age_seconds: int | None = None,
    prior_alpha: float = 1.0,
    directional_confidence: float = 0.60,
    flat_probability: float = 0.30,
    calibration_bin_count: int = 5,
    min_calibration_samples: int = 50,
    calibration_validation_fraction: float = 0.20,
    calibration_minimum_log_loss_improvement: float = 0.005,
    calibration_max_history: int = 250,
    max_source_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Evaluate four deterministic baselines with purged, embargoed point-in-time windows.

    A forecast cutoff is an actual availability timestamp (max of known,
    source-as-of, ingestion and revision availability). Training snapshots are
    rebuilt at each cutoff. Every training start and outcome record must be
    available by ``cutoff - embargo_seconds``; this purges overlapping labels
    and leaves an explicit embargo buffer before the test origin. The test
    outcome is selected only from the later evaluation snapshot. Historical
    backfills captured together therefore do not create artificial origins.
    The reported overlap-adjusted effective sample size is the maximum count
    of non-overlapping target intervals. It gates the SCORED status but does not
    claim to remove residual serial dependence or shared-source correlation.
    """
    if not isinstance(feature_id, str) or not feature_id.strip():
        raise WalkForwardEvaluationError("feature_id is required")
    feature_id = feature_id.strip()
    if not isinstance(asset, str) or not asset.strip():
        raise WalkForwardEvaluationError("asset is required")
    asset = asset.strip().upper()
    if isinstance(horizon_seconds, bool) or not isinstance(horizon_seconds, int) or horizon_seconds <= 0:
        raise WalkForwardEvaluationError("horizon_seconds must be a positive integer")
    if isinstance(min_train_samples, bool) or not isinstance(min_train_samples, int) or min_train_samples < 1:
        raise WalkForwardEvaluationError("min_train_samples must be a positive integer")
    if isinstance(min_out_of_sample_samples, bool) or not isinstance(min_out_of_sample_samples, int) or min_out_of_sample_samples < 1:
        raise WalkForwardEvaluationError("min_out_of_sample_samples must be a positive integer")
    if isinstance(min_effective_out_of_sample_samples, bool) or not isinstance(min_effective_out_of_sample_samples, int) or min_effective_out_of_sample_samples < 1:
        raise WalkForwardEvaluationError("min_effective_out_of_sample_samples must be a positive integer")
    if isinstance(target_tolerance_seconds, bool) or not isinstance(target_tolerance_seconds, int) or target_tolerance_seconds < 0:
        raise WalkForwardEvaluationError("target_tolerance_seconds must be a non-negative integer")
    if isinstance(embargo_seconds, bool) or not isinstance(embargo_seconds, int) or embargo_seconds < 0:
        raise WalkForwardEvaluationError("embargo_seconds must be a non-negative integer")
    if isinstance(calibration_bin_count, bool) or not isinstance(calibration_bin_count, int) or calibration_bin_count < 2:
        raise WalkForwardEvaluationError("calibration_bin_count must be an integer of at least two")
    if isinstance(min_calibration_samples, bool) or not isinstance(min_calibration_samples, int) or min_calibration_samples < 50:
        raise WalkForwardEvaluationError("min_calibration_samples must be an integer of at least 50")
    if isinstance(calibration_max_history, bool) or not isinstance(calibration_max_history, int) or calibration_max_history < min_calibration_samples:
        raise WalkForwardEvaluationError("calibration_max_history must be at least min_calibration_samples")
    if (
        isinstance(calibration_validation_fraction, bool)
        or not isinstance(calibration_validation_fraction, (int, float))
        or not math.isfinite(float(calibration_validation_fraction))
        or not 0.10 <= float(calibration_validation_fraction) <= 0.50
    ):
        raise WalkForwardEvaluationError("calibration_validation_fraction must be between 0.10 and 0.50")
    if (
        isinstance(calibration_minimum_log_loss_improvement, bool)
        or not isinstance(calibration_minimum_log_loss_improvement, (int, float))
        or not math.isfinite(float(calibration_minimum_log_loss_improvement))
        or calibration_minimum_log_loss_improvement < 0
    ):
        raise WalkForwardEvaluationError("calibration_minimum_log_loss_improvement must be finite and non-negative")
    if not isinstance(flat_band_bps, (int, float)) or isinstance(flat_band_bps, bool) or not math.isfinite(float(flat_band_bps)) or flat_band_bps <= 0:
        raise WalkForwardEvaluationError("flat_band_bps must be a finite positive number")
    if not isinstance(prior_alpha, (int, float)) or isinstance(prior_alpha, bool) or not math.isfinite(float(prior_alpha)) or prior_alpha <= 0:
        raise WalkForwardEvaluationError("prior_alpha must be a finite positive number")
    if (
        not isinstance(directional_confidence, (int, float))
        or isinstance(directional_confidence, bool)
        or not math.isfinite(float(directional_confidence))
        or not isinstance(flat_probability, (int, float))
        or isinstance(flat_probability, bool)
        or not math.isfinite(float(flat_probability))
        or directional_confidence <= 0
        or flat_probability <= 0
        or directional_confidence + flat_probability >= 1
    ):
        raise WalkForwardEvaluationError("directional_confidence and flat_probability must be positive and sum to less than one")

    evaluation_cutoff = _utc(evaluation_as_of_utc, "evaluation_as_of_utc")
    max_age = horizon_seconds if max_origin_age_seconds is None else max_origin_age_seconds
    if isinstance(max_age, bool) or not isinstance(max_age, int) or max_age <= 0:
        raise WalkForwardEvaluationError("max_origin_age_seconds must be a positive integer")

    raw_input = list(records)
    if not raw_input or any(not isinstance(item, Mapping) for item in raw_input):
        raise WalkForwardEvaluationError("records must be a non-empty iterable of feature-record objects")
    raw = [dict(item) for item in raw_input]
    selected = [
        item for item in raw
        if item.get("feature_id") == feature_id and str(item.get("asset", "")).upper() == asset
    ]
    if not selected:
        raise WalkForwardEvaluationError("no records match the requested asset and feature_id")

    venues = {item.get("venue") for item in selected}
    if venue is None:
        if len(venues) != 1:
            raise WalkForwardEvaluationError("select one venue; mixed or missing venue scope is not allowed")
        venue = next(iter(venues))
    else:
        selected = [item for item in selected if item.get("venue") == venue]
    if not selected:
        raise WalkForwardEvaluationError("no records remain after venue filtering")
    pairs = {item.get("currency_pair") for item in selected}
    if currency_pair is None:
        if len(pairs) != 1:
            raise WalkForwardEvaluationError("select one currency_pair; mixed or missing pair scope is not allowed")
        currency_pair = next(iter(pairs))
    else:
        selected = [item for item in selected if item.get("currency_pair") == currency_pair]
    if not selected:
        raise WalkForwardEvaluationError("no records remain after venue and currency_pair filtering")

    units = {item.get("unit") for item in selected}
    if len(units) != 1:
        raise WalkForwardEvaluationError("mixed price units are not allowed in one evaluation")
    unit = next(iter(units))

    evaluation_snapshot = build_feature_snapshot(
        selected,
        cutoff_utc=_format(evaluation_cutoff),
        captured_at_utc=_format(evaluation_cutoff),
        asset_scope=[asset],
        max_source_age_seconds=max_source_age_seconds,
    )
    evaluation_series = list(evaluation_snapshot["records"])
    evaluation_series.sort(key=lambda item: _utc(item["event_time_utc"], "event_time_utc"))
    event_times = set()
    for item in evaluation_series:
        event_time = _utc(item["event_time_utc"], "event_time_utc")
        available = _available_at(item)
        if available < event_time:
            raise WalkForwardEvaluationError("spot price bar is available before its event time")
        if event_time in event_times:
            raise WalkForwardEvaluationError("multiple eligible spot bars share one event time")
        event_times.add(event_time)
        _price(item)

    candidate_cutoffs = sorted(
        {
            _available_at(item)
            for item in selected
            if item.get("model_eligible") is True and item.get("quality_status") == "verified"
            and _available_at(item) < evaluation_cutoff
        }
    )
    forecasts: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    flat_band = float(flat_band_bps) / 10000.0

    for cutoff in candidate_cutoffs:
        cutoff_s = _format(cutoff)
        training_cutoff = cutoff - timedelta(seconds=embargo_seconds)
        training_cutoff_s = _format(training_cutoff)
        try:
            snapshot = build_feature_snapshot(
                selected,
                cutoff_utc=cutoff_s,
                captured_at_utc=cutoff_s,
                asset_scope=[asset],
                max_source_age_seconds=max_source_age_seconds,
            )
        except FeatureSnapshotError:
            skipped.append({"data_cutoff_utc": cutoff_s, "reason": "no_valid_point_in_time_snapshot"})
            continue
        series = [
            item for item in snapshot["records"]
            if _utc(item["event_time_utc"], "event_time_utc") <= cutoff
        ]
        series.sort(key=lambda item: _utc(item["event_time_utc"], "event_time_utc"))
        if not series:
            skipped.append({"data_cutoff_utc": cutoff_s, "reason": "no_price_bar_available_by_cutoff"})
            continue
        current = series[-1]
        current_event = _utc(current["event_time_utc"], "event_time_utc")
        origin_age = (cutoff - current_event).total_seconds()
        if origin_age < 0 or origin_age > max_age:
            skipped.append({"data_cutoff_utc": cutoff_s, "reason": "latest_price_bar_is_stale_at_cutoff"})
            continue

        target_time = cutoff + timedelta(seconds=horizon_seconds)
        target = _nearest_record(
            [item for item in evaluation_series if _utc(item["event_time_utc"], "event_time_utc") > cutoff],
            target_time,
            target_tolerance_seconds,
        )
        if target is None:
            skipped.append({"data_cutoff_utc": cutoff_s, "reason": "future_target_not_available_by_evaluation_cutoff"})
            continue

        training_returns: list[float] = []
        training_pairs: list[tuple[float, dict[str, Any], dict[str, Any]]] = []
        for start in series:
            start_event = _utc(start["event_time_utc"], "event_time_utc")
            if start_event >= current_event:
                continue
            start_available = _available_at(start)
            if start_available > training_cutoff:
                continue
            # The target is defined by market event time, not by when a
            # historical backfill happened to be ingested. Availability is a
            # separate guard: the outcome bar must already be known by cutoff.
            training_target_time = start_event + timedelta(seconds=horizon_seconds)
            outcome = _nearest_record(
                series,
                training_target_time,
                target_tolerance_seconds,
            )
            if outcome is None or outcome["record_id"] == start["record_id"]:
                continue
            outcome_event = _utc(outcome["event_time_utc"], "event_time_utc")
            if outcome_event <= start_event or outcome_event > training_cutoff or _available_at(outcome) > training_cutoff:
                continue
            realized = _price(outcome) / _price(start) - 1.0
            training_returns.append(realized)
            training_pairs.append((realized, start, outcome))

        if len(training_returns) < min_train_samples:
            skipped.append(
                {
                    "data_cutoff_utc": cutoff_s,
                    "reason": f"insufficient_point_in_time_training_examples:{len(training_returns)}<{min_train_samples}",
                }
            )
            continue

        trailing_return = None
        if embargo_seconds > 0:
            trailing_start = _nearest_record(
                series,
                current_event - timedelta(seconds=horizon_seconds),
                target_tolerance_seconds,
            )
            if trailing_start is not None and trailing_start["record_id"] != current["record_id"]:
                trailing_return = _price(current) / _price(trailing_start) - 1.0
        else:
            current_pairs = [pair for pair in training_pairs if pair[2]["record_id"] == current["record_id"]]
            if current_pairs:
                trailing_return = current_pairs[-1][0]
        if trailing_return is None and training_pairs:
            trailing_return = training_pairs[-1][0]
        trailing_class = _classify(trailing_return, flat_band) if trailing_return is not None else None

        prior = _class_prior(training_returns, flat_band, float(prior_alpha))
        baselines = {
            "naive_class_prior": prior,
            "momentum_sign": _directional_baseline(
                trailing_class,
                direction="momentum",
                prior=prior,
                directional_confidence=float(directional_confidence),
                flat_probability=float(flat_probability),
            ),
            "mean_reversion_sign": _directional_baseline(
                trailing_class,
                direction="mean_reversion",
                prior=prior,
                directional_confidence=float(directional_confidence),
                flat_probability=float(flat_probability),
            ),
            "volatility_normal": _normal_probabilities(training_returns, flat_band, prior),
        }

        actual_return = _price(target) / _price(current) - 1.0
        actual_class = _classify(actual_return, flat_band)
        target_event = _utc(target["event_time_utc"], "event_time_utc")
        target_available = _available_at(target)
        source_groups = sorted({
            source.get("independence_group")
            for record in [*series, target]
            for source in record.get("sources", [])
            if isinstance(source, Mapping)
            and isinstance(source.get("independence_group"), str)
            and source.get("independence_group").strip()
        })
        if target_event <= cutoff or target_available > evaluation_cutoff:
            skipped.append({"data_cutoff_utc": cutoff_s, "reason": "target_outcome_violates_point_in_time_boundary"})
            continue

        for model_id in _BASELINES:
            raw_probabilities = _normalize_probabilities(baselines[model_id])
            calibration_history = [
                {
                    "forecast_id": item["forecast_id"],
                    "target_record_id": item["target_record_id"],
                    "data_cutoff_utc": item["data_cutoff_utc"],
                    "outcome_event_time_utc": item["outcome"]["outcome_event_time_utc"],
                    "outcome_available_at_utc": item["outcome"]["outcome_available_at_utc"],
                    "raw_probabilities": item["raw_probabilities"],
                    "actual_class": item["outcome"]["actual_class"],
                }
                for item in forecasts
                if item["model_id"] == model_id
            ]
            calibration = apply_temporal_temperature_calibration(
                calibration_history,
                raw_probabilities,
                calibration_cutoff_utc=training_cutoff_s,
                min_samples=min_calibration_samples,
                validation_fraction=float(calibration_validation_fraction),
                minimum_log_loss_improvement=float(calibration_minimum_log_loss_improvement),
                max_history=calibration_max_history,
            )
            probabilities = calibration["probabilities"]
            scoring = _score(probabilities, actual_class)
            raw_scoring = _score(raw_probabilities, actual_class)
            identity = {
                "model_id": model_id,
                "data_cutoff_utc": cutoff_s,
                "horizon_seconds": horizon_seconds,
                "feature_id": feature_id,
                "origin_record_id": current["record_id"],
                "target_record_id": target["record_id"],
                "embargo_seconds": embargo_seconds,
            }
            forecast_id = hashlib.sha256(
                json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            forecasts.append(
                {
                    "forecast_id": forecast_id,
                    "forecast_type": "historical_backtest_only",
                    "model_id": model_id,
                    "model_version": "deterministic-baselines-v1",
                    "asset": asset,
                    "feature_id": feature_id,
                    "venue": venue,
                    "currency_pair": currency_pair,
                    "data_cutoff_utc": cutoff_s,
                    "training_cutoff_utc": training_cutoff_s,
                    "embargo_seconds": embargo_seconds,
                    "horizon_seconds": horizon_seconds,
                    "target_time_utc": _format(target_time),
                    "observed_target_event_time_utc": target["event_time_utc"],
                    "origin_record_id": current["record_id"],
                    "target_record_id": target["record_id"],
                    "raw_probabilities": raw_probabilities,
                    "probabilities": probabilities,
                    "calibration": {
                        key: value for key, value in calibration.items() if key != "probabilities"
                    },
                    "alternative_scenarios": [
                        {
                            "class": label,
                            "probability": probabilities[label],
                            "raw_probability": raw_probabilities[label],
                        }
                        for label in _CLASSES
                    ],
                    "assumptions": {
                        "training_example_count": len(training_returns),
                        "embargo_seconds": embargo_seconds,
                        "training_cutoff_utc": training_cutoff_s,
                        "training_latest_outcome_event_time_utc": max(_utc(pair[2]["event_time_utc"], "event_time_utc") for pair in training_pairs).isoformat(timespec="microseconds").replace("+00:00", "Z"),
                        "training_latest_outcome_available_at_utc": _format(max(_available_at(pair[2]) for pair in training_pairs)),
                        "trailing_return": trailing_return,
                        "flat_band_bps": float(flat_band_bps),
                        "target_tolerance_seconds": target_tolerance_seconds,
                        "source_independence_groups": source_groups,
                        "prior_smoothing_alpha": float(prior_alpha),
                        "directional_confidence": float(directional_confidence),
                        "flat_probability": float(flat_probability),
                        "trailing_return_class": trailing_class,
                        "volatility_distribution": "normal",
                        "training_rule": "all training start and outcome records were available by training_cutoff_utc (data_cutoff_utc minus embargo_seconds)",
                        "test_rule": "future target was excluded from the point-in-time training snapshot",
                    },
                    "outcome": {
                        "actual_class": actual_class,
                        "realized_return": actual_return,
                        "target_price": _price(target),
                        "target_unit": unit,
                        "outcome_event_time_utc": target["event_time_utc"],
                        "outcome_available_at_utc": _format(target_available),
                    },
                    "scoring": scoring,
                    "raw_scoring": raw_scoring,
                    "live_forecast_issued": False,
                    "paper_trade_executed": False,
                }
            )

    forecasts.sort(key=lambda item: (item["data_cutoff_utc"], item["model_id"]))
    paired_uncertainty = evaluate_paired_block_bootstrap([
        {
            "origin_id": item["data_cutoff_utc"],
            "origin_time_utc": item["data_cutoff_utc"],
            "source_group_id": (
                item["assumptions"]["source_independence_groups"][0]
                if len(item["assumptions"]["source_independence_groups"]) == 1
                else None
            ),
            "model_id": item["model_id"],
            "brier_loss": item["scoring"]["brier_score"],
            "log_loss": item["scoring"]["log_loss"],
        }
        for item in forecasts
    ])
    out_of_sample_origin_count = len({item["data_cutoff_utc"] for item in forecasts})
    reference_forecasts = [item for item in forecasts if item["model_id"] == "naive_class_prior"]
    overlap_metrics = _overlap_adjusted_effective_sample_size(reference_forecasts)
    out_of_sample_effective_sample_size = overlap_metrics["overlap_adjusted_effective_sample_size"]
    if out_of_sample_origin_count < min_out_of_sample_samples:
        status = "INSUFFICIENT_HISTORY"
        insufficient_history_reason = (
            f"insufficient_out_of_sample_origins:{out_of_sample_origin_count}<{min_out_of_sample_samples}"
        )
    elif out_of_sample_effective_sample_size < min_effective_out_of_sample_samples:
        status = "INSUFFICIENT_EFFECTIVE_HISTORY"
        insufficient_history_reason = (
            "insufficient_overlap_adjusted_effective_sample_size:"
            f"{out_of_sample_effective_sample_size}<{min_effective_out_of_sample_samples}"
        )
    else:
        status = "SCORED"
        insufficient_history_reason = None
    metrics = {
        model_id: _metrics([item for item in forecasts if item["model_id"] == model_id], calibration_bin_count)
        for model_id in _BASELINES
    }
    return {
        "schema_version": "barrot.xrp.walk-forward.v1",
        "evaluation_type": "chronological_walk_forward",
        "status": status,
        "min_train_samples": min_train_samples,
        "min_out_of_sample_samples": min_out_of_sample_samples,
        "min_effective_out_of_sample_samples": min_effective_out_of_sample_samples,
        "out_of_sample_origin_count": out_of_sample_origin_count,
        "out_of_sample_effective_sample_size": out_of_sample_effective_sample_size,
        "out_of_sample_overlap_adjustment_factor": overlap_metrics["overlap_adjustment_factor"],
        "effective_sample_size_method": _EFFECTIVE_SAMPLE_SIZE_METHOD,
        "effective_sample_size_limitation": "non-overlapping target-window count only; residual serial dependence and source correlation are not removed",
        "insufficient_history_reason": insufficient_history_reason,
        "asset": asset,
        "feature_id": feature_id,
        "venue": venue,
        "currency_pair": currency_pair,
        "unit": unit,
        "evaluation_as_of_utc": _format(evaluation_cutoff),
        "horizon_seconds": horizon_seconds,
        "embargo_seconds": embargo_seconds,
        "purge_policy": "training_start_and_outcome_available_by_cutoff_minus_embargo",
        "flat_band_bps": float(flat_band_bps),
        "dataset_record_count": len(selected),
        "forecast_count": len(forecasts),
        "metrics": metrics,
        "paired_uncertainty": paired_uncertainty,
        "forecasts": forecasts,
        "skipped_origins": skipped,
        "calibration_is_diagnostic_only": False,
        "calibration_method": "rolling_temporal_temperature_scaling_v1",
        "calibration_policy": (
            "Each forecast is calibrated only from earlier out-of-sample forecasts whose "
            "outcomes were available by training_cutoff_utc. The earliest 80% of eligible "
            "history fits temperature; the later 20% validates it. Identity is retained "
            "until the minimum sample count and temporal validation improvement are met."
        ),
        "min_calibration_samples": min_calibration_samples,
        "calibration_max_history": calibration_max_history,
        "live_forecast_issued": False,
        "paper_trade_executed": False,
        "prediction_boundary": (
            "Backtest results only. No live directional forecast or paper trade is issued. "
            "Rolling calibration uses only prior resolved out-of-sample outcomes. Baseline "
            "superiority must still be demonstrated on a sufficiently large, independent "
            "chronological holdout before any forecast is enabled."
        ),
    }
