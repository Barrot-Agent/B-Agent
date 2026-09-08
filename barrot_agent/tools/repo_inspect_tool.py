from __future__ import annotations

import hashlib
import os
from pathlib import Path


class RepoInspectTool:
    """Inspect the local Barrot repository using the real filesystem."""

    def __init__(self, root: str = ".") -> None:
        self.root = Path(root).resolve()

    def execute(
        self,
        target: str = ".",
        max_files: int = 250,
        include_content: bool = True,
    ) -> dict:
        requested = (self.root / target).resolve()

        if not requested.exists():
            return {
                "success": False,
                "message": f"Target does not exist: {target}",
            }

        try:
            requested.relative_to(self.root)
        except ValueError:
            return {
                "success": False,
                "message": "Target escapes repository root.",
            }

        files = []

        if requested.is_file():
            candidates = [requested]
        else:
            candidates = [
                p
                for p in requested.rglob("*")
                if p.is_file()
                and ".git" not in p.parts
                and "__pycache__" not in p.parts
                and ".pytest_cache" not in p.parts
            ]

        candidates = sorted(candidates)[:max_files]

        for file_path in candidates:
            relative = file_path.relative_to(self.root)
            info = {
                "path": str(relative),
                "bytes": file_path.stat().st_size,
            }

            if include_content:
                try:
                    content = file_path.read_text(errors="replace")
                    info["sha256"] = hashlib.sha256(
                        content.encode()
                    ).hexdigest()
                    info["content"] = content[:12000]
                except Exception as exc:
                    info["content_error"] = str(exc)

            files.append(info)

        return {
            "success": True,
            "tool": "repo_inspect",
            "root": str(self.root),
            "target": str(requested.relative_to(self.root)),
            "files_inspected": len(files),
            "files": files,
            "message": (
                f"Repository inspection completed. "
                f"Inspected {len(files)} file(s)."
            ),
        }
