"""Select progressively deeper repository learning goals for Barrot."""

from __future__ import annotations

from pathlib import Path

from .verified_learning_store import VerifiedLearningStore


class LearningCurriculum:
    """Choose repository learning goals that require deeper inspection."""

    def __init__(
        self,
        workspace: str = ".",
        learning_store: VerifiedLearningStore | None = None,
    ):
        self.workspace = Path(workspace)
        self.learning_store = (
            learning_store
            or VerifiedLearningStore()
        )

    def _known_text(self) -> str:
        try:
            records = self.learning_store.read_all()
        except Exception:
            return ""

        return "\n".join(
            str(record.get("lesson", ""))
            for record in records
        )

    def next_goal(self) -> str:
        known = self._known_text().lower()

        candidates = [
            (
                "autonomous_actions.py",
                (
                    "Read barrot_agent/orchestration/"
                    "autonomous_actions.py and identify how planning, "
                    "action execution, verification, rollback, outcome "
                    "evaluation, and learning are connected. "
                    "Use READ_FILE. Do not modify files."
                ),
            ),
            (
                "action_executor",
                (
                    "Inspect the Barrot action executor implementation "
                    "using READ_FILE and identify which action types can "
                    "change repository state and which are inspection-only. "
                    "Do not modify files."
                ),
            ),
            (
                "verification",
                (
                    "Inspect the Barrot verification implementation using "
                    "READ_FILE or SEARCH_TEXT. Identify what conditions "
                    "must pass before an autonomous attempt is accepted. "
                    "Do not modify files."
                ),
            ),
            (
                "repair_loop",
                (
                    "Read the Barrot repair loop and identify how failures "
                    "are retried or repaired. Use READ_FILE. "
                    "Do not modify files."
                ),
            ),
            (
                "outcome_evaluator",
                (
                    "Read the outcome evaluator and identify the criteria "
                    "used to classify autonomous attempts as successful "
                    "or unsuccessful. Use READ_FILE. "
                    "Do not modify files."
                ),
            ),
            (
                "shared_inference",
                (
                    "Inspect shared inference modules using READ_FILE and "
                    "identify how inference requests move through the "
                    "Barrot architecture. Do not modify files."
                ),
            ),
            (
                "tests",
                (
                    "Inspect repository tests using SEARCH_TEXT or "
                    "READ_FILE and identify one verification area that "
                    "has coverage and one that may need more coverage. "
                    "Do not modify files."
                ),
            ),
        ]

        for topic, goal in candidates:
            if topic.lower() not in known:
                return goal

        return (
            "Use SEARCH_TEXT and READ_FILE to inspect an architectural "
            "area of the repository not represented by the existing "
            "verified lessons. Identify one concrete relationship between "
            "two modules. Do not modify files."
        )
