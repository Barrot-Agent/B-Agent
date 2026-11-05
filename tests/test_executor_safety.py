from __future__ import annotations

from types import SimpleNamespace
import json

import pytest

from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.autonomous_actions import BarrotActionLoop
from barrot_agent.orchestration.repair_loop import BarrotRepairLoop
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
        "grep -RIn --exclude-dir=.git -- secret .",
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
        ["grep", "-rIn", "--exclude-dir=.git", "--", pattern, "."]
    )

    assert result.success is True
    assert captured["argv"] == [
        "grep",
        "-rIn",
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
    assert executor.run("find . -maxdepth 2 -type f -not -path ./.git/*").success

    assert len(calls) == 5
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


def test_action_search_does_not_follow_symlinks_outside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("private marker\n", encoding="utf-8")
    (workspace / "external.txt").symlink_to(outside)

    result = BarrotActionExecutor(workspace).execute(
        Action(type="SEARCH_TEXT", args={"query": "private marker", "path": "."})
    )

    assert result.success is True
    assert result.output == ""


def test_write_file_is_create_only_and_preserves_existing_content(tmp_path):
    target = tmp_path / "important.txt"
    target.write_text("user work\n", encoding="utf-8")
    executor = BarrotExecutor(tmp_path)

    with pytest.raises(ExecutionError, match="refuses to overwrite"):
        executor.write_file("important.txt", "replacement\n")

    assert target.read_text(encoding="utf-8") == "user work\n"


def test_write_file_compare_and_swap_requires_exact_preimage(tmp_path):
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    executor = BarrotExecutor(tmp_path)

    with pytest.raises(ExecutionError, match="preimage"):
        executor.write_file(
            "module.py",
            "value = 2\n",
            expected_existing_content="value = 0\n",
        )

    assert target.read_text(encoding="utf-8") == "value = 1\n"


def test_apply_patch_uses_compare_and_swap_and_updates_one_unique_match(tmp_path):
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    action_executor = BarrotActionExecutor(tmp_path)

    result = action_executor.execute(
        Action(
            type="APPLY_PATCH",
            args={
                "path": "module.py",
                "expected": "value = 1",
                "replacement": "value = 2",
            },
        )
    )

    assert result.success is True
    assert target.read_text(encoding="utf-8") == "value = 2\n"


def test_write_file_action_cannot_overwrite_existing_user_file(tmp_path):
    target = tmp_path / "user.txt"
    target.write_text("keep me\n", encoding="utf-8")
    action_executor = BarrotActionExecutor(tmp_path)

    result = action_executor.execute(
        Action(
            type="WRITE_FILE",
            args={"path": "user.txt", "content": "replace me\n"},
        )
    )

    assert result.success is False
    assert "refuses to overwrite" in result.error
    assert target.read_text(encoding="utf-8") == "keep me\n"


class StaticBrain:
    def __init__(self, payload):
        self.payload = payload

    def think(self, prompt):
        return json.dumps(self.payload)


def _prepare_loop_workspace(workspace):
    (workspace / "barrot_agent").mkdir()
    (workspace / "scripts").mkdir()


def test_autonomous_action_loop_rolls_back_patch_with_exact_postimage(tmp_path):
    _prepare_loop_workspace(tmp_path)
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    brain = StaticBrain(
        {
            "actions": [
                {
                    "type": "APPLY_PATCH",
                    "args": {
                        "path": "module.py",
                        "expected": "value = 1",
                        "replacement": "value = 2",
                    },
                },
                {
                    "type": "RUN_TESTS",
                    "args": {"command": "git push origin main"},
                },
            ]
        }
    )

    result = BarrotActionLoop(brain, workspace=str(tmp_path), max_attempts=1).run("test rollback")

    assert result.success is False
    assert target.read_text(encoding="utf-8") == "value = 1\n"
    assert result.history[0]["rollback"][0]["success"] is True


def test_autonomous_action_loop_removes_only_its_own_new_file_on_rollback(tmp_path):
    _prepare_loop_workspace(tmp_path)
    target = tmp_path / "generated.py"
    brain = StaticBrain(
        {
            "actions": [
                {
                    "type": "WRITE_FILE",
                    "args": {"path": "generated.py", "content": "value = 2\n"},
                },
                {
                    "type": "RUN_TESTS",
                    "args": {"command": "git push origin main"},
                },
            ]
        }
    )

    result = BarrotActionLoop(brain, workspace=str(tmp_path), max_attempts=1).run("test create rollback")

    assert result.success is False
    assert not target.exists()
    assert result.history[0]["rollback"][0]["success"] is True


def test_repair_loop_rolls_back_when_verification_command_is_rejected(tmp_path):
    _prepare_loop_workspace(tmp_path)
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    brain = StaticBrain(
        {
            "actions": [
                {
                    "type": "APPLY_PATCH",
                    "args": {
                        "path": "module.py",
                        "expected": "value = 1",
                        "replacement": "value = 2",
                    },
                }
            ]
        }
    )

    result = BarrotRepairLoop(brain, workspace=str(tmp_path), max_attempts=1).run(
        "test rejected verification rollback",
        verification_command="git push origin main",
    )

    assert result.success is False
    assert target.read_text(encoding="utf-8") == "value = 1\n"
    assert result.history[0]["verification"]["success"] is False
    assert result.history[0]["rollback"][0]["success"] is True


def test_restore_file_preserves_concurrent_user_change(tmp_path):
    target = tmp_path / "module.py"
    target.write_text("user edit = 3\n", encoding="utf-8")
    executor = BarrotExecutor(tmp_path)

    with pytest.raises(ExecutionError, match="changed"):
        executor.restore_file(
            "module.py",
            "value = 1\n",
            expected_current_content="agent edit = 2\n",
        )

    assert target.read_text(encoding="utf-8") == "user edit = 3\n"
