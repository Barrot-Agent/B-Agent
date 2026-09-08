from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class RepoCommandTool:
    """
    Execute approved repository commands from the repository root.
    """

    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root).resolve()

    def execute(
        self,
        command: str,
        timeout: int = 120,
    ) -> dict[str, Any]:
        result = subprocess.run(
            command,
            shell=True,
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            timeout=timeout,
        )

        output = "\n".join(
            part for part in [
                result.stdout.strip(),
                result.stderr.strip(),
            ]
            if part
        )

        return {
            "success": result.returncode == 0,
            "tool": "repo_command",
            "command": command,
            "returncode": result.returncode,
            "message": output or "Command completed successfully.",
        }
