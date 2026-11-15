"""Evidence-based comparison for recursive self-improvement."""
from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class EvaluationSnapshot:
    """Immutable, revision-bound metrics from one completed evaluation run."""

    run_id: str
    revision: str
    metrics: Mapping[str, float]

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not isinstance(self.revision, str):
            raise TypeError("run_id and revision must be strings")
        if not self.run_id.strip() or not self.revision.strip():
            raise ValueError("run_id and revision must be non-empty")
        if not isinstance(self.metrics, Mapping):
            raise TypeError("metrics must be a mapping of names to numeric values")
        if not self.metrics:
            raise ValueError("at least one measured metric is required")
        copied: dict[str, float] = {}
        for name, value in self.metrics.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("metric names must be non-empty strings")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("metric values must be numeric and not boolean")
            try:
                numeric = float(value)
            except OverflowError as exc:
                raise ValueError("metric values must be finite") from exc
            if not math.isfinite(numeric):
                raise ValueError("metric values must be finite")
            copied[name] = numeric
        object.__setattr__(self, "metrics", MappingProxyType(copied))


@dataclass(frozen=True)
class ImprovementAssessment:
    """Auditable paired-run comparison and promotion decision."""

    eligible: bool
    improved: bool
    score: float
    baseline_run_id: str
    candidate_run_id: str
    baseline_revision: str
    candidate_revision: str
    metric_deltas: Mapping[str, float]
    regressions: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict:
        """Return a JSON-compatible assessment."""
        return {
            "eligible": self.eligible,
            "improved": self.improved,
            "score": self.score,
            "baseline_run_id": self.baseline_run_id,
            "candidate_run_id": self.candidate_run_id,
            "baseline_revision": self.baseline_revision,
            "candidate_revision": self.candidate_revision,
            "metric_deltas": dict(self.metric_deltas),
            "regressions": list(self.regressions),
            "reason": self.reason,
        }


def assess_improvement(
    baseline: EvaluationSnapshot,
    candidate: EvaluationSnapshot,
    *,
    lower_is_better: frozenset[str] = frozenset(),
    tolerances: Mapping[str, float] | None = None,
) -> ImprovementAssessment:
    """Compare paired measurements; positive deltas always mean improvement."""
    if baseline.run_id == candidate.run_id:
        raise ValueError("baseline and candidate must be distinct evaluation runs")
    if baseline.revision == candidate.revision:
        raise ValueError("baseline and candidate must use distinct revisions")
    if set(baseline.metrics) != set(candidate.metrics):
        raise ValueError("baseline and candidate must contain identical metric names")
    if tolerances is None:
        tolerances = {}
    elif not isinstance(tolerances, Mapping):
        raise TypeError("tolerances must be a mapping")
    if any(not isinstance(name, str) for name in tolerances) or any(not isinstance(name, str) for name in lower_is_better):
        raise TypeError("metric policy names must be strings")
    unknown_tolerances = set(tolerances) - set(baseline.metrics)
    unknown_directions = set(lower_is_better) - set(baseline.metrics)
    if unknown_tolerances or unknown_directions:
        raise ValueError("unknown metric configuration: " + ", ".join(sorted(unknown_tolerances | unknown_directions)))
    deltas: dict[str, float] = {}
    regressions: list[str] = []
    normalized: list[float] = []
    for name in sorted(baseline.metrics):
        before = baseline.metrics[name]
        after = candidate.metrics[name]
        raw = before - after if name in lower_is_better else after - before
        try:
            tolerance = float(tolerances.get(name, 0.0))
        except OverflowError as exc:
            raise ValueError(f"invalid tolerance for metric {name}") from exc
        if not math.isfinite(raw) or not math.isfinite(tolerance) or tolerance < 0:
            raise ValueError(f"non-finite delta or invalid tolerance for metric {name}")
        scaled = raw / max(abs(before), 1e-12)
        if not math.isfinite(scaled):
            raise ValueError(f"non-finite normalized delta for metric {name}")
        deltas[name] = raw
        normalized.append(scaled)
        if raw < -tolerance:
            regressions.append(name)
    try:
        score = math.fsum(normalized) / len(normalized)
    except OverflowError as exc:
        raise ValueError("non-finite aggregate improvement score") from exc
    if not math.isfinite(score):
        raise ValueError("non-finite aggregate improvement score")
    improved = not regressions and score > 0.0
    eligible = improved
    if regressions:
        reason = "candidate regressed on: " + ", ".join(regressions)
    elif not improved:
        reason = "aggregate measured improvement is not positive; candidate not promoted"
    else:
        reason = "candidate improved aggregate measured metrics without a tolerance breach"
    return ImprovementAssessment(
        eligible, improved, score if eligible else 0.0,
        baseline.run_id, candidate.run_id, baseline.revision, candidate.revision,
        MappingProxyType(deltas), tuple(regressions), reason,
    )
