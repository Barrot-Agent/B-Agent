"""Safety tests for autonomous learning entry points and remote publishing."""

import subprocess
from pathlib import Path

from barrot_agent.orchestration.validated_publisher import ValidatedPublisher


ROOT = Path(__file__).resolve().parents[1]


def _source(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _completed(args, code=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(["git", *args], code, stdout, stderr)


def test_learning_daemon_requires_external_and_local_opt_in_and_never_publishes():
    source = _source("scripts/barrot_learning_daemon.py")
    assert '"--allow-external-inference"' in source
    assert '"--allow-local-mutations"' in source
    assert "sys.stdin.isatty()" in source
    assert "SEND BARROT LEARNING CONTEXT TO GITHUB MODELS OR GROQ" in source
    assert "START BARROT LEARNING ON CLEAN FEATURE BRANCH" in source
    assert "assert_clean_feature_worktree" in source
    assert "from barrot_agent.orchestration.autonomous_actions import BarrotActionLoop" in source
    assert "ValidatedPublisher" not in source
    assert ".publish(" not in source
    assert "DISABLED_BY_PRIMARY_MISSION_GUARDRAIL" in source


def test_knowledge_builder_requires_external_and_local_opt_in_on_clean_branch():
    source = _source("scripts/barrot_build_knowledge.py")
    assert '"--allow-external-inference"' in source
    assert '"--allow-local-mutations"' in source
    assert "sys.stdin.isatty()" in source
    assert "SEND REPOSITORY CONTEXT TO GITHUB MODELS OR GROQ" in source
    assert "ALLOW BARROT TO MODIFY THIS CLEAN FEATURE WORKTREE" in source
    assert "assert_clean_feature_worktree" in source
    assert source.index("assert_clean_feature_worktree(") < source.index("BarrotActionLoop(")


def test_brain_external_gate_precedes_provider_calls_inside_think():
    source = _source("barrot_agent/barrot_brain.py")
    start = source.index("    def think(")
    end = source.index("    @property", start)
    think = source[start:end]
    assert "if not self.allow_external_inference:" in think
    assert think.index("if not self.allow_external_inference:") < think.index("requests.post(")


def test_validated_publisher_is_noop_without_explicit_remote_permission(tmp_path, monkeypatch):
    publisher = ValidatedPublisher(workspace=str(tmp_path))
    calls = []
    monkeypatch.setattr(
        publisher,
        "_run",
        lambda *args: calls.append(args) or _completed(args),
    )
    result = publisher.publish(paths=["src/new.py"], message="validated update")
    assert result.success is False
    assert result.committed is False
    assert result.pushed == []
    assert "disabled" in result.reason.lower()
    assert calls == []


def test_validated_publisher_refuses_default_branch_before_staging(tmp_path, monkeypatch):
    publisher = ValidatedPublisher(workspace=str(tmp_path))
    calls = []

    def fake_run(*args):
        calls.append(args)
        return _completed(args, stdout="main\n")

    monkeypatch.setattr(publisher, "_run", fake_run)
    result = publisher.publish(
        paths=["src/new.py"],
        message="validated update",
        allow_remote_push=True,
    )
    assert result.success is False
    assert result.committed is False
    assert calls == [("branch", "--show-current")]


def test_validated_publisher_preserves_preexisting_staged_changes(tmp_path, monkeypatch):
    publisher = ValidatedPublisher(workspace=str(tmp_path))
    calls = []

    def fake_run(*args):
        calls.append(args)
        if args == ("branch", "--show-current"):
            return _completed(args, stdout="feature/xrp\n")
        if args == ("diff", "--cached", "--quiet"):
            return _completed(args, code=1)
        raise AssertionError(f"unexpected Git command: {args}")

    monkeypatch.setattr(publisher, "_run", fake_run)
    result = publisher.publish(
        paths=["src/new.py"],
        message="validated update",
        allow_remote_push=True,
    )
    assert result.success is False
    assert "pre-existing staged changes" in result.reason
    assert calls == [
        ("branch", "--show-current"),
        ("diff", "--cached", "--quiet"),
    ]


def test_validated_publisher_rejects_traversal_before_git(tmp_path, monkeypatch):
    publisher = ValidatedPublisher(workspace=str(tmp_path))
    calls = []
    monkeypatch.setattr(
        publisher,
        "_run",
        lambda *args: calls.append(args) or _completed(args),
    )
    result = publisher.publish(
        paths=["../outside.py"],
        message="unsafe",
        allow_remote_push=True,
    )
    assert result.success is False
    assert "unsafe publish path" in result.reason.lower()
    assert calls == []


def test_validated_publisher_pushes_only_explicit_paths_after_opt_in(tmp_path, monkeypatch):
    publisher = ValidatedPublisher(workspace=str(tmp_path), remotes=("origin", "gitlab"))
    calls = []
    responses = [
        _completed(("branch", "--show-current"), stdout="feature/xrp\n"),
        _completed(("diff", "--cached", "--quiet")),
        _completed(("add", "--", "src/new.py")),
        _completed(("diff", "--cached", "--quiet"), code=1),
        _completed(("diff", "--cached", "--name-only"), stdout="src/new.py\n"),
        _completed(("commit", "-m", "validated update")),
        _completed(("push", "origin", "HEAD")),
        _completed(("push", "gitlab", "HEAD")),
    ]

    def fake_run(*args):
        calls.append(args)
        return responses[len(calls) - 1]

    monkeypatch.setattr(publisher, "_run", fake_run)
    result = publisher.publish(
        paths=["src/new.py"],
        message="validated update",
        allow_remote_push=True,
    )
    assert result.success is True
    assert result.committed is True
    assert result.pushed == ["origin", "gitlab"]
    assert calls == [
        ("branch", "--show-current"),
        ("diff", "--cached", "--quiet"),
        ("add", "--", "src/new.py"),
        ("diff", "--cached", "--quiet"),
        ("diff", "--cached", "--name-only"),
        ("commit", "-m", "validated update"),
        ("push", "origin", "HEAD"),
        ("push", "gitlab", "HEAD"),
    ]
