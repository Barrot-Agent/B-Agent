"""Execute validated Barrot structured actions without shell interpolation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .actions import Action
from .executor import BarrotExecutor, ExecutionError
from barrot_agent.termux import TermuxBridge
from barrot_agent.orchestration.verified_bundle_delivery import deliver_verified_bundle


@dataclass
class ActionResult:
    action: str
    success: bool
    output: str = ""
    error: str = ""


class BarrotActionExecutor:
    """Execute only actions explicitly supported by the action protocol."""

    SKIP_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
    }
    MAX_SEARCH_FILE_BYTES = 2 * 1024 * 1024
    MAX_SEARCH_RESULTS = 200
    MAX_OUTPUT_CHARS = 12000

    def __init__(self, workspace: str | Path = "."):
        self.executor = BarrotExecutor(workspace)
        self.termux = TermuxBridge(
            allowed_roots=(
                str(Path(workspace).expanduser().resolve()),
            ),
        )

    def _resolve_action_path(self, value: object) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise ExecutionError("Action path must be a non-empty relative path.")
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise ExecutionError(f"Action path escapes workspace: {value}")
        target = (self.executor.workspace / relative).resolve()
        if target != self.executor.workspace and self.executor.workspace not in target.parents:
            raise ExecutionError(f"Action path escapes workspace: {value}")
        return target

    def _iter_files(self, root: Path):
        if root.is_file():
            if not root.is_symlink():
                yield root
            return
        if not root.is_dir():
            raise FileNotFoundError(str(root))
        for current, directories, filenames in os.walk(root, topdown=True, followlinks=False):
            current_path = Path(current)
            directories[:] = [
                name
                for name in directories
                if name not in self.SKIP_DIRECTORIES
                and not (current_path / name).is_symlink()
            ]
            for name in filenames:
                candidate = current_path / name
                if candidate.is_symlink() or not candidate.is_file():
                    continue
                yield candidate

    def _list_files(self) -> str:
        root = self.executor.workspace
        paths: list[str] = []
        for candidate in self._iter_files(root):
            paths.append(candidate.relative_to(root).as_posix())
            if len(paths) >= 5000:
                paths.append("[truncated after 5000 files]")
                break
        return "\n".join(sorted(paths))

    def _search_text(self, query: object, path: object) -> str:
        if not isinstance(query, str) or not query:
            raise ExecutionError("SEARCH_TEXT query must be a non-empty string.")
        root = self._resolve_action_path(path)
        matches: list[str] = []
        output_size = 0
        for candidate in self._iter_files(root):
            try:
                if candidate.stat().st_size > self.MAX_SEARCH_FILE_BYTES:
                    continue
                text = candidate.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            relative = candidate.relative_to(self.executor.workspace).as_posix()
            for line_number, line in enumerate(text.splitlines(), start=1):
                if query not in line:
                    continue
                item = f"{relative}:{line_number}:{line[:500]}"
                if len(matches) >= self.MAX_SEARCH_RESULTS or output_size + len(item) + 1 > self.MAX_OUTPUT_CHARS:
                    matches.append("[truncated search results]")
                    return "\n".join(matches)
                matches.append(item)
                output_size += len(item) + 1
        return "\n".join(matches)

    def execute(self, action: Action) -> ActionResult:
        try:
            if action.type == "LIST_FILES":
                return ActionResult(
                    action=action.type,
                    success=True,
                    output=self._list_files(),
                )

            if action.type == "READ_FILE":
                path = action.args["path"]
                return ActionResult(
                    action=action.type,
                    success=True,
                    output=self.executor.read_file(path),
                )

            if action.type == "SEARCH_TEXT":
                query = action.args["query"]
                path = action.args.get("path", ".")
                return ActionResult(
                    action=action.type,
                    success=True,
                    output=self._search_text(query, path),
                )

            if action.type == "RUN_TESTS":
                command = action.args["command"]
                result = self.executor.run(command)
                return ActionResult(
                    action=action.type,
                    success=result.success,
                    output=result.stdout,
                    error=result.stderr,
                )

            if action.type == "WRITE_FILE":
                path = action.args["path"]
                content = action.args["content"]
                if not isinstance(content, str):
                    raise ExecutionError("WRITE_FILE content must be a string")
                self.executor.write_file(path, content)
                return ActionResult(
                    action=action.type,
                    success=True,
                    output=f"Wrote {path}",
                )

            if action.type == "APPLY_PATCH":
                path = action.args["path"]
                expected = action.args["expected"]
                replacement = action.args["replacement"]
                if not all(isinstance(value, str) for value in (path, expected, replacement)):
                    raise ExecutionError(
                        "APPLY_PATCH path, expected, and replacement must be strings"
                    )
                original = self.executor.read_file(path)
                if expected not in original:
                    raise ExecutionError(f"Expected text not found in {path}")
                if original.count(expected) != 1:
                    raise ExecutionError(f"Expected text is not unique in {path}")
                updated = original.replace(expected, replacement, 1)
                self.executor.write_file(path, updated)
                return ActionResult(
                    action=action.type,
                    success=True,
                    output=f"Patched {path}",
                )

            if action.type == "GIT_STATUS":
                result = self.executor.run(["git", "status", "--short"])
                return ActionResult(
                    action=action.type,
                    success=result.success,
                    output=result.stdout,
                    error=result.stderr,
                )

            if action.type == "TERMUX_DROP":
                path = action.args["path"]
                content = action.args["content"]
                if not isinstance(path, str):
                    raise ExecutionError("TERMUX_DROP path must be a string")
                if not isinstance(content, str):
                    raise ExecutionError("TERMUX_DROP content must be a string")
                drop = self.termux.drop_text(path=path, content=content)
                return ActionResult(
                    action=action.type,
                    success=drop.success,
                    output=drop.path if drop.success else "",
                    error="" if drop.success else drop.reason,
                )

            if action.type == "DELIVER_BUNDLE":
                path = action.args["path"]
                content = action.args["content"]
                if not isinstance(path, str):
                    raise ExecutionError("DELIVER_BUNDLE path must be a string")
                if not isinstance(content, str):
                    raise ExecutionError("DELIVER_BUNDLE content must be a string")
                verified = deliver_verified_bundle(self, path=path, content=content)
                if not verified.delivery.success:
                    return ActionResult(
                        action=action.type,
                        success=False,
                        error=verified.delivery.error,
                    )
                if not verified.evidence.verified:
                    return ActionResult(
                        action=action.type,
                        success=False,
                        error=verified.evidence.reason,
                    )
                return ActionResult(
                    action=action.type,
                    success=True,
                    output=f"{verified.evidence.path} {verified.evidence.delivered_hash}",
                )

            raise ExecutionError(f"Action not implemented: {action.type}")

        except Exception as exc:
            return ActionResult(
                action=action.type,
                success=False,
                error=str(exc),
            )
