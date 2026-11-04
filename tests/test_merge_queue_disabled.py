from pathlib import Path


def test_merge_queue_is_read_only_and_inert():
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "merge-queue.yml"
    ).read_text(encoding="utf-8")

    assert "workflow_dispatch: {}" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert "contents: write" not in workflow
    assert "pull-requests: write" not in workflow
    assert "checks: write" not in workflow
    assert "secrets.GH_PAT" not in workflow
    assert "gh pr merge" not in workflow
    assert "update-branch" not in workflow
    assert "--delete-branch" not in workflow
    assert "Merge queue disabled" in workflow
