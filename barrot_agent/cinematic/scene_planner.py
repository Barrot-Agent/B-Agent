from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class Scene:
    scene_id: str
    number: int
    title: str
    location: str
    time_of_day: str
    purpose: str
    characters: list[str] = field(default_factory=list)
    action: str = ""
    dialogue_summary: str = ""
    continuity_assertions: list[dict[str, Any]] = field(default_factory=list)


class ScenePlanner:
    def __init__(self) -> None:
        self.scenes: list[Scene] = []

    def create_scene(
        self,
        number: int,
        title: str,
        location: str,
        time_of_day: str,
        purpose: str,
        characters: list[str] | None = None,
        action: str = "",
        dialogue_summary: str = "",
        continuity_assertions: list[dict[str, Any]] | None = None,
    ) -> Scene:
        scene = Scene(
            scene_id=f"scene-{number}-{uuid.uuid4().hex[:8]}",
            number=number,
            title=title,
            location=location,
            time_of_day=time_of_day,
            purpose=purpose,
            characters=characters or [],
            action=action,
            dialogue_summary=dialogue_summary,
            continuity_assertions=continuity_assertions or [],
        )
        self.scenes.append(scene)
        self.scenes.sort(key=lambda item: item.number)
        return scene

    def get(self, number: int) -> Scene | None:
        return next((scene for scene in self.scenes if scene.number == number), None)

    def timeline(self) -> list[Scene]:
        return list(self.scenes)
