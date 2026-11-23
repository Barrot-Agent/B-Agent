"""Select verified learning goals across Barrot's co-equal mission portfolio."""

from __future__ import annotations

from pathlib import Path

from .autonomous_state import AutonomousTaskStore
from .verified_learning_store import VerifiedLearningStore
from .mission_registry import MissionRegistry


class LearningCurriculum:
    """Choose validated goals without starving any co-equal mission."""

    CURSOR_TASK_ID = "mission_portfolio"
    CURSOR_SAVE_RETRIES = 3

    def __init__(
        self,
        workspace: str | Path | None = None,
        learning_store: VerifiedLearningStore | None = None,
        mission_registry: MissionRegistry | None = None,
    ):
        supplied_store = learning_store
        self.learning_store = learning_store or VerifiedLearningStore()
        if workspace is not None:
            self.workspace = Path(workspace).resolve()
        elif supplied_store is not None and getattr(supplied_store, "path", None) is not None:
            self.workspace = Path(supplied_store.path).resolve().parent
        else:
            self.workspace = Path(".").resolve()
        self.mission_registry = mission_registry or MissionRegistry()

    def _known_text(self) -> str:
        """Use only records that pass the store's current verification contract."""
        try:
            read_verified = getattr(self.learning_store, "read_verified", None)
            if not callable(read_verified):
                return ""
            records = read_verified()
        except Exception:
            return ""

        return "\n".join(
            record["lesson"]
            for record in records
            if isinstance(record, dict)
            and isinstance(record.get("lesson"), str)
        )

    def _next_portfolio_goal(self, known: str) -> str | None:
        """Advance a persistent round-robin cursor; corrupt state fails closed."""
        missions = self.mission_registry.portfolio_missions
        mission_ids = [mission["mission_id"] for mission in missions]
        if not mission_ids:
            return None

        cursor = AutonomousTaskStore(self.workspace)
        for _ in range(self.CURSOR_SAVE_RETRIES):
            state = cursor.load(self.CURSOR_TASK_ID) or {"history": []}
            history = state.get("history")
            if not isinstance(history, list):
                raise ValueError("mission portfolio cursor history must be a list")
            if len(history) > AutonomousTaskStore.MAX_HISTORY_ITEMS:
                raise ValueError("mission portfolio cursor history exceeds its retained limit")

            archived_count = state.get("history_archived_count", 0)
            if type(archived_count) is not int or archived_count < 0:
                raise ValueError("mission portfolio cursor archived history count is invalid")
            archive_digest = state.get("history_archive_digest")
            if archived_count:
                if (
                    not isinstance(archive_digest, str)
                    or len(archive_digest) != 64
                    or any(character not in "0123456789abcdef" for character in archive_digest)
                ):
                    raise ValueError("mission portfolio cursor archive digest is invalid")
                if not history:
                    raise ValueError("mission portfolio cursor retained history is missing")
            elif archive_digest not in (None, ""):
                raise ValueError("mission portfolio cursor has an archive digest without archived history")

            selection_count = state.get("selection_count", 0)
            if type(selection_count) is not int or selection_count < 0:
                raise ValueError("mission portfolio cursor selection count is invalid")
            if selection_count != archived_count + len(history):
                raise ValueError("mission portfolio cursor selection count does not match retained history")

            for offset, item in enumerate(history):
                if not isinstance(item, dict):
                    raise ValueError("mission portfolio cursor history entry is malformed")
                history_mission_id = item.get("mission_id")
                if history_mission_id not in mission_ids:
                    raise ValueError("mission portfolio cursor history references an unknown mission")
                expected_selection = archived_count + offset + 1
                if type(item.get("selection")) is not int or item["selection"] != expected_selection:
                    raise ValueError("mission portfolio cursor history selection sequence is invalid")

            last_selected = state.get("last_selected_mission_id")
            if history:
                if last_selected != history[-1]["mission_id"]:
                    raise ValueError("mission portfolio cursor last selected mission does not match history")
            elif last_selected is not None or selection_count != 0:
                raise ValueError("mission portfolio cursor has selections without retained history")

            start = (mission_ids.index(last_selected) + 1) % len(mission_ids) if last_selected else 0
            selected_goal = None
            selected_mission_id = None
            for offset in range(len(missions)):
                mission = missions[(start + offset) % len(missions)]
                goal = self.mission_registry.goal_for_mission(mission["mission_id"], known)
                if goal:
                    selected_goal = goal
                    selected_mission_id = mission["mission_id"]
                    break

            if selected_goal is None or selected_mission_id is None:
                return None

            next_state = dict(state)
            next_state["history"] = list(history) + [{
                "mission_id": selected_mission_id,
                "selection": selection_count + 1,
            }]
            next_state["last_selected_mission_id"] = selected_mission_id
            next_state["selection_count"] = selection_count + 1
            try:
                cursor.save(self.CURSOR_TASK_ID, next_state)
            except RuntimeError:
                # Another worker advanced the cursor after our read. Reload
                # and select the next mission; never overwrite its progress.
                continue
            return selected_goal

        raise RuntimeError(
            "mission portfolio cursor changed concurrently; retry the next run"
        )

    def next_goal(self) -> str:
        known = self._known_text().lower()
        manifest = self.mission_registry.manifest
        if manifest.get("status") == "active" and manifest.get("mission_portfolio"):
            mission_goal = self._next_portfolio_goal(known)
        else:
            mission_goal = self.mission_registry.next_goal(known)
        if mission_goal:
            return mission_goal

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
