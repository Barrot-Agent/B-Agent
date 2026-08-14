#!/usr/bin/env python3
"""Biomarker analysis module for longevity trials."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Any, DefaultDict, Dict, Iterable, List, Sequence, Tuple


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


@dataclass
class BiomarkerPoint:
    """Single biomarker measurement."""

    timestamp: str
    value: float


class BiomarkerTracker:
    """Tracks participant biomarkers over time."""

    def __init__(self) -> None:
        self._series: DefaultDict[str, List[BiomarkerPoint]] = defaultdict(list)

    def record(self, biomarker: str, timestamp: str, value: float) -> None:
        point = BiomarkerPoint(timestamp=timestamp, value=float(value))
        _parse_timestamp(point.timestamp)
        self._series[biomarker].append(point)
        self._series[biomarker].sort(key=lambda item: _parse_timestamp(item.timestamp))

    def trajectory(self, biomarker: str) -> List[BiomarkerPoint]:
        return list(self._series.get(biomarker, []))

    def detect_plateau(self, biomarker: str, window: int = 3, tolerance: float = 0.05) -> bool:
        points = self._series.get(biomarker, [])
        if len(points) < window:
            return False
        tail = [point.value for point in points[-window:]]
        return max(tail) - min(tail) <= tolerance


class AgingClockCalculator:
    """Computes epigenetic age using weighted methylation markers."""

    DEFAULT_WEIGHTS: Dict[str, float] = {
        "cg16867657": 0.32,
        "cg06639320": 0.24,
        "cg02228185": 0.29,
        "cg21572722": 0.15,
    }

    def __init__(self, baseline_age: float = 40.0) -> None:
        self.baseline_age = baseline_age

    def compute_epigenetic_age(self, methylation_data: Dict[str, float]) -> float:
        weighted_sum = 0.0
        weight_total = 0.0
        for marker, weight in self.DEFAULT_WEIGHTS.items():
            value = float(methylation_data.get(marker, 0.0))
            weighted_sum += value * weight
            weight_total += weight

        if weight_total == 0:
            return float(self.baseline_age)
        normalized = weighted_sum / weight_total
        return round(self.baseline_age + (normalized - 0.5) * 20.0, 3)


class TrialProgressMonitor:
    """Correlates treatment arms with age-reversal outcomes."""

    def __init__(self) -> None:
        self._rows: List[Dict[str, Any]] = []

    def add_outcome(
        self,
        treatment_arm: str,
        baseline_epigenetic_age: float,
        followup_epigenetic_age: float,
    ) -> None:
        self._rows.append(
            {
                "treatment_arm": treatment_arm,
                "baseline": float(baseline_epigenetic_age),
                "followup": float(followup_epigenetic_age),
            }
        )

    def reversal_by_arm(self) -> Dict[str, float]:
        grouped: DefaultDict[str, List[float]] = defaultdict(list)
        for row in self._rows:
            grouped[row["treatment_arm"]].append(row["baseline"] - row["followup"])
        return {arm: round(mean(values), 3) for arm, values in grouped.items() if values}

    def estimate_time_to_reversal(
        self, target_reversal_years: float = 10.0, outcome_interval_years: float = 1.0
    ) -> Dict[str, float]:
        """Estimate years required to reach a reversal target.

        Assumes each recorded outcome represents a constant treatment interval.
        """
        estimates: Dict[str, float] = {}
        for arm, annual_reversal in self.reversal_by_arm().items():
            if annual_reversal <= 0:
                continue
            intervals_needed = target_reversal_years / annual_reversal
            estimates[arm] = round(intervals_needed * outcome_interval_years, 2)
        return estimates


class BiomarkerVisualizer:
    """Produces dashboard-ready structures for charting layers."""

    @staticmethod
    def trend_series(points: Sequence[BiomarkerPoint]) -> Dict[str, List[Any]]:
        return {
            "x": [point.timestamp for point in points],
            "y": [point.value for point in points],
        }

    @staticmethod
    def comparison_table(rows: Iterable[Tuple[str, float]]) -> List[Dict[str, Any]]:
        return [{"label": label, "value": value} for label, value in rows]

    @staticmethod
    def heatmap_matrix(series: Dict[str, Sequence[BiomarkerPoint]]) -> Dict[str, Any]:
        biomarkers = sorted(series.keys())
        timestamps = sorted(
            {point.timestamp for points in series.values() for point in points},
            key=_parse_timestamp,
        )

        matrix: List[List[float]] = []
        for biomarker in biomarkers:
            lookup = {point.timestamp: point.value for point in series[biomarker]}
            matrix.append([float(lookup.get(ts, 0.0)) for ts in timestamps])

        return {"biomarkers": biomarkers, "timestamps": timestamps, "matrix": matrix}
