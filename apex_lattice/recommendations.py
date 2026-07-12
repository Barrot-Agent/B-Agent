"""
RecommendationEngine -- turns findings into structured improvement proposals.

Recommendations are grouped by category, ranked by severity, and persisted
under ``.apex_lattice/recommendations/`` as JSON.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .findings import Finding

_DEFAULT_REC_DIR = Path(".apex_lattice") / "recommendations"

# Severity ordering (higher = more urgent)
_SEVERITY_RANK = {
    "critical": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1,
}


class Recommendation:
    """A structured improvement proposal derived from one or more findings."""

    def __init__(
        self,
        *,
        rec_id: str,
        category: str,
        title: str,
        rationale: str,
        action_items: list[str],
        priority: str,
        source_finding_ids: list[str],
        created_at: float | None = None,
    ) -> None:
        self.rec_id = rec_id
        self.category = category
        self.title = title
        self.rationale = rationale
        self.action_items = action_items
        self.priority = priority
        self.source_finding_ids = source_finding_ids
        self.created_at = created_at or time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "rec_id": self.rec_id,
            "category": self.category,
            "title": self.title,
            "rationale": self.rationale,
            "action_items": self.action_items,
            "priority": self.priority,
            "source_finding_ids": self.source_finding_ids,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Recommendation":
        return cls(
            rec_id=data["rec_id"],
            category=data["category"],
            title=data["title"],
            rationale=data["rationale"],
            action_items=data.get("action_items", []),
            priority=data["priority"],
            source_finding_ids=data.get("source_finding_ids", []),
            created_at=data.get("created_at"),
        )

    def to_markdown(self) -> str:
        lines = [
            f"## {self.title}",
            "",
            f"**Category:** {self.category}  ",
            f"**Priority:** {self.priority}  ",
            "",
            "### Rationale",
            "",
            self.rationale,
            "",
            "### Action Items",
            "",
        ]
        for item in self.action_items:
            lines.append(f"- {item}")
        return "\n".join(lines)


class RecommendationEngine:
    """Aggregates findings into prioritised recommendations."""

    def __init__(self, rec_dir: Path | str | None = None) -> None:
        self._dir = Path(rec_dir) if rec_dir else _DEFAULT_REC_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, findings: list[Finding]) -> list[Recommendation]:
        """
        Convert a list of findings into a deduplicated, ranked list of
        recommendations (one per category).
        """
        # Group by category
        by_category: dict[str, list[Finding]] = {}
        for f in findings:
            by_category.setdefault(f.category, []).append(f)

        recs: list[Recommendation] = []
        for category, cat_findings in by_category.items():
            rec = self._build_recommendation(category, cat_findings)
            recs.append(rec)
            self._persist(rec)

        # Sort by priority (highest first)
        recs.sort(key=lambda r: _SEVERITY_RANK.get(r.priority, 0), reverse=True)
        return recs

    def load_all(self) -> list[Recommendation]:
        """Load all previously persisted recommendations."""
        recs: list[Recommendation] = []
        for fp in sorted(self._dir.glob("*.json")):
            try:
                recs.append(
                    Recommendation.from_dict(
                        json.loads(fp.read_text(encoding="utf-8"))
                    )
                )
            except (json.JSONDecodeError, KeyError):
                pass
        return recs

    def clear(self) -> None:
        """Delete all persisted recommendations."""
        for f in self._dir.glob("*.json"):
            f.unlink()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

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

    def _build_recommendation(
        self, category: str, findings: list[Finding]
    ) -> Recommendation:
        # Highest severity in the group drives the priority
        max_rank = max(
            (_SEVERITY_RANK.get(f.severity, 0) for f in findings), default=1
        )
        priority = next(
            (s for s, r in _SEVERITY_RANK.items() if r == max_rank), "info"
        )

        artefact_ids = list({f.artefact_id for f in findings})
        artefact_summary = ", ".join(artefact_ids[:3])
        if len(artefact_ids) > 3:
            artefact_summary += f" (+{len(artefact_ids) - 3} more)"

        rationale = (
            f"{len(findings)} finding(s) in the '{category}' category were identified "
            f"across artefact(s): {artefact_summary}. "
            "Addressing these items will improve the overall health and resilience "
            "of the system."
        )

        action_items = self._ACTION_TEMPLATES.get(
            category,
            ["Review the associated findings and determine appropriate remediation."],
        )

        return Recommendation(
            rec_id=str(uuid.uuid4()),
            category=category,
            title=f"Improve {category.replace('_', ' ').title()}",
            rationale=rationale,
            action_items=action_items,
            priority=priority,
            source_finding_ids=[f.finding_id for f in findings],
        )

    def _persist(self, rec: Recommendation) -> None:
        dest = self._dir / f"{rec.rec_id}.json"
        dest.write_text(json.dumps(rec.to_dict(), indent=2), encoding="utf-8")
