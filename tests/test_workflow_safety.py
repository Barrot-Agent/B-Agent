"""Regression checks for unattended GitHub Actions safety."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def read_workflow(name):
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def assert_read_only_and_non_mutating(text):
    assert re.search(r"(?m)^\s*schedule\s*:", text) is None
    assert re.search(r"(?m)^\s*(?:contents|pull-requests|statuses)\s*:\s*write\s*$", text) is None
    mutating_command = re.compile(
        r"(?m)^\s*(?:gh\s+pr\s+merge\b|git\s+(?:push|commit)\b|"
        r"gh\s+api\s+[^\n]*statuses\b)"
    )
    assert mutating_command.search(text) is None


def test_auto_merge_workflow_is_manual_read_only_and_disabled():
    text = read_workflow("barrot-pr-automerge.yml")
    assert "workflow_dispatch:" in text
    assert "Automatic PR merging is disabled" in text
    assert_read_only_and_non_mutating(text)


def test_gated_merge_workflow_is_manual_read_only_and_fail_closed():
    text = read_workflow("barrot-gated-merge.yml")
    assert "workflow_dispatch:" in text
    assert "Automatic merging is disabled" in text
    assert_read_only_and_non_mutating(text)


def test_signal_accuracy_workflow_is_artifact_only():
    text = read_workflow("check-signal-accuracy.yml")
    assert "workflow_dispatch:" in text
    assert "actions/upload-artifact@v4" in text
    assert "retention-days: 30" in text
    assert_read_only_and_non_mutating(text)


def test_ci_runs_workflow_safety_regression():
    ci = read_workflow("ci.yml")
    assert "tests/test_workflow_safety.py" in ci
