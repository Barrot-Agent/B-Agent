from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "barrot-gated-merge.yml"


def test_merge_gate_is_read_only_and_has_no_write_permissions() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "contents: read" in source
    assert "pull-requests: read" in source
    assert "checks: read" in source
    assert "statuses: read" in source
    assert "gh pr merge" not in source
    assert "contents: write" not in source
    assert "READINESS=BLOCKED" in source
    assert "READY_FOR_HUMAN_MERGE_REVIEW" in source


def test_merge_gate_requires_exact_head_current_base_and_independent_approval() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    for required in (
        "EXPECTED_HEAD_SHA",
        "actual_head",
        "draft",
        "mergeable_state",
        "current_main",
        "independent approving review",
        "branches/main/protection",
        "required_status_checks",
    ):
        assert required in source


def test_merge_gate_requires_full_suite_and_security_checks_on_exact_head() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    for required in (
        "Tests",
        "Full repository test suite",
        "GitHub Pages build (validation only)",
        "pip-audit",
        "audit",
        "commits/${actual_head}/check-runs",
    ):
        assert required in source


def test_merge_gate_runs_for_pull_requests_and_integration_pushes() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "pull_request:" in source
    assert "push:" in source
    assert 'branches: ["integration/**"]' in source
