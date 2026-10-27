from pathlib import Path
import re


WORKFLOW = Path(".github/workflows/merge-queue.yml")


def test_merge_queue_is_manual_read_only_and_non_mutating():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert re.search(r"^\s*workflow_dispatch:\s*$", text, re.MULTILINE)
    for trigger in ("schedule:", "push:", "pull_request:", "workflow_run:"):
        assert not re.search(rf"^\s*{re.escape(trigger)}", text, re.MULTILINE)

    assert re.search(r"^\s*contents:\s*read\s*$", text, re.MULTILINE)
    assert re.search(r"^\s*pull-requests:\s*read\s*$", text, re.MULTILINE)
    assert not re.search(r"^\s*(contents|pull-requests):\s*write\s*$", text, re.MULTILINE)

    forbidden = (
        "actions/checkout",
        "gh pr merge",
        "git push",
        "git commit",
        "update-branch",
        "secrets.GH_PAT",
        "secrets.GITHUB_TOKEN",
    )
    for token in forbidden:
        assert token not in text

    assert "disabled pending independent review" in text.lower()
