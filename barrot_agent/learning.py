"""Durable, reviewable learning records for Barrot improvement cycles.

This module records outcomes; it does not modify code, execute tools, or
promote a candidate automatically. A separate evaluator can use the summaries
to decide whether a Bob-assisted change is worth reviewing.
"""

from __future__ import annotations

import json
import math
import uuid
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _score(value: float | None) -> float | None:
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("score must be a finite number between 0 and 1")
    return value


@dataclass(frozen=True)
class Experience:
    """One observable task outcome suitable for later evaluation."""

    task: str
    success: bool
    score: float | None = None
    feedback: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    experience_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    recorded_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.task.strip():
            raise ValueError("task must not be empty")
        object.__setattr__(self, "score", _score(self.score))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExperienceLedger:
    """Append-only JSONL storage for task outcomes and benchmark evidence."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def record(self, experience: Experience) -> Experience:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(experience.to_dict(), sort_keys=True) + "\n")
        return experience

    def read(self) -> list[Experience]:
        if not self.path.exists():
            return []
        records: list[Experience] = []
        with self.path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if not isinstance(data, dict):
                        raise TypeError("experience must be an object")
                    known_fields = {item.name for item in fields(Experience)}
                    records.append(Experience(**{
                        key: value for key, value in data.items() if key in known_fields
                    }))
                except (TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise ValueError(f"invalid experience at line {line_number}") from exc
        return records

    def recent(self, limit: int = 20) -> list[Experience]:
        if limit < 0:
            raise ValueError("limit must not be negative")
        return self.read()[-limit:] if limit else []

    def summarize(self, experiences: Iterable[Experience] | None = None) -> dict[str, Any]:
        records = list(self.read() if experiences is None else experiences)
        scored = [item.score for item in records if item.score is not None]
        successes = sum(item.success for item in records)
        return {
            "count": len(records),
            "successes": successes,
            "success_rate": successes / len(records) if records else 0.0,
            "mean_score": sum(scored) / len(scored) if scored else None,
        }

    def compare(
        self,
        baseline: Iterable[Experience],
        candidate: Iterable[Experience],
        minimum_delta: float = 0.0,
    ) -> dict[str, Any]:
        """Return an evidence-only promotion recommendation.

        Promotion remains a human or CI policy decision. Missing scores are
        never treated as passing results.
        """

        minimum_delta = float(minimum_delta)
        if not math.isfinite(minimum_delta) or minimum_delta < 0:
            raise ValueError("minimum_delta must be a finite, non-negative number")
        baseline_summary = self.summarize(baseline)
        candidate_summary = self.summarize(candidate)
        baseline_score = baseline_summary["mean_score"]
        candidate_score = candidate_summary["mean_score"]
        score_delta = (
            candidate_score - baseline_score
            if baseline_score is not None and candidate_score is not None
            else None
        )
        return {
            "baseline": baseline_summary,
            "candidate": candidate_summary,
            "score_delta": score_delta,
            "eligible": (
                score_delta is not None
                and score_delta >= minimum_delta
                and baseline_summary["count"] > 0
                and candidate_summary["count"] > 0
            ),
        }
