from __future__ import annotations

import os
import shutil
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DropResult:
    success: bool
    source: str
    destination: Optional[str]
    action: str
    message: str
    checksum: Optional[str] = None


class DropRouter:
    """Deterministic repository-local file drop system."""

    def __init__(self, repository_root: str | Path):
        self.repository_root = Path(repository_root).resolve()

    def _inside_repository(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.repository_root)
            return True
        except ValueError:
            return False

    def _checksum(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _safe_destination(self, destination: str | Path) -> Path:
        destination_path = Path(destination)

        if not destination_path.is_absolute():
            destination_path = self.repository_root / destination_path

        destination_path = destination_path.resolve()

        if not self._inside_repository(destination_path):
            raise ValueError(
                f"Destination escapes repository root: {destination_path}"
            )

        return destination_path

    def drop(
        self,
        source: str | Path,
        destination: str | Path,
        overwrite: bool = False,
    ) -> DropResult:

        source_path = Path(source).expanduser().resolve()

        if not source_path.exists():
            return DropResult(
                False, str(source_path), None, "none",
                "Source does not exist."
            )

        if not source_path.is_file():
            return DropResult(
                False, str(source_path), None, "none",
                "Source is not a file."
            )

        try:
            destination_path = self._safe_destination(destination)
        except ValueError as error:
            return DropResult(
                False, str(source_path), None, "none", str(error)
            )

        if destination_path.suffix == "":
            destination_path.mkdir(parents=True, exist_ok=True)
            destination_path = destination_path / source_path.name
        else:
            destination_path.parent.mkdir(parents=True, exist_ok=True)

        if destination_path.exists() and not overwrite:
            return DropResult(
                False,
                str(source_path),
                str(destination_path),
                "none",
                "Destination already exists. Overwrite disabled.",
            )

        source_checksum = self._checksum(source_path)

        try:
            if source_path.stat().st_dev == destination_path.parent.stat().st_dev:
                os.replace(source_path, destination_path)
                action = "move"
            else:
                shutil.copy2(source_path, destination_path)

                if self._checksum(destination_path) != source_checksum:
                    destination_path.unlink(missing_ok=True)
                    return DropResult(
                        False,
                        str(source_path),
                        str(destination_path),
                        "copy",
                        "Checksum verification failed.",
                    )

                source_path.unlink()
                action = "copy-verify-delete"

        except Exception as error:
            return DropResult(
                False,
                str(source_path),
                str(destination_path),
                "none",
                str(error),
            )

        if not destination_path.exists():
            return DropResult(
                False,
                str(source_path),
                str(destination_path),
                action,
                "Destination verification failed.",
            )

        final_checksum = self._checksum(destination_path)

        if final_checksum != source_checksum:
            return DropResult(
                False,
                str(source_path),
                str(destination_path),
                action,
                "Final checksum verification failed.",
            )

        return DropResult(
            True,
            str(source_path),
            str(destination_path),
            action,
            "Drop completed and verified.",
            final_checksum,
        )
