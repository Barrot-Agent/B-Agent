"""Autonomous iterative refinement for Code-as-World."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RefinementAction:
    iteration: int
    action: str
    reason: str
    parameters: dict[str, Any] = field(
        default_factory=dict,
    )
    created_at: str = field(
        default_factory=utcnow,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RefinementPlan:
    validation_manifest: str
    passed: bool
    actions: list[RefinementAction] = field(
        default_factory=list,
    )
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_manifest": (
                self.validation_manifest
            ),
            "passed": self.passed,
            "actions": [
                action.to_dict()
                for action in self.actions
            ],
            "metadata": self.metadata,
        }


def load_validation(
    validation_manifest: str | Path,
) -> dict[str, Any]:
    path = Path(
        validation_manifest
    ).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Validation manifest must be a JSON object."
        )

    return data


def plan_refinement(
    validation_manifest: str | Path,
) -> RefinementPlan:
    """
    Produce the next deterministic refinement actions.

    This does not modify the world automatically yet. It creates
    a machine-readable action plan that later workflow stages can
    execute and revalidate.
    """

    path = Path(
        validation_manifest
    ).expanduser().resolve()

    validation = load_validation(path)

    passed = bool(
        validation.get(
            "passed",
            False,
        )
    )

    metrics = validation.get(
        "metrics",
        [],
    )

    actions: list[RefinementAction] = []

    if passed:
        actions.append(
            RefinementAction(
                iteration=1,
                action="accept_world",
                reason=(
                    "Current validation passed. "
                    "Preserve the generated world."
                ),
            )
        )
    else:
        failing_metrics = [
            metric
            for metric in metrics
            if isinstance(metric, dict)
            and not bool(
                metric.get(
                    "passed",
                    False,
                )
            )
        ]

        for index, metric in enumerate(
            failing_metrics,
            start=1,
        ):
            name = str(
                metric.get(
                    "name",
                    "unknown_metric",
                )
            )

            if name == "object_count_error":
                action = (
                    "rebuild_object_mapping"
                )
                reason = (
                    "Generated object count does not "
                    "match the structured world."
                )
            else:
                action = (
                    "reinspect_validation_metric"
                )
                reason = (
                    "A validation metric failed and "
                    "requires another generation pass."
                )

            actions.append(
                RefinementAction(
                    iteration=index,
                    action=action,
                    reason=reason,
                    parameters={
                        "metric": name,
                        "value": metric.get(
                            "value",
                        ),
                        "threshold": metric.get(
                            "threshold",
                        ),
                    },
                )
            )

        if not actions:
            actions.append(
                RefinementAction(
                    iteration=1,
                    action="revalidate",
                    reason=(
                        "Validation failed without a "
                        "specific failed metric."
                    ),
                )
            )

    return RefinementPlan(
        validation_manifest=str(path),
        passed=passed,
        actions=actions,
        metadata={
            "planned_at": utcnow(),
            "action_count": len(actions),
        },
    )


def save_refinement_plan(
    plan: RefinementPlan,
    output: str | Path,
) -> Path:
    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            plan.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path
