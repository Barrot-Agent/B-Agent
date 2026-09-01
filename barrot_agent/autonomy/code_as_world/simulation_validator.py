"""Simulation validation for Code-as-World."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import math
import xml.etree.ElementTree as ET


@dataclass
class ValidationMetric:
    name: str
    value: float
    threshold: float
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SimulationValidation:
    physics_program: str
    observation_manifest: str | None
    world_manifest: str | None
    passed: bool
    metrics: list[ValidationMetric] = field(
        default_factory=list,
    )
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "physics_program": self.physics_program,
            "observation_manifest": (
                self.observation_manifest
            ),
            "world_manifest": self.world_manifest,
            "passed": self.passed,
            "metrics": [
                metric.to_dict()
                for metric in self.metrics
            ],
            "metadata": self.metadata,
        }


def _load_json(
    path: str | Path | None,
) -> dict[str, Any]:
    if path is None:
        return {}

    source = Path(path).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(source)

    data = json.loads(
        source.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object: {source}"
        )

    return data


def validate_simulation(
    physics_program: str | Path,
    world_manifest: str | Path | None = None,
    observation_manifest: str | Path | None = None,
) -> SimulationValidation:
    """Validate generated physics structure against source manifests."""

    physics_path = Path(
        physics_program
    ).expanduser().resolve()

    if not physics_path.exists():
        raise FileNotFoundError(
            physics_path
        )

    world = _load_json(
        world_manifest
    )

    observation = _load_json(
        observation_manifest
    )

    root = ET.parse(
        physics_path
    ).getroot()

    if root.tag != "mujoco":
        raise ValueError(
            "Physics program is not a MuJoCo model."
        )

    expected_objects = 0

    for state in world.get(
        "states",
        [],
    ):
        if isinstance(state, dict):
            objects = state.get(
                "objects",
                [],
            )

            if isinstance(objects, list):
                expected_objects += len(
                    objects
                )

    generated_bodies = root.findall(
        "./worldbody/body"
    )

    generated_objects = len(
        generated_bodies
    )

    object_error = abs(
        generated_objects
        - expected_objects
    )

    object_threshold = 0.0

    object_metric = ValidationMetric(
        name="object_count_error",
        value=float(object_error),
        threshold=object_threshold,
        passed=(
            object_error
            <= object_threshold
        ),
    )

    expected_duration = 0.0

    if "duration_seconds" in observation:
        try:
            expected_duration = float(
                observation[
                    "duration_seconds"
                ]
            )
        except (
            TypeError,
            ValueError,
        ):
            expected_duration = 0.0

    if not math.isfinite(
        expected_duration
    ):
        expected_duration = 0.0

    simulation_time = max(
        expected_duration,
        0.0,
    )

    duration_metric = ValidationMetric(
        name="reference_duration_seconds",
        value=simulation_time,
        threshold=0.0,
        passed=True,
    )

    metrics = [
        object_metric,
        duration_metric,
    ]

    passed = all(
        metric.passed
        for metric in metrics
    )

    return SimulationValidation(
        physics_program=str(
            physics_path
        ),
        observation_manifest=(
            str(
                Path(
                    observation_manifest
                ).expanduser().resolve()
            )
            if observation_manifest
            else None
        ),
        world_manifest=(
            str(
                Path(
                    world_manifest
                ).expanduser().resolve()
            )
            if world_manifest
            else None
        ),
        passed=passed,
        metrics=metrics,
        metadata={
            "expected_objects": (
                expected_objects
            ),
            "generated_objects": (
                generated_objects
            ),
        },
    )


def save_validation(
    validation: SimulationValidation,
    output: str | Path,
) -> Path:
    """Persist simulation validation results."""

    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            validation.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path
