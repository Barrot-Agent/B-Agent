"""
<<<<<<< HEAD
Finding Generation.

Transforms raw analyzer results into structured Finding objects and
persists them to .apex_lattice/findings/<timestamp>_<type>_finding.json.
=======
FindingGenerator — analyses sandbox artefacts and produces structured findings.

Findings are persisted under ``.apex_lattice/findings/`` as individual
JSON files.
>>>>>>> origin/main
"""

from __future__ import annotations

import json
<<<<<<< HEAD
import uuid
from datetime import datetime, timezone
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from apex_lattice.audit import AuditTrail

_FINDINGS_DIR = Path(".apex_lattice") / "findings"


@dataclass
class Finding:
    """A single infrastructure improvement finding."""

    id: str
    cycle_id: str
    category: str          # e.g. "code", "security", "performance", …
    title: str
    description: str
    severity: str          # "critical" | "high" | "medium" | "low" | "info"
    evidence: list[str]    # Supporting evidence snippets
    tags: list[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_data: dict[str, Any] = field(default_factory=dict)


class FindingGenerator:
    """Converts raw pipeline results into persisted Finding records."""

    def __init__(self, cycle_id: str, base_dir: Path | None = None) -> None:
        self.cycle_id = cycle_id
        self._base_dir = base_dir or Path(".")
        self._findings_dir = self._base_dir / _FINDINGS_DIR
        self._findings_dir.mkdir(parents=True, exist_ok=True)
        self.audit = AuditTrail(cycle_id, base_dir=self._base_dir)

    # ------------------------------------------------------------------
    def generate(self, pipeline_results: list[dict[str, Any]]) -> list[Finding]:
        """Generate and persist findings from pipeline results."""
        findings: list[Finding] = []
        for result in pipeline_results:
            raw_findings = result.get("findings", [])
            category = result.get("analyzer", "unknown")
            for raw in raw_findings:
                finding = self._build_finding(category, raw)
                self._persist(finding)
                findings.append(finding)
        self.audit.log("findings_generated", {"count": len(findings)})
        return findings

    # ------------------------------------------------------------------
    def _build_finding(self, category: str, raw: dict[str, Any]) -> Finding:
        return Finding(
            id=f"finding_{uuid.uuid4().hex[:12]}",
            cycle_id=self.cycle_id,
            category=category,
            title=raw.get("title", "Untitled Finding"),
            description=raw.get("description", ""),
            severity=raw.get("severity", "info"),
            evidence=raw.get("evidence", []),
            tags=raw.get("tags", [category]),
            raw_data=raw,
        )

    def _persist(self, finding: Finding) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{ts}_{finding.category}_{finding.id}.json"
        path = self._findings_dir / filename
        with path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(finding), fh, indent=2, default=str)
        self.audit.log("finding_persisted", {"file": filename, "severity": finding.severity})

    # ------------------------------------------------------------------
    def load_all(self) -> list[Finding]:
        """Load every persisted finding for the current cycle."""
        findings: list[Finding] = []
        for p in sorted(self._findings_dir.glob(f"*_{self.cycle_id}_*.json")):
            with p.open(encoding="utf-8") as fh:
                data = json.load(fh)
            findings.append(Finding(**data))
        return findings
=======
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
>>>>>>> origin/main
