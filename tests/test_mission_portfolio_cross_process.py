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
    match = re.search(r"MISSION_TOPIC_ID:\\s*([A-Za-z0-9_]+)", goal)
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
