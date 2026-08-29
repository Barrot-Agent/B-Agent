"""
Barrot Cross-Corroboration Engine.

Compares claims against normalized evidence, groups records by independent
source identity, weights evidence quality, and preserves contradictions.
"""

from __future__ import annotations

import hashlib
from typing import Any

from barrot_agent.evolution.claim_integrity import ClaimIntegrityEngine
from barrot_agent.evolution.claim_lifecycle import ClaimLifecycleEngine
from barrot_agent.evolution.cognitive_integrity import CognitiveIntegrityLoop
from barrot_agent.evolution.confidence_calibration import (
    ConfidenceCalibrationEngine,
)
from barrot_agent.evolution.evidence_quality import EvidenceQualityEngine
from barrot_agent.evolution.evidence_store import EvidenceStore
from barrot_agent.evolution.source_independence import SourceIndependenceEngine


class CrossCorroborationEngine:
    """Evidence comparison layer for maintaining reasoning integrity."""

    def __init__(self) -> None:
        self.integrity = CognitiveIntegrityLoop()
        self.evidence_store = EvidenceStore()
        self.claim_integrity = ClaimIntegrityEngine()
        self.source_independence = SourceIndependenceEngine()
        self.quality = EvidenceQualityEngine()
        self.lifecycle = ClaimLifecycleEngine()
        self.calibration = ConfidenceCalibrationEngine()

    def corroborate(
        self,
        claim: Any,
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compare a claim against independently stored evidence."""

        normalized_claim = self.claim_integrity.normalize(claim)
        excluded_sources = set(sources or [])

        supporting_records: list[dict[str, Any]] = []
        conflicting_records: list[dict[str, Any]] = []

        for evidence in self.evidence_store.load():
            if evidence.get("source", "") in excluded_sources:
                continue

            comparison = self.claim_integrity.compare(
                claim,
                evidence.get("claim", ""),
            )

            if comparison["status"] == "agreement":
                supporting_records.append(evidence)
            elif comparison["status"] == "contradiction":
                conflicting_records.append(evidence)

        supporting_groups = self.source_independence.independent_sources(supporting_records)
        conflicting_groups = self.source_independence.independent_sources(conflicting_records)

        supporting = self._representatives(supporting_groups)
        conflicting = self._representatives(conflicting_groups)

        support_weight = self._average_quality(supporting_groups.values())
        conflict_weight = self._average_quality(conflicting_groups.values())

        # Compatibility confidence is based on the number of independent
        # sources. Quality remains separately exposed so evidence weighting
        # never silently changes established confidence semantics.
        confidence = 0.5
        confidence += min(0.4, len(supporting) * 0.1)
        confidence -= min(0.4, len(conflicting) * 0.15)
        confidence = max(0.05, min(0.95, confidence))

        lifecycle = self.lifecycle.determine(
            supporting_sources=len(supporting),
            conflicting_sources=len(conflicting),
            confidence=confidence,
        )

        claim_id = hashlib.sha256(normalized_claim["text"].encode("utf-8")).hexdigest()

        result = {
            "claim_id": claim_id,
            "supporting_records": supporting,
            "conflicting_records": conflicting,
            "independent_supporting_sources": len(supporting),
            "independent_conflicting_sources": len(conflicting),
            "support_quality": round(support_weight, 3),
            "conflict_quality": round(conflict_weight, 3),
            "evidence_count": len(supporting) + len(conflicting),
            "corroborated_confidence": round(confidence, 3),
            # Backward-compatible evidence status.
            "status": (
                "corroborated"
                if supporting and not conflicting
                else "conflicted" if conflicting else "insufficient_evidence"
            ),
            # Richer lifecycle state remains available separately.
            "lifecycle_status": lifecycle["status"],
        }

        self.calibration.record(
            claim_id=claim_id,
            confidence=confidence,
            status=lifecycle["status"],
        )

        self.integrity.record_outcome(
            operation="corroboration",
            outcome=result,
            sources=sources or ["internal_corroboration"],
            confidence=confidence,
        )

        return result

    @staticmethod
    def _representatives(
        groups: dict[str, list[dict[str, Any]]],
    ) -> list[str]:
        return [records[0]["claim_id"] for records in groups.values() if records]

    def _average_quality(self, groups: Any) -> float:
        scores: list[float] = []

        for records in groups:
            if not records:
                continue

            # One representative quality score per independent source.
            scores.append(self.quality.score(records[0])["quality_score"])

        if not scores:
            return 0.0

        return sum(scores) / len(scores)
