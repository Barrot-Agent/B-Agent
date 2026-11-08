"""Goal-driven verified repair loop for Barrot."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .actions import parse_actions
from .action_executor import BarrotActionExecutor
from .outcome_evaluator import OutcomeEvaluator


@dataclass
class RepairResult:
    success: bool
    attempts: int
    history: list[dict]


class BarrotRepairLoop:
    """Inspect, repair, verify, rollback on failure, and retry."""

    def __init__(
        self,
        brain,
        workspace: str = ".",
        max_attempts: int = 3,
    ):
        self.brain = brain
        self.actions = BarrotActionExecutor(workspace)
        self.max_attempts = max_attempts
        self.outcome_evaluator = OutcomeEvaluator()

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        start = text.find("{")
        end = text.rfind("}")

        if start < 0 or end < start:
            raise ValueError("No JSON object found")

        return json.loads(text[start:end + 1])

    def run(
        self,
        goal: str,
        verification_command: str,
    ) -> RepairResult:

        history: list[dict] = []

        for attempt in range(1, self.max_attempts + 1):

            previous = ""

            if history:
                previous = json.dumps(
                    history[-1],
                    default=str,
                )[-6000:]

            prompt = f"""
You are the Barrot autonomous repository repair engineer.

GOAL:
{goal}

REQUIRED VERIFICATION COMMAND:
{verification_command}

ATTEMPT:
{attempt}

PREVIOUS ATTEMPT:
{previous}

Return JSON only.

Schema:

{{
  "analysis": "brief diagnosis",
  "actions": [
    {{
      "type": "READ_FILE",
      "args": {{
        "path": "example.py"
      }}
    }}
  ]
}}

Allowed actions:

LIST_FILES
READ_FILE
SEARCH_TEXT
RUN_TESTS
WRITE_FILE
APPLY_PATCH
GIT_STATUS

Rules:

- Never invent action names.
- Never output shell commands.
- Never expose secrets.
- Never modify secrets.
- Do not restore Orbit.
- Inspect before modifying.
- Keep edits minimal.
- Prefer APPLY_PATCH.
- Do not modify unrelated files.
- Do not claim the repair succeeded.
- The repair succeeds only if the required verification command passes.
"""

            response = self.brain.think(prompt)

            record = {
                "attempt": attempt,
                "plan": response,
                "results": [],
            }

            history.append(record)

            try:
                payload = self._parse_json(response)
                actions = parse_actions(payload)

            except Exception as exc:
                record["planning_error"] = str(exc)
                continue

            snapshots: dict[str, str] = {}

            for action in actions:

                if action.type in {
                    "WRITE_FILE",
                    "APPLY_PATCH",
                }:
                    path = action.args.get("path")

                    if isinstance(path, str):
                        try:
                            snapshots[path] = (
                                self.actions.executor.read_file(path)
                            )
                        except FileNotFoundError:
                            snapshots[path] = ""

                result = self.actions.execute(action)

                record["results"].append(
                    {
                        "action": result.action,
                        "success": result.success,
                        "output": result.output[-4000:],
                        "error": result.error[-4000:],
                    }
                )

                if not result.success:
                    break

            verification = self.actions.executor.run(
                verification_command
            )

            record["verification"] = {
                "command": verification.command,
                "success": verification.success,
                "stdout": verification.stdout[-4000:],
                "stderr": verification.stderr[-4000:],
            }

            outcome = self.outcome_evaluator.evaluate(
                results=record["results"],
                verification_success=verification.success,
            )
            record["outcome"] = {
                "success": outcome.success,
                "reason": outcome.reason,
            }

            if outcome.success:
                return RepairResult(
                    success=True,
                    attempts=attempt,
                    history=history,
                )

            rollback = []

            for path, original in snapshots.items():
                try:
                    self.actions.executor.write_file(
                        path,
                        original,
                    )

                    rollback.append(
                        {
                            "path": path,
                            "success": True,
                        }
                    )

                except Exception as exc:
                    rollback.append(
                        {
                            "path": path,
                            "success": False,
                            "error": str(exc),
                        }
                    )

            if rollback:
                record["rollback"] = rollback

        return RepairResult(
            success=False,
            attempts=self.max_attempts,
            history=history,
        )
