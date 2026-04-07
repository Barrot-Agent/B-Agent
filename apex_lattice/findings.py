"""
Finding Generation.

Transforms raw analyzer results into structured Finding objects and
persists them to .apex_lattice/findings/<timestamp>_<type>_finding.json.
"""

from __future__ import annotations

import json
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
