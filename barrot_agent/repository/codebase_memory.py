"""Codebase Memory integration and safe GitHub repository synchronization.

This module delegates structural indexing to the optional, MIT-licensed
codebase-memory-mcp executable. It never edits source files or performs
Git pull, checkout, reset, merge, push, or ref deletion operations.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit


class CodebaseMemoryError(RuntimeError):
    """Raised when the optional Codebase Memory executable cannot complete a call."""


class CodebaseMemoryClient:
    """Small, allowlisted CLI client for Codebase Memory's documented MCP tools."""

    SAFE_TOOLS = frozenset(
        {
            "index_repository",
            "list_projects",
            "index_status",
            "check_index_coverage",
            "search_graph",
            "search_code",
            "trace_path",
            "detect_changes",
            "query_graph",
            "get_graph_schema",
            "get_code_snippet",
            "get_file_outline",
            "get_architecture",
            "compare_graphs",
        }
    )

    def __init__(
        self,
        repo_root: str | Path,
        binary: str | None = None,
        timeout_seconds: int = 900,
        runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        self.binary = binary or os.environ.get(
            "BARROT_CODEBASE_MEMORY_BIN", "codebase-memory-mcp"
        )
        if not self.binary or "\x00" in self.binary:
            raise ValueError("Codebase Memory executable must be a valid command name.")
        if not self.repo_root.is_dir():
            raise ValueError(f"Repository root does not exist: {self.repo_root}")
        if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 1800:
            raise ValueError("timeout_seconds must be between 1 and 1800.")
        self.timeout_seconds = timeout_seconds
        self._runner = runner or subprocess.run

    def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Invoke one explicitly allowlisted Codebase Memory CLI tool."""
        if tool_name not in self.SAFE_TOOLS:
            raise ValueError(f"Codebase Memory tool is not allowlisted: {tool_name}")

        payload = dict(arguments or {})
        if not all(isinstance(key, str) for key in payload):
            raise ValueError("Tool argument names must be strings.")

        if tool_name == "index_repository":
            requested_root = payload.pop("repo_path", str(self.repo_root))
            if Path(requested_root).expanduser().resolve() != self.repo_root:
                raise ValueError("Indexing is restricted to the configured repository root.")
            payload["repo_path"] = str(self.repo_root)
            payload.setdefault("mode", "full")
            payload.setdefault("persistence", False)
            if payload["mode"] not in {"full", "moderate", "fast"}:
                raise ValueError("Index mode must be full, moderate, or fast.")
            if payload["persistence"] is not False:
                raise ValueError("Shared graph artifact persistence is disabled by default.")

        command = [self.binary, "cli", tool_name, "--format", "json"]
        try:
            completed = self._runner(
                command,
                cwd=str(self.repo_root),
                input=json.dumps(payload, separators=(",", ":"), sort_keys=True),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise CodebaseMemoryError(
                "codebase-memory-mcp is not installed or not on PATH. "
                "Install the pinned, checksum-verified upstream release first."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise CodebaseMemoryError(
                f"Codebase Memory tool '{tool_name}' timed out after "
                f"{self.timeout_seconds} seconds."
            ) from exc
        except OSError as exc:
            raise CodebaseMemoryError(f"Could not start Codebase Memory: {exc}") from exc

        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "no diagnostic output").strip()
            raise CodebaseMemoryError(
                f"Codebase Memory tool '{tool_name}' failed "
                f"(exit {completed.returncode}): {detail[-4000:]}"
            )

        output = (completed.stdout or "").strip()
        if not output:
            raise CodebaseMemoryError(
                f"Codebase Memory tool '{tool_name}' returned no JSON output."
            )
        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise CodebaseMemoryError(
                f"Codebase Memory tool '{tool_name}' returned invalid JSON."
            ) from exc


@dataclass(frozen=True)
class RepositorySyncResult:
    """Auditable outcome of a fetch-and-index pass."""

    repository_root: str
    branch: str
    head_sha: str
    remote_url: str
    remote_branch: str
    remote_sha: str
    ahead: int | None
    behind: int | None
    working_tree_dirty: bool
    fetch_succeeded: bool
    index_succeeded: bool
    index_result: Any = None
    error: str = ""

    @property
    def synchronized(self) -> bool:
        return bool(
            self.fetch_succeeded
            and self.index_succeeded
            and self.branch == self.remote_branch
            and self.head_sha
            and self.head_sha == self.remote_sha
            and not self.working_tree_dirty
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["synchronized"] = self.synchronized
        return result


class RepositorySyncController:
    """Fetch remote-tracking metadata and refresh the local code graph safely.

    Fetch updates only Git's object database and remote-tracking metadata. The
    checked-out branch and working tree are never changed.
    """

    def __init__(
        self,
        repo_root: str | Path,
        indexer: CodebaseMemoryClient,
        git_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        if not self.repo_root.is_dir():
            raise ValueError(f"Repository root does not exist: {self.repo_root}")
        self.indexer = indexer
        self._git_runner = git_runner or subprocess.run

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self._git_runner(
            ["git", "-C", str(self.repo_root), *args],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

    @staticmethod
    def _text(result: subprocess.CompletedProcess[str], operation: str) -> str:
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "unknown Git error").strip()
            raise CodebaseMemoryError(f"Git {operation} failed: {detail[-2000:]}")
        return (result.stdout or "").strip()

    def sync(self, default_branch: str = "main") -> RepositorySyncResult:
        """Fetch origin's default branch, then index the current checkout.

        This method deliberately does not pull or switch branches. A mismatch
        or dirty worktree is reported as not fully synchronized rather than
        silently overwritten.
        """
        if (
            not isinstance(default_branch, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", default_branch)
            or ".." in default_branch
            or "//" in default_branch
            or default_branch.endswith(("/", "."))
        ):
            raise ValueError("Invalid default branch name.")

        branch = self._text(self._git("branch", "--show-current"), "branch lookup")
        head_sha = self._text(self._git("rev-parse", "HEAD"), "HEAD lookup")
        dirty = bool(self._text(self._git("status", "--porcelain"), "status lookup"))
        remote_result = self._git("remote", "get-url", "origin")
        configured_remote = remote_result.stdout.strip() if remote_result.returncode == 0 else ""
        remote_url = ""
        remote_allowed = False
        if configured_remote:
            if configured_remote.startswith("git@github.com:"):
                remote_allowed = bool(
                    re.fullmatch(
                        r"git@github\.com:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?",
                        configured_remote,
                    )
                )
            elif configured_remote.startswith(("https://", "ssh://")):
                parsed_remote = urlsplit(configured_remote)
                remote_allowed = bool(
                    parsed_remote.hostname == "github.com"
                    and parsed_remote.username in (None, "git")
                    and parsed_remote.password is None
                    and not parsed_remote.query
                    and not parsed_remote.fragment
                    and re.fullmatch(
                        r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?",
                        parsed_remote.path,
                    )
                )
            if remote_allowed:
                remote_url = configured_remote

        fetch_succeeded = False
        remote_sha = ""
        ahead: int | None = None
        behind: int | None = None
        errors: list[str] = []

        if remote_allowed:
            fetch = self._git(
                "fetch",
                "--no-tags",
                "origin",
                f"refs/heads/{default_branch}:refs/remotes/origin/{default_branch}",
            )
            if fetch.returncode == 0:
                fetch_succeeded = True
                remote_ref = f"refs/remotes/origin/{default_branch}"
                remote_sha_result = self._git("rev-parse", "--verify", remote_ref)
                if remote_sha_result.returncode == 0:
                    remote_sha = remote_sha_result.stdout.strip()
                    counts = self._git("rev-list", "--left-right", "--count", f"HEAD...{remote_ref}")
                    if counts.returncode == 0:
                        fields = counts.stdout.split()
                        if len(fields) == 2 and all(value.isdigit() for value in fields):
                            ahead, behind = int(fields[0]), int(fields[1])
                        else:
                            errors.append("Git returned an invalid ahead/behind count.")
                    else:
                        errors.append((counts.stderr or "Could not compare local and remote refs.").strip())
                else:
                    errors.append((remote_sha_result.stderr or "Remote branch ref is unavailable.").strip())
            else:
                errors.append((fetch.stderr or "Git fetch failed.").strip())
        elif configured_remote:
            errors.append(
                "Origin is not an approved credential-free GitHub URL; remote fetch was blocked."
            )
        else:
            errors.append("No origin remote is configured; remote synchronization was not checked.")

        index_result: Any = None
        index_succeeded = False
        try:
            index_result = self.indexer.call_tool(
                "index_repository",
                {
                    "repo_path": str(self.repo_root),
                    "mode": "full",
                    "persistence": False,
                },
            )
            index_succeeded = True
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Index refresh failed: {exc}")

        return RepositorySyncResult(
            repository_root=str(self.repo_root),
            branch=branch,
            head_sha=head_sha,
            remote_url=remote_url,
            remote_branch=default_branch,
            remote_sha=remote_sha,
            ahead=ahead,
            behind=behind,
            working_tree_dirty=dirty,
            fetch_succeeded=fetch_succeeded,
            index_succeeded=index_succeeded,
            index_result=index_result,
            error="; ".join(error for error in errors if error),
        )
