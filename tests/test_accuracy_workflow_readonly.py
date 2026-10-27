"""Regression tests for the disabled legacy signal-accuracy workflow."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "check-signal-accuracy.yml"
CI = ROOT / ".github" / "workflows" / "ci.yml"


def test_legacy_accuracy_workflow_is_manual_read_only_and_non_mutating():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "contents: read" in text
    assert "contents: write" not in text
    for forbidden in (
        "python3 scripts/check_signal_accuracy.py",
        "git add",
        "git commit",
        "git push",
        "git pull",
        "actions/checkout",
    ):
        assert forbidden not in text
    assert "disabled pending fixed-horizon evaluator" in text.lower()
    assert "historical signal records will be rewritten" in text.lower()


def test_core_ci_executes_this_regression_test():
    text = CI.read_text(encoding="utf-8")
    assert "tests/test_accuracy_workflow_readonly.py" in text
