"""Build structured world representations from scene manifests."""

from __future__ import annotations

from pathlib import Path
import json

from barrot_agent.autonomy.code_as_world.world_models import (
    PhysicalWorld,
    WorldObject,
    WorldState,
    Vector3,
)


def build_world(
    scene_manifest: str | Path,
) -> PhysicalWorld:
    """
    Convert extracted scene data into an initial structured world.

    This phase establishes a stable representation boundary.
    Object semantics and physics inference are added later.
    """

    manifest_path = Path(
        scene_manifest
    ).expanduser().resolve()

    if not manifest_path.exists():
        raise FileNotFoundError(
            manifest_path
        )

    raw = json.loads(
        manifest_path.read_text(
            encoding="utf-8",
        )
    )

    states: list[WorldState] = []

    for scene in raw.get("scenes", []):
        scene_index = int(
            scene["scene_index"]
        )

        duration = max(
            0.0,
            float(scene["end_time"])
            - float(scene["start_time"]),
        )

        representative = (
            scene["representative_frame"]
        )

        object_id = (
            f"scene_anchor_{scene_index}"
        )

        anchor = WorldObject(
            id=object_id,
            kind="scene_anchor",
            position=Vector3(
                x=0.0,
                y=0.0,
                z=0.0,
            ),
            size=Vector3(
                x=1.0,
                y=1.0,
                z=1.0,
            ),
            metadata={
                "scene_index": scene_index,
                "start_frame": scene[
                    "start_frame"
                ],
                "end_frame": scene[
                    "end_frame"
                ],
                "duration_seconds": duration,
                "representative_frame": (
                    representative
                ),
            },
        )

        states.append(
            WorldState(
                time_seconds=float(
                    scene["start_time"]
                ),
                objects=[anchor],
            )
        )

    return PhysicalWorld(
        source_path=raw.get(
            "source_path",
            "",
        ),
        fps=float(
            raw.get("fps", 0.0)
        ),
        states=states,
        metadata={
            "representation_version": "1",
            "scene_count": len(
                raw.get("scenes", [])
            ),
            "object_semantics": (
                "placeholder"
            ),
        },
    )


def save_world(
    world: PhysicalWorld,
    output: str | Path,
) -> Path:
    """Persist a structured physical world."""

    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            world.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path
