from pathlib import Path


WORKFLOW = Path(".github/workflows/merge-queue.yml")


def test_merge_queue_is_manual_only_and_disabled():
    text = WORKFLOW.read_text()
    assert "workflow_dispatch:" in text
    for trigger in ("\n  push:", "\n  pull_request:", "\n  schedule:", "\n  workflow_run:"):
        assert trigger not in text


def test_merge_queue_uses_read_only_permissions():
    text = WORKFLOW.read_text()
    assert "contents: read" in text
    assert "pull-requests: read" in text
    assert "checks: read" in text
    assert "statuses: read" in text
    assert "contents: write" not in text
    assert "pull-requests: write" not in text


def test_merge_queue_contains_no_mutating_operations():
    text = WORKFLOW.read_text().lower()
    forbidden = (
        "gh pr merge",
        "update-branch",
        "git push",
        "git merge",
        "gh pr comment",
        "gh api --method post",
        "gh api --method put",
        "labels[]=",
    )
    for operation in forbidden:
        assert operation not in text


def test_merge_queue_explicitly_fails_closed():
    text = WORKFLOW.read_text().lower()
    assert "disabled" in text
    assert "no branch updates" in text
    assert "no repository content was changed" in text


def test_ci_preserves_risk_manager_coverage_and_runs_merge_queue_safety():
    ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "tests/test_risk_manager.py" in ci
    assert "tests/test_merge_queue_safety.py" in ci


def test_ci_preserves_risk_manager_coverage_and_runs_merge_queue_safety():
    ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "tests/test_risk_manager.py" in ci
    assert "tests/test_merge_queue_safety.py" in ci
