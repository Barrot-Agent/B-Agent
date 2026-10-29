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



@pytest.mark.parametrize(
    "args",
    [
        ["git", "checkout", "-B", "barrot/dry-run-test"],
        ["git", "fetch", "origin", "main"],
        ["git", "branch", "-D", "main"],
        ["git", "update-ref", "refs/heads/main", "deadbeef"],
        ["git", "config", "user.name", "unsafe"],
        ["git", "add", "."],
        ["git", "restore", "--worktree", "."],
        ["git", "stash", "push"],
        ["git", "worktree", "add", "../other"],
    ],
)
def test_dry_run_blocks_local_git_mutations(monkeypatch, args):
    module = _load_script(monkeypatch)
    called = []
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: called.append(a))
    with pytest.raises(RuntimeError, match="DRY_RUN_WRITE_GUARD"):
        module.run(args)
    assert called == []


@pytest.mark.parametrize(
    "args",
    [
        ["pr", "merge", "1"],
        ["pr", "close", "1"],
        ["issue", "edit", "1", "--add-label", "unsafe"],
        ["workflow", "run", "barrot-agent.yml"],
        ["api", "repos/Barrot-Agent/B-Agent/pulls/1", "--method", "PATCH"],
        ["api", "repos/Barrot-Agent/B-Agent/issues", "-f", "title=unsafe"],
    ],
)
def test_dry_run_blocks_github_mutations(monkeypatch, args):
    module = _load_script(monkeypatch)
    called = []
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: called.append(a))
    with pytest.raises(RuntimeError, match="DRY_RUN_WRITE_GUARD"):
        module.run_gh(args)
    assert called == []


def test_dry_run_allows_required_read_only_git_and_gh_commands(monkeypatch):
    import subprocess
    module = _load_script(monkeypatch)
    called = []
    def fake_run(args, **kwargs):
        called.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
    monkeypatch.setattr(module.subprocess, "run", fake_run)
    module.run(["git", "status", "--short"])
    module.run_gh(["pr", "list", "--repo", "Barrot-Agent/B-Agent"])
    module.run_gh(["api", "repos/Barrot-Agent/B-Agent/pulls"])
    assert len(called) == 3


def test_dry_run_skips_git_config_and_branch_checkout(monkeypatch):
    module = _load_script(monkeypatch)
    called = []
    monkeypatch.setattr(module, "configure_git", lambda: called.append("configure"))
    monkeypatch.setattr(module, "checkout_branch", lambda branch: called.append(("checkout", branch)))
    module.prepare_workspace()
    assert called == []


def test_dry_run_bundle_plan_stays_outside_workspace(tmp_path, monkeypatch):
    module = _load_script(monkeypatch)
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path / "runner-temp"))
    class FakeStore:
        def save_plan(self, *args, **kwargs):
            raise AssertionError("dry-run must not write lifecycle state under .git")
    class FakeResult:
        def to_dict(self):
            return {"status": "READY_FOR_EXECUTION_REVIEW", "bundle": {"objective": "test"}}
    path = module.persist_bundle_plan(FakeStore(), "work-1", FakeResult(), request_fingerprint="sha256:test")
    assert path.parent == (tmp_path / "runner-temp").resolve()
    assert path.name == "barrot-dry-run-bundle.json"
    assert '"objective": "test"' in path.read_text(encoding="utf-8")


def test_workflow_uploads_both_dry_run_report_and_bundle_plan():
    workflow = (SCRIPT_PATH.parents[1] / ".github" / "workflows" / "barrot-agent.yml").read_text()
    dry_job = workflow.split("  dry-run-agent:", 1)[1].split("  agent:", 1)[0]
    assert "barrot-dry-run.json" in dry_job
    assert "barrot-dry-run-bundle.json" in dry_job
