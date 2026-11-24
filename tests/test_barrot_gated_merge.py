from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "barrot-gated-merge.yml"


def test_merge_gate_is_read_only_and_uses_minimal_permissions() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    for required in ("contents: read", "pull-requests: read", "checks: read"):
        assert required in source
    assert "contents: write" not in source
    assert "gh pr merge" not in source
    assert "READINESS=BLOCKED" in source
    assert "READINESS=READY_FOR_EXPLICIT_MERGE" in source


def test_merge_gate_checks_exact_head_and_current_main_without_admin_or_review_gates() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    for required in ("EXPECTED_HEAD_SHA", "actual_head", "current_main", "mergeable", "base_ref"):
        assert required in source
    for obsolete in (
        "branches/main/protection",
        "independent approving review",
        "BARROT_MAINTAINER_LOGIN",
        "BARROT_BRANCH_PROTECTION_READ_TOKEN",
        "allow_force_pushes",
        "required_approving_review_count",
    ):
        assert obsolete not in source


def test_merge_gate_requires_only_named_exact_head_validation_checks() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    for required in (
        '"Tests"',
        '"Full repository test suite"',
        '"pip-audit"',
        '"audit"',
        '"Verify PR merge tree against current base"',
        'commits/${actual_head}/check-runs',
    ):
        assert required in source
    assert "GitHub Pages build (validation only)" not in source


def test_merge_gate_runs_for_pull_requests_and_integration_pushes() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "pull_request:" in source
    assert "push:" in source
    assert 'branches: ["integration/**"]' in source


def test_merge_gate_preserves_explicit_false_draft_state_and_fails_closed() -> None:
    import json
    import shutil
    import subprocess
    import pytest

    source = WORKFLOW.read_text(encoding="utf-8")
    expression = 'if has("draft") then (.draft|tostring) else "unknown" end'
    expected_assignment = f'draft="$(jq -r \'{expression}\' <<< "$pr_json")"'
    assert expected_assignment in source
    assert ".draft // true" not in source
    assert '[[ "$draft" == "false" ]]' in source

    jq = shutil.which("jq")
    if jq is None:
        pytest.skip("jq is unavailable; GitHub Actions Ubuntu runner includes jq")

    cases = (
        ({"draft": False}, "false"),
        ({"draft": True}, "true"),
        ({}, "unknown"),
        ({"draft": None}, "null"),
    )
    for payload, expected in cases:
        result = subprocess.run(
            [jq, "-r", expression],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
        )
        assert result.stdout.strip() == expected


def test_skipped_integration_push_full_suite_has_a_distinct_check_name() -> None:
    ci_source = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "Full repository test suite (PR event only)" in ci_source
    assert "name: Full repository test suite" not in ci_source
    assert "if: github.event_name != 'push' || github.ref == 'refs/heads/main'" in ci_source
