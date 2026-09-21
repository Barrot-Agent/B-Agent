from pathlib import Path
import json

from scripts.barrot_mission_bundle_planner import (
    ALLOWED_ACTION,
    MissionPlannerError,
    build_proposal,
    load_mission,
)


ROOT = Path(__file__).resolve().parents[1]


def test_active_mission_loads():
    mission = load_mission(ROOT)

    assert isinstance(mission, dict)
    assert mission["handoff"]["next_capability"] == (
        "AUTONOMOUS_BUNDLE_PRODUCTION"
    )
    assert mission["handoff"]["existing_capability"] == "SELF_DROP"


def test_build_proposal_is_self_drop_probe_only():
    mission = load_mission(ROOT)

    proposal = build_proposal(
        mission,
        task_id="planner_test",
    )

    assert proposal["proposal_mode"] is True
    assert proposal["execution_requested"] is False
    assert proposal["action"] == ALLOWED_ACTION
    assert proposal["action"] == "SELF_DROP_PROBE"
    assert proposal["task_id"] == "planner_test"
    assert len(proposal["proposal_sha256"]) == 64

    # No shell payload is permitted in the proposal.
    assert "shell" not in proposal
    assert "command" not in proposal
    assert "script" not in proposal
    assert "payload" not in proposal


def test_proposal_is_deterministic():
    mission = load_mission(ROOT)

    first = build_proposal(
        mission,
        task_id="deterministic_test",
    )
    second = build_proposal(
        mission,
        task_id="deterministic_test",
    )

    assert first == second


def test_invalid_handoff_is_rejected():
    mission = load_mission(ROOT)
    broken = json.loads(json.dumps(mission))
    broken["handoff"]["existing_capability"] = "UNSAFE_EXECUTOR"

    try:
        build_proposal(broken)
    except MissionPlannerError:
        pass
    else:
        raise AssertionError(
            "unsafe handoff should have been rejected"
        )


def test_destructive_governance_is_rejected():
    mission = load_mission(ROOT)
    broken = json.loads(json.dumps(mission))
    broken["governance"]["reset"] = True

    try:
        build_proposal(broken)
    except MissionPlannerError:
        pass
    else:
        raise AssertionError(
            "destructive governance flag should have been rejected"
        )
