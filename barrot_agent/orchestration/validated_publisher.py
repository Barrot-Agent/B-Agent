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
        allow_remote_push: bool = False,
    ) -> PublishResult:
        """Commit and push explicit paths only after a separate remote-write opt-in."""

        if allow_remote_push is not True:
            return PublishResult(
                success=False,
                committed=False,
                pushed=[],
                reason="Remote publishing is disabled; no Git mutation was attempted.",
            )

        workspace = self.workspace.resolve()
        normalized_paths = []

        for raw_path in paths:
            if not isinstance(raw_path, str) or not raw_path.strip():
                return PublishResult(False, False, [], "Every publish path must be a non-empty relative path.")
            candidate = Path(raw_path.strip())
            if candidate.is_absolute() or ".." in candidate.parts or candidate == Path("."):
                return PublishResult(False, False, [], f"Unsafe publish path rejected: {raw_path}")
            target = workspace / candidate
            if target.is_symlink():
                return PublishResult(False, False, [], f"Symbolic-link publish path rejected: {raw_path}")
            resolved = target.resolve()
            if workspace not in resolved.parents:
                return PublishResult(False, False, [], f"Publish path escapes the repository: {raw_path}")
            normalized = candidate.as_posix()
            if normalized not in normalized_paths:
                normalized_paths.append(normalized)

        if not normalized_paths:
            return PublishResult(
                success=True,
                committed=False,
                pushed=[],
                reason="No validated paths supplied.",
            )

        branch = self._run("branch", "--show-current")
        branch_name = branch.stdout.strip()
        if branch.returncode != 0 or not branch_name or branch_name in {"main", "master"}:
            return PublishResult(
                success=False,
                committed=False,
                pushed=[],
                reason="Remote publishing requires a named non-default feature branch.",
            )

        pre_staged = self._run("diff", "--cached", "--quiet")
        if pre_staged.returncode != 0:
            reason = "Pre-existing staged changes detected; they were preserved and not committed."
            if pre_staged.returncode not in {1}:
                reason = "Unable to verify the staged index; no commit or push was attempted."
            return PublishResult(False, False, [], reason)

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

        staged_names = self._run("diff", "--cached", "--name-only")
        if staged_names.returncode != 0:
            return PublishResult(False, False, [], "Unable to verify staged paths; no commit or push was attempted.")
        staged_paths = {line.strip() for line in staged_names.stdout.splitlines() if line.strip()}
        if not staged_paths.issubset(set(normalized_paths)):
            return PublishResult(False, False, [], "Staged index contains paths outside the explicit allowlist; no commit or push was attempted.")

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
