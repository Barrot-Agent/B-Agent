"""Security regression test: the merge-queue workflow must not mutate or merge PRs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "merge-queue.yml"


def test_merge_queue_is_read_only_and_fail_closed():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "contents: read" in text
    assert "pull-requests: read" in text
    assert "checks: read" in text
    assert "statuses: read" in text
    assert not re.search(r"^\s*(contents|pull-requests|checks|statuses):\s*write\s*$", text, re.M)
    assert "gh pr merge" not in text
    assert "update-branch" not in text
    assert "gh pr comment" not in text
    assert "gh api --method PUT" not in text
    assert "mode: all" not in text
    assert "No repository content was changed" in text
