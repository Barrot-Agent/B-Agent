import json
from pathlib import Path

from scripts.barrot_bundle_spec_generator import (
    BundleSpecError,
    generate_spec,
    load_mission,
)


ROOT = Path(__file__).resolve().parents[1]


def test_mission_generates_development_spec():
    mission = load_mission(ROOT)

    spec = generate_spec(
        mission,
        task_id="test_bundle",
    )

    assert spec["schema"] == (
        "barrot.development_bundle_spec.v1"
    )
    assert spec["task"]["task_id"] == "test_bundle"
    assert spec["task"]["execution_requested"] is False
    assert spec["execution_boundary"]["arbitrary_shell"] is False
    assert spec["execution_boundary"]["raw_command_payload"] is False
    assert spec["execution_boundary"]["automatic_execution"] is False
    assert len(spec["spec_sha256"]) == 64


def test_spec_contains_current_build_targets():
    mission = load_mission(ROOT)

    spec = generate_spec(
        mission,
        task_id="target_test",
    )

    targets = spec["requested_work"]["current_build_targets"]

    assert "provider-neutral controller" in targets
    assert "self-drop capability" in targets
    assert "autonomous engineering loop" in targets


def test_spec_is_deterministic():
    mission = load_mission(ROOT)

    a = generate_spec(
        mission,
        task_id="same_task",
    )

    b = generate_spec(
        mission,
        task_id="same_task",
    )

    assert a == b


def test_unsafe_governance_is_rejected():
    mission = load_mission(ROOT)
    broken = json.loads(json.dumps(mission))

    broken["governance"]["reset"] = True

    try:
        generate_spec(broken)
    except BundleSpecError:
        pass
    else:
        raise AssertionError(
            "unsafe governance must be rejected"
        )


def test_wrong_handoff_is_rejected():
    mission = load_mission(ROOT)
    broken = json.loads(json.dumps(mission))

    broken["handoff"]["next_capability"] = (
        "UNAUTHORIZED_EXECUTION"
    )

    try:
        generate_spec(broken)
    except BundleSpecError:
        pass
    else:
        raise AssertionError(
            "unauthorized handoff must be rejected"
        )
