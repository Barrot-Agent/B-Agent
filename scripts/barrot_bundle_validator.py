#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

BUNDLE_DIR = (
    ROOT / ".barrot" / "autonomous_bundle" / "generated"
)

HANDOFF_DIR = (
    ROOT / ".barrot" / "autonomous_bundle" / "handoff"
)

PROTOCOL = "BARROT-V3-DEVELOPMENT-BUNDLE-VALIDATOR"
VERSION = "1"


class BundleValidationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise BundleValidationError(
            f"missing artifact: {path}"
        )

    value = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(value, dict):
        raise BundleValidationError(
            f"artifact is not a JSON object: {path}"
        )

    return value


def latest_bundle() -> Path:
    candidates = sorted(
        BUNDLE_DIR.glob(
            "development_bundle_*.json"
        )
    )

    if not candidates:
        raise BundleValidationError(
            "no generated development bundle exists"
        )

    return candidates[-1]


def validate_bundle(
    bundle_path: Path,
) -> dict[str, Any]:

    data = load_json(bundle_path)

    if data.get("protocol") != (
        "BARROT-V3-DEVELOPMENT-BUNDLE-BUILDER"
    ):
        raise BundleValidationError(
            "unexpected bundle protocol"
        )

    if data.get("status") != (
        "BUILT_NOT_EXECUTED"
    ):
        raise BundleValidationError(
            "bundle is not in BUILT_NOT_EXECUTED state"
        )

    if data.get("execution_requested") is not False:
        raise BundleValidationError(
            "bundle execution_requested must be false"
        )

    governance = data.get("governance")

    if not isinstance(governance, dict):
        raise BundleValidationError(
            "bundle governance is missing"
        )

    forbidden_true = (
        "arbitrary_shell",
        "raw_command_payload",
        "automatic_execution",
        "destructive_git_operations",
        "unverified_mutation",
    )

    for key in forbidden_true:
        if governance.get(key) is not False:
            raise BundleValidationError(
                f"governance violation: {key}"
            )

    if governance.get(
        "human_governance_boundary"
    ) is not True:
        raise BundleValidationError(
            "human governance boundary missing"
        )

    operations = data.get("operations")

    if not isinstance(operations, list):
        raise BundleValidationError(
            "operations must be a list"
        )

    if not operations:
        raise BundleValidationError(
            "bundle contains no operations"
        )

    for operation in operations:
        if not isinstance(operation, dict):
            raise BundleValidationError(
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
            raise BundleValidationError(
                f"operation missing fields: {sorted(missing)}"
            )

        if operation["execution"] != "NOT_REQUESTED":
            raise BundleValidationError(
                "bundle contains an executable operation"
            )

    provenance = data.get("provenance")

    if not isinstance(provenance, dict):
        raise BundleValidationError(
            "provenance missing"
        )

    for key in (
        "builder_sha256",
        "mission_sha256",
        "spec_sha256",
        "spec_record_sha256",
    ):
        value = provenance.get(key)

        if not isinstance(value, str):
            raise BundleValidationError(
                f"missing provenance hash: {key}"
            )

        if len(value) != 64:
            raise BundleValidationError(
                f"invalid provenance hash: {key}"
            )

    return data


def create_handoff(
    bundle_path: Path,
    bundle: dict[str, Any],
) -> Path:

    HANDOFF_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    bundle_hash = sha256_file(bundle_path)

    request = {
        "schema": (
            "barrot.governed_bundle_handoff.v1"
        ),
        "protocol": PROTOCOL,
        "protocol_version": VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "handoff": {
            "status": "VALIDATED_NOT_EXECUTED",
            "executor": (
                "existing_governed_self_drop"
            ),
            "execution_requested": False,
        },

        "source_bundle": {
            "path": str(
                bundle_path.relative_to(ROOT)
            ),
            "sha256": bundle_hash,
            "protocol": bundle["protocol"],
            "bundle_id": bundle["bundle_id"],
        },

        "authorization": {
            "mission_bound": True,
            "specification_bound": True,
            "bundle_validated": True,
            "arbitrary_shell": False,
            "raw_command_payload": False,
            "automatic_execution": False,
            "destructive_git_operations": False,
            "unverified_mutation": False,
            "human_governance_boundary": True,
        },

        "allowed_transition": (
            "VALIDATED_BUNDLE -> "
            "GOVERNED_SELF_DROP"
        ),

        "execution": {
            "requested": False,
            "reason": (
                "Validation and handoff preparation "
                "only. Execution requires a separate "
                "governed authorization path."
            ),
        },
    }

    path = HANDOFF_DIR / (
        f"handoff_{stamp}.json"
    )

    path.write_text(
        json.dumps(
            request,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bundle",
        type=Path,
    )
    args = parser.parse_args()

    bundle_path = (
        args.bundle.resolve()
        if args.bundle
        else latest_bundle()
    )

    bundle = validate_bundle(
        bundle_path
    )

    handoff = create_handoff(
        bundle_path,
        bundle,
    )

    print(
        "BARROT DEVELOPMENT BUNDLE VALIDATOR"
    )
    print(
        f"PROTOCOL={PROTOCOL}"
    )
    print(
        "VALIDATION=PASS"
    )
    print(
        "BUNDLE_STATUS=VALIDATED_NOT_EXECUTED"
    )
    print(
        "ARBITRARY_SHELL=FALSE"
    )
    print(
        "RAW_COMMAND_PAYLOAD=FALSE"
    )
    print(
        "AUTOMATIC_EXECUTION=FALSE"
    )
    print(
        "DESTRUCTIVE_GIT=FALSE"
    )
    print(
        "PROVENANCE=PASS"
    )
    print(
        f"BUNDLE_SHA256={sha256_file(bundle_path)}"
    )
    print(
        f"HANDOFF={handoff}"
    )
    print(
        "GOVERNED_HANDOFF=READY"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
