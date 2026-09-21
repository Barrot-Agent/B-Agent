from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MODULE_PATH = (
    ROOT
    / "scripts"
    / "barrot_autonomous_continuation.py"
)

spec = importlib.util.spec_from_file_location(
    "barrot_autonomous_continuation",
    MODULE_PATH,
)

module = importlib.util.module_from_spec(spec)

assert spec.loader is not None
spec.loader.exec_module(module)


def mission():
    return {
        "protocol":
            "BARROT-V3-MISSION",
        "protocol_version":
            "1",
        "mission": {
            "objective":
                "continue V3",
            "continuation_target":
                "autonomous engineering loop",
            "immediate_priority": [
                "Initialize governed autonomous "
                "bundle generation."
            ],
            "current_build_targets": [
                "provider-neutral controller",
                "self-drop capability",
                "autonomous engineering loop",
            ],
        },
    }


def test_mission_validates():
    module.validate_mission(
        mission()
    )


def test_priority_is_selected():
    assert module.select_priority(
        mission()
    ) == (
        "Initialize governed autonomous "
        "bundle generation."
    )


def test_record_is_governed():
    record = (
        module.build_continuation_record(
            ROOT
            / ".barrot"
            / "autonomous_bundle"
            / "active_mission.json",
            mission(),
        )
    )

    boundary = record[
        "execution_boundary"
    ]

    assert boundary[
        "arbitrary_shell"
    ] is False

    assert boundary[
        "raw_command_payload"
    ] is False

    assert boundary[
        "automatic_execution"
    ] is False

    assert boundary[
        "destructive_git_operations"
    ] is False

    assert boundary[
        "unverified_mutation"
    ] is False


def test_transition_is_not_executed():
    record = (
        module.build_continuation_record(
            ROOT
            / ".barrot"
            / "autonomous_bundle"
            / "active_mission.json",
            mission(),
        )
    )

    assert record[
        "transition"
    ][
        "status"
    ] == "PLANNED_NOT_EXECUTED"
