from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_merge_queue_workflow_fails_closed_without_merge_permissions() -> None:
    workflow_path = REPO_ROOT / ".github" / "workflows" / "merge-queue.yml"
    workflow = workflow_path.read_text(encoding="utf-8")

    assert "workflow_dispatch" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert "Automatic merging is disabled" not in workflow or "fail-closed" in workflow.lower()
    assert "gh pr merge" not in workflow
    assert "pull-requests: write" not in workflow
    assert "contents: write" not in workflow
    assert "No pull request was modified" in workflow
