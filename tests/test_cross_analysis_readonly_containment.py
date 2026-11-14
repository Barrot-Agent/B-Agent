from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cross_analysis_is_read_only_and_cannot_push_to_main() -> None:
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "cross-analysis.yml"
    ).read_text(encoding="utf-8")
    lowered = workflow.lower()

    assert "permissions:\n  contents: read" in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "retention-days: 30" in workflow
    assert "if-no-files-found: error" in workflow
    assert "conclusion == 'success'" in workflow

    for output in (
        "ping-pongings/knowledge-base/entity_cooccurrence.json",
        "ping-pongings/knowledge-base/sentiment_shift.json",
        "ping-pongings/knowledge-base/entity_sentiment_profile.json",
        "web/entity_cooccurrence.json",
        "web/sentiment_shift.json",
        "web/entity_sentiment_profile.json",
    ):
        assert output in workflow

    for forbidden in (
        "contents: write",
        "git add",
        "git commit",
        "git push",
        "persist-credentials: true",
        "secrets.",
    ):
        assert forbidden not in lowered
