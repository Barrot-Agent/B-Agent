from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ".github/workflows/barrot-autonomous-resolver.yml",
    ".github/workflows/auto-resolve-issues.yml",
    ".github/workflows/daily-digest.yml",
    ".github/workflows/self-schedule.yml",
    ".github/workflows/riemann-harvest.yml",
    ".github/workflows/gumroad-metrics.yml",
    ".github/workflows/webmcp-monetization-enrich.yml",
)


def test_scheduled_mutation_workflows_are_quarantined():
    for relative in WORKFLOWS:
        workflow = (ROOT / relative).read_text(encoding="utf-8")
        assert "workflow_dispatch: {}" in workflow, relative
        assert "permissions: {}" in workflow, relative
        assert "if: false" in workflow, relative
        assert "No credentials are read" in workflow, relative
        assert "secrets." not in workflow, relative
        assert not re.search(r"(?m)^\s*(schedule|workflow_run|push):", workflow), relative
        assert not re.search(r"(?m)^\s*(contents|actions|issues|pull-requests):\s*write\b", workflow), relative
        assert not re.search(r"(?m)^\s*(git push|gh issue (create|close|edit|comment)|gh pr edit)\b", workflow), relative


def test_daily_digest_cannot_publish_unvalidated_accuracy_while_quarantined():
    workflow = (ROOT / ".github/workflows/daily-digest.yml").read_text(encoding="utf-8")
    assert "if: false" in workflow
    assert "legacy unvalidated signal-accuracy percentage" in workflow


def test_gumroad_metrics_quarantine_records_raw_api_log_risk():
    workflow = (ROOT / ".github/workflows/gumroad-metrics.yml").read_text(encoding="utf-8")
    assert "if: false" in workflow
    assert "printed the raw product API response" in workflow
