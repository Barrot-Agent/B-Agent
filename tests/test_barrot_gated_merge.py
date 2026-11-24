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


def test_merge_gate_accepts_only_the_configured_sole_human_maintainer() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "AUTHORIZED_MAINTAINER: ${{ vars.BARROT_MAINTAINER_LOGIN }}" in source
    assert "BARROT_MAINTAINER_LOGIN repository variable is missing" in source
    assert "configured human maintainer matches the PR author; self-approval is prohibited" in source
    assert "select(.user.login == $maintainer and .user.login != $author)" in source
    assert 'group_by(.user.login) | map(last) | map(select(.state == "APPROVED"))' in source
    assert "no independent approving review exists from the configured sole human maintainer" in source


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
    assert "PR draft state could not be verified" in source

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
    # The integration push intentionally skips the expensive full suite; its skipped
    # check must not collide with the authoritative pull_request full-suite check.
    assert "Full repository test suite (PR event only)" in ci_source
    assert "name: Full repository test suite" not in ci_source
    assert "if: github.event_name != 'push' || github.ref == 'refs/heads/main'" in ci_source
