"""
Recommendation Engine.

Takes a list of Finding objects and produces structured Recommendation
objects with rationale, proposed actions and priority ordering.

Recommendations are persisted to
.apex_lattice/recommendations/<timestamp>_recommendation.json.
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

# Severity → numeric priority (lower = more urgent)
_SEVERITY_PRIORITY: dict[str, int] = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "info": 5,
}


@dataclass
class Recommendation:
    """A structured improvement proposal."""

    id: str
    cycle_id: str
    title: str
    rationale: str
    proposed_actions: list[str]
    priority: int            # 1 (highest) – 5 (lowest)
    category: str
    related_finding_ids: list[str]
    estimated_effort: str    # "low" | "medium" | "high"
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

    # ------------------------------------------------------------------
    def generate(self, findings: list[Finding]) -> list[Recommendation]:
        """Group related findings and produce recommendations."""
        # Group by category
        by_category: dict[str, list[Finding]] = {}
        for f in findings:
            by_category.setdefault(f.category, []).append(f)

        recommendations: list[Recommendation] = []
        for category, cat_findings in by_category.items():
            rec = self._build_recommendation(category, cat_findings)
            self._persist(rec)
            recommendations.append(rec)

        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)
        self.audit.log(
            "recommendations_generated",
            {"count": len(recommendations)},
        )
        return recommendations

    # ------------------------------------------------------------------
    def _build_recommendation(
        self, category: str, findings: list[Finding]
    ) -> Recommendation:
        # Determine overall priority from the most severe finding
        min_priority = min(
            _SEVERITY_PRIORITY.get(f.severity, 5) for f in findings
        )

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
        """Generate a minimal set of concrete action items."""
        actions: list[str] = []
        for finding in findings[:5]:  # cap to avoid overwhelming PRs
            if finding.description:
                actions.append(finding.description)
        if not actions:
            actions.append(f"Review {category} module for improvement opportunities.")
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

    # ------------------------------------------------------------------
    def _persist(self, rec: Recommendation) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{ts}_{rec.category}_{rec.id}.json"
        path = self._rec_dir / filename
        with path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(rec), fh, indent=2, default=str)
        self.audit.log("recommendation_persisted", {"file": filename})
