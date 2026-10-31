"""
PerformanceAnalyzer — flags performance and bottleneck signals.
"""

from __future__ import annotations

from typing import Any

_PERF_KEYWORDS = [
    "performance",
    "bottleneck",
    "latency",
    "throughput",
    "scalab",
    "speed",
    "slow",
    "fast",
    "efficienc",
    "benchmark",
    "profile",
]

_HIGH_WORD_COUNT_THRESHOLD = 3000


class PerformanceAnalyzer:
    """Analyses artefacts for performance-related signals."""

    category = "performance"

    def analyze(self, artefact: dict[str, Any]) -> list[dict[str, Any]]:
        text = (artefact.get("preview", "") + " " + artefact.get("raw", "")).lower()
        word_count: int = artefact.get("word_count", 0)
        hits = [kw for kw in _PERF_KEYWORDS if kw in text]

        results: list[dict[str, Any]] = []

        if hits:
            results.append(
                {
                    "category": self.category,
                    "title": (
                        f"Performance signals found in '{artefact.get('id', '?')}'"
                    ),
                    "description": (
                        f"Matched {len(hits)} performance-related term(s): "
                        f"{', '.join(hits[:5])}. "
                        "Evaluate whether the described system can be profiled or tuned."
                    ),
                    "severity": "low",
                    "details": {"matched_keywords": hits},
                }
            )

        if word_count > _HIGH_WORD_COUNT_THRESHOLD:
            results.append(
                {
                    "category": self.category,
                    "title": f"Large artefact may indicate processing overhead",
                    "description": (
                        f"Artefact '{artefact.get('id', '?')}' contains "
                        f"{word_count:,} words. "
                        "Consider chunking or summarisation to reduce memory pressure."
                    ),
                    "severity": "low",
                    "details": {"word_count": word_count},
                }
            )

        return results
