from __future__ import annotations

import json
from importlib.resources import files as package_files
from pathlib import Path

import pytest

from barrot_agent.orchestration.learning_curriculum import LearningCurriculum
from barrot_agent.orchestration.learning_filter import LearningRecord
from barrot_agent.orchestration.mission_registry import (
    MissionRegistry,
    MissionRegistryError,
)
from barrot_agent.orchestration.verified_learning_store import (
    VERIFIED_LEARNING_REASON,
    VerifiedLearningStore,
)


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


def _verified_record(topic_id: str) -> LearningRecord:
    lesson = (
        f"Goal: MISSION_TOPIC_ID: {topic_id}\\n"
        "Verified findings:\\n"
        "- READ_FILE: inspected the implementation and acceptance criteria.\\n"
        "- RUN_TESTS: focused regression tests passed."
    )
    return LearningRecord(
        accepted=True,
        lesson=lesson,
        reason=VERIFIED_LEARNING_REASON,
    )


def test_xrp_primary_mission_preempts_generic_learning_curriculum(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    curriculum = LearningCurriculum(learning_store=store)

    goal = curriculum.next_goal()

    assert "XRP Intelligence and Prediction-Engine Mastery" in goal
    assert "MISSION_PRIORITY: 1" in goal
    assert "MISSION_TOPIC_ID: xrp_source_provenance" in goal
    assert "Barrot V3" in goal
    assert "directional forecast" in goal.lower()
    assert "No guaranteed returns" in goal


def test_structurally_verified_xrp_lesson_advances_to_next_workstream(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    assert store.append(_verified_record("xrp_source_provenance")) is True

    curriculum = LearningCurriculum(learning_store=store)
    goal = curriculum.next_goal()

    assert "MISSION_TOPIC_ID: xrp_public_data_ingestion" in goal
    assert "PRIMARY MISSION — HIGHEST PRIORITY" in goal


def test_primary_mission_continues_after_initial_workstreams(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    for item in _manifest()["workstreams"]:
        assert store.append(_verified_record(item["topic_id"])) is True

    curriculum = LearningCurriculum(learning_store=store)
    goal = curriculum.next_goal()

    assert "MISSION_TOPIC_ID: xrp_continuous_mission_review" in goal
    assert "highest-priority unmet XRP" in goal


def test_legacy_or_shallow_records_cannot_advance_primary_mission(tmp_path: Path) -> None:
    path = tmp_path / "verified_lessons.jsonl"
    path.write_text(
        json.dumps(
            {
                "lesson": (
                    "Goal: MISSION_TOPIC_ID: xrp_source_provenance\\n"
                    "Verified findings:\\n"
                    "- LIST_FILES: listed repository files."
                ),
                "reason": "Actions and verification succeeded.",
                "recorded_at": "2026-09-08T06:03:17.717106+00:00",
            }
        )
        + "\\n",
        encoding="utf-8",
    )
    store = VerifiedLearningStore(path)

    assert len(store.read_all()) == 1
    assert store.read_verified() == []
    assert "MISSION_TOPIC_ID: xrp_source_provenance" in LearningCurriculum(
        learning_store=store
    ).next_goal()


def test_tampered_verified_lesson_does_not_advance_primary_mission(tmp_path: Path) -> None:
    path = tmp_path / "verified_lessons.jsonl"
    store = VerifiedLearningStore(path)
    assert store.append(_verified_record("xrp_source_provenance")) is True

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["lesson"] = payload["lesson"].replace("READ_FILE", "LIST_FILES")
    path.write_text(json.dumps(payload) + "\\n", encoding="utf-8")

    assert store.read_verified() == []
    assert "MISSION_TOPIC_ID: xrp_source_provenance" in LearningCurriculum(
        learning_store=store
    ).next_goal()


def test_store_rejects_accepted_records_without_deep_verification(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    shallow = LearningRecord(
        accepted=True,
        lesson=(
            "Goal: inspect repository.\\n"
            "Verified findings:\\n"
            "- LIST_FILES: listed files."
        ),
        reason=VERIFIED_LEARNING_REASON,
    )

    assert store.append(shallow) is False
    assert store.read_verified() == []


def test_store_rejects_records_without_successful_verification_reason(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    record = LearningRecord(
        accepted=True,
        lesson=(
            "Goal: inspect repository.\\n"
            "Verified findings:\\n"
            "- READ_FILE: inspected source."
        ),
        reason="Actions and verification succeeded.",
    )

    assert store.append(record) is False
    assert store.read_verified() == []


def test_paused_primary_mission_falls_back_to_generic_curriculum(tmp_path: Path) -> None:
    manifest = _manifest()
    manifest["status"] = "paused"
    registry = MissionRegistry(_write_manifest(tmp_path, manifest))
    curriculum = LearningCurriculum(
        learning_store=VerifiedLearningStore(tmp_path / "verified_lessons.jsonl"),
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


def test_primary_mission_manifest_is_packaged_and_matches_repository_copy() -> None:
    packaged = package_files("barrot_agent").joinpath(
        "data", "missions", "primary_mission.json"
    )

    assert packaged.is_file()
    assert json.loads(packaged.read_text(encoding="utf-8")) == _manifest()


def test_installed_package_falls_back_to_packaged_primary_mission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from barrot_agent.orchestration import mission_registry as registry_module

    missing_checkout_path = (
        tmp_path / "source-checkout" / "data" / "missions" / "primary_mission.json"
    )
    monkeypatch.setattr(registry_module, "DEFAULT_MISSION_PATH", missing_checkout_path)

    registry = MissionRegistry()

    assert registry.mission_id == "xrp_intelligence_prediction_engine"


def test_primary_mission_resource_is_declared_as_package_data() -> None:
    pyproject = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
        encoding="utf-8"
    )

    assert "[tool.setuptools.package-data]" in pyproject
    assert 'barrot_agent = ["data/missions/*.json"]' in pyproject
    assert "[tool.setuptools.packages.find]" in pyproject
    assert 'include = ["barrot_agent", "barrot_agent.*", "data", "directive_platform", "directive_platform.*"]' in pyproject
    assert 'data = [' in pyproject
    assert '"merge_conflict_unified.json"' in pyproject
    assert '"research/navier_stokes_research_bundle.json"' in pyproject
