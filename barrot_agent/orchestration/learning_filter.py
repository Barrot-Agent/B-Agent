"""Filter autonomous outcomes into verified reusable learning records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LearningRecord:
    accepted: bool
    lesson: str
    reason: str


class LearningFilter:
    """Accept only verified, non-trivial autonomous outcomes."""

    def filter(
        self,
        *,
        goal: str,
        results: list[dict[str, Any]],
        verification_success: bool,
    ) -> LearningRecord:

        if not results:
            return LearningRecord(
                accepted=False,
                lesson="",
                reason="No actions were executed.",
            )

        if any(
            not result.get("success", False)
            for result in results
        ):
            return LearningRecord(
                accepted=False,
                lesson="",
                reason="One or more actions failed.",
            )

        if not verification_success:
            return LearningRecord(
                accepted=False,
                lesson="",
                reason="Verification failed.",
            )

        actions = [
            str(result.get("action", "UNKNOWN"))
            for result in results
        ]

        # LIST_FILES alone is useful for navigation but is not deep learning.
        deep_actions = {
            "READ_FILE",
            "SEARCH_TEXT",
            "RUN_TESTS",
        }

        if not any(action in deep_actions for action in actions):
            return LearningRecord(
                accepted=False,
                lesson="",
                reason=(
                    "No deep inspection action succeeded. "
                    "Require READ_FILE, SEARCH_TEXT, or RUN_TESTS."
                ),
            )

        findings: list[str] = []

        for result in results:
            action = str(result.get("action", "UNKNOWN"))
            output = str(result.get("output", "")).strip()

            if not output:
                continue

            compact = " ".join(output.split())

            if len(compact) > 500:
                compact = compact[:500] + "..."

            findings.append(
                f"{action}: {compact}"
            )

        if not findings:
            return LearningRecord(
                accepted=False,
                lesson="",
                reason="Deep actions succeeded but produced no reusable findings.",
            )

        lesson = (
            f"Goal: {goal.strip()}\n"
            f"Verified findings:\n"
            + "\n".join(
                f"- {finding}"
                for finding in findings
            )
        )

        return LearningRecord(
            accepted=True,
            lesson=lesson,
            reason="Deep inspection actions and verification succeeded.",
        )
