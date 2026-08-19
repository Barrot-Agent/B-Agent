#!/usr/bin/env python3
"""Longevity research micro-ingestion pipeline for B-Agent."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional

LOGGER = logging.getLogger(__name__)


@dataclass
class AgingMechanism:
    """Structured aging mechanism extracted from research content."""

    mechanism: str
    evidence: str
    confidence: float
    tags: List[str]


@dataclass
class TrialOutcome:
    """Normalized trial participant outcome record."""

    participant_id: str
    treatment_arm: str
    baseline_epigenetic_age: float
    followup_epigenetic_age: float
    nad_level_change_pct: float
    adverse_events: List[str]


class LongevityMicroIngestion:
    """Ingests longevity research and produces Ω-Ingest/MMI-ready outputs."""

    _MECHANISM_KEYWORDS: Dict[str, List[str]] = {
        "epigenetic_reprogramming": ["epigenetic", "reprogram", "methylation"],
        "yamanaka_factors": ["oct4", "sox2", "klf4", "c-myc", "yamanaka"],
        "nad_metabolism": ["nad+", "mitochondria", "sirtuin", "metabolism"],
        "senescence_clearance": ["senescent", "p16", "p21", "clearance"],
    }

    def extract_aging_mechanisms(self, text: str) -> List[AgingMechanism]:
        """Extract candidate aging mechanisms from unstructured text."""
        lowered = text.lower()
        mechanisms: List[AgingMechanism] = []
        for name, keywords in self._MECHANISM_KEYWORDS.items():
            hits = [keyword for keyword in keywords if keyword in lowered]
            if not hits:
                continue
            confidence = min(1.0, 0.35 + 0.15 * len(hits))
            mechanisms.append(
                AgingMechanism(
                    mechanism=name,
                    evidence=f"Detected keywords: {', '.join(hits)}",
                    confidence=round(confidence, 2),
                    tags=hits,
                )
            )

        LOGGER.info("Extracted %d aging mechanisms", len(mechanisms))
        return mechanisms

    def parse_trial_data(self, records: Iterable[Dict[str, Any]]) -> List[TrialOutcome]:
        """Normalize trial rows and compute baseline/follow-up deltas safely."""
        outcomes: List[TrialOutcome] = []
        for row in records:
            try:
                baseline = float(row.get("baseline_epigenetic_age", 0.0))
                followup = float(row.get("followup_epigenetic_age", baseline))
                nad_baseline = float(row.get("nad_baseline", 0.0))
                nad_followup = float(row.get("nad_followup", nad_baseline))
                nad_change = 0.0
                if nad_baseline > 0:
                    nad_change = ((nad_followup - nad_baseline) / nad_baseline) * 100.0

                outcomes.append(
                    TrialOutcome(
                        participant_id=str(row.get("participant_id", "unknown")),
                        treatment_arm=str(row.get("treatment_arm", "unassigned")),
                        baseline_epigenetic_age=baseline,
                        followup_epigenetic_age=followup,
                        nad_level_change_pct=round(nad_change, 3),
                        adverse_events=list(row.get("adverse_events", [])),
                    )
                )
            except (TypeError, ValueError) as exc:
                LOGGER.warning("Skipping malformed trial row: %s", exc)

        LOGGER.info("Parsed %d trial outcomes", len(outcomes))
        return outcomes

    def generate_epigenetic_pattern_matrix(
        self, methylation_samples: Iterable[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Build an epigenetic matrix for dashboard and analytics consumers."""
        samples = list(methylation_samples)
        if not samples:
            return {"markers": [], "matrix": [], "marker_averages": {}, "sample_count": 0}

        markers = sorted({marker for sample in samples for marker in sample.keys()})
        matrix: List[List[float]] = []
        for sample in samples:
            matrix.append([float(sample.get(marker, 0.0)) for marker in markers])

        averages = {
            marker: round(mean([row[idx] for row in matrix]), 6)
            for idx, marker in enumerate(markers)
        }

        return {
            "markers": markers,
            "matrix": matrix,
            "marker_averages": averages,
            "sample_count": len(samples),
        }

    def track_biomarker_progression(
        self,
        participant_id: str,
        biomarker: str,
        measurements: Iterable[Dict[str, Any]],
        *,
        higher_is_better: bool = True,
    ) -> Dict[str, Any]:
        """Create a sorted timeline for a participant biomarker."""
        timeline = sorted(
            [
                {
                    "timestamp": str(item.get("timestamp")),
                    "value": float(item.get("value", 0.0)),
                    "source": str(item.get("source", "trial_observation")),
                }
                for item in measurements
            ],
            key=lambda item: self._parse_timestamp(item["timestamp"]),
        )

        return {
            "participant_id": participant_id,
            "biomarker": biomarker,
            "timeline": timeline,
            "trend": self._trend_label(
                [entry["value"] for entry in timeline],
                higher_is_better=higher_is_better,
            ),
        }

    def build_unified_payload(
        self,
        paper_text: str,
        trial_records: Iterable[Dict[str, Any]],
        methylation_samples: Iterable[Dict[str, float]],
        biomarker_measurements: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Build a unified longevity payload with Ω-Ingest and MMI hooks."""
        mechanisms = [asdict(item) for item in self.extract_aging_mechanisms(paper_text)]
        outcomes = [asdict(item) for item in self.parse_trial_data(trial_records)]
        matrix = self.generate_epigenetic_pattern_matrix(methylation_samples)

        timelines = []
        for biomarker_name, measures in biomarker_measurements.items():
            timelines.append(
                self.track_biomarker_progression(
                    participant_id="cohort",
                    biomarker=biomarker_name,
                    measurements=measures,
                    higher_is_better=self._higher_is_better_biomarker(biomarker_name),
                )
            )

        payload = {
            "research_domain": "longevity",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "aging_mechanisms": mechanisms,
            "trial_outcomes": outcomes,
            "epigenetic_pattern_matrices": [matrix],
            "biomarker_timelines": timelines,
            "_meta": {"schema_version": "1.0", "source": "longevity_micro_ingestion"},
        }
        payload["omega_ingest"] = self._omega_ingest_metadata(payload)
        payload["mmi_breakthroughs"] = self.extract_breakthroughs_for_mmi(payload)
        return payload

    def extract_breakthroughs_for_mmi(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Surface high-impact discoveries for MMI ingestion."""
        breakthroughs: List[Dict[str, Any]] = []

        for outcome in payload.get("trial_outcomes", []):
            age_reversal = outcome.get("baseline_epigenetic_age", 0.0) - outcome.get(
                "followup_epigenetic_age", 0.0
            )
            nad_gain = outcome.get("nad_level_change_pct", 0.0)
            if age_reversal >= 2.0 or nad_gain >= 15.0:
                breakthroughs.append(
                    {
                        "category": "trial_signal",
                        "participant_id": outcome.get("participant_id"),
                        "age_reversal_years": round(age_reversal, 2),
                        "nad_gain_pct": round(nad_gain, 2),
                        "impact": "high" if age_reversal >= 4.0 else "medium",
                    }
                )

        for timeline in payload.get("biomarker_timelines", []):
            if timeline.get("trend") == "improving":
                breakthroughs.append(
                    {
                        "category": "biomarker_trend",
                        "biomarker": timeline.get("biomarker"),
                        "impact": "medium",
                        "summary": "Sustained improving biomarker trajectory detected",
                    }
                )

        return breakthroughs

    @staticmethod
    def _trend_label(values: List[float], *, higher_is_better: bool = True) -> str:
        if len(values) < 2:
            return "stable"
        delta = values[-1] - values[0]
        if delta > 0 and higher_is_better:
            return "improving"
        if delta > 0 and not higher_is_better:
            return "declining"
        if delta < 0 and higher_is_better:
            return "declining"
        if delta < 0 and not higher_is_better:
            return "improving"
        return "stable"

    @staticmethod
    def _higher_is_better_biomarker(biomarker_name: str) -> bool:
        lowered = biomarker_name.lower()
        lower_is_better_tokens = ("age", "senescence", "inflammation")
        return not any(token in lowered for token in lower_is_better_tokens)

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            # Fallback so malformed or partial timestamps remain sortable.
            return datetime.min.replace(tzinfo=timezone.utc)

    @staticmethod
    def _omega_ingest_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Attach Ω-Ingest compatible metadata envelope."""
        return {
            "topic": "aging_reversal",
            "signal_density": len(payload.get("aging_mechanisms", []))
            + len(payload.get("trial_outcomes", [])),
            "compatibility": "omega_ingest_v1",
        }
