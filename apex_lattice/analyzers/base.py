"""
Base analyzer interface.

Every concrete analyzer must subclass BaseAnalyzer and implement
the `analyze()` method which returns a dict with at least a
"findings" key containing a list of raw finding dicts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseAnalyzer(ABC):
    """Abstract base for all Apex Lattice analyzers."""

    #: Human-readable name; override in subclasses.
    name: str = "base"

    def __init__(self, repo_root: Path, sandbox_dir: Path) -> None:
        self.repo_root = repo_root
        self.sandbox_dir = sandbox_dir

    @abstractmethod
    def analyze(self) -> dict[str, Any]:
        """Run the analysis and return a result dict.

        The returned dict MUST contain:
            - "findings": list[dict]  – each item has at least
              "title", "description", "severity", "evidence", "tags".

        It MAY contain additional keys for context.
        """
        ...  # pragma: no cover

    # ------------------------------------------------------------------
    # Helpers shared across analyzers
    # ------------------------------------------------------------------

    def _iter_source_files(self, extensions: tuple[str, ...] = (".py",)):
        """Yield all source files in the repo matching the given extensions."""
        for ext in extensions:
            yield from self.repo_root.rglob(f"*{ext}")

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    @staticmethod
    def _make_finding(
        title: str,
        description: str,
        severity: str = "info",
        evidence: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "title": title,
            "description": description,
            "severity": severity,
            "evidence": evidence or [],
            "tags": tags or [],
        }
