import json

import pytest

from barrot_agent.orchestration.autonomous_loop import BarrotAutonomousLoop
from barrot_agent.orchestration.executor import ExecutionResult
from barrot_agent.orchestration.verifier import VerificationResult
from barrot_agent.orchestration.autonomous_state import AutonomousTaskStore


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
    second = BarrotAutonomousLoop(SequenceBrain([plan]), workspace=tmp_path, max_attempts=1)
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
    loop = BarrotAutonomousLoop(SequenceBrain([plan]), workspace=tmp_path, max_attempts=1)
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
