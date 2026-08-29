"""
Barrot Claim Integrity Engine.

Normalizes simple factual claims and detects explicit contradictions.
This layer flags uncertainty rather than treating weak textual similarity
as proof.
"""

from __future__ import annotations

import re
from typing import Any


class ClaimIntegrityEngine:
    """Normalize claims and detect explicit positive/negative conflicts."""

    NEGATIONS = {
        "not",
        "no",
        "never",
        "false",
        "cannot",
        "isn't",
        "aren't",
        "doesn't",
        "don't",
    }

    @staticmethod
    def normalize(claim: Any) -> dict[str, Any]:
        """Convert a claim into a comparable representation."""
        if isinstance(claim, dict):
            text = str(claim.get("claim", claim))
        else:
            text = str(claim)

        tokens = re.findall(r"[a-z0-9']+", text.lower())
        negated = any(token in ClaimIntegrityEngine.NEGATIONS for token in tokens)
        core_tokens = [token for token in tokens if token not in ClaimIntegrityEngine.NEGATIONS]

        return {
            "text": text,
            "tokens": set(core_tokens),
            "negated": negated,
        }

    def compare(self, claim_a: Any, claim_b: Any) -> dict[str, Any]:
        """Compare two claims without overstating certainty."""
        a = self.normalize(claim_a)
        b = self.normalize(claim_b)

        shared = a["tokens"] & b["tokens"]
        union = a["tokens"] | b["tokens"]
        similarity = len(shared) / len(union) if union else 0.0

        # A contradiction requires substantial subject/predicate overlap
        # plus opposite explicit polarity.
        contradiction = similarity >= 0.5 and a["negated"] != b["negated"]

        if contradiction:
            status = "contradiction"
        elif similarity >= 0.5:
            status = "agreement"
        else:
            status = "unrelated"

        return {
            "status": status,
            "similarity": round(similarity, 3),
            "shared_terms": sorted(shared),
            "claim_a_negated": a["negated"],
            "claim_b_negated": b["negated"],
        }
