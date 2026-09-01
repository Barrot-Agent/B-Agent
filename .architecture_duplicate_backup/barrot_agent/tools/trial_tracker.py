#!/usr/bin/env python3
"""Longevity trial tracking and discovery extraction."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from statistics import mean
from typing import Any, Dict, List


@dataclass
class TrialMetadata:
    """Trial-level metadata and timeline fields."""

    trial_id: str
    sponsor: str
    phase: str
    status: str
    start_date: str
    expected_end_date: str


@dataclass
class ParticipantCohort:
    """Cohort-level trial analysis container."""

    phase_number: int
    total_participants: int
    outcomes: List[Dict[str, Any]] = field(default_factory=list)

    def add_participant_outcome(
        self, participant_id: str, treatment_arm: str, age_reversal: float
    ) -> None:
        self.outcomes.append(
            {
                "participant_id": participant_id,
                "treatment_arm": treatment_arm,
                "age_reversal": float(age_reversal),
            }
        )

    def calculate_mean_age_reversal(self) -> float:
        if not self.outcomes:
            return 0.0
        return round(mean(row["age_reversal"] for row in self.outcomes), 3)

    def identify_responders(self, threshold_years: float = 5.0) -> List[str]:
        return [
            row["participant_id"]
            for row in self.outcomes
            if row.get("age_reversal", 0.0) >= threshold_years
        ]

    def compare_treatment_arms(self) -> Dict[str, float]:
        grouped: defaultdict[str, List[float]] = defaultdict(list)
        for row in self.outcomes:
            grouped[row["treatment_arm"]].append(row["age_reversal"])
        return {arm: round(mean(values), 3) for arm, values in grouped.items() if values}


class EfficacyAnalyzer:
    """Predicts trial efficacy and success probabilities."""

    def __init__(self, cohort: ParticipantCohort) -> None:
        self.cohort = cohort

    def estimate_success_probability(self, efficacy_threshold: float = 3.0) -> float:
        outcomes = self.cohort.outcomes
        if not outcomes:
            return 0.0
        responders = [row for row in outcomes if row["age_reversal"] >= efficacy_threshold]
        return round(len(responders) / len(outcomes), 3)


class SafetyMonitor:
    """Tracks and summarizes adverse events by treatment arm."""

    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    def log_adverse_event(
        self, participant_id: str, treatment_arm: str, severity: str, description: str
    ) -> None:
        self._events.append(
            {
                "participant_id": participant_id,
                "treatment_arm": treatment_arm,
                "severity": severity,
                "description": description,
            }
        )

    def calculate_safety_score(self) -> float:
        if not self._events:
            return 1.0
        severity_weights = {"mild": 0.1, "moderate": 0.3, "severe": 0.6}
        penalty = sum(severity_weights.get(event["severity"], 0.2) for event in self._events)
        return round(max(0.0, 1.0 - penalty / max(len(self._events), 1)), 3)

    def events_by_arm(self) -> Dict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int)
        for event in self._events:
            counts[event["treatment_arm"]] += 1
        return dict(counts)


class DiscoveryExtractor:
    """Extracts high-impact findings and prepares MMI hooks."""

    def __init__(self, cohort: ParticipantCohort, safety_monitor: SafetyMonitor) -> None:
        self.cohort = cohort
        self.safety_monitor = safety_monitor

    def surface_high_impact_discoveries(self) -> List[Dict[str, Any]]:
        discoveries: List[Dict[str, Any]] = []
        arm_comparison = self.cohort.compare_treatment_arms()

        for arm, value in arm_comparison.items():
            if value >= 4.0:
                discoveries.append(
                    {
                        "type": "efficacy_breakthrough",
                        "treatment_arm": arm,
                        "mean_age_reversal": value,
                    }
                )

        if self.safety_monitor.calculate_safety_score() >= 0.8:
            discoveries.append(
                {
                    "type": "safety_signal",
                    "summary": "Strong safety profile with limited severe adverse events",
                }
            )
        return discoveries

    def to_mmi_payload(self) -> Dict[str, Any]:
        return {
            "topic": "longevity_breakthroughs",
            "discoveries": self.surface_high_impact_discoveries(),
            "source": "trial_tracker",
        }
