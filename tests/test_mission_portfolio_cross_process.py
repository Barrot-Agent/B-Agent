from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

_SELECT_GOAL = """
import os
from pathlib import Path

from barrot_agent.orchestration.learning_curriculum import LearningCurriculum
from barrot_agent.orchestration.verified_learning_store import VerifiedLearningStore

workspace = Path(os.environ["BARROT_TEST_WORKSPACE"])
store = VerifiedLearningStore(workspace / "verified_lessons.jsonl")
goal = LearningCurriculum(workspace=workspace, learning_store=store).next_goal()
print(goal)
"""


def _select_goal_in_fresh_process(workspace: Path) -> str:
    env = os.environ.copy()
    env["BARROT_TEST_WORKSPACE"] = str(workspace)
    env["PYTHONPATH"] = os.pathsep.join(
        value for value in (str(ROOT), env.get("PYTHONPATH", "")) if value
    )
    result = subprocess.run(
        [sys.executable, "-c", _SELECT_GOAL],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    return result.stdout.strip()


def _topic_id(goal: str) -> str:
    match = re.search(r"MISSION_TOPIC_ID:\s*([A-Za-z0-9_]+)", goal)
    assert match is not None, goal
    return match.group(1)


def test_mission_round_robin_cursor_recovers_across_fresh_processes(
    tmp_path: Path,
) -> None:
    selected_topics = [
        _topic_id(_select_goal_in_fresh_process(tmp_path))
        for _ in range(4)
    ]

    assert selected_topics == [
        "xrp_source_provenance",
        "audio_capability_inventory",
        "continuity_versioned_state_model",
        "xrp_source_provenance",
    ]

    cursor_path = (
        tmp_path / ".barrot" / "autonomous_tasks" / "mission_portfolio.json"
    )
    cursor = json.loads(cursor_path.read_text(encoding="utf-8"))
    assert cursor["selection_count"] == 4
    assert cursor["last_selected_mission_id"] == "xrp_intelligence_prediction_engine"
    assert [
        item["mission_id"] for item in cursor["history"][-4:]
    ] == [
        "xrp_intelligence_prediction_engine",
        "professional_audio_production",
        "long_horizon_continuity_capability_development",
        "xrp_intelligence_prediction_engine",
    ]



def _mission_cursor_store(workspace: Path) -> AutonomousTaskStore:
    from barrot_agent.orchestration.autonomous_state import AutonomousTaskStore

    return AutonomousTaskStore(workspace)


def _curriculum_for_workspace(workspace: Path) -> LearningCurriculum:
    from barrot_agent.orchestration.verified_learning_store import VerifiedLearningStore

    return LearningCurriculum(
        workspace=workspace,
        learning_store=VerifiedLearningStore(workspace / "verified_lessons.jsonl"),
    )


import pytest


@pytest.mark.parametrize(
    ("history", "overrides", "message"),
    [
        (
            [{"mission_id": "unknown_mission", "selection": 1}],
            {"last_selected_mission_id": "unknown_mission", "selection_count": 1},
            "history references an unknown mission",
        ),
        (
            [{"mission_id": "xrp_intelligence_prediction_engine", "selection": 1}],
            {"last_selected_mission_id": "xrp_intelligence_prediction_engine", "selection_count": 2},
            "selection count does not match retained history",
        ),
        (
            [{"mission_id": "xrp_intelligence_prediction_engine", "selection": 2}],
            {"last_selected_mission_id": "xrp_intelligence_prediction_engine", "selection_count": 1},
            "selection sequence is invalid",
        ),
        (
            [{"mission_id": "xrp_intelligence_prediction_engine", "selection": 1}],
            {"last_selected_mission_id": "professional_audio_production", "selection_count": 1},
            "last selected mission does not match history",
        ),
    ],
)
def test_mission_cursor_rejects_inconsistent_persisted_history(
    tmp_path: Path,
    history: list[dict],
    overrides: dict,
    message: str,
) -> None:
    state = {"history": history, **overrides}
    _mission_cursor_store(tmp_path).save("mission_portfolio", state)

    with pytest.raises(ValueError, match=message):
        _curriculum_for_workspace(tmp_path).next_goal()


def test_mission_cursor_rejects_malformed_archive_digest(tmp_path: Path) -> None:
    _mission_cursor_store(tmp_path).save(
        "mission_portfolio",
        {
            "history": [{"mission_id": "xrp_intelligence_prediction_engine", "selection": 6}],
            "history_archived_count": 5,
            "history_archive_digest": "not-a-sha256",
            "last_selected_mission_id": "xrp_intelligence_prediction_engine",
            "selection_count": 6,
        },
    )

    with pytest.raises(ValueError, match="archive digest is invalid"):
        _curriculum_for_workspace(tmp_path).next_goal()


def test_mission_cursor_accepts_valid_compacted_history_and_continues_round_robin(
    tmp_path: Path,
) -> None:
    missions = [
        "xrp_intelligence_prediction_engine",
        "professional_audio_production",
        "long_horizon_continuity_capability_development",
    ]
    history = [
        {"mission_id": mission_id, "selection": selection}
        for selection, mission_id in zip(range(6, 9), missions)
    ]
    _mission_cursor_store(tmp_path).save(
        "mission_portfolio",
        {
            "history": history,
            "history_archived_count": 5,
            "history_archive_digest": "a" * 64,
            "last_selected_mission_id": missions[-1],
            "selection_count": 8,
        },
    )

    goal = _curriculum_for_workspace(tmp_path).next_goal()

    assert "MISSION_TOPIC_ID: xrp_source_provenance" in goal
    cursor = _mission_cursor_store(tmp_path).load("mission_portfolio")
    assert cursor["selection_count"] == 9
    assert cursor["history"][-1] == {
        "mission_id": "xrp_intelligence_prediction_engine",
        "selection": 9,
    }
