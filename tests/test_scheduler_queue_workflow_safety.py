from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "scheduler-tick.yml").read_text(encoding="utf-8")


def test_scheduler_queue_audit_is_scheduled_and_read_only():
    assert "schedule:" in WORKFLOW
    assert 'cron: "*/15 * * * *"' in WORKFLOW
    assert "workflow_dispatch:" in WORKFLOW
    assert re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", WORKFLOW)
    assert "contents: write" not in WORKFLOW
    assert "actions: write" not in WORKFLOW
    assert "GH_TOKEN:" not in WORKFLOW
    assert "scheduler.py list" in WORKFLOW
    assert "scheduler.py tick" not in WORKFLOW
    assert "gh workflow run" not in WORKFLOW
    assert "git push" not in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "actions/upload-artifact@v4" in WORKFLOW
    assert "retention-days: 30" in WORKFLOW


def test_scheduler_queue_audit_does_not_run_on_push_or_pull_request():
    assert re.search(r"(?m)^  push:\s*$", WORKFLOW) is None
    assert re.search(r"(?m)^  pull_request:\s*$", WORKFLOW) is None
