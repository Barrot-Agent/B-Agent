from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any


_CLASSES = ("down", "flat", "up")
METHOD = "rolling_temporal_temperature_scaling_v1"


class ProbabilityCalibrationError(ValueError):
    """A calibration input violates the temporal or probability contract."""


def _utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ProbabilityCalibrationError(
            f"{field} must be a timezone-aware ISO-8601 timestamp"
        )
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProbabilityCalibrationError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProbabilityCalibrationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _format(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _normalize(probabilities: Mapping[str, Any], field: str) -> dict[str, float]:
    if not isinstance(probabilities, Mapping) or set(probabilities) != set(_CLASSES):
        raise ProbabilityCalibrationError(
            f"{field} must contain exactly down, flat and up probabilities"
        )
    values: dict[str, float] = {}
    for label in _CLASSES:
        value = probabilities[label]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0
        ):
            raise ProbabilityCalibrationError(
                f"{field} values must be finite non-negative numbers"
            )
        values[label] = max(float(value), 1e-12)
    total = math.fsum(values.values())
    if not math.isfinite(total) or total <= 0:
        raise ProbabilityCalibrationError(f"{field} must have positive total mass")
    return {label: values[label] / total for label in _CLASSES}


def _apply_temperature(
    probabilities: Mapping[str, float], temperature: float
) -> dict[str, float]:
    logits = {
        label: math.log(max(probabilities[label], 1e-12)) / temperature
        for label in _CLASSES
    }
    maximum = max(logits.values())
    weights = {
        label: math.exp(logits[label] - maximum)
        for label in _CLASSES
    }
    total = math.fsum(weights.values())
    return {label: weights[label] / total for label in _CLASSES}


def _mean_log_loss(samples: list[dict[str, Any]], temperature: float) -> float:
    losses = []
    for sample in samples:
        calibrated = _apply_temperature(sample["raw_probabilities"], temperature)
        losses.append(-math.log(max(calibrated[sample["actual_class"]], 1e-15)))
    return math.fsum(losses) / len(losses)


def apply_temporal_temperature_calibration(
    history: Iterable[Mapping[str, Any]],
    probabilities: Mapping[str, Any],
    *,
    calibration_cutoff_utc: str,
    min_samples: int = 50,
    validation_fraction: float = 0.20,
    minimum_log_loss_improvement: float = 0.005,
    max_history: int = 250,
) -> dict[str, Any]:
    """Calibrate one forecast using only earlier OOS outcomes available by its cutoff.

    History is sorted by outcome availability. Duplicate target records retain the
    latest eligible forecast for that target. The earliest 80% fits temperature;
    the later 20% validates it. The identity transform is retained unless the
    later temporal validation improves log loss by the configured minimum.
    """
    cutoff = _utc(calibration_cutoff_utc, "calibration_cutoff_utc")
    raw_current = _normalize(probabilities, "probabilities")
    for name, value in (("min_samples", min_samples), ("max_history", max_history)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ProbabilityCalibrationError(f"{name} must be a positive integer")
    if max_history < min_samples:
        raise ProbabilityCalibrationError("max_history cannot be less than min_samples")
    if (
        isinstance(validation_fraction, bool)
        or not isinstance(validation_fraction, (int, float))
        or not math.isfinite(float(validation_fraction))
        or not 0.10 <= float(validation_fraction) <= 0.50
    ):
        raise ProbabilityCalibrationError(
            "validation_fraction must be between 0.10 and 0.50"
        )
    if (
        isinstance(minimum_log_loss_improvement, bool)
        or not isinstance(minimum_log_loss_improvement, (int, float))
        or not math.isfinite(float(minimum_log_loss_improvement))
        or minimum_log_loss_improvement < 0
    ):
        raise ProbabilityCalibrationError(
            "minimum_log_loss_improvement must be finite and non-negative"
        )

    eligible: list[dict[str, Any]] = []
    for raw in history:
        if not isinstance(raw, Mapping):
            raise ProbabilityCalibrationError("each calibration history item must be an object")
        data_cutoff = _utc(raw.get("data_cutoff_utc"), "data_cutoff_utc")
        outcome_available = _utc(
            raw.get("outcome_available_at_utc"), "outcome_available_at_utc"
        )
        if data_cutoff >= cutoff or outcome_available > cutoff:
            continue
        actual = raw.get("actual_class")
        if actual not in _CLASSES:
            raise ProbabilityCalibrationError("actual_class must be down, flat or up")
        target_id = raw.get("target_record_id") or raw.get("forecast_id")
        if not isinstance(target_id, str) or not target_id.strip():
            raise ProbabilityCalibrationError(
                "calibration history requires target_record_id or forecast_id"
            )
        eligible.append(
            {
                "target_record_id": target_id,
                "data_cutoff": data_cutoff,
                "outcome_available": outcome_available,
                "actual_class": actual,
                "raw_probabilities": _normalize(
                    raw.get("raw_probabilities"), "raw_probabilities"
                ),
            }
        )

    latest_by_target: dict[str, dict[str, Any]] = {}
    for sample in sorted(
        eligible,
        key=lambda item: (
            item["target_record_id"],
            item["data_cutoff"],
            item["outcome_available"],
        ),
    ):
        latest_by_target[sample["target_record_id"]] = sample
    samples = sorted(
        latest_by_target.values(),
        key=lambda item: (
            item["outcome_available"],
            item["data_cutoff"],
            item["target_record_id"],
        ),
    )[-max_history:]

    max_available = (
        max(item["outcome_available"] for item in samples) if samples else None
    )
    max_data_cutoff = (
        max(item["data_cutoff"] for item in samples) if samples else None
    )
    result: dict[str, Any] = {
        "method": METHOD,
        "recalibration_applied": False,
        "temperature": 1.0,
        "calibration_sample_count": len(samples),
        "fit_sample_count": 0,
        "validation_sample_count": 0,
        "fit_cutoff_utc": _format(cutoff),
        "history_max_data_cutoff_utc": _format(max_data_cutoff)
        if max_data_cutoff
        else None,
        "history_max_outcome_available_at_utc": _format(max_available)
        if max_available
        else None,
        "validation_log_loss_before": None,
        "validation_log_loss_after": None,
        "validation_log_loss_improvement": None,
        "reason": None,
        "probabilities": raw_current,
    }
    if len(samples) < min_samples:
        result["reason"] = "insufficient_prior_resolved_oos_samples"
        return result

    split = int(len(samples) * (1.0 - float(validation_fraction)))
    fit_samples = samples[:split]
    validation_samples = samples[split:]
    if len(fit_samples) < 30 or len(validation_samples) < 10:
        result["reason"] = "insufficient_temporal_fit_or_validation_partition"
        return result
    result["fit_sample_count"] = len(fit_samples)
    result["validation_sample_count"] = len(validation_samples)

    candidates = [round(0.50 + index * 0.05, 2) for index in range(91)]
    best_temperature = min(
        candidates,
        key=lambda temperature: (
            _mean_log_loss(fit_samples, temperature)
            + 0.001 * (math.log(temperature) ** 2),
            abs(temperature - 1.0),
            temperature,
        ),
    )
    validation_before = _mean_log_loss(validation_samples, 1.0)
    validation_after = _mean_log_loss(validation_samples, best_temperature)
    improvement = validation_before - validation_after
    result.update(
        {
            "temperature": best_temperature,
            "validation_log_loss_before": validation_before,
            "validation_log_loss_after": validation_after,
            "validation_log_loss_improvement": improvement,
        }
    )
    if improvement < float(minimum_log_loss_improvement):
        result["temperature"] = 1.0
        result["reason"] = "temporal_validation_did_not_improve_log_loss"
        return result

    result["recalibration_applied"] = True
    result["reason"] = "temporal_validation_improved_log_loss"
    result["probabilities"] = _apply_temperature(raw_current, best_temperature)
    return result
