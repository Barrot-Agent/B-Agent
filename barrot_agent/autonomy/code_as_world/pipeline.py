"""End-to-end Code-as-World orchestration pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import subprocess
import sys

from barrot_agent.autonomy.code_as_world.video_observer import (
    observe_video,
    save_observation,
)
from barrot_agent.autonomy.code_as_world.scene_extractor import (
    extract_scenes,
    save_scene_manifest,
)
from barrot_agent.autonomy.code_as_world.world_builder import (
    build_world,
    save_world,
)
from barrot_agent.autonomy.code_as_world.autonomous_refiner import (
    plan_refinement,
    save_refinement_plan,
)


@dataclass
class PipelineStage:
    name: str
    status: str
    output: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineResult:
    source_path: str
    passed: bool
    stages: list[PipelineStage] = field(
        default_factory=list,
    )
    outputs: dict[str, str] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "passed": self.passed,
            "stages": [
                stage.to_dict()
                for stage in self.stages
            ],
            "outputs": self.outputs,
        }


def _run_mujoco_generator(
    world_path: Path,
    output_path: Path,
) -> None:
    """Run the repository's MuJoCo generator."""

    command = [
        sys.executable,
        "-m",
        "barrot_agent.autonomy.code_as_world.run_mujoco_generator",
        str(world_path),
        "--output",
        str(output_path),
    ]

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            completed.stderr
            or completed.stdout
            or "MuJoCo generation failed."
        )


def _run_validator(
    physics_path: Path,
    world_path: Path,
    observation_path: Path,
    output_path: Path,
) -> None:
    """Run the simulation validator."""

    command = [
        sys.executable,
        "-m",
        "barrot_agent.autonomy.code_as_world.run_simulation_validator",
        str(physics_path),
        "--world",
        str(world_path),
        "--observation",
        str(observation_path),
        "--output",
        str(output_path),
    ]

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            completed.stderr
            or completed.stdout
            or "Simulation validation failed."
        )


def run_pipeline(
    video: str | Path,
    output_dir: str | Path,
    sample_every: int = 30,
    scene_threshold: float = 25.0,
) -> PipelineResult:
    """Run the complete Code-as-World pipeline."""

    source_path = Path(
        video
    ).expanduser().resolve()

    root = Path(
        output_dir
    ).expanduser().resolve()

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    frames_dir = root / "frames"
    observation_path = root / "observation.json"
    scenes_path = root / "scenes.json"
    world_path = root / "world.json"
    physics_path = root / "world.xml"
    validation_path = root / "validation.json"
    refinement_path = root / "refinement_plan.json"
    result_path = root / "pipeline_result.json"

    stages: list[PipelineStage] = []
    outputs: dict[str, str] = {}

    try:
        observation = observe_video(
            source_path,
            sample_every=sample_every,
        )

        save_observation(
            observation,
            observation_path,
        )

        outputs["observation"] = str(
            observation_path
        )

        stages.append(
            PipelineStage(
                name="video_observation",
                status="implemented",
                output=str(
                    observation_path
                ),
            )
        )

        extraction = extract_scenes(
            source=source_path,
            output_dir=frames_dir,
            sample_every=sample_every,
            scene_threshold=scene_threshold,
        )

        save_scene_manifest(
            extraction,
            scenes_path,
        )

        outputs["scenes"] = str(
            scenes_path
        )

        stages.append(
            PipelineStage(
                name="scene_extraction",
                status="implemented",
                output=str(
                    scenes_path
                ),
            )
        )

        world = build_world(
            scenes_path
        )

        save_world(
            world,
            world_path,
        )

        outputs["world"] = str(
            world_path
        )

        stages.append(
            PipelineStage(
                name="world_representation",
                status="implemented",
                output=str(
                    world_path
                ),
            )
        )

        _run_mujoco_generator(
            world_path,
            physics_path,
        )

        outputs["physics_program"] = str(
            physics_path
        )

        stages.append(
            PipelineStage(
                name="physics_program_generation",
                status="implemented",
                output=str(
                    physics_path
                ),
            )
        )

        _run_validator(
            physics_path=physics_path,
            world_path=world_path,
            observation_path=observation_path,
            output_path=validation_path,
        )

        outputs["validation"] = str(
            validation_path
        )

        stages.append(
            PipelineStage(
                name="simulation_validation",
                status="implemented",
                output=str(
                    validation_path
                ),
            )
        )

        plan = plan_refinement(
            validation_path
        )

        save_refinement_plan(
            plan,
            refinement_path,
        )

        outputs["refinement"] = str(
            refinement_path
        )

        stages.append(
            PipelineStage(
                name="autonomous_refinement",
                status="implemented",
                output=str(
                    refinement_path
                ),
            )
        )

        result = PipelineResult(
            source_path=str(
                source_path
            ),
            passed=plan.passed,
            stages=stages,
            outputs=outputs,
        )

    except Exception as exc:
        stages.append(
            PipelineStage(
                name="pipeline",
                status="failed",
                error=str(exc),
            )
        )

        result = PipelineResult(
            source_path=str(
                source_path
            ),
            passed=False,
            stages=stages,
            outputs=outputs,
        )

    result_path.write_text(
        json.dumps(
            result.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    outputs["pipeline_result"] = str(
        result_path
    )

    return result
