from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .project_manager import ProjectManager, CinematicProject
from .story_bible import StoryBible
from .character_registry import CharacterRegistry
from .continuity_engine import ContinuityEngine
from .scene_planner import ScenePlanner, Scene
from .shot_director import ShotDirector, Shot
from .asset_registry import AssetRegistry


class ProductionPipeline:
    """
    Unified interface for a Barrot cinematic production.

    This is the subsystem integration point for future LLM, image, video,
    voice, music, and editing adapters.
    """

    def __init__(self, project_root: str = "data/cinematic_projects") -> None:
        self.projects = ProjectManager(project_root)
        self.story = StoryBible()
        self.characters = CharacterRegistry()
        self.continuity = ContinuityEngine()
        self.scenes = ScenePlanner()
        self.shots = ShotDirector()
        self.assets = AssetRegistry()
        self.project: CinematicProject | None = None

    def start_project(
        self,
        name: str,
        premise: str,
        metadata: dict[str, Any] | None = None,
    ) -> CinematicProject:
        self.project = self.projects.create_project(name, premise, metadata)
        self.story.set_fact("premise", premise, locked=True)
        return self.project

    def add_scene(self, **kwargs: Any) -> Scene:
        scene = self.scenes.create_scene(**kwargs)

        conflicts = self.continuity.validate_scene(
            scene.scene_id,
            scene.continuity_assertions,
        )
        if conflicts:
            details = "; ".join(
                f"{c.subject}.{c.attribute}: "
                f"{c.established_value!r} -> {c.proposed_value!r}"
                for c in conflicts
            )
            raise ValueError(f"Continuity conflict in Scene {scene.number}: {details}")

        for assertion in scene.continuity_assertions:
            self.continuity.record(
                scene.scene_id,
                assertion["subject"],
                assertion["attribute"],
                assertion["value"],
            )

        return scene

    def add_shot(self, **kwargs: Any) -> Shot:
        return self.shots.create_shot(**kwargs)

    def production_status(self) -> dict[str, Any]:
        return {
            "project": self.project.to_dict() if self.project else None,
            "characters": len(self.characters.all_characters()),
            "scenes": len(self.scenes.scenes),
            "shots": len(self.shots.shots),
            "assets": len(self.assets.assets),
            "continuity_events": len(self.continuity.events),
            "ledger_valid": self.continuity.verify_integrity(),
        }

    def export_plan(self) -> dict[str, Any]:
        return {
            "project": self.project.to_dict() if self.project else None,
            "story_bible": self.story.facts(),
            "characters": [
                {
                    "name": character.name,
                    "attributes": character.attributes,
                    "relationships": character.relationships,
                    "history": character.history,
                }
                for character in self.characters.all_characters()
            ],
            "scenes": [asdict(scene) for scene in self.scenes.timeline()],
            "shots": [asdict(shot) for shot in self.shots.shots],
            "continuity_ledger": self.continuity.ledger(),
            "assets": [asdict(asset) for asset in self.assets.assets.values()],
        }
