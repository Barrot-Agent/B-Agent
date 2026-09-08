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

                return ActionResult(
                    action=action.type,
                    success=result.returncode in (0, 1),
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
                    raise ExecutionError(
                        "WRITE_FILE content must be a string"
                    )

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

                if not all(
                    isinstance(value, str)
                    for value in (path, expected, replacement)
                ):
                    raise ExecutionError(
                        "APPLY_PATCH path, expected, and replacement "
                        "must be strings"
                    )

                original = self.executor.read_file(path)

                if expected not in original:
                    raise ExecutionError(
                        f"Expected text not found in {path}"
                    )

                if original.count(expected) != 1:
                    raise ExecutionError(
                        f"Expected text is not unique in {path}"
                    )

                updated = original.replace(
                    expected,
                    replacement,
                    1,
                )

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

            raise ExecutionError(
                f"Action not implemented: {action.type}"
            )

        except Exception as exc:
            return ActionResult(
                action=action.type,
                success=False,
                error=str(exc),
            )
