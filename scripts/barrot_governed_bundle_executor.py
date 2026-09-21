#!/usr/bin/env python3
"""
Barrot V3 — Governed Development Bundle Executor.

Consumes an already validated development bundle and its governed handoff.

This executor deliberately does NOT:
  - accept arbitrary shell;
  - accept raw command payloads;
  - execute the existing SELF_DROP_PROBE;
  - mutate repository files;
  - perform destructive Git operations;
  - automatically execute a BUILT_NOT_EXECUTED bundle.

The first supported transition is a governed capability handoff/no-op.
Actual repository mutation requires a future typed-operation contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

HANDOFF_DIR = (
    ROOT / ".barrot" / "autonomous_bundle" / "handoff"
)

EVIDENCE_DIR = (
    ROOT / ".barrot" / "autonomous_bundle" / "execution_evidence"
)

PROTOCOL = "BARROT-V3-GOVERNED-BUNDLE-EXECUTOR"
SCHEMA = "barrot.governed_bundle_execution.v1"

ALLOWED_TRANSITION = (
    "VALIDATED_BUNDLE -> GOVERNED_SELF_DROP"
)

SUPPORTED_CAPABILITIES = {
    "GENERATE_BUNDLE",
    "VALIDATE_BUNDLE",
    "EXECUTE_BUNDLE",
}


class GovernedBundleExecutionError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise GovernedBundleExecutionError(
            f"missing artifact: {path}"
        )

    try:
        value = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise GovernedBundleExecutionError(
            f"invalid JSON: {path}: {exc}"
        ) from exc

    if not isinstance(value, dict):
        raise GovernedBundleExecutionError(
            f"artifact must be a JSON object: {path}"
        )

    return value


def validate_handoff(
    handoff_path: Path,
    bundle_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], str]:

    handoff = load_json(handoff_path)
    bundle = load_json(bundle_path)

    if handoff.get("schema") != (
        "barrot.governed_bundle_handoff.v1"
    ):
        raise GovernedBundleExecutionError(
            "unexpected handoff schema"
        )

    if handoff.get("protocol") != (
        "BARROT-V3-DEVELOPMENT-BUNDLE-VALIDATOR"
    ):
        raise GovernedBundleExecutionError(
            "unexpected handoff protocol"
        )

    if handoff.get("allowed_transition") != ALLOWED_TRANSITION:
        raise GovernedBundleExecutionError(
            "handoff transition is not authorized"
        )

    handoff_state = handoff.get("handoff")

    if not isinstance(handoff_state, dict):
        raise GovernedBundleExecutionError(
            "handoff state missing"
        )

    if handoff_state.get("status") != (
        "VALIDATED_NOT_EXECUTED"
    ):
        raise GovernedBundleExecutionError(
            "handoff is not VALIDATED_NOT_EXECUTED"
        )

    if handoff_state.get("executor") != (
        "existing_governed_self_drop"
    ):
        raise GovernedBundleExecutionError(
            "handoff executor is not governed self-drop"
        )

    authorization = handoff.get("authorization")

    if not isinstance(authorization, dict):
        raise GovernedBundleExecutionError(
            "handoff authorization missing"
        )

    required_false = (
        "arbitrary_shell",
        "raw_command_payload",
        "automatic_execution",
        "destructive_git_operations",
        "unverified_mutation",
    )

    for key in required_false:
        if authorization.get(key) is not False:
            raise GovernedBundleExecutionError(
                f"authorization violation: {key}"
            )

    if authorization.get("bundle_validated") is not True:
        raise GovernedBundleExecutionError(
            "bundle has not been validated"
        )

    if authorization.get("mission_bound") is not True:
        raise GovernedBundleExecutionError(
            "handoff is not mission-bound"
        )

    if authorization.get("specification_bound") is not True:
        raise GovernedBundleExecutionError(
            "handoff is not specification-bound"
        )

    if authorization.get(
        "human_governance_boundary"
    ) is not True:
        raise GovernedBundleExecutionError(
            "human governance boundary missing"
        )

    source_bundle = handoff.get("source_bundle")

    if not isinstance(source_bundle, dict):
        raise GovernedBundleExecutionError(
            "source_bundle missing"
        )

    try:
        expected_path = str(
            bundle_path.relative_to(ROOT)
        )
    except ValueError:
        # Isolated test artifacts may live outside the repository
        # root. Keep the identity check deterministic without
        # weakening the cryptographic binding.
        expected_path = bundle_path.name

    source_path = source_bundle.get("path")

    if source_path != expected_path:
        # Permit the absolute path only for isolated artifacts.
        # Repository-bound handoffs must remain repository-relative.
        if bundle_path.is_relative_to(ROOT):
            raise GovernedBundleExecutionError(
                "handoff points to a different bundle"
            )

        if source_path != bundle_path.name:
            raise GovernedBundleExecutionError(
                "handoff points to a different bundle"
            )

    actual_hash = sha256_file(bundle_path)

    if source_bundle.get("sha256") != actual_hash:
        raise GovernedBundleExecutionError(
            "bundle SHA-256 does not match governed handoff"
        )

    if bundle.get("status") != "BUILT_NOT_EXECUTED":
        raise GovernedBundleExecutionError(
            "bundle is not BUILT_NOT_EXECUTED"
        )

    if bundle.get("execution_requested") is not False:
        raise GovernedBundleExecutionError(
            "bundle execution_requested must remain false"
        )

    governance = bundle.get("governance")

    if not isinstance(governance, dict):
        raise GovernedBundleExecutionError(
            "bundle governance missing"
        )

    for key in required_false:
        if governance.get(key) is not False:
            raise GovernedBundleExecutionError(
                f"bundle governance violation: {key}"
            )

    operations = bundle.get("operations")

    if not isinstance(operations, list) or not operations:
        raise GovernedBundleExecutionError(
            "bundle operations missing"
        )

    for operation in operations:
        if not isinstance(operation, dict):
            raise GovernedBundleExecutionError(
                "operation must be an object"
            )

        required = {
            "operation_id",
            "capability",
            "authorization",
            "execution",
        }

        missing = required - set(operation)

        if missing:
            raise GovernedBundleExecutionError(
                f"operation missing fields: {sorted(missing)}"
            )

        if operation["execution"] != "NOT_REQUESTED":
            raise GovernedBundleExecutionError(
                "executable operation found in "
                "non-executable bundle"
            )

        if operation["capability"] not in SUPPORTED_CAPABILITIES:
            raise GovernedBundleExecutionError(
                "unsupported capability: "
                f"{operation['capability']}"
            )

    return handoff, bundle, actual_hash


def execute_validated_handoff(
    handoff_path: Path,
    bundle_path: Path,
) -> Path:

    handoff, bundle, bundle_hash = validate_handoff(
        handoff_path,
        bundle_path,
    )

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    evidence_path = (
        EVIDENCE_DIR
        / f"execution_{timestamp}.json"
    )

    evidence = {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "HANDOFF_VALIDATED_NOT_EXECUTED",
        "execution_performed": False,
        "repository_mutation": False,
        "arbitrary_shell": False,
        "raw_command_payload": False,
        "destructive_git_operations": False,
        "automatic_execution": False,
        "unverified_mutation": False,
        "human_governance_boundary": True,
        "bundle": {
            "path": str(bundle_path.relative_to(ROOT)),
            "sha256": bundle_hash,
            "bundle_id": bundle["bundle_id"],
        },
        "handoff": {
            "path": str(handoff_path.relative_to(ROOT)),
            "schema": handoff["schema"],
            "allowed_transition": handoff[
                "allowed_transition"
            ],
        },
        "supported_operations": [
            operation["operation_id"]
            for operation in bundle["operations"]
        ],
        "decision": (
            "VALIDATED_HANDOFF_RECORDED; "
            "NO_BUNDLE_EXECUTION_REQUESTED"
        ),
    }

    evidence_path.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    return evidence_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bundle",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--handoff",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    bundle_path = args.bundle.resolve()
    handoff_path = args.handoff.resolve()

    evidence = execute_validated_handoff(
        handoff_path,
        bundle_path,
    )

    print("BARROT GOVERNED BUNDLE EXECUTOR")
    print(f"PROTOCOL={PROTOCOL}")
    print("HANDOFF_VALIDATION=PASS")
    print("BUNDLE_EXECUTION=NOT_PERFORMED")
    print("REPOSITORY_MUTATION=FALSE")
    print("ARBITRARY_SHELL=FALSE")
    print("RAW_COMMAND_PAYLOAD=FALSE")
    print("DESTRUCTIVE_GIT=FALSE")
    print("AUTOMATIC_EXECUTION=FALSE")
    print("HUMAN_GOVERNANCE_BOUNDARY=TRUE")
    print(f"EVIDENCE={evidence}")
    print("GOVERNED_EXECUTOR=PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
