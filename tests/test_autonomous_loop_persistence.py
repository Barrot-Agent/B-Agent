import json

import pytest

from barrot_agent.orchestration import BarrotAutonomousLoop, AutonomousTaskStore
from barrot_agent.orchestration.executor import ExecutionResult
from barrot_agent.orchestration.verifier import VerificationResult


class SequenceBrain:
    def __init__(self, responses):
        self.responses = iter(responses)

    def think(self, prompt):
        return next(self.responses)


def test_autonomous_loop_resumes_checkpoint_after_process_restart(tmp_path):
    goal = "Inspect the repository and verify Python syntax."
    task_id = "resume-task"
    first = BarrotAutonomousLoop(SequenceBrain(["not json"]), workspace=tmp_path, max_attempts=1)
    paused = first.run(goal, task_id=task_id)
    assert not paused.success
    assert paused.status == "paused"
    assert paused.attempts == 1

    plan = json.dumps({"analysis": "inspect", "commands": ["pwd"]})
    second = BarrotAutonomousLoop(SequenceBrain([plan]), workspace=tmp_path, max_attempts=1, goal_verifier=lambda goal, record: {"success": True, "evidence": {"verified_goal": goal}})
    second.executor.run = lambda command: ExecutionResult(command, True, "workspace", "", 0)
    second.verifier.verify_python = lambda: VerificationResult(True, [{"success": True}])
    completed = second.run(goal, task_id=task_id)

    assert completed.success
    assert completed.status == "complete"
    assert completed.attempts == 2
    assert len(completed.history) == 2
    saved = AutonomousTaskStore(tmp_path).load(task_id)
    assert saved["status"] == "complete"
    assert saved["attempts_completed"] == 2


def test_autonomous_task_id_is_bound_to_original_goal(tmp_path):
    loop = BarrotAutonomousLoop(SequenceBrain(["not json"]), workspace=tmp_path, max_attempts=1)
    loop.run("original goal", task_id="bound-task")
    with pytest.raises(ValueError, match="different goal"):
        loop.run("different goal", task_id="bound-task")


def test_autonomous_checkpoint_redacts_common_credentials(tmp_path):
    plan = json.dumps({"analysis": "inspect", "commands": ["pwd"]})
    loop = BarrotAutonomousLoop(SequenceBrain([plan]), workspace=tmp_path, max_attempts=1, goal_verifier=lambda goal, record: {"success": True, "evidence": {"verified": True}})
    loop.executor.run = lambda command: ExecutionResult(
        command, True, "api_key=super-secret-value ghp_abcdefghijklmnopqrstuvwxyz123456", "", 0
    )
    loop.verifier.verify_python = lambda: VerificationResult(True, [{"success": True, "stderr": "token=verification-secret"}])
    result = loop.run("inspect safely", task_id="redaction-task")
    checkpoint = open(result.checkpoint_path, encoding="utf-8").read()
    assert "super-secret-value" not in checkpoint
    assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in checkpoint
    assert "verification-secret" not in checkpoint
    assert "[REDACTED]" in checkpoint


def test_autonomous_task_store_rejects_unsafe_ids_and_corrupt_state(tmp_path):
    store = AutonomousTaskStore(tmp_path)
    with pytest.raises(ValueError):
        store.path_for("../escape")
    path = store.path_for("corrupt-task")
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="unreadable"):
        store.load("corrupt-task")

def test_compile_success_without_goal_verifier_does_not_complete_task(tmp_path):
    plan = json.dumps({"analysis": "inspect", "commands": ["pwd"]})
    loop = BarrotAutonomousLoop(SequenceBrain([plan]), workspace=tmp_path, max_attempts=1)
    loop.executor.run = lambda command: ExecutionResult(command, True, "workspace", "", 0)
    loop.verifier.verify_python = lambda: VerificationResult(True, [{"success": True}])
    result = loop.run("perform a task", task_id="needs-goal-proof")
    assert not result.success
    assert result.status == "awaiting_goal_verification"
    assert result.history[0]["goal_verification"]["status"] == "unavailable"
def test_autonomous_store_rejects_workspace_symlink_escape(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (workspace / ".barrot").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes workspace"):
        AutonomousTaskStore(workspace)
    assert not (outside / "autonomous_tasks").exists()
def test_autonomous_checkpoint_size_is_bounded(tmp_path):
    store = AutonomousTaskStore(tmp_path)
    store.MAX_CHECKPOINT_BYTES = 128
    with pytest.raises(ValueError, match="size limit"):
        store.save("large-task", {"history": [{"output": "x" * 500}]})
def test_autonomous_history_is_bounded_with_archive_digest(tmp_path):
    store = AutonomousTaskStore(tmp_path)
    state = {"history": [{"attempt": index} for index in range(1, 61)]}
    store.save("long-task", state)
    first_digest = state["history_archive_digest"]
    state["history"].append({"attempt": 61})
    store.save("long-task", state)
    loaded = store.load("long-task")
    assert len(loaded["history"]) == store.MAX_HISTORY_ITEMS
    assert loaded["history_archived_count"] == 11
    assert len(loaded["history_archive_digest"]) == 64
    assert loaded["history_archive_digest"] != first_digest
    assert loaded["history"][0]["attempt"] == 12
def test_autonomous_store_rejects_stale_concurrent_writer(tmp_path):
    store = AutonomousTaskStore(tmp_path)
    store.save("concurrent-task", {"history": [], "value": 0})
    first = store.load("concurrent-task")
    stale = store.load("concurrent-task")
    first["value"] = 1
    store.save("concurrent-task", first)
    stale["value"] = 2
    with pytest.raises(RuntimeError, match="changed since it was loaded"):
        store.save("concurrent-task", stale)