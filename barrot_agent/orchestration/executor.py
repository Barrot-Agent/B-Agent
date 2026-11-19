"""Controlled command executor for Barrot."""

from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExecutionResult:
    command: str
    success: bool
    stdout: str
    stderr: str
    returncode: int


class ExecutionError(RuntimeError):
    pass


class BarrotExecutor:
    """Execute repository commands inside controlled boundaries."""

    BLOCKED = (
        "rm -rf /",
        "rm -rf ~",
        "mkfs",
        "dd if=",
        ":(){",
        "shutdown",
        "reboot",
        "poweroff",
        "curl | sh",
        "wget | sh",
    )

    def __init__(self, workspace: str | Path | None = None):
        self.workspace = Path(
            workspace or os.getenv("BARROT_WORKSPACE", ".")
        ).resolve()

    def _validate(self, command: str) -> None:
        normalized = command.lower()

        if any(blocked in normalized for blocked in self.BLOCKED):
            raise ExecutionError(
                f"Blocked unsafe command: {command}"
            )

    def run(
        self,
        command: str,
        *,
        timeout: int = 120,
    ) -> ExecutionResult:
        """Run a shell command inside the configured workspace."""

        self._validate(command)

        completed = subprocess.run(
            command,
            shell=True,
            cwd=self.workspace,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return ExecutionResult(
            command=command,
            success=completed.returncode == 0,
            stdout=completed.stdout[-12000:],
            stderr=completed.stderr[-12000:],
            returncode=completed.returncode,
        )

    def read_file(self, path: str) -> str:
        target = (self.workspace / path).resolve()

        if self.workspace not in target.parents and target != self.workspace:
            raise ExecutionError("Path escapes workspace")

        return target.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> None:
        target = (self.workspace / path).resolve()

        if self.workspace not in target.parents:
            raise ExecutionError("Path escapes workspace")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
