from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "cross-analysis.yml").read_text(encoding="utf-8")


def test_cross_analysis_preserves_supported_triggers_and_success_guard():
    assert 'workflows: ["Knowledge Signal Cycle"]' in WORKFLOW
    assert "types: [completed]" in WORKFLOW
    assert "schedule:" in WORKFLOW
    assert "cron: '50 * * * *'" in WORKFLOW
    assert "workflow_dispatch:" in WORKFLOW
    assert "github.event.workflow_run.conclusion == 'success'" in WORKFLOW


def test_cross_analysis_is_read_only_and_does_not_persist_checkout_credentials():
    assert re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", WORKFLOW)
    assert not re.search(r"(?m)^\s*(contents|actions|pull-requests|issues):\s*write\s*$", WORKFLOW)
    assert "persist-credentials: false" in WORKFLOW
    assert "GH_TOKEN:" not in WORKFLOW
    assert "git add" not in WORKFLOW
    assert "git commit" not in WORKFLOW
    assert "git pull" not in WORKFLOW
    assert "git push" not in WORKFLOW


def test_cross_analysis_uploads_all_generated_outputs_without_repository_mutation():
    for path in (
        "ping-pongings/knowledge-base/entity_cooccurrence.json",
        "ping-pongings/knowledge-base/sentiment_shift.json",
        "ping-pongings/knowledge-base/entity_sentiment_profile.json",
        "web/entity_cooccurrence.json",
        "web/sentiment_shift.json",
        "web/entity_sentiment_profile.json",
    ):
        assert path in WORKFLOW
    assert "actions/upload-artifact@v4" in WORKFLOW
    assert "if-no-files-found: error" in WORKFLOW
    assert "retention-days: 30" in WORKFLOW
    assert "No repository files were committed or pushed." in WORKFLOW
