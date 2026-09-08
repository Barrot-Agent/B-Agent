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
    """Accept only verified outcomes as reusable Barrot knowledge."""

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

        lesson = (
            f"Verified goal: {goal.strip()} "
            f"Successful actions: {', '.join(actions)}."
        )

        return LearningRecord(
            accepted=True,
            lesson=lesson,
            reason="Actions and verification succeeded.",
        )
