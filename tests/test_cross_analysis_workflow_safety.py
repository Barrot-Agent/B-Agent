from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "cross-analysis.yml"
WORKFLOW_TEXT = WORKFLOW_PATH.read_text(encoding="utf-8")
WORKFLOW = yaml.safe_load(WORKFLOW_TEXT)


def test_cross_analysis_workflow_is_valid_yaml():
    assert isinstance(WORKFLOW, dict)
    assert isinstance(WORKFLOW.get("jobs"), dict)


def test_cross_analysis_has_read_only_repository_permissions():
    assert WORKFLOW.get("permissions") == {"contents": "read"}
    assert "contents: write" not in WORKFLOW_TEXT


def test_cross_analysis_never_commits_or_pushes_to_main():
    lowered = WORKFLOW_TEXT.lower()
    assert "git add" not in lowered
    assert "git commit" not in lowered
    assert "git push" not in lowered


def test_cross_analysis_preserves_outputs_as_bounded_artifact():
    assert "actions/upload-artifact@v4" in WORKFLOW_TEXT
    assert "retention-days: 30" in WORKFLOW_TEXT
    assert "if-no-files-found: error" in WORKFLOW_TEXT
    for output in (
        "ping-pongings/knowledge-base/entity_cooccurrence.json",
        "ping-pongings/knowledge-base/sentiment_shift.json",
        "ping-pongings/knowledge-base/entity_sentiment_profile.json",
        "web/entity_cooccurrence.json",
        "web/sentiment_shift.json",
        "web/entity_sentiment_profile.json",
    ):
        assert output in WORKFLOW_TEXT


def test_cross_analysis_only_accepts_successful_upstream_cycle():
    assert "workflow_run:" in WORKFLOW_TEXT
    assert "conclusion == 'success'" in WORKFLOW_TEXT
    assert "schedule:" in WORKFLOW_TEXT


def test_cross_analysis_checkout_does_not_persist_credentials():
    checkout = next(
        step for step in WORKFLOW["jobs"]["analyze"]["steps"]
        if step.get("name") == "Checkout"
    )
    assert checkout["with"]["persist-credentials"] is False


def test_cross_analysis_safety_test_is_registered_in_core_ci():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "tests/test_cross_analysis_workflow_safety.py" in ci
    assert "pyyaml" in ci.lower()
