"""
SecurityAnalyzer — highlights security-related considerations.
"""

from __future__ import annotations

from typing import Any

_SECURITY_KEYWORDS = [
    "vulnerabilit",
    "exploit",
    "attack",
    "injection",
    "privilege",
    "authenti",
    "authoris",
    "authoriz",
    "encrypt",
    "credential",
    "secret",
    "token",
    "exposure",
    "sanitiz",
    "sanitise",
    "input validation",
]


class SecurityAnalyzer:
    """Scans artefacts for security-concern keywords."""

    category = "security"

    def analyze(self, artefact: dict[str, Any]) -> list[dict[str, Any]]:
        text = (artefact.get("preview", "") + " " + artefact.get("raw", "")).lower()
        hits = [kw for kw in _SECURITY_KEYWORDS if kw in text]
        if not hits:
            return []
        severity = "medium" if len(hits) >= 3 else "low"
        return [
            {
                "category": self.category,
                "title": (
                    f"Security considerations present in '{artefact.get('id', '?')}'"
                ),
                "description": (
                    f"Found {len(hits)} security-related term(s): "
                    f"{', '.join(hits[:5])}. "
                    "Review whether these concepts require mitigations in the system."
                ),
                "severity": severity,
                "details": {"matched_keywords": hits},
            }
        ]
