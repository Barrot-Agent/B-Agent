#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

MISSION = (
    ROOT
    / ".barrot"
    / "autonomous_bundle"
    / "active_mission.json"
)

SPEC_DIR = (
    ROOT
    / ".barrot"
    / "autonomous_bundle"
    / "specifications"
)

HANDOFF_DIR = (
    ROOT
    / ".barrot"
    / "autonomous_bundle"
    / "handoff"
)

EVIDENCE_DIR = (
    ROOT
    / ".barrot"
    / "autonomous_bundle"
    / "continuation_evidence"
)

PROTOCOL = (
    "BARROT-V3-AUTONOMOUS-CONTINUATION"
)


class ContinuationError(RuntimeError):
    pass


def digest(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ContinuationError(
            f"missing required artifact: {path}"
        )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ContinuationError(
            f"artifact must be an object: {path}"
        )

    return data


def validate_mission(
    mission: dict[str, Any],
) -> None:

    required = {
        "protocol",
        "protocol_version",
        "mission",
    }

    missing = required - set(mission)

    if missing:
        raise ContinuationError(
            f"mission missing: {sorted(missing)}"
        )

    mission_data = mission["mission"]

    if not isinstance(
        mission_data,
        dict,
    ):
        raise ContinuationError(
            "mission.mission must be an object"
        )

    for key in (
        "objective",
        "continuation_target",
        "immediate_priority",
        "current_build_targets",
    ):
        if key not in mission_data:
            raise ContinuationError(
                f"mission missing {key}"
            )

    if not mission_data[
        "immediate_priority"
    ]:
        raise ContinuationError(
            "mission has no immediate priorities"
        )


def select_priority(
    mission: dict[str, Any],
) -> str:

    priorities = mission[
        "mission"
    ][
        "immediate_priority"
    ]

    return str(priorities[0])


def build_continuation_record(
    mission_path: Path,
    mission: dict[str, Any],
) -> dict[str, Any]:

    mission_data = mission["mission"]
    priority = select_priority(mission)

    return {
        "schema":
            "barrot.autonomous_continuation.v1",

        "protocol":
            PROTOCOL,

        "protocol_version":
            "1",

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "mission": {
            "source":
                str(
                    mission_path.relative_to(
                        ROOT
                    )
                ),
            "sha256":
                sha256_file(mission_path),
            "objective":
                mission_data["objective"],
            "continuation_target":
                mission_data[
                    "continuation_target"
                ],
        },

        "selected_work": {
            "priority":
                priority,
            "current_build_targets":
                mission_data[
                    "current_build_targets"
                ],
        },

        "execution_boundary": {
            "arbitrary_shell":
                False,
            "raw_command_payload":
                False,
            "automatic_execution":
                False,
            "destructive_git_operations":
                False,
            "unverified_mutation":
                False,
        },

        "transition": {
            "from":
                "MISSION",
            "to":
                "DEVELOPMENT_BUNDLE_SPECIFICATION",
            "status":
                "PLANNED_NOT_EXECUTED",
        },
    }


def write_record(
    record: dict[str, Any],
) -> Path:

    SPEC_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    record["record_sha256"] = digest(
        record
    )

    path = (
        SPEC_DIR
        / f"continuation_{stamp}.json"
    )

    path.write_text(
        json.dumps(
            record,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    return path


def write_evidence(
    mission_path: Path,
    continuation_path: Path,
    record: dict[str, Any],
) -> Path:

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    evidence = {
        "schema":
            "barrot.autonomous_continuation_evidence.v1",

        "protocol":
            PROTOCOL,

        "status":
            "PLANNED_NOT_EXECUTED",

        "mission_sha256":
            sha256_file(
                mission_path
            ),

        "continuation_sha256":
            sha256_file(
                continuation_path
            ),

        "record_sha256":
            record[
                "record_sha256"
            ],

        "execution_requested":
            False,

        "governance": {
            "arbitrary_shell":
                False,
            "raw_command_payload":
                False,
            "automatic_execution":
                False,
            "destructive_git_operations":
                False,
            "unverified_mutation":
                False,
        },
    }

    path = (
        EVIDENCE_DIR
        / f"continuation_{stamp}.json"
    )

    path.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    return path


def main() -> int:

    mission = load_json(MISSION)

    validate_mission(
        mission
    )

    record = build_continuation_record(
        MISSION,
        mission,
    )

    continuation = write_record(
        record
    )

    evidence = write_evidence(
        MISSION,
        continuation,
        record,
    )

    print(
        "BARROT AUTONOMOUS CONTINUATION"
    )
    print(
        f"PROTOCOL={PROTOCOL}"
    )
    print(
        "MISSION=VALID"
    )
    print(
        "PRIORITY_SELECTED="
        + record[
            "selected_work"
        ][
            "priority"
        ]
    )
    print(
        "CONTINUATION=PLANNED"
    )
    print(
        "EXECUTION_REQUESTED=FALSE"
    )
    print(
        "ARBITRARY_SHELL=FALSE"
    )
    print(
        "DESTRUCTIVE_GIT=FALSE"
    )
    print(
        f"CONTINUATION={continuation}"
    )
    print(
        f"EVIDENCE={evidence}"
    )
    print(
        "AUTONOMOUS_CONTINUATION=PASS"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
