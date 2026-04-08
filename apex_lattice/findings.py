"""
FindingGenerator — analyses sandbox artefacts and produces structured findings.

Findings are persisted under ``.apex_lattice/findings/`` as individual
JSON files.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .analyzers import ALL_ANALYZERS

_DEFAULT_FINDINGS_DIR = Path(".apex_lattice") / "findings"


class Finding:
    """A single analysis finding."""

    def __init__(
        self,
        *,
        finding_id: str,
        category: str,
        title: str,
        description: str,
        severity: str,
        artefact_id: str,
        details: dict[str, Any] | None = None,
        created_at: float | None = None,
    ) -> None:
        self.finding_id = finding_id
        self.category = category
        self.title = title
        self.description = description
        self.severity = severity  # info | low | medium | high | critical
        self.artefact_id = artefact_id
        self.details: dict[str, Any] = details or {}
        self.created_at = created_at or time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "artefact_id": self.artefact_id,
            "details": self.details,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Finding":
        return cls(
            finding_id=data["finding_id"],
            category=data["category"],
            title=data["title"],
            description=data["description"],
            severity=data["severity"],
            artefact_id=data["artefact_id"],
            details=data.get("details", {}),
            created_at=data.get("created_at"),
        )


class FindingGenerator:
    """
    Runs all registered analyzers over sandbox artefacts and persists findings.
    """

    def __init__(self, findings_dir: Path | str | None = None) -> None:
        self._dir = Path(findings_dir) if findings_dir else _DEFAULT_FINDINGS_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, artefacts: list[dict[str, Any]]) -> list[Finding]:
        """Run all analyzers over *artefacts* and return the findings list."""
        findings: list[Finding] = []
        for artefact in artefacts:
            for analyzer in ALL_ANALYZERS:
                results = analyzer.analyze(artefact)
                for raw in results:
                    f = Finding(
                        finding_id=str(uuid.uuid4()),
                        artefact_id=artefact.get("id", "unknown"),
                        **raw,
                    )
                    findings.append(f)
                    self._persist(f)
        return findings

    def load_all(self) -> list[Finding]:
        """Load all previously persisted findings."""
        findings: list[Finding] = []
        for fp in sorted(self._dir.glob("*.json")):
            try:
                findings.append(Finding.from_dict(json.loads(fp.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, KeyError):
                pass
        return findings

    def clear(self) -> None:
        """Delete all persisted findings."""
        for f in self._dir.glob("*.json"):
            f.unlink()

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _persist(self, finding: Finding) -> None:
        dest = self._dir / f"{finding.finding_id}.json"
        dest.write_text(json.dumps(finding.to_dict(), indent=2), encoding="utf-8")
