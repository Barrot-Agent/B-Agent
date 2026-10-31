"""
CodePatternAnalyzer — identifies code-pattern optimisation opportunities
within the processed sandbox artefacts.
"""

from __future__ import annotations

from typing import Any

_PATTERN_KEYWORDS = [
    "algorithm",
    "complexity",
    "refactor",
    "optimis",
    "optim",
    "inefficien",
    "loop",
    "recursion",
    "iteration",
    "pattern",
]


class CodePatternAnalyzer:
    """Scans artefact text for code-pattern improvement signals."""

    category = "code_patterns"

    def analyze(self, artefact: dict[str, Any]) -> list[dict[str, Any]]:
        text = (artefact.get("preview", "") + " " + artefact.get("raw", "")).lower()
        hits = [kw for kw in _PATTERN_KEYWORDS if kw in text]
        if not hits:
            return []
        return [
            {
                "category": self.category,
                "title": f"Code-pattern signals detected in '{artefact.get('id', '?')}'",
                "description": (
                    f"The artefact references {len(hits)} code-pattern keyword(s): "
                    f"{', '.join(hits[:5])}. "
                    "Consider reviewing for algorithmic optimisation opportunities."
                ),
                "severity": "info",
                "details": {"matched_keywords": hits},
            }
        ]
