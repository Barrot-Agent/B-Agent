"""Structured autonomous repository action loop for Barrot."""

from __future__ import annotations

from .bundle_delivery import BundleDelivery, deliver_bundle
from .bundle_validation import validate_python_bundle, BundleValidationError

import json
from dataclasses import dataclass

from .actions import parse_actions
from .action_executor import BarrotActionExecutor
from .verifier import BarrotVerifier
from .outcome_evaluator import OutcomeEvaluator
from .learning_filter import LearningFilter
from .verified_learning_store import VerifiedLearningStore
from .learning_curriculum import LearningCurriculum


def deliver_autonomous_bundle(
    executor,
    *,
    path: str,
    content: str,
):
    """Validate and deliver an approved Python bundle through TERMUX_DROP."""
    validation = validate_python_bundle(
        path=path,
        content=content,
    )

    if not validation.valid:
        raise BundleValidationError(
            validation.reason
        )

    result = deliver_bundle(
        executor,
        BundleDelivery(
            path=path,
            content=content,
        ),
    )

    return result


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
        self.learning_filter = LearningFilter()
        self.learning_store = VerifiedLearningStore()
        self.learning_curriculum = LearningCurriculum(
            workspace=workspace,
            learning_store=self.learning_store,
        )

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
- TERMUX_DROP

Action rules:

- Never invent action names.
- Never output shell commands.
- Never expose secrets.
- Never modify secrets.
- Do not restore Orbit.
- Prefer inspection before modification.
- Keep changes minimal.
- TERMUX_DROP may write only inside the configured Termux workspace.
- WRITE_FILE may create new files only; it cannot overwrite existing files.
- APPLY_PATCH requires one exact preimage match and uses compare-and-swap.
- RUN_TESTS accepts only allowlisted pytest/compileall commands; no shell.
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

            snapshots: dict[str, dict[str, object]] = {}

            for action in actions:
                snapshot = None
                path = action.args.get("path") if action.type in {"WRITE_FILE", "APPLY_PATCH"} else None
                if isinstance(path, str):
                    if path not in snapshots:
                        try:
                            before = self.actions.executor.read_file(path)
                        except FileNotFoundError:
                            before = None
                        snapshots[path] = {
                            "before": before,
                            "expected_after": before,
                            "applied": False,
                        }
                    snapshot = snapshots[path]
                    current = snapshot["expected_after"]
                    expected_after = None
                    if action.type == "WRITE_FILE":
                        proposed = action.args.get("content")
                        if current is None and isinstance(proposed, str):
                            expected_after = proposed
                    elif action.type == "APPLY_PATCH":
                        expected = action.args.get("expected")
                        replacement = action.args.get("replacement")
                        if (
                            isinstance(current, str)
                            and isinstance(expected, str)
                            and isinstance(replacement, str)
                            and expected in current
                            and current.count(expected) == 1
                        ):
                            expected_after = current.replace(expected, replacement, 1)
                    snapshot["pending_after"] = expected_after

                result = self.actions.execute(action)

                if snapshot is not None:
                    pending_after = snapshot.pop("pending_after", None)
                    if result.success and isinstance(pending_after, str):
                        snapshot["expected_after"] = pending_after
                        snapshot["applied"] = True

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
                learning = self.learning_filter.filter(
                    goal=goal,
                    results=record["results"],
                    verification_success=verification.success,
                )

                stored = False

                if learning.accepted:
                    stored = self.learning_store.append(learning)

                record["learning"] = {
                    "accepted": learning.accepted,
                    "stored": stored,
                    "lesson": learning.lesson,
                    "reason": learning.reason,
                }

                return AutonomousActionResult(
                    success=True,
                    attempts=attempt,
                    history=history,
                )

            if snapshots:
                rollback_results = []

                for path, snapshot in snapshots.items():
                    if not snapshot.get("applied"):
                        continue
                    original = snapshot.get("before")
                    expected_after = snapshot.get("expected_after")
                    try:
                        if not isinstance(expected_after, str):
                            raise RuntimeError("Missing exact post-action content; preserving current file.")
                        if original == expected_after:
                            rollback_results.append({"path": path, "success": True, "unchanged": True})
                            continue
                        self.actions.executor.restore_file(
                            path,
                            original if isinstance(original, str) or original is None else None,
                            expected_current_content=expected_after,
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

    def run_next_learning_goal(
        self,
    ) -> AutonomousActionResult:
        """Select and execute the next progressive learning goal."""

        goal = self.learning_curriculum.next_goal()

        return self.run(goal)
