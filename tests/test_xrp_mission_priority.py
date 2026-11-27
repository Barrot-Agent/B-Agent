from __future__ import annotations

import json
from importlib.resources import files as package_files
from pathlib import Path

import pytest

from barrot_agent.orchestration.autonomous_state import AutonomousTaskStore
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

from scripts.ask_barrot import (
    INFRASTRUCTURE_CONSTRAINTS,
    SYSTEM_BASE,
    load_mission_portfolio_status,
    load_platform_capability_map,
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
        f"Goal: MISSION_TOPIC_ID: {topic_id}\n"
        "Verified findings:\n"
        "- READ_FILE: inspected the implementation and acceptance criteria.\n"
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


def test_structurally_verified_xrp_lesson_advances_without_starving_other_missions(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    assert store.append(_verified_record("xrp_source_provenance")) is True

    curriculum = LearningCurriculum(learning_store=store)
    xrp_goal = curriculum.next_goal()
    audio_goal = curriculum.next_goal()
    continuity_goal = curriculum.next_goal()

    assert "MISSION_TOPIC_ID: xrp_public_data_ingestion" in xrp_goal
    assert "MISSION_TOPIC_ID: audio_capability_inventory" in audio_goal
    assert "MISSION_TOPIC_ID: continuity_versioned_state_model" in continuity_goal
    assert "co-equal" in audio_goal.lower()
    assert "Barrot V3" in continuity_goal


def test_portfolio_round_robin_cursor_persists_across_curriculum_instances(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    expected = [
        ("xrp_intelligence_prediction_engine", "xrp_source_provenance"),
        ("professional_audio_production", "audio_capability_inventory"),
        ("long_horizon_continuity_capability_development", "continuity_versioned_state_model"),
        ("xrp_intelligence_prediction_engine", "xrp_source_provenance"),
    ]

    goals = [
        LearningCurriculum(learning_store=store).next_goal()
        for _ in expected
    ]
    for goal, (_, topic_id) in zip(goals, expected):
        assert f"MISSION_TOPIC_ID: {topic_id}" in goal

    cursor = AutonomousTaskStore(tmp_path).load("mission_portfolio")
    assert cursor is not None
    assert cursor["selection_count"] == len(expected)
    assert [item["mission_id"] for item in cursor["history"][-4:]] == [
        mission_id for mission_id, _ in expected
    ]


def test_portfolio_manifest_rejects_silent_priority_demotion(tmp_path: Path) -> None:
    manifest = _manifest()
    manifest["mission_portfolio"]["missions"][1]["priority"] = 2
    with pytest.raises(MissionRegistryError, match="co-equal"):
        MissionRegistry(_write_manifest(tmp_path, manifest))


def test_primary_mission_continues_after_initial_workstreams(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    for item in _manifest()["workstreams"]:
        assert store.append(_verified_record(item["topic_id"])) is True

    known = "\n".join(item["lesson"] for item in store.read_verified()).lower()
    goal = MissionRegistry().next_goal(known)

    assert "MISSION_TOPIC_ID: xrp_continuous_mission_review" in goal
    assert "highest-priority unmet XRP" in goal
    assert "co-equal standing" in goal


def test_legacy_or_shallow_records_cannot_advance_primary_mission(tmp_path: Path) -> None:
    path = tmp_path / "verified_lessons.jsonl"
    path.write_text(
        json.dumps(
            {
                "lesson": (
                    "Goal: MISSION_TOPIC_ID: xrp_source_provenance\n"
                    "Verified findings:\n"
                    "- LIST_FILES: listed repository files."
                ),
                "reason": "Actions and verification succeeded.",
                "recorded_at": "2026-09-08T06:03:17.717106+00:00",
            }
        )
        + "\n",
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
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    assert store.read_verified() == []
    assert "MISSION_TOPIC_ID: xrp_source_provenance" in LearningCurriculum(
        learning_store=store
    ).next_goal()


def test_store_rejects_accepted_records_without_deep_verification(tmp_path: Path) -> None:
    store = VerifiedLearningStore(tmp_path / "verified_lessons.jsonl")
    shallow = LearningRecord(
        accepted=True,
        lesson=(
            "Goal: inspect repository.\n"
            "Verified findings:\n"
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
            "Goal: inspect repository.\n"
            "Verified findings:\n"
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


def test_ask_barrot_system_prompt_preserves_three_coequal_missions() -> None:
    prompt = SYSTEM_BASE.lower()

    assert "three co-equal highest-priority missions" in prompt
    assert "xrp intelligence" in prompt
    assert "professional audio production" in prompt
    assert "long-horizon continuity and capability development" in prompt
    assert "none may be deferred behind the others" in prompt
    assert "barrot v3 remains the shared" in prompt
    assert "sellbird is restricted to barrot technology only" in prompt
    assert "your highest-priority mission is xrp" not in prompt


def test_ask_barrot_reads_exactly_three_active_priority_one_missions(tmp_path: Path) -> None:
    path = tmp_path / "data" / "missions"
    path.mkdir(parents=True)
    (path / "primary_mission.json").write_text(
        json.dumps(_manifest()),
        encoding="utf-8",
    )

    status = load_mission_portfolio_status(tmp_path)

    assert "Verified co-equal mission portfolio" in status
    assert "XRP Intelligence and Prediction-Engine Mastery" in status
    assert "Professional Audio Production" in status
    assert "Long-Horizon Continuity and Capability Development" in status
    assert "priority=1; status=active" in status


def test_ask_barrot_fails_closed_on_mission_priority_demotion(tmp_path: Path) -> None:
    path = tmp_path / "data" / "missions"
    path.mkdir(parents=True)
    manifest = _manifest()
    manifest["mission_portfolio"]["missions"][1]["priority"] = 2
    (path / "primary_mission.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    status = load_mission_portfolio_status(tmp_path)

    assert "INVALID" in status
    assert "do not silently demote" in status


def test_ask_barrot_platform_map_requires_authentication_permissions_and_data_flow(
    tmp_path: Path,
) -> None:
    path = tmp_path / "research" / "operations"
    path.mkdir(parents=True)
    payload = {
        "captured_at_utc": "2026-11-25T21:38:00Z",
        "platforms": {
            "ChatGPT": {
                "capabilities": ["GitHub repository and workflow inspection"],
                "authentication": {"status": "VERIFIED_FOR_GITHUB_CONNECTOR"},
                "permissions": {"observed_actions": ["read repository", "write existing branch"]},
                "data_flow": {
                    "verified": True,
                    "status": "LIVE_TESTED",
                    "external_transfer_occurred": False,
                },
            },
            "Claude": {
                "capability_status": "NOT_ASSESSED",
                "authentication": {"status": "NOT_TESTED"},
                "permissions": {"status": "UNKNOWN_NOT_TESTED"},
                "data_flow": {
                    "verified": False,
                    "status": "NOT_TESTED",
                    "external_transfer_occurred": False,
                },
            },
        },
        "coordination": {
            "status": "DESIGNED_NOT_EXECUTED",
            "structured_evidence_exchange_across_nine_platforms": False,
            "external_model_data_transfer_occurred": False,
        },
    }
    (path / "nine_platform_operational_map_current.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    status = load_platform_capability_map(tmp_path)

    assert "ChatGPT: connection=VERIFIED" in status
    assert "Claude: connection=UNVERIFIED" in status
    assert "Grok: connection=UNVERIFIED" in status
    assert "structured_evidence_exchange=False" in status
    assert "external_model_data_transfer=False" in status


def test_ask_barrot_platform_map_unavailable_never_claims_connections(tmp_path: Path) -> None:
    status = load_platform_capability_map(tmp_path)

    assert "UNAVAILABLE" in status
    assert "no external platform connection may be claimed" in status


def test_ask_barrot_mission_loader_fails_closed_on_malformed_json_shapes(tmp_path: Path) -> None:
    path = tmp_path / "data" / "missions"
    path.mkdir(parents=True)
    malformed_manifests = [
        [],
        {"mission_portfolio": [], "foundation": {}},
        {**_manifest(), "foundation": []},
    ]

    for manifest in malformed_manifests:
        (path / "primary_mission.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )
        status = load_mission_portfolio_status(tmp_path)
        assert "INVALID" in status
        assert "\n" in status
        assert "\\n" not in status


def test_ask_barrot_platform_map_fails_closed_on_malformed_root_and_unverified_auth(
    tmp_path: Path,
) -> None:
    path = tmp_path / "research" / "operations"
    path.mkdir(parents=True)
    map_path = path / "nine_platform_operational_map_current.json"
    map_path.write_text("[]", encoding="utf-8")

    invalid_status = load_platform_capability_map(tmp_path)
    assert "INVALID" in invalid_status
    assert "\n" in invalid_status
    assert "\\n" not in invalid_status

    payload = {
        "platforms": {
            "ChatGPT": {
                "authentication": {"status": "UNVERIFIED"},
                "permissions": {"observed_actions": ["read repository"]},
                "data_flow": {"verified": True, "status": "LIVE_TESTED"},
            },
            "Claude": {
                "authentication": {"status": "NOT_VERIFIED"},
                "permissions": {"observed_actions": ["read profile"]},
                "data_flow": {"verified": True, "status": "LIVE_TESTED"},
            },
        }
    }
    map_path.write_text(json.dumps(payload), encoding="utf-8")
    status = load_platform_capability_map(tmp_path)

    assert "ChatGPT: connection=UNVERIFIED" in status
    assert "Claude: connection=UNVERIFIED" in status
    assert "\n" in status
    assert "\\n" not in status


def test_ask_barrot_infrastructure_constraints_use_actual_newlines() -> None:
    assert "\n" in INFRASTRUCTURE_CONSTRAINTS
    assert "\\n" not in INFRASTRUCTURE_CONSTRAINTS


def test_ask_barrot_platform_map_reads_current_operational_map_schema(tmp_path: Path) -> None:
    path = tmp_path / "research" / "operations"
    path.mkdir(parents=True)
    payload = {
        "captured_at_utc": "2026-11-27T23:04:34Z",
        "platforms": {
            "ChatGPT": {
                "capability_status": "VERIFIED_CURRENT_SESSION_WITH_ADMIN_LIMITATIONS",
                "authentication_status": "VERIFIED_CURRENT_SESSION",
                "permissions": {
                    "repository_contents_read": True,
                    "repository_contents_write_on_existing_pr_branches": True,
                    "administration_read": False,
                },
                "verified_data_flow": {
                    "status": "VERIFIED",
                    "path": "ChatGPT session -> GitHub connector -> repository",
                    "operations_observed": ["read repository", "write existing PR branch"],
                    "external_model_data_transfer": False,
                },
            },
            "Claude": {
                "capability_status": "NOT_ASSESSED_THIS_SESSION",
                "authentication_status": "NOT_TESTED_THIS_SESSION",
                "permissions": {"status": "UNKNOWN"},
                "verified_data_flow": {
                    "status": "NOT_TESTED",
                    "external_model_data_transfer": False,
                },
            },
            "Gemini": {
                "capability_status": "NOT_ASSESSED_THIS_SESSION",
                "authentication_status": "VERIFIED_CURRENT_SESSION",
                "permissions": {},
                "verified_data_flow": {
                    "status": "VERIFIED",
                    "path": "untrusted test path",
                    "operations_observed": ["test observation"],
                    "external_model_data_transfer": False,
                },
            },
        },
        "coordination": {
            "status": "DESIGNED_NOT_EXECUTED",
            "structured_evidence_exchange_across_nine_platforms": False,
            "external_model_data_transfer_occurred": False,
        },
    }
    (path / "nine_platform_operational_map_current.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    status = load_platform_capability_map(tmp_path)

    assert "ChatGPT: connection=VERIFIED" in status
    assert "Claude: connection=UNVERIFIED" in status
    assert "Gemini: connection=UNVERIFIED" in status
    assert "external_transfer=False" in status
    assert "structured_evidence_exchange=False" in status
