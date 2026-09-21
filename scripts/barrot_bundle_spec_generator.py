#!/usr/bin/env python3
"""
Barrot V3 — governed development-bundle specification generator.

Mission
  -> deterministic development bundle specification
  -> validated structured artifact
  -> later execution layer

This layer NEVER executes the specification.
It NEVER accepts arbitrary shell.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "BARROT-V3-DEVELOPMENT-BUNDLE-SPEC"
VERSION = 1


class BundleSpecError(RuntimeError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(
        canonical(value).encode("utf-8")
    ).hexdigest()


def load_mission(root: Path = ROOT) -> dict[str, Any]:
    path = root / ".barrot" / "autonomous_bundle" / "active_mission.json"

    if not path.exists():
        raise BundleSpecError(f"missing active mission: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise BundleSpecError(
            f"invalid mission JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise BundleSpecError("mission must be an object")

    return data


def generate_spec(
    mission: dict[str, Any],
    *,
    task_id: str = "barrot_v3_next_build",
) -> dict[str, Any]:

    governance = mission.get("governance", {})
    handoff = mission.get("handoff", {})
    mission_data = mission.get("mission", {})

    if not isinstance(governance, dict):
        raise BundleSpecError("governance must be an object")

    if not isinstance(handoff, dict):
        raise BundleSpecError("handoff must be an object")

    if not isinstance(mission_data, dict):
        raise BundleSpecError("mission section must be an object")

    # Hard safety boundary.
    for key in (
        "reset",
        "clean",
        "stash",
        "destructive_git_operations",
        "discard_dirty_work",
    ):
        if governance.get(key) is True:
            raise BundleSpecError(
                f"unsafe governance flag enabled: {key}"
            )

    if handoff.get("next_capability") != (
        "AUTONOMOUS_BUNDLE_PRODUCTION"
    ):
        raise BundleSpecError(
            "mission does not authorize autonomous bundle production"
        )

    priorities = mission_data.get("immediate_priority", [])

    if not isinstance(priorities, list):
        raise BundleSpecError(
            "immediate_priority must be a list"
        )

    priorities = [
        item.strip()
        for item in priorities
        if isinstance(item, str) and item.strip()
    ]

    if not priorities:
        raise BundleSpecError(
            "mission contains no actionable priorities"
        )

    targets = mission_data.get("current_build_targets", [])

    if not isinstance(targets, list):
        raise BundleSpecError(
            "current_build_targets must be a list"
        )

    targets = [
        item.strip()
        for item in targets
        if isinstance(item, str) and item.strip()
    ]

    spec = {
        "schema": "barrot.development_bundle_spec.v1",
        "protocol": PROTOCOL,
        "protocol_version": VERSION,

        "task": {
            "task_id": task_id,
            "mode": "GOVERNED_DEVELOPMENT",
            "execution_requested": False,
        },

        "mission": {
            "protocol": mission.get("protocol"),
            "protocol_version": mission.get(
                "protocol_version"
            ),
            "objective": mission_data.get("objective"),
            "continuation_target": mission_data.get(
                "continuation_target"
            ),
        },

        "requested_work": {
            "priorities": priorities,
            "current_build_targets": targets,
            "first_priority": priorities[0],
        },

        "execution_boundary": {
            "arbitrary_shell": False,
            "raw_command_payload": False,
            "automatic_execution": False,
            "destructive_git_operations": False,
            "unverified_mutation": False,
        },

        "required_validation": [
            "syntax validation",
            "scope-appropriate tests",
            "git diff --check",
            "provenance evidence",
            "execution evidence",
            "rollback path where mutation occurs",
        ],

        "handoff": {
            "planner": (
                "barrot_mission_bundle_planner"
            ),
            "executor": (
                "existing_governed_self_drop"
            ),
            "status": "SPECIFICATION_ONLY",
        },
    }

    spec["spec_sha256"] = digest(spec)

    return spec


def write_spec(
    spec: dict[str, Any],
    root: Path = ROOT,
) -> Path:

    out_dir = (
        root
        / ".barrot"
        / "autonomous_bundle"
        / "specifications"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    out = out_dir / (
        f"development_bundle_{stamp}.json"
    )

    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "schema": "barrot.development_bundle_record.v1",
        "specification": spec,
    }

    out.write_text(
        json.dumps(
            record,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
    )
    parser.add_argument(
        "--task-id",
        default="barrot_v3_next_build",
    )
    parser.add_argument(
        "--write",
        action="store_true",
    )

    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    mission = load_mission(root)

    spec = generate_spec(
        mission,
        task_id=args.task_id,
    )

    print("BARROT DEVELOPMENT BUNDLE SPEC")
    print(f"PROTOCOL={PROTOCOL}")
    print("MODE=GOVERNED_DEVELOPMENT")
    print("EXECUTION_REQUESTED=FALSE")
    print("ARBITRARY_SHELL=FALSE")
    print(
        "FIRST_PRIORITY="
        + spec["requested_work"]["first_priority"]
    )
    print(
        "SPEC_SHA256="
        + spec["spec_sha256"]
    )

    if args.write:
        path = write_spec(spec, root)
        print(f"SPEC_EVIDENCE={path}")

    print("DEVELOPMENT_BUNDLE_SPEC=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
