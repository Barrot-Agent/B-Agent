import json

import pytest

from barrot_agent.orchestration.bundle_lifecycle import BundleLifecycleStore


class Review:
    def to_dict(self):
        return {"valid": True, "quality_score": 100, "fingerprint": "sha256:test", "findings": []}


class Result:
    status = "READY_FOR_EXECUTION_REVIEW"
    bundle = {"bundle_id": "unit-test"}
    review = Review()
    attempts = [{"kind": "draft", "accepted": True}]


def test_lifecycle_persists_plan_and_execution_evidence(tmp_path):
    store = BundleLifecycleStore(tmp_path)
    path = store.save_plan("issue-12:branch", Result())
    assert path.exists()
    saved = store.load("issue-12:branch")
    assert saved["status"] == "READY_FOR_EXECUTION_REVIEW"
    assert saved["review"]["valid"] is True
    assert saved["execution_evidence"] == []

    store.record_execution("issue-12:branch", {
        "status": "BLOCKED",
        "cycle_id": "cycle-1",
        "local_validation_passed": False,
    })
    saved = store.load("issue-12:branch")
    assert saved["execution_status"] == "BLOCKED"
    assert saved["execution_evidence"][0]["cycle_id"] == "cycle-1"


def test_lifecycle_rejects_empty_work_id(tmp_path):
    store = BundleLifecycleStore(tmp_path)
    with pytest.raises(ValueError, match="work_id"):
        store.save_plan(" ", Result())


def test_execution_cannot_start_without_persisted_plan(tmp_path):
    store = BundleLifecycleStore(tmp_path)
    with pytest.raises(FileNotFoundError):
        store.record_execution("missing", {"status": "COMPLETE"})


def test_lifecycle_does_not_interpolate_work_id_into_path(tmp_path):
    store = BundleLifecycleStore(tmp_path)
    path = store.save_plan("../../outside", Result())
    assert path.resolve().is_relative_to((tmp_path / ".git" / "barrot_repair" / "bundles").resolve())
    assert json.loads(path.read_text())["work_id"] == "../../outside"


def test_live_entrypoint_wires_bundle_gate_before_repair():
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    source = (root / "scripts" / "barrot_agent.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert "BundleEngineeringController" in imports
    assert "BundleLifecycleStore" in imports
    assert "BundleEngineeringController" in source
    assert "READY_FOR_EXECUTION_REVIEW" in source
    assert "record_execution" in source
    assert "WorkQueueController" in imports
