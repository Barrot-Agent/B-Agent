"""
ArchitectureAnalyzer — highlights system-architecture refinement opportunities.
"""

from __future__ import annotations

from typing import Any

_ARCH_KEYWORDS = [
    "architecture",
    "design pattern",
    "microservice",
    "monolith",
    "coupling",
    "cohesion",
    "abstraction",
    "interface",
    "contract",
    "separation of concerns",
    "scalab",
    "modular",
    "layer",
]


class ArchitectureAnalyzer:
    """Analyses artefacts for architectural improvement signals."""

    category = "architecture"

    def analyze(self, artefact: dict[str, Any]) -> list[dict[str, Any]]:
        text = (artefact.get("preview", "") + " " + artefact.get("raw", "")).lower()
        hits = [kw for kw in _ARCH_KEYWORDS if kw in text]
        if not hits:
            return []
        severity = "medium" if len(hits) >= 4 else "info"
        return [
            {
                "category": self.category,
                "title": (
                    f"Architectural signals in '{artefact.get('id', '?')}'"
                ),
                "description": (
                    f"Identified {len(hits)} architecture-related term(s): "
                    f"{', '.join(hits[:5])}. "
                    "These may indicate areas where structural refactoring "
                    "or design-pattern adoption would improve maintainability."
                ),
                "severity": severity,
                "details": {"matched_keywords": hits},
            }
        ]
