#!/usr/bin/env python3
"""
Barrot V3 — Governed Development Bundle Builder

Mission:
    Convert a validated development-bundle specification into a concrete,
    deterministic, reviewable implementation bundle.

Safety contract:
    - proposal/build artifact only
    - no arbitrary shell
    - no automatic execution
    - no git mutation
    - no destructive filesystem operations
    - preserves provenance and hashes
    - execution remains behind the existing governed self-drop boundary
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

MISSION = ROOT / ".barrot" / "autonomous_bundle" / "active_mission.json"
SPEC_DIR = ROOT / ".barrot" / "autonomous_bundle" / "specifications"
BUNDLE_DIR = ROOT / ".barrot" / "autonomous_bundle" / "generated"


PROTOCOL = "BARROT-V3-DEVELOPMENT-BUNDLE-BUILDER"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"required artifact missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"artifact must contain a JSON object: {path}")
    return value


def latest_spec() -> Path:
    candidates = sorted(SPEC_DIR.glob("development_bundle_*.json"))
    if not candidates:
        raise RuntimeError("no development bundle specification exists")
    return candidates[-1]


def unwrap_spec_record(spec: dict[str, Any]) -> dict[str, Any]:
    """
    Accept either:
      1. the raw development specification, or
      2. the persisted development_bundle_record.v1 wrapper.
    """
    if isinstance(spec.get("specification"), dict):
        inner = spec["specification"]

        if inner.get("protocol") == "BARROT-V3-DEVELOPMENT-BUNDLE-SPEC":
            return inner

    return spec


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """
    Validate the canonical barrot.development_bundle_spec.v1
    produced by barrot_bundle_spec_generator.py.

    Accepts either the raw specification or the persisted
    development_bundle_record.v1 wrapper.
    """
    spec = unwrap_spec_record(spec)

    required = {
        "schema",
        "protocol",
        "protocol_version",
        "task",
        "mission",
        "requested_work",
        "execution_boundary",
        "required_validation",
        "handoff",
        "spec_sha256",
    }

    missing = sorted(required - set(spec))
    if missing:
        raise RuntimeError(
            f"spec missing required fields: {missing}"
        )

    if spec["schema"] != "barrot.development_bundle_spec.v1":
        raise RuntimeError(
            "unexpected development specification schema"
        )

    if spec["protocol"] != (
        "BARROT-V3-DEVELOPMENT-BUNDLE-SPEC"
    ):
        raise RuntimeError(
            "unexpected development specification protocol"
        )

    task = spec["task"]
    mission = spec["mission"]
    requested = spec["requested_work"]
    boundary = spec["execution_boundary"]
    handoff = spec["handoff"]

    if not isinstance(task, dict):
        raise RuntimeError("spec.task must be an object")

    if not isinstance(mission, dict):
        raise RuntimeError("spec.mission must be an object")

    if not isinstance(requested, dict):
        raise RuntimeError(
            "spec.requested_work must be an object"
        )

    if not isinstance(boundary, dict):
        raise RuntimeError(
            "spec.execution_boundary must be an object"
        )

    if not isinstance(handoff, dict):
        raise RuntimeError(
            "spec.handoff must be an object"
        )

    if task.get("mode") != "GOVERNED_DEVELOPMENT":
        raise RuntimeError(
            "spec task is not governed development mode"
        )

    if task.get("execution_requested") is not False:
        raise RuntimeError(
            "spec execution_requested must be false"
        )

    for key in (
        "arbitrary_shell",
        "raw_command_payload",
        "automatic_execution",
        "destructive_git_operations",
        "unverified_mutation",
    ):
        if boundary.get(key) is not False:
            raise RuntimeError(
                f"execution boundary violation: {key}"
            )

    priorities = requested.get("priorities")
    targets = requested.get("current_build_targets")
    first_priority = requested.get("first_priority")

    if not isinstance(priorities, list) or not priorities:
        raise RuntimeError(
            "requested_work.priorities must be non-empty"
        )

    if not isinstance(targets, list):
        raise RuntimeError(
            "requested_work.current_build_targets "
            "must be a list"
        )

    if not isinstance(first_priority, str) or not first_priority.strip():
        raise RuntimeError(
            "requested_work.first_priority must be non-empty"
        )

    if handoff.get("status") != "SPECIFICATION_ONLY":
        raise RuntimeError(
            "specification must remain specification-only"
        )

    if handoff.get("executor") != (
        "existing_governed_self_drop"
    ):
        raise RuntimeError(
            "unexpected execution handoff"
        )

    return spec



def build_bundle(spec_path: Path) -> tuple[Path, Path]:
    mission = load_json(MISSION)
    spec_record = load_json(spec_path)
    spec = validate_spec(spec_record)

    timestamp = utc_stamp()
    bundle_id = f"development_bundle_{timestamp}"

    bundle = {
        "protocol": PROTOCOL,
        "bundle_id": bundle_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "BUILT_NOT_EXECUTED",
        "execution_requested": False,

        "mission": {
            "mission_file": str(MISSION.relative_to(ROOT)),
            "mission_sha256": sha256_file(MISSION),
            "objective": mission.get("objective"),
            "next_capability": mission.get(
                "handoff", {}
            ).get("next_capability"),
            "existing_capability": mission.get(
                "handoff", {}
            ).get("existing_capability"),
            "required_transition": mission.get(
                "handoff", {}
            ).get("required_transition"),
        },

        "specification": {
            "spec_file": str(spec_path.relative_to(ROOT)),
            "spec_sha256": spec["spec_sha256"],
            "spec_record_sha256": sha256_file(spec_path),
        },

        "development": {
            "first_priority": spec[
                "requested_work"
            ]["first_priority"],
            "priorities": spec[
                "requested_work"
            ]["priorities"],
            "current_build_targets": spec[
                "requested_work"
            ]["current_build_targets"],
            "objective": (
                "Implement the governed autonomous bundle-generation layer "
                "without granting arbitrary shell execution."
            ),
            "implementation_contract": [
                "Produce a deterministic structured bundle artifact.",
                "Carry mission and specification provenance into the bundle.",
                "Represent implementation intent as typed operations.",
                "Keep execution disabled until separately validated.",
                "Permit later handoff to the existing governed self-drop boundary.",
                "Record enough evidence to reproduce the bundle decision."
            ],
        },

        "operations": [
            {
                "operation_id": "GENERATE_GOVERNED_BUNDLE",
                "capability": "GENERATE_BUNDLE",
                "authorization": "MISSION_SPEC_BOUND",
                "inputs": [
                    "validated_development_specification"
                ],
                "outputs": [
                    "structured_bundle",
                    "provenance",
                    "sha256_evidence"
                ],
                "execution": "NOT_REQUESTED",
            },
            {
                "operation_id": "VALIDATE_GENERATED_BUNDLE",
                "capability": "VALIDATE_BUNDLE",
                "authorization": "GOVERNED_VALIDATION",
                "inputs": [
                    "structured_bundle"
                ],
                "outputs": [
                    "validation_result"
                ],
                "execution": "NOT_REQUESTED",
            },
            {
                "operation_id": "HANDOFF_TO_SELF_DROP",
                "capability": "EXECUTE_BUNDLE",
                "authorization": "EXPLICIT_GOVERNED_HANDOFF",
                "inputs": [
                    "validated_bundle"
                ],
                "outputs": [
                    "execution_evidence"
                ],
                "execution": "NOT_REQUESTED",
            },
        ],

        "governance": {
            "arbitrary_shell": spec[
                "execution_boundary"
            ]["arbitrary_shell"],
            "raw_command_payload": spec[
                "execution_boundary"
            ]["raw_command_payload"],
            "automatic_execution": spec[
                "execution_boundary"
            ]["automatic_execution"],
            "destructive_git_operations": spec[
                "execution_boundary"
            ]["destructive_git_operations"],
            "unverified_mutation": spec[
                "execution_boundary"
            ]["unverified_mutation"],
            "human_governance_boundary": True,
        },

        "required_validation": spec[
            "required_validation"
        ],

        "provenance": {
            "builder": str(Path(__file__).relative_to(ROOT)),
            "builder_sha256": sha256_file(Path(__file__)),
            "mission_sha256": sha256_file(MISSION),
            "spec_sha256": spec["spec_sha256"],
            "spec_record_sha256": sha256_file(spec_path),
        },

        "continuation": {
            "next_transition": (
                "BUILT_BUNDLE -> VALIDATED_BUNDLE -> "
                "GOVERNED_SELF_DROP_HANDOFF"
            ),
            "automatic_execution": False,
        },
    }

    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    payload = canonical_json(bundle)
    bundle_hash = sha256_bytes(payload)

    bundle["bundle_sha256"] = bundle_hash

    final_payload = json.dumps(
        bundle,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    ) + "\n"

    bundle_path = BUNDLE_DIR / f"{bundle_id}.json"
    bundle_path.write_text(final_payload, encoding="utf-8")

    evidence = {
        "protocol": PROTOCOL,
        "bundle_id": bundle_id,
        "bundle_file": str(bundle_path.relative_to(ROOT)),
        "bundle_sha256": sha256_file(bundle_path),
        "source_spec": str(spec_path.relative_to(ROOT)),
        "source_spec_sha256": sha256_file(spec_path),

        "source_spec_record_sha256": sha256_file(spec_path),
        "mission_file": str(MISSION.relative_to(ROOT)),
        "mission_sha256": sha256_file(MISSION),
        "status": "BUILT_NOT_EXECUTED",
        "execution_requested": False,
        "arbitrary_shell": False,
        "automatic_execution": False,
        "destructive_git": False,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    evidence_path = BUNDLE_DIR / f"{bundle_id}.evidence.json"
    evidence_path.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    return bundle_path, evidence_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path)
    args = parser.parse_args()

    spec_path = args.spec.resolve() if args.spec else latest_spec()

    bundle_path, evidence_path = build_bundle(spec_path)

    print("BARROT DEVELOPMENT BUNDLE BUILDER")
    print(f"PROTOCOL={PROTOCOL}")
    print("MODE=GOVERNED_DEVELOPMENT")
    print("EXECUTION_REQUESTED=FALSE")
    print("ARBITRARY_SHELL=FALSE")
    print("RAW_COMMAND_PAYLOAD=FALSE")
    print("AUTOMATIC_EXECUTION=FALSE")
    print("DESTRUCTIVE_GIT=FALSE")
    print(f"BUNDLE={bundle_path}")
    print(f"EVIDENCE={evidence_path}")
    print(f"BUNDLE_SHA256={sha256_file(bundle_path)}")
    print("DEVELOPMENT_BUNDLE_BUILD=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
