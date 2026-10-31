from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/cross-analysis.yml").read_text(encoding="utf-8")
CI_WORKFLOW = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")


def test_cross_analysis_uses_read_only_repository_permissions():
    assert "permissions:\n  contents: read" in WORKFLOW
    assert "contents: write" not in WORKFLOW


def test_cross_analysis_never_commits_or_pushes_to_main():
    lowered = WORKFLOW.lower()
    assert "git add" not in lowered
    assert "git commit" not in lowered
    assert "git push" not in lowered


def test_cross_analysis_preserves_outputs_as_a_bounded_artifact():
    assert "actions/upload-artifact@v4" in WORKFLOW
    assert "retention-days: 30" in WORKFLOW
    assert "if-no-files-found: error" in WORKFLOW
    for output in (
        "ping-pongings/knowledge-base/entity_cooccurrence.json",
        "ping-pongings/knowledge-base/sentiment_shift.json",
        "ping-pongings/knowledge-base/entity_sentiment_profile.json",
        "web/entity_cooccurrence.json",
        "web/sentiment_shift.json",
        "web/entity_sentiment_profile.json",
    ):
        assert output in WORKFLOW


def test_cross_analysis_only_runs_after_successful_upstream_cycle():
    assert "workflow_run:" in WORKFLOW
    assert "conclusion == 'success'" in WORKFLOW
    assert "schedule:" in WORKFLOW


def test_cross_analysis_checkout_does_not_persist_credentials():
    assert "persist-credentials: false" in WORKFLOW


def test_cross_analysis_safety_tests_are_registered_in_core_ci():
    assert "tests/test_cross_analysis_workflow_safety.py" in CI_WORKFLOW
