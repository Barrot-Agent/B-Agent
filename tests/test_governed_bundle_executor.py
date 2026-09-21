from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MODULE_PATH = (
    ROOT
    / "scripts"
    / "barrot_governed_bundle_executor.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "barrot_governed_bundle_executor",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_artifacts(tmp_path: Path):
    module = load_module()

    bundle = {
        "protocol":
            "BARROT-V3-DEVELOPMENT-BUNDLE-BUILDER",
        "bundle_id":
            "development_bundle_test",
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
    }

    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(
        json.dumps(bundle, sort_keys=True),
        encoding="utf-8",
    )

    bundle_hash = module.sha256_file(bundle_path)

    handoff = {
        "schema":
            "barrot.governed_bundle_handoff.v1",
        "protocol":
            "BARROT-V3-DEVELOPMENT-BUNDLE-VALIDATOR",
        "handoff": {
            "status":
                "VALIDATED_NOT_EXECUTED",
            "executor":
                "existing_governed_self_drop",
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
        "allowed_transition":
            "VALIDATED_BUNDLE -> GOVERNED_SELF_DROP",
        "source_bundle": {
            "path": "bundle.json",
            "sha256": bundle_hash,
        },
    }

    handoff_path = tmp_path / "handoff.json"
    handoff_path.write_text(
        json.dumps(handoff, sort_keys=True),
        encoding="utf-8",
    )

    return module, bundle_path, handoff_path


def test_validated_handoff_is_recorded_without_execution(
    tmp_path,
    monkeypatch,
):
    module, bundle_path, handoff_path = make_artifacts(
        tmp_path
    )

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(
        module,
        "EVIDENCE_DIR",
        tmp_path / "evidence",
    )

    evidence_path = module.execute_validated_handoff(
        handoff_path,
        bundle_path,
    )

    evidence = json.loads(
        evidence_path.read_text(encoding="utf-8")
    )

    assert evidence["execution_performed"] is False
    assert evidence["repository_mutation"] is False
    assert evidence["arbitrary_shell"] is False
    assert evidence["raw_command_payload"] is False
    assert evidence["destructive_git_operations"] is False
    assert evidence["automatic_execution"] is False


def test_tampered_bundle_is_rejected(tmp_path):
    module, bundle_path, handoff_path = make_artifacts(
        tmp_path
    )

    bundle_path.write_text(
        bundle_path.read_text(encoding="utf-8")
        + "\n",
        encoding="utf-8",
    )

    try:
        module.validate_handoff(
            handoff_path,
            bundle_path,
        )
    except module.GovernedBundleExecutionError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError(
            "tampered bundle was accepted"
        )


def test_executable_operation_is_rejected(tmp_path):
    module, bundle_path, handoff_path = make_artifacts(
        tmp_path
    )

    data = json.loads(
        bundle_path.read_text(encoding="utf-8")
    )

    data["operations"][0]["execution"] = "REQUESTED"

    bundle_path.write_text(
        json.dumps(data, sort_keys=True),
        encoding="utf-8",
    )

    # The handoff must bind to the exact bundle bytes being tested.
    # Recompute its hash so this test reaches the operation-policy
    # gate rather than failing first at the integrity gate.
    handoff = json.loads(
        handoff_path.read_text(encoding="utf-8")
    )
    handoff["source_bundle"]["sha256"] = (
        module.sha256_file(bundle_path)
    )
    handoff_path.write_text(
        json.dumps(handoff, sort_keys=True),
        encoding="utf-8",
    )

    try:
        module.validate_handoff(
            handoff_path,
            bundle_path,
        )
    except module.GovernedBundleExecutionError as exc:
        assert "executable operation" in str(exc)
    else:
        raise AssertionError(
            "executable operation was accepted"
        )
