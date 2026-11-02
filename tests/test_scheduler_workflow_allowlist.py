import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEDULER_PATH = REPO_ROOT / "scripts" / "scheduler.py"


def load_scheduler():
    spec = importlib.util.spec_from_file_location("barrot_safe_scheduler", SCHEDULER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_queue(path, entry):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")


def test_scheduler_allowlist_contains_only_read_only_validation_workflows():
    scheduler = load_scheduler()
    assert scheduler.SAFE_WORKFLOWS == {
        "ci.yml",
        "barrot-bundle-operational-smoke.yml",
    }
    for name in scheduler.SAFE_WORKFLOWS:
        content = (REPO_ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        assert "workflow_dispatch:" in content
        assert "inputs:" not in content
        assert "contents: write" not in content
        assert "actions: write" not in content
        assert "issues: write" not in content
        assert "pull-requests: write" not in content
        assert "secrets." not in content


def test_schedule_rejects_existing_but_unapproved_workflow(tmp_path, monkeypatch):
    scheduler = load_scheduler()
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "force-deploy-space.yml").write_text("name: Force Deploy", encoding="utf-8")
    monkeypatch.setattr(scheduler, "WORKFLOWS_DIR", str(workflows))
    monkeypatch.setattr(scheduler, "QUEUE_PATH", str(tmp_path / "queue.jsonl"))
    with pytest.raises(SystemExit, match="safe workflow allowlist"):
        scheduler.schedule("force-deploy-space.yml", "2026-11-03T00:00:00Z")


def test_schedule_rejects_naive_run_after_timestamp(tmp_path, monkeypatch):
    scheduler = load_scheduler()
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "ci.yml").write_text("name: CI", encoding="utf-8")
    monkeypatch.setattr(scheduler, "WORKFLOWS_DIR", str(workflows))
    monkeypatch.setattr(scheduler, "QUEUE_PATH", str(tmp_path / "queue.jsonl"))
    with pytest.raises(SystemExit, match="include a timezone offset"):
        scheduler.schedule("ci.yml", "2026-11-03T00:00:00")


def test_schedule_rejects_inputs_for_allowlisted_workflows(tmp_path, monkeypatch):
    scheduler = load_scheduler()
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "ci.yml").write_text("name: CI", encoding="utf-8")
    monkeypatch.setattr(scheduler, "WORKFLOWS_DIR", str(workflows))
    monkeypatch.setattr(scheduler, "QUEUE_PATH", str(tmp_path / "queue.jsonl"))
    with pytest.raises(SystemExit, match="allowlisted workflows must be input-free"):
        scheduler.schedule(
            "ci.yml",
            "2026-11-03T00:00:00Z",
            inputs={"ref": "main"},
        )


def test_tick_rejects_tampered_queue_entry_before_dispatch(tmp_path, monkeypatch):
    scheduler = load_scheduler()
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "force-deploy-space.yml").write_text("name: Force Deploy", encoding="utf-8")
    queue = tmp_path / "queue.jsonl"
    write_queue(queue, {
        "id": "unsafe-1",
        "workflow": "force-deploy-space.yml",
        "inputs": {},
        "run_after": "2026-11-02T00:00:00Z",
        "status": "pending",
    })
    monkeypatch.setattr(scheduler, "WORKFLOWS_DIR", str(workflows))
    monkeypatch.setattr(scheduler, "QUEUE_PATH", str(queue))
    monkeypatch.setattr(scheduler, "_now", lambda: datetime(2026, 11, 2, 6, 0, tzinfo=timezone.utc))
    calls = []
    monkeypatch.setattr(scheduler.subprocess, "run", lambda *args, **kwargs: calls.append(args))
    scheduler.tick()
    entry = json.loads(queue.read_text(encoding="utf-8").splitlines()[0])
    assert entry["status"] == "failed"
    assert "safe dispatch allowlist" in entry["error"]
    assert calls == []


def test_tick_marks_naive_run_after_failed_without_dispatch(tmp_path, monkeypatch):
    scheduler = load_scheduler()
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "ci.yml").write_text("name: CI", encoding="utf-8")
    queue = tmp_path / "queue.jsonl"
    write_queue(queue, {
        "id": "unsafe-naive-time-1",
        "workflow": "ci.yml",
        "inputs": {},
        "run_after": "2026-11-02T00:00:00",
        "status": "pending",
    })
    monkeypatch.setattr(scheduler, "WORKFLOWS_DIR", str(workflows))
    monkeypatch.setattr(scheduler, "QUEUE_PATH", str(queue))
    monkeypatch.setattr(scheduler, "_now", lambda: datetime(2026, 11, 2, 6, 0, tzinfo=timezone.utc))
    calls = []
    monkeypatch.setattr(scheduler.subprocess, "run", lambda *args, **kwargs: calls.append(args))
    scheduler.tick()
    entry = json.loads(queue.read_text(encoding="utf-8").splitlines()[0])
    assert entry["status"] == "failed"
    assert "timezone offset" in entry["error"]
    assert calls == []


def test_tick_rejects_inputs_in_tampered_queue_entry(tmp_path, monkeypatch):
    scheduler = load_scheduler()
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "ci.yml").write_text("name: CI", encoding="utf-8")
    queue = tmp_path / "queue.jsonl"
    write_queue(queue, {
        "id": "unsafe-input-1",
        "workflow": "ci.yml",
        "inputs": {"ref": "attacker-controlled"},
        "run_after": "2026-11-02T00:00:00Z",
        "status": "pending",
    })
    monkeypatch.setattr(scheduler, "WORKFLOWS_DIR", str(workflows))
    monkeypatch.setattr(scheduler, "QUEUE_PATH", str(queue))
    monkeypatch.setattr(scheduler, "_now", lambda: __import__("datetime").datetime(2026, 11, 2, 6, 0, tzinfo=__import__("datetime").timezone.utc))
    calls = []
    monkeypatch.setattr(scheduler.subprocess, "run", lambda *args, **kwargs: calls.append(args))
    scheduler.tick()
    entry = json.loads(queue.read_text(encoding="utf-8").splitlines()[0])
    assert entry["status"] == "failed"
    assert "inputs are disabled" in entry["error"]
    assert calls == []


def test_scheduler_tick_is_serialized_bounded_and_minimally_scoped():
    workflow = (REPO_ROOT / ".github" / "workflows" / "scheduler-tick.yml").read_text(encoding="utf-8")
    assert "group: scheduler-tick" in workflow
    assert "cancel-in-progress: false" in workflow
    assert "timeout-minutes: 5" in workflow
    assert "contents: write" in workflow
    assert "actions: write" in workflow
    assert "pull-requests: write" not in workflow
    assert "issues: write" not in workflow
