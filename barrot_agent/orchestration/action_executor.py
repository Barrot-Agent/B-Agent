"""Execute validated Barrot structured actions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .actions import Action
from .executor import BarrotExecutor, ExecutionError


@dataclass
class ActionResult:
    action: str
    success: bool
    output: str = ""
    error: str = ""


class BarrotActionExecutor:
    """Execute only actions explicitly supported by the action protocol."""

    def __init__(self, workspace: str | Path = "."):
        self.executor = BarrotExecutor(workspace)

    def execute(self, action: Action) -> ActionResult:
        try:
            if action.type == "LIST_FILES":
                result = self.executor.run(
                    "find . -type f -not -path './.git/*' | sort"
                )
                return ActionResult(
                    action=action.type,
                    success=result.success,
                    output=result.stdout,
                    error=result.stderr,
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

                result = self.executor.run(
                    f"grep -RIn --exclude-dir=.git -- {query!r} {path!r}"
                )

                # grep exit code 1 means no matches, not executor failure.
                success = result.returncode in (0, 1)

                return ActionResult(
                    action=action.type,
                    success=success,
                    output=result.stdout,
                    error=result.stderr,
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
                old_text = action.args["old"]
                new_text = action.args["new"]

                if not isinstance(old_text, str) or not isinstance(new_text, str):
                    raise ExecutionError(
                        "APPLY_PATCH old and new values must be strings"
                    )

                current = self.executor.read_file(path)

                if old_text not in current:
                    raise ExecutionError(
                        f"Patch target was not found in {path}"
                    )

                if current.count(old_text) != 1:
                    raise ExecutionError(
                        f"Patch target must occur exactly once in {path}"
                    )

                updated = current.replace(old_text, new_text, 1)
                self.executor.write_file(path, updated)

                return ActionResult(
                    action=action.type,
                    success=True,
                    output=f"Patched {path}",
                )

            if action.type == "GIT_STATUS":
                result = self.executor.run("git status --short")

                return ActionResult(
                    action=action.type,
                    success=result.success,
                    output=result.stdout,
                    error=result.stderr,
                )

            raise ExecutionError(f"Action not implemented: {action.type}")

        except Exception as exc:
            return ActionResult(
                action=action.type,
                success=False,
                error=str(exc),
            )
