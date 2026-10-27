"""Autonomous execution loop for Barrot."""

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
You are Barrot, operating a real Python repository in Termux.

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

- Commands are executed literally by /bin/sh.
- Every command must be a real shell command available in Termux/Linux.
- Never invent tools, functions, APIs, or commands.
- NEVER output Python function calls such as repo_browser.*.
- Use standard commands such as:
  pwd
  ls
  find
  grep
  cat
  sed
  git status
  git diff
  python
  pytest

- Do not modify files unless the goal explicitly requires modification.
- Do not expose or modify secrets.
- Do not restore Orbit or removed integrations.
- Keep actions minimal.
- Prefer inspection before modification.
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

                record["planning_error"] = (
                    "commands field is not a list"
                )

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
                and all(
                    item.get("success", False)
                    for item in record["execution"]
                )
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
