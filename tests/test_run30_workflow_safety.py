from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def read_workflow(name):
    return (WORKFLOWS / name).read_text(encoding="utf-8").lower()


def assert_manual_read_only_notice(text):
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "pull_request:" not in text
    assert "contents: read" in text
    assert "pull-requests: read" in text
    assert "contents: write" not in text
    assert "pull-requests: write" not in text
    assert "statuses: write" not in text
    assert "gh pr merge" not in text
    assert "gh api" not in text
    assert "actions/checkout" not in text


def test_scheduled_automerge_is_disabled_and_read_only():
    assert_manual_read_only_notice(read_workflow("barrot-pr-automerge.yml"))


def test_gated_merge_is_disabled_and_read_only():
    text = read_workflow("barrot-gated-merge.yml")
    assert_manual_read_only_notice(text)
    assert "not an approval" in text
    assert "must not be interpreted as merge approval" in text


def test_ci_runs_on_barrot_branch_pushes():
    text = read_workflow("ci.yml")
    assert "push:" in text
    assert "branches: [main, 'barrot/**']" in text
