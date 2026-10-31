from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re
import uuid


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return value.strip("-") or "untitled-project"


@dataclass
class CinematicProject:
    name: str
    premise: str
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "premise": self.premise,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


class ProjectManager:
    """Creates and loads isolated cinematic production projects."""

    DEFAULT_DIRECTORIES = (
        "bibles",
        "screenplay",
        "scenes",
        "shots",
        "assets",
        "ledger",
        "output",
    )

    def __init__(self, root: str | Path = "data/cinematic_projects"):
        self.root = Path(root)

    def create_project(
        self,
        name: str,
        premise: str,
        metadata: dict[str, Any] | None = None,
    ) -> CinematicProject:
        project = CinematicProject(
            name=name,
            premise=premise,
            metadata=metadata or {},
        )
        directory = self.project_path(project.name)
        directory.mkdir(parents=True, exist_ok=True)

        for child in self.DEFAULT_DIRECTORIES:
            (directory / child).mkdir(exist_ok=True)

        self.save_project(project)
        return project

    def project_path(self, name: str) -> Path:
        return self.root / _slugify(name)

    def save_project(self, project: CinematicProject) -> Path:
        directory = self.project_path(project.name)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "project.json"
        path.write_text(
            json.dumps(project.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def load_project(self, name: str) -> CinematicProject:
        path = self.project_path(name) / "project.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return CinematicProject(**data)
