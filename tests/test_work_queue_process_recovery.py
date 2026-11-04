import json
import subprocess
import sys
import time
from pathlib import Path

from barrot_agent.orchestration.repository_repair import (
    RepairCycleEvidence,
    WorkQueueController,
)


WORK_ID = "v3-case17-process-recovery"


def _queue_arguments() -> dict[str, object]:
    return {
        "work_id": WORK_ID,
        "project_identity": {
            "path_with_namespace": "local/test",
            "namespace_path": "local",
            "namespace_kind": "unknown",
        },
        "task_title": "Exercise durable queue recovery",
        "task_body": "Verify persisted work resumes after process termination.",
        "issue_number": "0",
        "repo": "local/test",
        "branch": "barrot/task-v3-case17",
        "audit_context": {},
    }


def _child_code(root: Path, ready: Path) -> str:
    return f'''
import sys
import time
from pathlib import Path

sys.path.insert(0, {str(Path.cwd())!r})

from barrot_agent.orchestration.repository_repair import WorkQueueController


class CrashController:
    def __init__(self, workspace):
        self.workspace = workspace

    def run(self, **kwargs):
        Path({str(ready)!r}).write_text("READY", encoding="utf-8")
        time.sleep(60)
        return None


root = Path({str(root)!r})
controller = WorkQueueController(
    repair_controller=CrashController(root),
)
controller.run(
    work_id={WORK_ID!r},
    project_identity={{
        "path_with_namespace": "local/test",
        "namespace_path": "local",
        "namespace_kind": "unknown",
    }},
    task_title="Exercise durable queue recovery",
    task_body="Verify persisted work resumes after process termination.",
    issue_number="0",
    repo="local/test",
    branch="barrot/task-v3-case17",
    audit_context={{}},
)
'''


def test_work_queue_survives_real_process_termination_and_resumes(tmp_path):
    root = tmp_path / "workspace"
    root.mkdir()
    ready = tmp_path / "worker_ready"

    child = subprocess.Popen(
        [sys.executable, "-c", _child_code(root, ready)],
        cwd=str(Path.cwd()),
    )

    try:
        deadline = time.time() + 10
        while time.time() < deadline and not ready.exists():
            if child.poll() is not None:
                raise AssertionError(
                    f"worker exited before readiness: {child.returncode}"
                )
            time.sleep(0.05)

        assert ready.exists(), "worker never reached persisted execution state"

        queue_file = (
            root
            / ".git"
            / "barrot_repair"
            / "work_queue"
            / f"{WORK_ID}.json"
        )
        deadline = time.time() + 10
        while time.time() < deadline and not queue_file.exists():
            if child.poll() is not None:
                raise AssertionError(
                    f"worker exited before durable queue state: {child.returncode}"
                )
            time.sleep(0.05)

        assert queue_file.exists(), "durable queue state was not persisted"
        persisted = json.loads(queue_file.read_text(encoding="utf-8"))
        assert persisted["attempt_count"] == 1
        assert persisted["current_state"] == "REPAIRING"
        assert persisted["status"] != "complete"

        child.kill()
        return_code = child.wait(timeout=10)
        assert return_code != 0, "worker was not actually terminated"

        class ResumeController:
            def __init__(self, workspace):
                self.workspace = workspace

            def run(self, **kwargs):
                return RepairCycleEvidence(
                    cycle_id="v3-case17-resumed",
                    status="complete",
                    current_state="COMPLETE",
                )

        resumed = WorkQueueController(
            repair_controller=ResumeController(root),
        )
        result = resumed.run(**_queue_arguments())

        assert result.current_state == "COMPLETE"
        assert result.status == "complete"
        assert result.queue_advanced is True
        assert result.attempt_count == 2

        final = json.loads(queue_file.read_text(encoding="utf-8"))
        assert final["attempt_count"] == 2
        assert final["current_state"] == "COMPLETE"
        assert final["status"] == "complete"
        assert final["queue_advanced"] is True

    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=10)
