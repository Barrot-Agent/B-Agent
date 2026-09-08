"""Structured autonomous repository action loop for Barrot."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .actions import parse_actions
from .action_executor import BarrotActionExecutor
from .verifier import BarrotVerifier
from .outcome_evaluator import OutcomeEvaluator


@dataclass
class AutonomousActionResult:
    success: bool
    attempts: int
    history: list[dict]


class BarrotActionLoop:
    """Plan, execute structured actions, verify, and retry."""

    def __init__(
        self,
        brain,
        workspace: str = ".",
        max_attempts: int = 3,
    ):
        self.brain = brain
        self.actions = BarrotActionExecutor(workspace)
        self.verifier = BarrotVerifier(self.actions.executor)
        self.max_attempts = max_attempts
        self.outcome_evaluator = OutcomeEvaluator()

    @staticmethod
    def _parse_json(response: str) -> dict:
        """Extract a JSON object from model output."""
        response = response.strip()

        if response.startswith("```"):
            response = response.split("\n", 1)[1]
            response = response.rsplit("```", 1)[0].strip()

        start = response.find("{")
        end = response.rfind("}")

        if start < 0 or end < start:
            raise ValueError("No JSON object found in model response")

        return json.loads(response[start : end + 1])

    def run(self, goal: str) -> AutonomousActionResult:
        history: list[dict] = []

        for attempt in range(1, self.max_attempts + 1):
            previous = ""

            if history:
                previous = json.dumps(
                    history[-1],
                    default=str,
                )[-6000:]

            prompt = f"""
You are the Barrot autonomous repository engineer.

GOAL:
{goal}

ATTEMPT:
{attempt}

PREVIOUS RESULT:
{previous}

Return JSON only.

Required schema:

{{
  "analysis": "brief diagnosis",
  "actions": [
    {{
      "type": "LIST_FILES",
      "args": {{}}
    }}
  ]
}}

Allowed action types only:

- LIST_FILES
- READ_FILE
- SEARCH_TEXT
- RUN_TESTS
- WRITE_FILE
- APPLY_PATCH
- GIT_STATUS

Action rules:

- Never invent action names.
- Never output shell commands.
- Never expose secrets.
- Never modify secrets.
- Do not restore Orbit.
- Prefer inspection before modification.
- Keep changes minimal.
- Use APPLY_PATCH for small edits.
- Run verification after modification.
- If the previous attempt failed, inspect the failure and correct it.
- Do not claim success without verification.
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
                if action.type in {"WRITE_FILE", "APPLY_PATCH"}:
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

            verification = self.verifier.verify_python()

            record["verification"] = verification.checks

            outcome = self.outcome_evaluator.evaluate(
                results=record["results"],
                verification_success=verification.success,
            )
            record["outcome"] = {
                "success": outcome.success,
                "reason": outcome.reason,
            }

            if outcome.success:
                return AutonomousActionResult(
                    success=True,
                    attempts=attempt,
                    history=history,
                )

            if snapshots:
                rollback_results = []

                for path, original in snapshots.items():
                    try:
                        self.actions.executor.write_file(
                            path,
                            original,
                        )

                        rollback_results.append(
                            {
                                "path": path,
                                "success": True,
                            }
                        )

                    except Exception as exc:
                        rollback_results.append(
                            {
                                "path": path,
                                "success": False,
                                "error": str(exc),
                            }
                        )

                record["rollback"] = rollback_results

        return AutonomousActionResult(
            success=False,
            attempts=self.max_attempts,
            history=history,
        )
