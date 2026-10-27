from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class Shot:
    shot_id: str
    scene_id: str
    number: int
    framing: str
    camera_movement: str
    action: str
    lighting: str = ""
    audio: str = ""
    visual_effects: str = ""
    generation_notes: dict[str, Any] = field(default_factory=dict)


class ShotDirector:
    """Converts scene intent into tool-neutral production specifications."""

    def __init__(self) -> None:
        self.shots: list[Shot] = []

    def create_shot(
        self,
        scene_id: str,
        number: int,
        framing: str,
        camera_movement: str,
        action: str,
        lighting: str = "",
        audio: str = "",
        visual_effects: str = "",
        generation_notes: dict[str, Any] | None = None,
    ) -> Shot:
        shot = Shot(
            shot_id=f"shot-{uuid.uuid4().hex[:12]}",
            scene_id=scene_id,
            number=number,
            framing=framing,
            camera_movement=camera_movement,
            action=action,
            lighting=lighting,
            audio=audio,
            visual_effects=visual_effects,
            generation_notes=generation_notes or {},
        )
        self.shots.append(shot)
        return shot

    def for_scene(self, scene_id: str) -> list[Shot]:
        return sorted(
            [shot for shot in self.shots if shot.scene_id == scene_id],
            key=lambda shot: shot.number,
        )

    def generation_prompt(self, shot: Shot) -> str:
        return (
            f"{shot.framing} shot. "
            f"Camera: {shot.camera_movement}. "
            f"Action: {shot.action}. "
            f"Lighting: {shot.lighting or 'production appropriate'}. "
            f"Visual effects: {shot.visual_effects or 'none specified'}."
        )
