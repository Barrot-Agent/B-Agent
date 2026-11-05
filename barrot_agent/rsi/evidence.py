"""Evidence-based comparison for recursive self-improvement."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import math
from typing import Mapping

@dataclass(frozen=True)
class EvaluationSnapshot:
    run_id: str
    revision: str
    metrics: Mapping[str, float]
    def __post_init__(self) -> None:
        if not self.run_id.strip() or not self.revision.strip(): raise ValueError("run_id and revision must be non-empty")
        if not self.metrics: raise ValueError("at least one measured metric is required")
        for name, value in self.metrics.items():
            if not name.strip() or not math.isfinite(float(value)): raise ValueError("metric names must be non-empty and values finite")

@dataclass(frozen=True)
class ImprovementAssessment:
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
    def to_dict(self) -> dict: return asdict(self)

def assess_improvement(baseline: EvaluationSnapshot, candidate: EvaluationSnapshot, *, lower_is_better: frozenset[str] = frozenset(), tolerances: Mapping[str, float] | None = None) -> ImprovementAssessment:
    """Compare paired measurements; positive deltas always mean improvement."""
    if baseline.run_id == candidate.run_id: raise ValueError("baseline and candidate must be distinct evaluation runs")
    if set(baseline.metrics) != set(candidate.metrics): raise ValueError("baseline and candidate must contain identical metric names")
    tolerances = tolerances or {}
    deltas: dict[str, float] = {}; regressions: list[str] = []; normalized: list[float] = []
    for name in sorted(baseline.metrics):
        before, after = float(baseline.metrics[name]), float(candidate.metrics[name])
        raw = before - after if name in lower_is_better else after - before
        tolerance = float(tolerances.get(name, 0.0))
        if not math.isfinite(tolerance) or tolerance < 0: raise ValueError(f"invalid tolerance for metric {name}")
        deltas[name] = raw; normalized.append(raw / max(abs(before), 1e-12))
        if raw < -tolerance: regressions.append(name)
    score = sum(normalized) / len(normalized)
    improved = not regressions and any(delta > 0 for delta in deltas.values())
    eligible = not regressions
    reason = "candidate improved measured metrics without a tolerance breach" if improved else ("candidate regressed on: " + ", ".join(regressions) if regressions else "no measured improvement; candidate not promoted")
    return ImprovementAssessment(eligible, improved, score if eligible else 0.0, baseline.run_id, candidate.run_id, baseline.revision, candidate.revision, deltas, tuple(regressions), reason)
