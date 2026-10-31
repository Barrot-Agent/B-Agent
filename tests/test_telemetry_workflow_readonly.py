from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "autonomous_self_deployment.yml").read_text(encoding="utf-8")


def test_telemetry_workflow_is_read_only_and_artifact_only():
    assert "contents: read" in WORKFLOW
    assert "contents: write" not in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "actions/upload-artifact@v4" in WORKFLOW
    assert "TELEMETRY_ONLY" in WORKFLOW
    assert "NOT_PERFORMED" in WORKFLOW
    for forbidden in ("git add", "git commit", "git push", "wrangler deploy", "vercel deploy"):
        assert forbidden not in WORKFLOW.lower()
