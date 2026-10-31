from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/autonomous_self_deployment.yml").read_text(encoding="utf-8")
CI_WORKFLOW = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")


def test_telemetry_workflow_has_read_only_repository_permissions():
    assert "permissions:\n  contents: read" in WORKFLOW
    assert "contents: write" not in WORKFLOW


def test_telemetry_checkout_does_not_persist_repository_credentials():
    assert "persist-credentials: false" in WORKFLOW


def test_telemetry_workflow_never_commits_pushes_or_deploys():
    lowered = WORKFLOW.lower()
    for forbidden in ("git add", "git commit", "git push", "actions/deploy-pages@", "hf upload", "vercel deploy"):
        assert forbidden not in lowered


def test_telemetry_is_uploaded_as_a_bounded_artifact():
    assert "actions/upload-artifact@v4" in WORKFLOW
    assert "retention-days: 30" in WORKFLOW
    assert "if-no-files-found: error" in WORKFLOW
    assert "AUTONOMOUS_DEPLOYMENT_REPORT.md" in WORKFLOW


def test_telemetry_report_distinguishes_observation_from_deployment():
    assert "TELEMETRY_ONLY" in WORKFLOW
    assert "NOT_PERFORMED" in WORKFLOW
    assert "no files committed or pushed" in WORKFLOW.lower()


def test_scheduled_and_manual_telemetry_triggers_are_preserved():
    assert "schedule:" in WORKFLOW
    assert "workflow_dispatch:" in WORKFLOW


def test_telemetry_safety_test_is_registered_in_core_ci():
    assert "tests/test_telemetry_snapshot_workflow_safety.py" in CI_WORKFLOW
