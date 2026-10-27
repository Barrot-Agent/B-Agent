from __future__ import annotations

from pathlib import Path
from typing import Any

from barrot_agent.tools.drop_router import DropRouter


class FileDropTool:
    """
    Barrot tool interface for deterministic repository-local file drops.

    This wrapper converts a Barrot task/tool request into a verified
    DropRouter operation.
    """

    name = "file_drop"

    def __init__(self, repository_root: str | Path):
        self.repository_root = Path(repository_root).resolve()
        self.router = DropRouter(self.repository_root)

    def execute(
        self,
        source: str,
        destination: str,
        overwrite: bool = False,
    ) -> dict[str, Any]:

        result = self.router.drop(
            source=source,
            destination=destination,
            overwrite=overwrite,
        )

        return {
            "success": result.success,
            "tool": self.name,
            "action": result.action,
            "source": result.source,
            "destination": result.destination,
            "message": result.message,
            "checksum": result.checksum,
        }

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": (
                "Moves a file into an approved repository-local destination "
                "and verifies the completed drop with SHA-256."
            ),
            "parameters": {
                "source": {
                    "type": "string",
                    "required": True,
                },
                "destination": {
                    "type": "string",
                    "required": True,
                },
                "overwrite": {
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
            },
        }
