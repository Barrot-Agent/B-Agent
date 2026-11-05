"""Controlled command executor for Barrot.

Commands are parsed into argv and executed with shell=False. Only bounded,
read-only repository inspection, pytest, and compileall commands are accepted.
Model-generated shell pipelines, interpreters, package managers, network tools,
and repository mutations are rejected before process creation.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


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
    """Execute a narrow allowlist of repository-local commands without a shell."""

    ALLOWED_PROGRAMS = {
        "cat",
        "find",
        "git",
        "grep",
        "ls",
        "pwd",
        "python",
        "python3",
        "pytest",
        "sed",
    }
    PYTEST_FLAGS = {
        "-q",
        "-v",
        "-x",
        "--no-cov",
        "--disable-warnings",
        "--strict-markers",
        "--strict-config",
        "--collect-only",
    }
    PYTEST_VALUE_FLAGS = {"-k", "-m", "--maxfail", "--tb"}
    PYTEST_TB_VALUES = {"short", "long", "line", "no"}

    def __init__(self, workspace: str | Path | None = None):
        self.workspace = Path(
            workspace or os.getenv("BARROT_WORKSPACE", ".")
        ).resolve()

    def _workspace_path(self, value: str) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise ExecutionError("Command path must be a non-empty string.")
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise ExecutionError(f"Command path escapes workspace: {value}")
        target = (self.workspace / relative).resolve()
        if target != self.workspace and self.workspace not in target.parents:
            raise ExecutionError(f"Command path escapes workspace: {value}")
        return target

    def _validate_pytest_args(self, args: list[str]) -> None:
        if not args:
            raise ExecutionError("pytest requires an explicit in-workspace test path.")
        has_target = False
        index = 0
        while index < len(args):
            token = args[index]
            if token in self.PYTEST_FLAGS:
                index += 1
                continue
            if token in self.PYTEST_VALUE_FLAGS:
                if index + 1 >= len(args):
                    raise ExecutionError(f"pytest option requires a value: {token}")
                value = args[index + 1]
                if token == "--maxfail":
                    if not value.isdigit() or not 1 <= int(value) <= 10:
                        raise ExecutionError("pytest --maxfail must be between 1 and 10.")
                elif token == "--tb" and value not in self.PYTEST_TB_VALUES:
                    raise ExecutionError("Unsupported pytest traceback mode.")
                elif token in {"-k", "-m"} and not value.strip():
                    raise ExecutionError(f"pytest option requires a non-empty value: {token}")
                index += 2
                continue
            if token.startswith("--maxfail="):
                value = token.split("=", 1)[1]
                if not value.isdigit() or not 1 <= int(value) <= 10:
                    raise ExecutionError("pytest --maxfail must be between 1 and 10.")
                index += 1
                continue
            if token.startswith("--tb="):
                if token.split("=", 1)[1] not in self.PYTEST_TB_VALUES:
                    raise ExecutionError("Unsupported pytest traceback mode.")
                index += 1
                continue
            if token.startswith("-"):
                raise ExecutionError(f"Unsupported pytest option: {token}")
            path_part = token.split("::", 1)[0]
            self._workspace_path(path_part)
            has_target = True
            index += 1
        if not has_target:
            raise ExecutionError("pytest requires an explicit in-workspace test path.")

    def _validate_argv(self, argv: list[str]) -> None:
        if not argv or any(not isinstance(item, str) or "\x00" in item for item in argv):
            raise ExecutionError("Command argv must contain non-empty text arguments.")
        program = argv[0]
        if program not in self.ALLOWED_PROGRAMS or "/" in program or "\\" in program:
            raise ExecutionError(f"Unsupported executable: {program}")

        args = argv[1:]
        if program in {"python", "python3"}:
            if args[:3] == ["-m", "compileall", "-q"]:
                paths = args[3:]
                if not paths or any(path not in {"barrot_agent", "scripts", "tests"} for path in paths):
                    raise ExecutionError("compileall is limited to barrot_agent, scripts, and tests.")
                return
            if args[:2] == ["-m", "pytest"]:
                self._validate_pytest_args(args[2:])
                return
            raise ExecutionError("Python execution is limited to pytest and compileall modules.")

        if program == "pytest":
            self._validate_pytest_args(args)
            return

        if program == "git":
            if args in (["status"], ["status", "--short"]):
                return
            if args in (
                ["diff", "--no-ext-diff"],
                ["diff", "--no-ext-diff", "--stat"],
            ):
                return
            if len(args) >= 4 and args[:3] == ["diff", "--no-ext-diff", "--"]:
                for path in args[3:]:
                    self._workspace_path(path)
                return
            raise ExecutionError("Git is limited to status and non-external read-only diff commands.")

        if program == "pwd":
            if args:
                raise ExecutionError("pwd accepts no arguments.")
            return

        if program == "ls":
            for item in args:
                if item in {"-a", "-l", "-la", "-al"}:
                    continue
                self._workspace_path(item)
            return

        if program == "find":
            if len(args) not in {5, 6, 9} or args[0] != ".":
                raise ExecutionError("find is limited to bounded workspace listings.")
            if args[1] != "-maxdepth" or not args[2].isdigit() or not 1 <= int(args[2]) <= 8:
                raise ExecutionError("find requires -maxdepth between 1 and 8.")
            if args[3] != "-type" or args[4] not in {"f", "d"}:
                raise ExecutionError("find is limited to -type f or -type d.")
            if len(args) == 9 and args[5:] != ["-not", "-path", "./.git/*"]:
                raise ExecutionError("Unsupported find predicate.")
            if len(args) == 6:
                raise ExecutionError("Unsupported find predicate.")
            return

        if program == "grep":
            if len(args) != 5 or args[0] != "-RIn" or args[1] != "--exclude-dir=.git" or args[2] != "--":
                raise ExecutionError("grep is limited to recursive, read-only workspace searches.")
            if not args[3]:
                raise ExecutionError("grep pattern must be non-empty.")
            self._workspace_path(args[4])
            return

        if program == "cat":
            if not args:
                raise ExecutionError("cat requires an in-workspace file path.")
            for path in args:
                self._workspace_path(path)
            return

        if program == "sed":
            if len(args) != 3 or args[0] != "-n":
                raise ExecutionError("sed is limited to read-only line-range printing.")
            if not re.fullmatch(r"[1-9][0-9]*(,[1-9][0-9]*)?p", args[1]):
                raise ExecutionError("sed accepts only a numeric print range.")
            self._workspace_path(args[2])
            return

        raise ExecutionError(f"Unsupported command: {program}")

    def _parse_command(self, command: str | Sequence[str]) -> list[str]:
        if isinstance(command, str):
            if not command.strip():
                raise ExecutionError("Command must be non-empty.")
            try:
                argv = shlex.split(command, posix=True)
            except ValueError as exc:
                raise ExecutionError(f"Command quoting is invalid: {exc}") from exc
        elif isinstance(command, (list, tuple)):
            argv = list(command)
        else:
            raise ExecutionError("Command must be a string or argv sequence.")
        self._validate_argv(argv)
        return argv

    def _validate(self, command: str | Sequence[str]) -> list[str]:
        """Validate a command and return its shell-free argv representation."""
        return self._parse_command(command)

    def run(
        self,
        command: str | Sequence[str],
        *,
        timeout: int = 120,
    ) -> ExecutionResult:
        """Run an allowlisted command with shell execution disabled."""
        if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 600:
            raise ExecutionError("Command timeout must be an integer between 1 and 600 seconds.")
        argv = self._parse_command(command)
        display = command if isinstance(command, str) else shlex.join(argv)
        try:
            completed = subprocess.run(
                argv,
                shell=False,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            return ExecutionResult(
                command=display,
                success=False,
                stdout=stdout[-12000:],
                stderr=(stderr + f"\nCommand timed out after {timeout}s")[-12000:],
                returncode=124,
            )

        return ExecutionResult(
            command=display,
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
