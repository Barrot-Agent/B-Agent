#!/usr/bin/env python3
"""
Barrot V3 mission-driven bundle planner.

This module is deliberately proposal-only.

It converts the active Barrot mission into a deterministic, governed
SELF_DROP_PROBE request for the existing self-drop bridge.

It does NOT:
- execute the request,
- execute arbitrary shell,
- modify repository source,
- invoke git,
- choose arbitrary actions,
- bypass the existing self-drop bridge.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROTOCOL = "BARROT-V3-MISSION-BUNDLE-PLANNER"
VERSION = 1
ALLOWED_ACTION = "SELF_DROP_PROBE"

DEFAULT_ROOT = Path(__file__).resolve().parents[1]


class MissionPlannerError(RuntimeError):
    """Raised when the active mission cannot produce a safe proposal."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_mission(root: Path = DEFAULT_ROOT) -> dict[str, Any]:
    path = root / ".barrot" / "autonomous_bundle" / "active_mission.json"

    if not path.exists():
        raise MissionPlannerError(f"active mission missing: {path}")

    try:
        mission = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise MissionPlannerError(
            f"active mission is not valid JSON: {exc}"
        ) from exc

    if not isinstance(mission, dict):
        raise MissionPlannerError("active mission must be a JSON object")

    required = (
        "protocol",
        "protocol_version",
        "mission",
        "governance",
        "handoff",
        "integrity",
    )

    missing = [key for key in required if key not in mission]

    if missing:
        raise MissionPlannerError(
            "active mission missing required fields: "
            + ", ".join(missing)
        )

    return mission


def _validate_governance(mission: dict[str, Any]) -> None:
    governance = mission.get("governance")

    if not isinstance(governance, dict):
        raise MissionPlannerError("mission governance must be an object")

    forbidden = (
        "destructive_git_operations",
        "reset",
        "clean",
        "stash",
        "discard_dirty_work",
        "unverified_execution",
        "unverified_push",
    )

    violations = [
        key for key in forbidden
        if governance.get(key) is True
    ]

    if violations:
        raise MissionPlannerError(
            "mission governance contains prohibited enabled flags: "
            + ", ".join(violations)
        )


def _objective(mission: dict[str, Any]) -> str:
    section = mission.get("mission")

    if not isinstance(section, dict):
        raise MissionPlannerError("mission.mission must be an object")

    value = section.get("objective")

    if not isinstance(value, str) or not value.strip():
        raise MissionPlannerError("mission objective is missing")

    return value.strip()


def _priority(mission: dict[str, Any]) -> list[str]:
    section = mission.get("mission")

    if not isinstance(section, dict):
        raise MissionPlannerError("mission.mission must be an object")

    values = section.get("immediate_priority", [])

    if not isinstance(values, list):
        raise MissionPlannerError(
            "mission immediate_priority must be a list"
        )

    result = []

    for value in values:
        if isinstance(value, str) and value.strip():
            result.append(value.strip())

    return result


def build_proposal(
    mission: dict[str, Any],
    *,
    task_id: str = "mission_next_bundle",
) -> dict[str, Any]:
    """
    Build a deterministic proposal.

    The only executable action permitted at this layer is the already
    allowlisted SELF_DROP_PROBE action.

    The proposal contains no shell payload.
    """

    _validate_governance(mission)

    handoff = mission.get("handoff")

    if not isinstance(handoff, dict):
        raise MissionPlannerError("mission handoff must be an object")

    next_capability = handoff.get("next_capability")
    existing_capability = handoff.get("existing_capability")

    if next_capability != "AUTONOMOUS_BUNDLE_PRODUCTION":
        raise MissionPlannerError(
            "unexpected next capability: "
            f"{next_capability!r}"
        )

    if existing_capability != "SELF_DROP":
        raise MissionPlannerError(
            "existing capability is not SELF_DROP: "
            f"{existing_capability!r}"
        )

    if not task_id or not isinstance(task_id, str):
        raise MissionPlannerError("task_id must be a non-empty string")

    proposal = {
        "protocol": PROTOCOL,
        "protocol_version": VERSION,
        "proposal_mode": True,
        "execution_requested": False,

        "source_mission": {
            "protocol": mission.get("protocol"),
            "protocol_version": mission.get("protocol_version"),
            "integrity": mission.get("integrity"),
        },

        "task_id": task_id,

        # This is the only action the existing bridge accepts.
        "action": ALLOWED_ACTION,

        "intent": {
            "objective": _objective(mission),
            "priority": _priority(mission),
            "next_capability": next_capability,
            "required_transition": handoff.get(
                "required_transition"
            ),
        },

        "governance": {
            "destructive_git_operations": False,
            "arbitrary_shell_input": False,
            "execution_requested": False,
            "human_governance_boundary": True,
        },
    }

    canonical = _canonical_json(proposal)

    proposal["proposal_sha256"] = _sha256_text(canonical)

    return proposal


def write_proposal(
    proposal: dict[str, Any],
    root: Path = DEFAULT_ROOT,
) -> Path:
    evidence_dir = root / ".barrot" / "self_drop" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    output = evidence_dir / (
        f"mission_bundle_proposal_{now}.json"
    )

    record = {
        "schema": "barrot.mission_bundle_proposal.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "proposal": proposal,
        "execution": {
            "requested": False,
            "executed": False,
        },
    }

    output.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return output


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=str(DEFAULT_ROOT),
    )
    parser.add_argument(
        "--task-id",
        default="mission_next_bundle",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write proposal evidence; never execute it",
    )

    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    mission = load_mission(root)
    proposal = build_proposal(
        mission,
        task_id=args.task_id,
    )

    print("BARROT MISSION BUNDLE PLANNER")
    print("PROTOCOL=" + PROTOCOL)
    print("MODE=PROPOSAL_ONLY")
    print("EXECUTION_REQUESTED=FALSE")
    print("ACTION=" + proposal["action"])
    print("TASK_ID=" + proposal["task_id"])
    print("PROPOSAL_SHA256=" + proposal["proposal_sha256"])

    if args.write:
        evidence = write_proposal(proposal, root)
        print("PROPOSAL_EVIDENCE=" + str(evidence))

    print("MISSION_BUNDLE_PROPOSAL=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
