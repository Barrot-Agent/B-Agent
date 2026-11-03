from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ".github/workflows/barrot-autonomous-resolver.yml",
    ".github/workflows/auto-resolve-issues.yml",
    ".github/workflows/daily-digest.yml",
    ".github/workflows/self-schedule.yml",
    ".github/workflows/riemann-harvest.yml",
    ".github/workflows/gumroad-metrics.yml",
    ".github/workflows/webmcp-monetization-enrich.yml",
    ".github/workflows/Barrot.Cognitive.PingPong.Engine.yml",
)


def test_scheduled_mutation_workflows_are_valid_yaml_and_quarantined():
    for relative in WORKFLOWS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        parsed = yaml.safe_load(text)
        assert isinstance(parsed, dict), relative
        on_config = parsed.get("on", parsed.get(True))
        assert isinstance(on_config, dict), relative
        assert set(on_config) == {"workflow_dispatch"}, relative
        assert parsed.get("permissions") == {}, relative
        assert parsed["jobs"]["disabled"]["if"] is False, relative
        assert "No credentials are read" in text, relative
        assert "secrets." not in text, relative
        assert not re.search(r"(?m)^\s*(schedule|workflow_run|push):", text), relative
        assert not re.search(r"(?m)^\s*(contents|actions|issues|pull-requests):\s*write\b", text), relative
        assert not re.search(r"(?m)^\s*(git push|gh issue (create|close|edit|comment)|gh pr edit)\b", text), relative


def test_daily_digest_cannot_publish_unvalidated_accuracy_while_quarantined():
    workflow = (ROOT / ".github/workflows/daily-digest.yml").read_text(encoding="utf-8")
    assert "if: false" in workflow
    assert "legacy unvalidated signal-accuracy percentage" in workflow


def test_gumroad_metrics_quarantine_records_raw_api_log_risk():
    workflow = (ROOT / ".github/workflows/gumroad-metrics.yml").read_text(encoding="utf-8")
    assert "if: false" in workflow
    assert "printed the raw product API response" in workflow
