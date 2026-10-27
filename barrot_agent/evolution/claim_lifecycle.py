"""
Barrot Claim Lifecycle Engine.

Claims remain revisable. Status reflects available evidence rather than
permanently declaring a claim true or false.
"""

from __future__ import annotations

from typing import Any


class ClaimLifecycleEngine:
    """Determine a claim's current evidence-based lifecycle state."""

    def determine(
        self,
        supporting_sources: int,
        conflicting_sources: int,
        confidence: float,
    ) -> dict[str, Any]:
        if conflicting_sources > 0 and supporting_sources > 0:
            status = "disputed"
        elif conflicting_sources > 0:
            status = "challenged"
        elif supporting_sources >= 2:
            status = "supported"
        elif supporting_sources >= 1:
            status = "candidate"
        else:
            status = "unverified"

        return {
            "status": status,
            "supporting_sources": supporting_sources,
            "conflicting_sources": conflicting_sources,
            "confidence": round(confidence, 3),
        }
