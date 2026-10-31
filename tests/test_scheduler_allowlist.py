import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scripts import scheduler


def _prepare_workflows(tmp_path, monkeypatch, names):
    workflow_dir = tmp_path / "workflows"
    workflow_dir.mkdir()
    for name in names:
        (workflow_dir / name).write_text("name: test\non:\n  workflow_dispatch:\n", encoding="utf-8")
    monkeypatch.setattr(scheduler, "WORKFLOWS_DIR", str(workflow_dir))
    monkeypatch.setattr(scheduler, "QUEUE_PATH", str(tmp_path / "schedule_queue.jsonl"))
    return workflow_dir


def test_scheduler_allows_only_reviewed_unattended_validation_workflows(tmp_path, monkeypatch):
    names = set(scheduler.ALLOWED_SCHEDULED_WORKFLOWS) | {
        "ask-barrot.yml",
        "merge-queue.yml",
        "deploy-a2a-worker.yml",
        "sync-self-hosted-brain.yml",
        "rotate-databricks-token.yml",
        "release.yml",
        "formal-verification-benchmarks.yml",
        "sindy-mcp-cicd.yml",
    }
    _prepare_workflows(tmp_path, monkeypatch, names)

    for allowed in scheduler.ALLOWED_SCHEDULED_WORKFLOWS:
        assert scheduler._valid_workflow(allowed)

    for denied in names - scheduler.ALLOWED_SCHEDULED_WORKFLOWS:
        assert not scheduler._valid_workflow(denied)

    assert not scheduler._valid_workflow("../ask-barrot.yml")


def test_schedule_rejects_privileged_workflow_without_queue_mutation(tmp_path, monkeypatch):
    _prepare_workflows(tmp_path, monkeypatch, {"ask-barrot.yml"})

    with pytest.raises(SystemExit, match="reviewed unattended allowlist"):
        scheduler.schedule("ask-barrot.yml", "2026-10-31T01:00:00Z", "must be denied")

    assert not (tmp_path / "schedule_queue.jsonl").exists()


def test_tick_marks_disallowed_pending_entry_failed_without_dispatch(tmp_path, monkeypatch):
    _prepare_workflows(tmp_path, monkeypatch, {"deploy-a2a-worker.yml"})
    queue = tmp_path / "schedule_queue.jsonl"
    queue.write_text(
        json.dumps({
            "id": "blocked01",
            "workflow": "deploy-a2a-worker.yml",
            "inputs": {},
            "run_after": "2026-10-30T00:00:00Z",
            "status": "pending",
        }) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(scheduler, "_now", lambda: datetime(2026, 10, 31, tzinfo=timezone.utc))
    dispatch = Mock()
    monkeypatch.setattr(scheduler.subprocess, "run", dispatch)

    scheduler.tick()

    updated = json.loads(queue.read_text(encoding="utf-8").splitlines()[0])
    assert updated["status"] == "failed"
    assert "reviewed unattended allowlist" in updated["error"]
    dispatch.assert_not_called()


def test_tick_still_dispatches_an_allowlisted_validation_workflow(tmp_path, monkeypatch):
    _prepare_workflows(tmp_path, monkeypatch, {"barrot-bundle-operational-smoke.yml"})
    queue = tmp_path / "schedule_queue.jsonl"
    queue.write_text(
        json.dumps({
            "id": "safe0001",
            "workflow": "barrot-bundle-operational-smoke.yml",
            "inputs": {},
            "run_after": "2026-10-30T00:00:00Z",
            "status": "pending",
        }) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(scheduler, "_now", lambda: datetime(2026, 10, 31, tzinfo=timezone.utc))
    dispatch = Mock(return_value=SimpleNamespace(returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(scheduler.subprocess, "run", dispatch)

    scheduler.tick()

    updated = json.loads(queue.read_text(encoding="utf-8").splitlines()[0])
    assert updated["status"] == "done"
    dispatch.assert_called_once_with(
        ["gh", "workflow", "run", "barrot-bundle-operational-smoke.yml"],
        capture_output=True,
        text=True,
    )


def test_scheduler_tick_serializes_concurrent_dispatch_runs():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "scheduler-tick.yml").read_text(encoding="utf-8")
    assert "concurrency:\n  group: barrot-scheduler-tick\n  cancel-in-progress: false" in workflow
