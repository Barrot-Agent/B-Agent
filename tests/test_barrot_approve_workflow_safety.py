from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "barrot-approve-pr.yml"


def test_push_events_are_explicit_read_only_noops():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "push:" in text
    assert '"research/**"' in text
    assert '"safety/**"' in text
    push_job = text.split("  push_noop:", 1)[1].split("  approve:", 1)[0]
    assert "if: github.event_name == 'push'" in push_job
    assert "pull-requests: write" not in push_job
    assert "No approval action" in push_job


def test_only_manual_dispatch_can_run_approval_job():
    text = WORKFLOW.read_text(encoding="utf-8")
    approval_job = text.split("  approve:", 1)[1]
    assert "if: github.event_name == 'workflow_dispatch'" in approval_job
    assert "Apply approved label" in approval_job
    assert "MERGE_PERFORMED=FALSE" in approval_job
    assert "the `approved` label only" not in approval_job


def test_write_permission_is_scoped_to_approval_job():
    text = WORKFLOW.read_text(encoding="utf-8")
    global_permissions = text.split("permissions:", 1)[1].split("jobs:", 1)[0]
    push_job = text.split("  push_noop:", 1)[1].split("  approve:", 1)[0]
    approval_job = text.split("  approve:", 1)[1]
    assert "pull-requests: write" not in global_permissions
    assert "pull-requests: write" not in push_job
    assert "pull-requests: write" in approval_job
