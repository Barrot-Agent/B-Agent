"""Autonomous execution loop for Barrot.

Model-proposed commands are passed through BarrotExecutor's argv allowlist.
They are never interpreted by a shell.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .executor import BarrotExecutor
from .verifier import BarrotVerifier


@dataclass
class AutonomousResult:
    success: bool
    attempts: int
    history: list[dict]


class BarrotAutonomousLoop:

    def __init__(
        self,
        brain,
        workspace: str = ".",
        max_attempts: int = 5,
    ):
        self.brain = brain
        self.executor = BarrotExecutor(workspace)
        self.verifier = BarrotVerifier(self.executor)
        self.max_attempts = max_attempts

    def _extract_json(self, text: str) -> dict:
        """Extract the first JSON object from a model response."""
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in Barrot response")
        return json.loads(match.group(0))

    def run(self, goal: str) -> AutonomousResult:
        history: list[dict] = []

        for attempt in range(1, self.max_attempts + 1):
            task = f"""
You are Barrot, operating a real Python repository in a controlled workspace.

GOAL:
{goal}

ATTEMPT:
{attempt}

Return ONLY valid JSON.

Use this exact schema:

{{
  "analysis": "brief diagnosis",
  "commands": [
    "find . -maxdepth 2 -type f",
    "python -m compileall -q barrot_agent scripts"
  ]
}}

CRITICAL EXECUTION RULES:

- Every command is parsed into argv and executed with shell=False.
- There is no shell, pipeline, redirection, command substitution, or command chaining.
- Use one command per string. Never include shell operators such as semicolon, &&, ||, pipe, >, <, backticks, or command substitution.
- Never invoke sh, bash, powershell, cmd, curl, wget, pip, npm, or arbitrary executables.
- Python is limited to python -m pytest with explicit test paths and python -m compileall -q barrot_agent scripts.
- pytest is limited to explicit in-workspace test paths and bounded read-only test options.
- Git is limited to git status --short and git diff --no-ext-diff, optionally with --stat.
- Read-only inspection commands may include pwd, ls, find, grep, cat, and numeric-range sed.
- File paths must remain inside the configured workspace.
- Do not modify files unless the goal explicitly requires modification.
- Do not expose or modify secrets.
- Do not restore Orbit or removed integrations.
- Keep actions minimal and prefer inspection before modification.
- If a command is rejected, inspect the error and choose an allowed command; do not attempt a shell workaround.
"""

            plan_text = self.brain.think(task)
            record = {
                "attempt": attempt,
                "plan": plan_text,
                "execution": [],
                "verification": [],
            }
            history.append(record)

            try:
                plan = self._extract_json(plan_text)
            except Exception as exc:
                record["planning_error"] = str(exc)
                continue

            commands = plan.get("commands", [])
            if not isinstance(commands, list):
                record["planning_error"] = "commands field is not a list"
                continue

            for command in commands:
                if not isinstance(command, str):
                    record["execution"].append(
                        {
                            "success": False,
                            "error": "Command was not a string",
                        }
                    )
                    continue

                try:
                    result = self.executor.run(command)
                    record["execution"].append(
                        {
                            "command": command,
                            "success": result.success,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "returncode": result.returncode,
                        }
                    )
                except Exception as exc:
                    record["execution"].append(
                        {
                            "command": command,
                            "success": False,
                            "error": str(exc),
                        }
                    )

            verification = self.verifier.verify_python()
            record["verification"] = verification.checks

            commands_ok = (
                len(record["execution"]) > 0
                and all(item.get("success", False) for item in record["execution"])
            )
            if commands_ok and verification.success:
                return AutonomousResult(
                    success=True,
                    attempts=attempt,
                    history=history,
                )

        return AutonomousResult(
            success=False,
            attempts=self.max_attempts,
            history=history,
        )
