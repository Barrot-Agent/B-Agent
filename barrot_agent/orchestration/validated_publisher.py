"""Commit and publish explicitly validated repository changes."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PublishResult:
    success: bool
    committed: bool
    pushed: list[str]
    reason: str


class ValidatedPublisher:
    """Commit and publish only explicitly supplied repository paths."""

    def __init__(
        self,
        workspace: str = ".",
        remotes: tuple[str, ...] = (
            "origin",
            "gitlab",
        ),
    ):
        self.workspace = Path(workspace)
        self.remotes = remotes

    def _run(
        self,
        *args: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.workspace,
            text=True,
            capture_output=True,
            check=False,
        )

    def publish(
        self,
        *,
        paths: list[str],
        message: str,
    ) -> PublishResult:
        """Stage explicit paths, commit them, then push configured remotes."""

        normalized_paths = []

        for path in paths:
            candidate = str(path).strip()

            if candidate and candidate not in normalized_paths:
                normalized_paths.append(candidate)

        if not normalized_paths:
            return PublishResult(
                success=True,
                committed=False,
                pushed=[],
                reason="No validated paths supplied.",
            )

        add = self._run(
            "add",
            "--",
            *normalized_paths,
        )

        if add.returncode != 0:
            return PublishResult(
                success=False,
                committed=False,
                pushed=[],
                reason=add.stderr.strip(),
            )

        staged = self._run(
            "diff",
            "--cached",
            "--quiet",
        )

        if staged.returncode == 0:
            return PublishResult(
                success=True,
                committed=False,
                pushed=[],
                reason="Validated paths produced no staged changes.",
            )

        if staged.returncode not in {0, 1}:
            return PublishResult(
                success=False,
                committed=False,
                pushed=[],
                reason=staged.stderr.strip(),
            )

        commit = self._run(
            "commit",
            "-m",
            message,
        )

        if commit.returncode != 0:
            return PublishResult(
                success=False,
                committed=False,
                pushed=[],
                reason=commit.stderr.strip(),
            )

        pushed: list[str] = []

        for remote in self.remotes:
            push = self._run(
                "push",
                remote,
                "HEAD",
            )

            if push.returncode != 0:
                return PublishResult(
                    success=False,
                    committed=True,
                    pushed=pushed,
                    reason=(
                        f"Push to {remote} failed: "
                        f"{push.stderr.strip()}"
                    ),
                )

            pushed.append(remote)

        return PublishResult(
            success=True,
            committed=True,
            pushed=pushed,
            reason=(
                "Validated paths committed and pushed "
                "to configured remotes."
            ),
        )
