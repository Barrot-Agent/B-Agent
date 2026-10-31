"""
Barrot Evidence Quality Engine.

Scores evidence using transparent, auditable factors. A quality score is not
a declaration of truth; it estimates how suitable a record is for reasoning.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class EvidenceQualityEngine:
    """Evaluate evidence quality without treating source reputation as truth."""

    def score(self, evidence: dict[str, Any]) -> dict[str, Any]:
        factors: dict[str, float] = {}

        # Provenance: identifiable source and URL make evidence auditable.
        source = str(evidence.get("source", "")).strip()
        source_url = str(evidence.get("source_url", "")).strip()
        factors["provenance"] = 1.0 if source and source_url else 0.7 if source else 0.3

        # Completeness: essential fields required for inspection.
        required = ("claim_id", "claim", "source")
        present = sum(bool(evidence.get(field)) for field in required)
        factors["completeness"] = present / len(required)

        # Recency: evidence without a timestamp is usable but less informative.
        retrieved_at = evidence.get("retrieved_at")
        factors["recency"] = self._recency_score(retrieved_at)

        score = (
            factors["provenance"] * 0.40
            + factors["completeness"] * 0.35
            + factors["recency"] * 0.25
        )

        return {
            "quality_score": round(score, 3),
            "factors": factors,
        }

    @staticmethod
    def _recency_score(value: Any) -> float:
        if not value:
            return 0.5

        try:
            timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            age_days = max(
                0,
                (datetime.now(timezone.utc) - timestamp).days,
            )

            if age_days <= 30:
                return 1.0
            if age_days <= 180:
                return 0.8
            if age_days <= 365:
                return 0.6
            return 0.4
        except (TypeError, ValueError):
            return 0.5
