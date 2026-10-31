from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "barrot_agent.py"


def _load_script(monkeypatch):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", "Dry-run safety test")
    monkeypatch.setenv("TASK_TITLE", "Dry-run safety test")
    monkeypatch.setenv("ISSUE_NUMBER", "0")
    monkeypatch.setenv("BRANCH", "barrot/dry-run-test")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    spec = importlib.util.spec_from_file_location("barrot_dry_run_script_test", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DRY_RUN = True
    return module


@pytest.mark.parametrize(
    "args",
    [
        ["git", "push", "origin", "HEAD:main"],
        ["git", "commit", "-m", "should be blocked"],
        ["git", "reset", "--hard"],
        ["gh", "pr", "create", "--title", "unsafe"],
        ["gh", "issue", "comment", "1", "--body", "unsafe"],
        ["gh", "issue", "edit", "1", "--add-label", "unsafe"],
    ],
)
def test_dry_run_rejects_mutating_commands_before_subprocess(monkeypatch, args):
    module = _load_script(monkeypatch)
    called = []
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: called.append(a))
    with pytest.raises(RuntimeError, match="DRY_RUN_WRITE_GUARD"):
        if args[0] == "gh":
            module.run_gh(args[1:])
        else:
            module.run(args)
    assert called == []


def test_dry_run_suppresses_issue_comments_and_pull_requests(monkeypatch):
    module = _load_script(monkeypatch)
    called = []
    monkeypatch.setattr(module, "run_gh", lambda args: called.append(args))
    module.post_issue_comment("must not be posted")
    module.create_pull_request({"repair_cycle": {"status": "complete"}})
    assert called == []


def test_workflow_dry_run_job_is_read_only_and_uploads_evidence():
    workflow = (SCRIPT_PATH.parents[1] / ".github" / "workflows" / "barrot-agent.yml").read_text()
    dry_job = workflow.split("  dry-run-agent:", 1)[1].split("  agent:", 1)[0]
    assert "contents: read" in dry_job
    assert "pull-requests: read" in dry_job
    assert "issues: read" in dry_job
    assert "contents: write" not in dry_job
    assert "pull-requests: write" not in dry_job
    assert "issues: write" not in dry_job
    assert "actions/upload-artifact@v4" in dry_job
    assert 'DRY_RUN: "true"' in dry_job

def test_groq_messages_are_bounded_for_small_token_budget(monkeypatch):
    module = _load_script(monkeypatch)
    messages = [
        {"role": "system", "content": "system instructions"},
        {"role": "user", "content": "old context " * 2000},
        {"role": "user", "content": "CURRENT TASK: repair the 8000 TPM request size"},
    ]
    bounded = module._bound_groq_messages(messages, max_chars=1000)
    assert sum(len(str(item.get("content", ""))) for item in bounded) <= 1000
    assert bounded[0]["content"] == "system instructions"
    assert "CURRENT TASK" in bounded[-1]["content"]

