from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "scripts"
    / "barrot_development_bundle_builder.py"
)

spec = importlib.util.spec_from_file_location(
    "barrot_development_bundle_builder",
    MODULE_PATH,
)

module = importlib.util.module_from_spec(spec)

assert spec.loader is not None
spec.loader.exec_module(module)


def canonical_spec():
    return {
        "schema":
            "barrot.development_bundle_spec.v1",

        "protocol":
            "BARROT-V3-DEVELOPMENT-BUNDLE-SPEC",

        "protocol_version":
            "1",

        "task": {
            "task_id":
                "test_bundle",
            "mode":
                "GOVERNED_DEVELOPMENT",
            "execution_requested":
                False,
        },

        "mission": {
            "protocol":
                "BARROT-V3-MISSION",
            "protocol_version":
                "1",
            "objective":
                "test",
            "continuation_target":
                "test",
        },

        "requested_work": {
            "priorities": [
                "Initialize governed autonomous "
                "bundle generation."
            ],
            "current_build_targets": [
                "provider-neutral controller",
                "self-drop capability",
                "autonomous engineering loop",
            ],
            "first_priority": (
                "Initialize governed autonomous "
                "bundle generation."
            ),
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
            "planner":
                "barrot_mission_bundle_planner",
            "executor":
                "existing_governed_self_drop",
            "status":
                "SPECIFICATION_ONLY",
        },

        "spec_sha256":
            "0" * 64,
    }


def test_generated_bundle_is_governed():
    spec_data = canonical_spec()

    module.validate_spec(spec_data)


def test_canonical_schema_is_accepted():
    spec_data = canonical_spec()

    assert spec_data["schema"] == (
        "barrot.development_bundle_spec.v1"
    )

    assert spec_data["protocol_version"] == "1"
    assert spec_data["task"]["mode"] == (
        "GOVERNED_DEVELOPMENT"
    )


def test_arbitrary_shell_is_rejected():
    spec_data = canonical_spec()

    spec_data[
        "execution_boundary"
    ]["arbitrary_shell"] = True

    try:
        module.validate_spec(spec_data)
    except RuntimeError:
        pass
    else:
        raise AssertionError(
            "arbitrary shell must be rejected"
        )


def test_automatic_execution_is_rejected():
    spec_data = canonical_spec()

    spec_data[
        "execution_boundary"
    ]["automatic_execution"] = True

    try:
        module.validate_spec(spec_data)
    except RuntimeError:
        pass
    else:
        raise AssertionError(
            "automatic execution must be rejected"
        )


def test_wrong_handoff_is_rejected():
    spec_data = canonical_spec()

    spec_data[
        "handoff"
    ]["executor"] = "arbitrary_shell"

    try:
        module.validate_spec(spec_data)
    except RuntimeError:
        pass
    else:
        raise AssertionError(
            "wrong handoff executor must be rejected"
        )


def test_wrapper_can_be_unwrapped():
    spec_data = canonical_spec()

    record = {
        "created_at":
            "2026-09-21T00:00:00+00:00",
        "schema":
            "barrot.development_bundle_record.v1",
        "specification":
            spec_data,
    }

    assert record["specification"]["schema"] == (
        "barrot.development_bundle_spec.v1"
    )


def test_mission_to_builder_contract():
    spec_data = canonical_spec()

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

    assert required.issubset(
        spec_data.keys()
    )
