"""MOCKED end-to-end test of scripts/barrot_agent.py main() bundle orchestration.

This is NOT a live Groq/provider run. The LLM brain, bundle author, GitHub CLI calls,
and per-task repair queue are replaced with deterministic fakes. What is real:
main() control flow, request fingerprinting, BundleLifecycleStore persistence on
disk, dispatch_bundle_tasks dependency ordering, resume, and the no-change / PR gates.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "barrot_agent.py"


def _load(name, monkeypatch, tmp_path, title="Repair issue", body="Fix the reproduced issue."):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", body)
    monkeypatch.setenv("TASK_TITLE", title)
    monkeypatch.setenv("ISSUE_NUMBER", "77")
    monkeypatch.setenv("BRANCH", "barrot/task-77")
    monkeypatch.setenv("GROQ_API_KEY", "mocked-not-a-real-key")
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    return module


BUNDLE = {
    "objective": "Repair issue",
    "tasks": [
        {"id": "task-b", "title": "B", "description": "second", "depends_on": ["task-a"],
         "files": [], "acceptance_criteria": ["ok"], "tests": ["t"], "rollback_plan": ["r"]},
        {"id": "task-a", "title": "A", "description": "first", "depends_on": [],
         "files": [], "acceptance_criteria": ["ok"], "tests": ["t"], "rollback_plan": ["r"]},
    ],
}


def _complete(task_id):
    return {"status": "complete", "queue_advanced": True, "repair_cycle": {
        "cycle_id": "c-" + task_id, "status": "complete", "local_validation_passed": True,
        "resolution_verified": True, "commit": {"sha": "sha-" + task_id, "remote_verified": True}}}


def _no_change(task_id):
    return {"status": "complete", "queue_advanced": True, "repair_cycle": {
        "cycle_id": "c-" + task_id, "status": "no_repair_required", "report_only": False,
        "issue_reproduced": False, "local_validation_passed": True, "resolution_verified": False,
        "validation": {"issue_reproduction": {"issue_reproduced": False}},
        "commit": {"sha": "", "remote_verified": False}}}


def _wire(module, monkeypatch, calls, task_result, interrupt_on=None):
    class FakeBrain:  # no network: any LLM call would be a test failure
        def __init__(self, *a, **k):
            pass

        def think(self, *a, **k):
            raise AssertionError("mocked e2e must not call the LLM")

    class FakeBundleController:
        def __init__(self, *a, **k):
            pass

        def run(self, **kwargs):
            calls.setdefault("bundle_authored", 0)
            calls["bundle_authored"] += 1
            return SimpleNamespace(
                status="READY_FOR_EXECUTION_REVIEW", bundle=BUNDLE, attempts=(),
                review=SimpleNamespace(quality_score=100, fingerprint="sha256:mock", to_dict=lambda: {"valid": True}),
            )

    class FakeQueue:
        def __init__(self, **kwargs):
            self.work_store = SimpleNamespace(load=lambda work_id: None)

        def run(self, **kwargs):
            task_id = kwargs["work_id"].rsplit(":task:", 1)[-1]
            if task_id == interrupt_on:
                raise KeyboardInterrupt("simulated process kill")
            calls.setdefault("executed", []).append(task_id)
            return task_result(task_id)

    monkeypatch.setattr(module, "ScriptBrain", FakeBrain)
    monkeypatch.setattr(module, "BundleEngineeringController", FakeBundleController)
    monkeypatch.setattr(module, "RepositoryRepairController", lambda **k: None)
    monkeypatch.setattr(module, "WorkQueueController", FakeQueue)
    monkeypatch.setattr(module, "configure_git", lambda: None)
    monkeypatch.setattr(module, "checkout_branch", lambda b: None)
    monkeypatch.setattr(module, "build_audit_context", lambda t, b: {"inventory": ""})
    monkeypatch.setattr(module, "post_issue_comment", lambda m: calls.setdefault("comments", []).append(m))
    monkeypatch.setattr(module, "create_pull_request", lambda w: calls.setdefault("prs", []).append(w))
    monkeypatch.setattr(module, "write_collaboration_record", lambda c: None)


def test_mocked_main_runs_tasks_in_order_and_opens_one_pr(monkeypatch, tmp_path):
    module = _load("mock_e2e_ok", monkeypatch, tmp_path)
    calls = {}
    _wire(module, monkeypatch, calls, _complete)
    module.main()
    assert calls["executed"] == ["task-a", "task-b"]
    assert len(calls["prs"]) == 1


def test_mocked_main_resumes_after_kill_without_repeating_completed_task(monkeypatch, tmp_path):
    module = _load("mock_e2e_kill", monkeypatch, tmp_path)
    calls = {}
    _wire(module, monkeypatch, calls, _complete, interrupt_on="task-b")
    with pytest.raises(KeyboardInterrupt):
        module.main()
    assert calls["executed"] == ["task-a"]
    assert "prs" not in calls

    fresh = _load("mock_e2e_kill_resume", monkeypatch, tmp_path)
    calls2 = {}
    _wire(fresh, monkeypatch, calls2, _complete)
    fresh.main()
    assert calls2["executed"] == ["task-b"]          # task-a not repeated
    assert len(calls2["prs"]) == 1


def test_mocked_main_changed_task_body_discards_resume_state(monkeypatch, tmp_path):
    module = _load("mock_e2e_fp", monkeypatch, tmp_path)
    calls = {}
    _wire(module, monkeypatch, calls, _complete, interrupt_on="task-b")
    with pytest.raises(KeyboardInterrupt):
        module.main()
    fresh = _load("mock_e2e_fp2", monkeypatch, tmp_path, body="A different request body.")
    calls2 = {}
    _wire(fresh, monkeypatch, calls2, _complete)
    fresh.main()
    assert calls2["bundle_authored"] == 1
    assert calls2["executed"] == ["task-a", "task-b"]


def test_mocked_main_verified_no_change_creates_no_pr(monkeypatch, tmp_path):
    module = _load("mock_e2e_nochange", monkeypatch, tmp_path)
    calls = {}
    _wire(module, monkeypatch, calls, _no_change)
    # Root task verified no-change => dependent task is blocked; run fails closed, no PR.
    with pytest.raises(SystemExit):
        module.main()
    assert "prs" not in calls
    assert calls["executed"] == ["task-a"]


def test_mocked_main_single_task_verified_no_change_reports_and_creates_no_pr(monkeypatch, tmp_path):
    module = _load("mock_e2e_nochange_single", monkeypatch, tmp_path)
    calls = {}
    monkeypatch.setitem(BUNDLE, "tasks", [dict(BUNDLE["tasks"][1])])
    _wire(module, monkeypatch, calls, _no_change)
    module.main()
    assert "prs" not in calls
    assert calls["executed"] == ["task-a"]
    assert any("no pull request was created" in c for c in calls["comments"])


def test_mocked_main_unverified_completion_fails_closed(monkeypatch, tmp_path):
    module = _load("mock_e2e_unverified", monkeypatch, tmp_path)
    calls = {}

    def unverified(task_id):
        r = _complete(task_id)
        r["repair_cycle"]["commit"]["remote_verified"] = False
        return r

    _wire(module, monkeypatch, calls, unverified)
    with pytest.raises(SystemExit):
        module.main()
    assert "prs" not in calls
