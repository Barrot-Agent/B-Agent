from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "scheduler-tick.yml").read_text(encoding="utf-8")


def test_scheduler_queue_audit_is_manual_only_and_read_only():
    assert "workflow_dispatch:" in WORKFLOW
    assert "schedule:" not in WORKFLOW
    assert "contents: read" in WORKFLOW
    assert "contents: write" not in WORKFLOW
    assert "actions: write" not in WORKFLOW
    assert "GH_TOKEN:" not in WORKFLOW
    assert "scheduler.py list" in WORKFLOW
    assert "scheduler.py tick" not in WORKFLOW
    assert "gh workflow run" not in WORKFLOW
    assert "git push" not in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "actions/upload-artifact@v4" in WORKFLOW


def test_scheduler_queue_audit_does_not_run_on_push_or_pull_request():
    assert "push:" not in WORKFLOW
    assert "pull_request:" not in WORKFLOW
