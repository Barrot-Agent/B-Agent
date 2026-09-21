from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MODULE_PATH = (
    ROOT
    / "scripts"
    / "barrot_bundle_validator.py"
)

spec = importlib.util.spec_from_file_location(
    "barrot_bundle_validator",
    MODULE_PATH,
)

module = importlib.util.module_from_spec(spec)

assert spec.loader is not None
spec.loader.exec_module(module)


def valid_bundle():
    return {
        "protocol":
            "BARROT-V3-DEVELOPMENT-BUNDLE-BUILDER",
        "bundle_id":
            "test_bundle",
        "status":
            "BUILT_NOT_EXECUTED",
        "execution_requested":
            False,

        "governance": {
            "arbitrary_shell": False,
            "raw_command_payload": False,
            "automatic_execution": False,
            "destructive_git_operations": False,
            "unverified_mutation": False,
            "human_governance_boundary": True,
        },

        "operations": [
            {
                "operation_id":
                    "GENERATE_GOVERNED_BUNDLE",
                "capability":
                    "GENERATE_BUNDLE",
                "authorization":
                    "MISSION_SPEC_BOUND",
                "execution":
                    "NOT_REQUESTED",
            }
        ],

        "provenance": {
            "builder_sha256": "a" * 64,
            "mission_sha256": "b" * 64,
            "spec_sha256": "c" * 64,
            "spec_record_sha256": "d" * 64,
        },
    }


def test_valid_bundle_passes(tmp_path):
    path = tmp_path / "bundle.json"

    import json

    path.write_text(
        json.dumps(valid_bundle()),
        encoding="utf-8",
    )

    result = module.validate_bundle(path)

    assert result["status"] == (
        "BUILT_NOT_EXECUTED"
    )


def test_arbitrary_shell_rejected(tmp_path):
    path = tmp_path / "bundle.json"

    import json

    bundle = valid_bundle()

    bundle["governance"][
        "arbitrary_shell"
    ] = True

    path.write_text(
        json.dumps(bundle),
        encoding="utf-8",
    )

    try:
        module.validate_bundle(path)
    except module.BundleValidationError:
        pass
    else:
        raise AssertionError(
            "arbitrary shell must be rejected"
        )


def test_automatic_execution_rejected(tmp_path):
    path = tmp_path / "bundle.json"

    import json

    bundle = valid_bundle()

    bundle["execution_requested"] = True

    path.write_text(
        json.dumps(bundle),
        encoding="utf-8",
    )

    try:
        module.validate_bundle(path)
    except module.BundleValidationError:
        pass
    else:
        raise AssertionError(
            "automatic execution must be rejected"
        )


def test_executable_operation_rejected(tmp_path):
    path = tmp_path / "bundle.json"

    import json

    bundle = valid_bundle()

    bundle["operations"][0][
        "execution"
    ] = "REQUESTED"

    path.write_text(
        json.dumps(bundle),
        encoding="utf-8",
    )

    try:
        module.validate_bundle(path)
    except module.BundleValidationError:
        pass
    else:
        raise AssertionError(
            "executable operation must be rejected"
        )


def test_missing_provenance_rejected(tmp_path):
    path = tmp_path / "bundle.json"

    import json

    bundle = valid_bundle()

    del bundle["provenance"][
        "spec_sha256"
    ]

    path.write_text(
        json.dumps(bundle),
        encoding="utf-8",
    )

    try:
        module.validate_bundle(path)
    except module.BundleValidationError:
        pass
    else:
        raise AssertionError(
            "missing provenance must be rejected"
        )
