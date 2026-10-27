"""
DependencyAnalyzer — identifies dependency improvement opportunities.
"""

from __future__ import annotations

from typing import Any

_DEP_KEYWORDS = [
    "dependenc",
    "library",
    "package",
    "version",
    "upgrade",
    "deprecat",
    "obsolete",
    "legacy",
    "integration",
    "import",
    "module",
]


class DependencyAnalyzer:
    """Analyses artefacts for dependency-related signals."""

    category = "dependencies"

    def analyze(self, artefact: dict[str, Any]) -> list[dict[str, Any]]:
        text = (artefact.get("preview", "") + " " + artefact.get("raw", "")).lower()
        hits = [kw for kw in _DEP_KEYWORDS if kw in text]
        if not hits:
            return []
        return [
            {
                "category": self.category,
                "title": (
                    f"Dependency signals in '{artefact.get('id', '?')}'"
                ),
                "description": (
                    f"Detected {len(hits)} dependency-related term(s): "
                    f"{', '.join(hits[:5])}. "
                    "Review whether referenced libraries or integrations require "
                    "version updates or replacements."
                ),
                "severity": "info",
                "details": {"matched_keywords": hits},
            }
        ]
