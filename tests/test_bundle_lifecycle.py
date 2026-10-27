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



def test_task_evidence_is_append_only_and_latest_state_survives_reload(tmp_path):
    store = BundleLifecycleStore(tmp_path)
    store.save_plan("resume-me", Result())
    store.record_task_execution("resume-me", "task-a", {"status": "RUNNING"})
    store.record_task_execution("resume-me", "task-a", {"status": "COMPLETE", "queue_advanced": True})
    latest = store.latest_task_states("resume-me")
    assert latest["task-a"]["status"] == "COMPLETE"
    payload = store.load("resume-me")
    assert len(payload["task_states"]["task-a"]) == 2


def test_task_evidence_requires_existing_plan_and_task_id(tmp_path):
    store = BundleLifecycleStore(tmp_path)
    with pytest.raises(FileNotFoundError):
        store.record_task_execution("missing", "task-a", {"status": "RUNNING"})
    store.save_plan("resume-me", Result())
    with pytest.raises(ValueError, match="task_id"):
        store.record_task_execution("resume-me", " ", {"status": "RUNNING"})


def test_save_plan_preserves_execution_evidence_for_identical_bundle(tmp_path):
    store = BundleLifecycleStore(tmp_path)
    result = Result()
    store.save_plan("resume-me", result)
    store.record_task_execution("resume-me", "task-a", {"status": "COMPLETE"})
    store.record_execution("resume-me", {"status": "COMPLETE"})
    store.save_plan("resume-me", result)
    payload = store.load("resume-me")
    assert payload["task_states"]["task-a"][-1]["status"] == "COMPLETE"
    assert payload["execution_evidence"][-1]["status"] == "COMPLETE"



def _complete_task_result(task_id):
    return {
        "status": "complete",
        "queue_advanced": True,
        "repair_cycle": {
            "cycle_id": "cycle-" + task_id,
            "status": "complete",
            "local_validation_passed": True,
            "resolution_verified": True,
            "commit": {"sha": "sha-" + task_id, "remote_verified": True},
        },
    }


def test_dispatcher_respects_dependencies_and_records_evidence(tmp_path):
    from barrot_agent.orchestration.bundle_lifecycle import dispatch_bundle_tasks

    store = BundleLifecycleStore(tmp_path)
    store.save_plan("bundle", Result())
    bundle = {"tasks": [
        {"id": "task-c", "depends_on": ["task-b"]},
        {"id": "task-a", "depends_on": []},
        {"id": "task-b", "depends_on": ["task-a"]},
    ]}
    calls = []
    result = dispatch_bundle_tasks(
        store=store,
        work_id="bundle",
        bundle=bundle,
        execute_task=lambda task: (calls.append(task["id"]) or _complete_task_result(task["id"])),
    )
    assert result["complete"] is True
    assert calls == ["task-a", "task-b", "task-c"]
    states = store.latest_task_states("bundle")
    assert all(states[task_id]["status"] == "complete" for task_id in calls)
    assert states["task-a"]["result"]["repair_cycle"]["commit"]["sha"] == "sha-task-a"


def test_dispatcher_resume_skips_completed_tasks(tmp_path):
    from barrot_agent.orchestration.bundle_lifecycle import dispatch_bundle_tasks

    store = BundleLifecycleStore(tmp_path)
    store.save_plan("bundle", Result())
    store.record_task_execution("bundle", "task-a", {
        "status": "complete", "queue_advanced": True, "local_validation_passed": True,
        "remote_verified": True, "resolution_verified": True, "result": _complete_task_result("task-a"),
    })
    calls = []
    bundle = {"tasks": [
        {"id": "task-a", "depends_on": []},
        {"id": "task-b", "depends_on": ["task-a"]},
    ]}
    result = dispatch_bundle_tasks(
        store=store,
        work_id="bundle",
        bundle=bundle,
        execute_task=lambda task: (calls.append(task["id"]) or _complete_task_result(task["id"])),
    )
    assert result["complete"] is True
    assert calls == ["task-b"]
    assert result["last_result"]["repair_cycle"]["cycle_id"] == "cycle-task-b"


def test_dispatcher_blocks_dependents_when_prerequisite_fails(tmp_path):
    from barrot_agent.orchestration.bundle_lifecycle import dispatch_bundle_tasks

    store = BundleLifecycleStore(tmp_path)
    store.save_plan("bundle", Result())
    calls = []
    bundle = {"tasks": [
        {"id": "task-a", "depends_on": []},
        {"id": "task-b", "depends_on": ["task-a"]},
        {"id": "task-c", "depends_on": []},
    ]}
    def execute(task):
        calls.append(task["id"])
        if task["id"] == "task-a":
            return {"status": "failed", "queue_advanced": False, "repair_cycle": {"status": "failed"}}
        return _complete_task_result(task["id"])
    result = dispatch_bundle_tasks(store=store, work_id="bundle", bundle=bundle, execute_task=execute)
    assert result["complete"] is False
    assert calls == ["task-a", "task-c"]
    assert "task-b" in result["blocked_tasks"]



def test_dispatcher_increments_attempt_after_interrupted_failed_attempt(tmp_path):
    from barrot_agent.orchestration.bundle_lifecycle import dispatch_bundle_tasks

    store = BundleLifecycleStore(tmp_path)
    store.save_plan("bundle", Result())
    store.record_task_execution("bundle", "task-a", {"status": "failed", "reason": "transient"})
    result = dispatch_bundle_tasks(
        store=store,
        work_id="bundle",
        bundle={"tasks": [{"id": "task-a", "depends_on": []}]},
        execute_task=lambda task: _complete_task_result(task["id"]),
    )
    assert result["complete"] is True
    history = store.load("bundle")["task_states"]["task-a"]
    running_records = [item for item in history if item.get("status") == "running"]
    assert running_records[-1]["attempt"] == 2
