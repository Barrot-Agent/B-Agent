"""Regression checks for the scheduled signal-accuracy writer."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "check-signal-accuracy.yml"


def test_accuracy_workflow_is_manual_read_only_and_artifact_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert re.search(r"(?m)^\s*workflow_dispatch\s*:", text)
    assert re.search(r"(?m)^\s*schedule\s*:", text) is None
    assert re.search(r"(?m)^\s*contents\s*:\s*write\s*$", text) is None
    assert re.search(r"(?m)^\s*git\s+(?:push|commit)\b", text) is None
    assert "actions/upload-artifact@v4" in text
    assert "retention-days: 30" in text
