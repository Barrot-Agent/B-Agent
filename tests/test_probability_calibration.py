from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from barrot_agent.evolution.probability_calibration import (
    ProbabilityCalibrationError,
    apply_temporal_temperature_calibration,
)


CLASSES = ("down", "flat", "up")
BASE = datetime(2026, 11, 7, 0, 0, tzinfo=timezone.utc)
CUTOFF = "2026-11-07T03:00:00Z"


def stamp(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def history(count: int = 60) -> list[dict]:
    records = []
    for index in range(count):
        available = BASE + timedelta(minutes=index)
        records.append(
            {
                "forecast_id": f"forecast-{index}",
                "target_record_id": f"target-{index}",
                "data_cutoff_utc": stamp(available - timedelta(seconds=30)),
                "outcome_available_at_utc": stamp(available),
                "raw_probabilities": {
                    "down": 0.90,
                    "flat": 0.05,
                    "up": 0.05,
                },
                "actual_class": CLASSES[index % len(CLASSES)],
            }
        )
    return records


def test_insufficient_prior_outcomes_keep_identity_probabilities() -> None:
    raw = {"down": 0.60, "flat": 0.20, "up": 0.20}
    result = apply_temporal_temperature_calibration(
        history(20),
        raw,
        calibration_cutoff_utc=CUTOFF,
        min_samples=50,
    )
    assert result["method"] == "rolling_temporal_temperature_scaling_v1"
    assert result["recalibration_applied"] is False
    assert result["temperature"] == 1.0
    assert result["calibration_sample_count"] == 20
    assert result["reason"] == "insufficient_prior_resolved_oos_samples"
    assert result["probabilities"] == raw


def test_temperature_is_fit_on_earlier_history_and_validated_on_later_history() -> None:
    raw = {"down": 0.90, "flat": 0.05, "up": 0.05}
    records = history(60)
    records.append(
        {
            "forecast_id": "future-data-cutoff",
            "target_record_id": "future-target-a",
            "data_cutoff_utc": "2026-11-07T03:01:00Z",
            "outcome_available_at_utc": "2026-11-07T03:02:00Z",
            "raw_probabilities": raw,
            "actual_class": "up",
        }
    )
    records.append(
        {
            "forecast_id": "future-outcome",
            "target_record_id": "future-target-b",
            "data_cutoff_utc": "2026-11-07T02:00:00Z",
            "outcome_available_at_utc": "2026-11-07T03:01:00Z",
            "raw_probabilities": raw,
            "actual_class": "up",
        }
    )
    # A second forecast for the same target is deduplicated to the latest
    # eligible forecast, rather than counted as an independent outcome.
    records.append(
        {
            "forecast_id": "forecast-0-later",
            "target_record_id": "target-0",
            "data_cutoff_utc": "2026-11-07T00:01:30Z",
            "outcome_available_at_utc": "2026-11-07T00:01:00Z",
            "raw_probabilities": raw,
            "actual_class": "down",
        }
    )

    result = apply_temporal_temperature_calibration(
        records,
        raw,
        calibration_cutoff_utc=CUTOFF,
        min_samples=50,
    )

    assert result["calibration_sample_count"] == 60
    assert result["fit_sample_count"] == 48
    assert result["validation_sample_count"] == 12
    assert result["recalibration_applied"] is True
    assert result["temperature"] > 1.0
    assert result["validation_log_loss_improvement"] >= 0.005
    assert result["history_max_data_cutoff_utc"] < result["fit_cutoff_utc"]
    assert result["history_max_outcome_available_at_utc"] <= result["fit_cutoff_utc"]
    assert result["probabilities"] != raw
    assert sum(result["probabilities"].values()) == pytest.approx(1.0)


def test_calibration_refuses_naive_timestamps() -> None:
    records = history(60)
    records[0]["outcome_available_at_utc"] = "2026-11-07T00:00:00"
    with pytest.raises(ProbabilityCalibrationError, match="must include a timezone"):
        apply_temporal_temperature_calibration(
            records,
            {"down": 0.4, "flat": 0.3, "up": 0.3},
            calibration_cutoff_utc=CUTOFF,
        )


def test_calibration_rejects_invalid_probability_vectors() -> None:
    with pytest.raises(ProbabilityCalibrationError, match="exactly down, flat and up"):
        apply_temporal_temperature_calibration(
            [],
            {"down": 0.5, "up": 0.5},
            calibration_cutoff_utc=CUTOFF,
        )


def test_calibration_requires_nonnegative_temporal_validation_improvement() -> None:
    with pytest.raises(
        ProbabilityCalibrationError,
        match="minimum_log_loss_improvement must be finite and non-negative",
    ):
        apply_temporal_temperature_calibration(
            history(60),
            {"down": 0.4, "flat": 0.3, "up": 0.3},
            calibration_cutoff_utc=CUTOFF,
            minimum_log_loss_improvement=-0.01,
        )
