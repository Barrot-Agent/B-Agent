"""
Recommendation Engine.

Takes a list of Finding objects and produces structured Recommendation
objects with rationale, proposed actions and priority ordering.

Recommendations are persisted to
.apex_lattice/recommendations/<timestamp>_<category>_<id>.json.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apex_lattice.audit import AuditTrail
from apex_lattice.findings import Finding

_RECOMMENDATIONS_DIR = Path(".apex_lattice") / "recommendations"

_SEVERITY_PRIORITY: dict[str, int] = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "info": 5,
}

_ACTION_TEMPLATES: dict[str, list[str]] = {
    "code_patterns": [
        "Profile hot paths and identify O(n^2) or worse algorithms.",
        "Introduce design patterns (strategy, factory, decorator) where appropriate.",
        "Extract duplicated logic into shared utilities.",
        "Add type annotations and static analysis to surface latent bugs.",
    ],
    "performance": [
        "Benchmark the critical path before and after any changes.",
        "Consider caching or memoisation for expensive repeated computations.",
        "Chunk large data sets to reduce peak memory usage.",
        "Enable async/concurrent processing where I/O is the bottleneck.",
    ],
    "security": [
        "Audit all external inputs for injection risks.",
        "Rotate and vault any secrets or credentials found in the codebase.",
        "Apply least-privilege principles to all service accounts and tokens.",
        "Add automated dependency vulnerability scanning to CI.",
    ],
    "dependencies": [
        "Upgrade pinned dependencies to their latest stable releases.",
        "Remove unused or transitive dependencies.",
        "Document the rationale for each major dependency.",
        "Consider lighter-weight alternatives to heavy dependencies.",
    ],
    "architecture": [
        "Introduce explicit module boundaries and public-API contracts.",
        "Separate domain logic from infrastructure concerns.",
        "Document the high-level architecture in an ADR (Architecture Decision Record).",
        "Evaluate whether the current coupling hinders independent scaling.",
    ],
    "capabilities": [
        "Catalogue the intended capability set and identify gaps.",
        "Design extension points (plugins, hooks) for future capabilities.",
        "Automate repetitive tasks that are currently performed manually.",
        "Prototype the highest-value capability addition in an isolated branch.",
    ],
}


@dataclass
class Recommendation:
    """A structured improvement proposal."""

    id: str
    cycle_id: str
    title: str
    rationale: str
    proposed_actions: list[str]
    priority: int
    category: str
    related_finding_ids: list[str]
    estimated_effort: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class RecommendationEngine:
    """Converts findings into actionable recommendations."""

    def __init__(self, cycle_id: str, base_dir: Path | None = None) -> None:
        self.cycle_id = cycle_id
        self._base_dir = base_dir or Path(".")
        self._rec_dir = self._base_dir / _RECOMMENDATIONS_DIR
        self._rec_dir.mkdir(parents=True, exist_ok=True)
        self.audit = AuditTrail(cycle_id, base_dir=self._base_dir)

    def generate(self, findings: list[Finding]) -> list[Recommendation]:
        """Group related findings by category and produce one recommendation per group."""
        by_category: dict[str, list[Finding]] = {}
        for f in findings:
            by_category.setdefault(f.category, []).append(f)

        recommendations: list[Recommendation] = []
        for category, cat_findings in by_category.items():
            rec = self._build_recommendation(category, cat_findings)
            self._persist(rec)
            recommendations.append(rec)

        recommendations.sort(key=lambda r: r.priority)
        self.audit.log("recommendations_generated", {"count": len(recommendations)})
        return recommendations

    def _build_recommendation(self, category: str, findings: list[Finding]) -> Recommendation:
        min_priority = min((_SEVERITY_PRIORITY.get(f.severity, 5) for f in findings), default=5)
        actions = self._derive_actions(category, findings)
        effort = self._estimate_effort(findings)

        return Recommendation(
            id=f"rec_{uuid.uuid4().hex[:12]}",
            cycle_id=self.cycle_id,
            title=f"Improve {category.replace('_', ' ').title()} Quality",
            rationale=(
                f"Analysis identified {len(findings)} finding(s) in the "
                f"'{category}' category. Addressing these will improve "
                "system stability, security and performance."
            ),
            proposed_actions=actions,
            priority=min_priority,
            category=category,
            related_finding_ids=[f.id for f in findings],
            estimated_effort=effort,
            metadata={
                "finding_count": len(findings),
                "severity_breakdown": self._severity_breakdown(findings),
            },
        )

    @staticmethod
    def _derive_actions(category: str, findings: list[Finding]) -> list[str]:
        actions: list[str] = []
        for finding in findings[:5]:
            if finding.description:
                actions.append(finding.description)
        if not actions:
            actions = list(
                _ACTION_TEMPLATES.get(
                    category,
                    [f"Review {category} module for improvement opportunities."],
                )
            )
        return actions

    @staticmethod
    def _estimate_effort(findings: list[Finding]) -> str:
        criticals = sum(1 for f in findings if f.severity in ("critical", "high"))
        if criticals >= 3:
            return "high"
        if criticals >= 1:
            return "medium"
        return "low"

    @staticmethod
    def _severity_breakdown(findings: list[Finding]) -> dict[str, int]:
        breakdown: dict[str, int] = {}
        for f in findings:
            breakdown[f.severity] = breakdown.get(f.severity, 0) + 1
        return breakdown

    def _persist(self, rec: Recommendation) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{ts}_{rec.category}_{rec.id}.json"
        path = self._rec_dir / filename
        with path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(rec), fh, indent=2, default=str)
        self.audit.log("recommendation_persisted", {"file": filename})

    def load_all(self) -> list[Recommendation]:
        """Load all previously persisted recommendations for the current cycle."""
        recs: list[Recommendation] = []
        for p in sorted(self._rec_dir.glob(f"*_{self.cycle_id}_*.json")):
            try:
                with p.open(encoding="utf-8") as fh:
                    data = json.load(fh)
                recs.append(Recommendation(**data))
            except (json.JSONDecodeError, TypeError, KeyError):
                continue
        return recs
