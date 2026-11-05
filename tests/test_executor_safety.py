from __future__ import annotations

from types import SimpleNamespace

import pytest

from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.actions import Action
from barrot_agent.orchestration.executor import BarrotExecutor, ExecutionError


def test_executor_uses_argv_and_disables_the_shell(monkeypatch, tmp_path):
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="tests passed", stderr="")

    monkeypatch.setattr("barrot_agent.orchestration.executor.subprocess.run", fake_run)
    result = BarrotExecutor(tmp_path).run(
        "python -m pytest tests/test_xrp_mission_priority.py -q"
    )

    assert result.success is True
    assert result.stdout == "tests passed"
    assert captured["argv"] == [
        "python",
        "-m",
        "pytest",
        "tests/test_xrp_mission_priority.py",
        "-q",
    ]
    assert captured["shell"] is False
    assert captured["cwd"] == tmp_path


@pytest.mark.parametrize(
    "command",
    [
        "python -c \"import os; os.system('id')\"",
        "python -m pip install requests",
        "git push origin main",
        "git reset --hard",
        "git status --short; touch /tmp/barrot-shell-injection",
        "find . -maxdepth 2 -type f -exec touch /tmp/barrot-shell-injection \\;",
        "pytest -p arbitrary_plugin tests/test_executor_safety.py",
        "cat ../../etc/passwd",
        "sed -i 's/a/b/' README.md",
    ],
)
def test_executor_rejects_shell_or_mutation_commands_before_process_creation(
    monkeypatch, tmp_path, command
):
    def forbidden_run(*args, **kwargs):
        raise AssertionError("rejected commands must not create a process")

    monkeypatch.setattr("barrot_agent.orchestration.executor.subprocess.run", forbidden_run)
    with pytest.raises(ExecutionError):
        BarrotExecutor(tmp_path).run(command)


def test_executor_passes_search_metacharacters_as_literal_arguments(monkeypatch, tmp_path):
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("barrot_agent.orchestration.executor.subprocess.run", fake_run)
    pattern = "; touch /tmp/barrot-shell-injection"
    result = BarrotExecutor(tmp_path).run(
        ["grep", "-RIn", "--exclude-dir=.git", "--", pattern, "."]
    )

    assert result.success is True
    assert captured["argv"] == [
        "grep",
        "-RIn",
        "--exclude-dir=.git",
        "--",
        pattern,
        ".",
    ]
    assert captured["shell"] is False


def test_executor_allows_bounded_read_only_verification_commands(monkeypatch, tmp_path):
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("barrot_agent.orchestration.executor.subprocess.run", fake_run)
    executor = BarrotExecutor(tmp_path)

    assert executor.run("python -m compileall -q barrot_agent scripts").success
    assert executor.run("git status --short").success
    assert executor.run("git diff --no-ext-diff --stat").success
    assert executor.run("find . -maxdepth 2 -type f").success

    assert len(calls) == 4
    assert all(kwargs["shell"] is False for _, kwargs in calls)


def test_executor_rejects_unbounded_timeouts(tmp_path):
    with pytest.raises(ExecutionError, match="timeout"):
        BarrotExecutor(tmp_path).run("git status --short", timeout=601)


def test_action_search_treats_query_as_data_and_stays_in_workspace(tmp_path):
    note = tmp_path / "notes.txt"
    note.write_text("literal marker ; touch /tmp/not-executed\n", encoding="utf-8")
    action_executor = BarrotActionExecutor(tmp_path)

    result = action_executor.execute(
        Action(
            type="SEARCH_TEXT",
            args={"query": "; touch /tmp/not-executed", "path": "."},
        )
    )

    assert result.success is True
    assert "notes.txt:1:" in result.output
    assert "; touch /tmp/not-executed" in result.output


def test_action_list_files_is_read_only_and_excludes_git_metadata(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("[core]\n", encoding="utf-8")

    result = BarrotActionExecutor(tmp_path).execute(
        Action(type="LIST_FILES", args={})
    )

    assert result.success is True
    assert "src/module.py" in result.output
    assert ".git/config" not in result.output


def test_run_tests_action_rejects_shell_chaining(monkeypatch, tmp_path):
    def forbidden_run(*args, **kwargs):
        raise AssertionError("shell payload must be rejected before process creation")

    monkeypatch.setattr("barrot_agent.orchestration.executor.subprocess.run", forbidden_run)
    result = BarrotActionExecutor(tmp_path).execute(
        Action(
            type="RUN_TESTS",
            args={"command": "python -m pytest tests -q; touch /tmp/not-executed"},
        )
    )

    assert result.success is False
    assert "Unsupported" in result.error or "limited" in result.error
