"""Security regression tests for the disabled merge queue."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "merge-queue.yml"
CI = ROOT / ".github" / "workflows" / "ci.yml"


def test_merge_queue_is_read_only_and_has_no_mutation_commands():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "contents: read" in text
    assert "pull-requests: read" in text
    assert "checks: read" in text
    assert "statuses: read" in text
    assert not re.search(r"^\s*(contents|pull-requests|checks|statuses):\s*write\s*$", text, re.M)
    for forbidden in (
        "gh pr merge",
        "gh pr comment",
        "update-branch",
        "git push",
        "git commit",
        "mode: all",
        "max_prs",
        "DRY_RUN",
    ):
        assert forbidden not in text
    assert "disabled pending approval" in text.lower()


def test_core_ci_executes_this_regression_test():
    text = CI.read_text(encoding="utf-8")
    assert "tests/test_merge_queue_fail_closed.py" in text
