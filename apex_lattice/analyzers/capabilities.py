"""
CapabilityAnalyzer — surfaces capability-expansion opportunities.
"""

from __future__ import annotations

from typing import Any

_CAP_KEYWORDS = [
    "capabilit",
    "feature",
    "functionality",
    "extend",
    "expan",
    "enhance",
    "improve",
    "addition",
    "new ",
    "automat",
    "generat",
    "learn",
    "adapt",
    "self-improv",
]


class CapabilityAnalyzer:
    """Analyses artefacts for capability expansion opportunities."""

    category = "capabilities"

    def analyze(self, artefact: dict[str, Any]) -> list[dict[str, Any]]:
        text = (artefact.get("preview", "") + " " + artefact.get("raw", "")).lower()
        hits = [kw for kw in _CAP_KEYWORDS if kw in text]
        if not hits:
            return []
        return [
            {
                "category": self.category,
                "title": (
                    f"Capability opportunities in '{artefact.get('id', '?')}'"
                ),
                "description": (
                    f"Found {len(hits)} capability-expansion signal(s): "
                    f"{', '.join(hits[:5])}. "
                    "Consider whether new features or automated workflows "
                    "could be derived from the identified concepts."
                ),
                "severity": "info",
                "details": {"matched_keywords": hits},
            }
        ]
