"""
Barrot Cinematic Production System.

The intelligence and continuity layer for AI-assisted film production.
"""

from .project_manager import CinematicProject, ProjectManager
from .story_bible import StoryBible
from .character_registry import CharacterRegistry
from .continuity_engine import ContinuityEngine, ContinuityConflict
from .scene_planner import ScenePlanner
from .shot_director import ShotDirector
from .asset_registry import AssetRegistry
from .production_pipeline import ProductionPipeline

__all__ = [
    "CinematicProject",
    "ProjectManager",
    "StoryBible",
    "CharacterRegistry",
    "ContinuityEngine",
    "ContinuityConflict",
    "ScenePlanner",
    "ShotDirector",
    "AssetRegistry",
    "ProductionPipeline",
]
