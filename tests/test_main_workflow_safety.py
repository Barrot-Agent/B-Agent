from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def read(name):
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_cross_analysis_is_read_only_and_artifact_only():
    workflow = read("cross-analysis.yml")
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "git push" not in workflow
    assert "git commit" not in workflow
    assert "workflow_run:" in workflow
    assert "schedule:" in workflow
    assert "workflow_dispatch:" in workflow


def test_scheduler_tick_cannot_dispatch_or_write_repository_state():
    workflow = read("scheduler-tick.yml")
    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "actions: write" not in workflow
    assert "scheduler.py list" in workflow
    assert "scheduler.py tick" not in workflow
    assert "gh workflow run" not in workflow
    assert "git push" not in workflow
    assert "persist-credentials: false" in workflow


def test_merge_queue_is_read_only_and_cannot_merge_or_delete_branches():
    workflow = read("merge-queue.yml")
    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert "pull-requests: write" not in workflow
    assert "gh api" in workflow
    assert "gh pr merge" not in workflow
    assert "--delete-branch" not in workflow
    assert "update-branch" not in workflow
    assert "git push" not in workflow


def test_telemetry_workflow_does_not_commit_or_deploy():
    workflow = read("autonomous_self_deployment.yml")
    lowered = workflow.lower()
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "telemetry_only" in lowered
    assert "not_performed" in lowered
    for forbidden in ("git add", "git commit", "git push", "wrangler deploy", "vercel deploy"):
        assert forbidden not in lowered


def test_cloudflare_deploy_requires_manual_explicit_confirmation_and_environment():
    workflow = read("deploy-a2a-worker.yml")
    assert "workflow_dispatch:" in workflow
    assert "push:" not in workflow
    assert "confirm_external_deploy:" in workflow
    assert "default: NO" in workflow
    assert "environment: barrot-production" in workflow
    assert "inputs.confirm_external_deploy == 'YES'" in workflow
    assert "persist-credentials: false" in workflow
    assert "contents: read" in workflow


def test_ci_registers_workflow_and_signal_integrity_tests():
    ci = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    assert "tests/test_main_workflow_safety.py" in ci
    assert "tests/test_signal_accuracy_fail_closed.py" in ci
    assert "tests/test_sentiment_shift_data_quality.py" in ci

def test_cognitive_pingpong_is_manual_diagnostic_not_a_writer():
    workflow = read("Barrot.Cognitive.PingPong.Engine.yml")
    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow
    assert "push:" not in workflow
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "issues: write" not in workflow
    assert "pull-requests: write" not in workflow
    assert "NOT_IMPLEMENTED" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "git push" not in workflow


def test_scheduled_research_writers_are_artifact_only():
    for name in (
        "riemann-harvest.yml",
        "gumroad-metrics.yml",
        "barrot-transparency-audit.yml",
        "webmcp-live-sandbox.yml",
        "webmcp-monetization-enrich.yml",
    ):
        workflow = read(name)
        assert "contents: read" in workflow, name
        assert "contents: write" not in workflow, name
        assert "persist-credentials: false" in workflow, name
        assert "actions/upload-artifact@" in workflow, name
        assert "git push" not in workflow, name
        assert "git commit" not in workflow, name


def test_hover_bike_workflow_needs_no_repository_write_permission():
    workflow = read("hover_bike_updates.yml")
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "git push" not in workflow
