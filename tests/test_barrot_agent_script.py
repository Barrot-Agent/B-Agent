from __future__ import annotations

import importlib.util
import os
from pathlib import Path

from barrot_agent.orchestration.repository_repair import RepairCycleEvidence


SCRIPT_PATH = Path("/home/runner/work/B-Agent/B-Agent/scripts/barrot_agent.py")


def load_script_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_barrot_agent_main_routes_through_repository_repair_controller(monkeypatch):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", "Fix the reproduced issue.")
    monkeypatch.setenv("TASK_TITLE", "Repair issue")
    monkeypatch.setenv("ISSUE_NUMBER", "42")
    monkeypatch.setenv("BRANCH", "barrot/task-42")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    module = load_script_module("barrot_agent_script_test")

    calls: dict[str, object] = {}

    class FakeController:
        def __init__(self, **kwargs):
            calls["init"] = kwargs

        def run(self, **kwargs):
            calls["run"] = kwargs
            cycle = RepairCycleEvidence(cycle_id="cycle-123")
            cycle.status = "no_repair_required"
            cycle.current_state = "NO_REPAIR_REQUIRED"
            cycle.report = "Already healthy."
            return cycle

    monkeypatch.setattr(module, "RepositoryRepairController", FakeController)
    monkeypatch.setattr(module, "configure_git", lambda: calls.setdefault("configured", True))
    monkeypatch.setattr(module, "checkout_branch", lambda branch: calls.setdefault("branch", branch))
    monkeypatch.setattr(module, "build_audit_context", lambda title, body: {"inventory": f"{title}:{body}"})
    monkeypatch.setattr(module, "post_issue_comment", lambda message: calls.setdefault("comment", message))
    monkeypatch.setattr(module, "create_pull_request", lambda cycle: calls.setdefault("pr", cycle))

    module.main()

    assert "init" in calls
    assert "run" in calls
    assert calls["run"]["branch"] == "barrot/task-42"
    assert calls["comment"] == "Already healthy."
    assert "pr" not in calls
