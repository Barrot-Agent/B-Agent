from __future__ import annotations

import json
from pathlib import Path

import pytest

from barrot_agent.orchestration.learning_curriculum import LearningCurriculum
from barrot_agent.orchestration.mission_registry import (
    MissionRegistry,
    MissionRegistryError,
)


class StubLearningStore:
    def __init__(self, records: list[dict] | None = None) -> None:
        self.records = records or []

    def read_all(self) -> list[dict]:
        return self.records


def _manifest() -> dict:
    return json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "data"
            / "missions"
            / "primary_mission.json"
        ).read_text(encoding="utf-8")
    )


def _write_manifest(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "primary_mission.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_xrp_primary_mission_preempts_generic_learning_curriculum() -> None:
    curriculum = LearningCurriculum(learning_store=StubLearningStore([]))

    goal = curriculum.next_goal()

    assert "XRP Intelligence and Prediction-Engine Mastery" in goal
    assert "MISSION_PRIORITY: 1" in goal
    assert "MISSION_TOPIC_ID: xrp_source_provenance" in goal
    assert "Barrot V3" in goal
    assert "No directional forecast" in goal
    assert "No guaranteed returns" in goal


def test_verified_xrp_lesson_advances_to_next_primary_workstream() -> None:
    store = StubLearningStore(
        [{"lesson": "Goal: MISSION_TOPIC_ID: xrp_source_provenance\nVerified findings: byte receipts."}]
    )
    curriculum = LearningCurriculum(learning_store=store)

    goal = curriculum.next_goal()

    assert "MISSION_TOPIC_ID: xrp_public_data_ingestion" in goal
    assert "PRIMARY MISSION — HIGHEST PRIORITY" in goal


def test_primary_mission_continues_after_initial_workstreams() -> None:
    manifest = _manifest()
    records = [
        {"lesson": f"Goal: MISSION_TOPIC_ID: {item['topic_id']}\nVerified findings: complete."}
        for item in manifest["workstreams"]
    ]
    curriculum = LearningCurriculum(learning_store=StubLearningStore(records))

    goal = curriculum.next_goal()

    assert "MISSION_TOPIC_ID: xrp_continuous_mission_review" in goal
    assert "highest-priority unmet XRP" in goal


def test_paused_primary_mission_falls_back_to_generic_curriculum(tmp_path: Path) -> None:
    manifest = _manifest()
    manifest["status"] = "paused"
    registry = MissionRegistry(_write_manifest(tmp_path, manifest))
    curriculum = LearningCurriculum(
        learning_store=StubLearningStore([]),
        mission_registry=registry,
    )

    assert "autonomous_actions.py" in curriculum.next_goal()


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda data: data.update(priority=2), "priority 1"),
        (lambda data: data["foundation"].update(preserve=False), "Barrot V3"),
        (lambda data: data.update(guardrails=["Use public data only."]), "Forecast and real-money"),
    ],
)
def test_primary_mission_manifest_fails_closed_on_safety_downgrade(
    tmp_path: Path,
    mutate,
    message: str,
) -> None:
    manifest = _manifest()
    mutate(manifest)

    with pytest.raises(MissionRegistryError, match=message):
        MissionRegistry(_write_manifest(tmp_path, manifest))
