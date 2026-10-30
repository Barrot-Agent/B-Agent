from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_merge_queue_is_read_only_and_cannot_merge_or_update_branches() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "merge-queue.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert not re.search(r"(?m)^\s*contents:\s*write\s*$", workflow)
    assert not re.search(r"(?m)^\s*pull-requests:\s*write\s*$", workflow)
    assert "gh pr merge" not in workflow
    assert "pulls/" + "$PR/update-branch" not in workflow
    assert "update-branch" not in workflow
    assert "mode=all" not in workflow
    assert "No pull request was modified." in workflow
