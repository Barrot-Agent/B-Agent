from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "merge-queue.yml").read_text(encoding="utf-8")


def test_merge_queue_is_disabled_and_read_only():
    assert "workflow_dispatch:" in WORKFLOW
    assert "permissions:\n  contents: read\n  pull-requests: read" in WORKFLOW
    assert "contents: write" not in WORKFLOW
    assert "pull-requests: write" not in WORKFLOW
    assert "checks: read" not in WORKFLOW
    assert "gh pr merge" not in WORKFLOW
    assert "update-branch" not in WORKFLOW
    assert "merge_method" not in WORKFLOW
    assert "dry_run" not in WORKFLOW
    assert "Automatic merging is disabled" in WORKFLOW
    assert "No pull request was modified or merged." in WORKFLOW


def test_merge_queue_has_no_automatic_or_batch_merge_inputs():
    assert "schedule:" not in WORKFLOW
    assert "push:" not in WORKFLOW
    assert "pull_request:" not in WORKFLOW
    assert "mode:" not in WORKFLOW
    assert "max_prs:" not in WORKFLOW
