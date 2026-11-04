from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_merge_queue_workflow_is_read_only_and_fail_closed() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "merge-queue.yml").read_text(
        encoding="utf-8"
    )

    assert "workflow_dispatch:" in workflow
    assert re.search(r"(?m)^\s*contents:\s*read\s*$", workflow)
    assert re.search(r"(?m)^\s*pull-requests:\s*read\s*$", workflow)
    assert not re.search(r"(?m)^\s*contents:\s*write\s*$", workflow)
    assert not re.search(r"(?m)^\s*pull-requests:\s*write\s*$", workflow)
    assert not re.search(r"(?m)^\s*actions:\s*write\s*$", workflow)

    forbidden = (
        "gh pr merge",
        "update-branch",
        "git push",
        "git commit",
        "pulls/",
        "issues/",
    )
    for command in forbidden:
        assert command not in workflow

    assert "This workflow performs no PR, branch, label, comment, or merge mutations." in workflow
