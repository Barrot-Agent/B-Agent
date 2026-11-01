import json
from pathlib import Path
import textwrap


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
PINGPONG = WORKFLOWS / "Barrot.Cognitive.PingPong.Engine.yml"


def test_cognitive_relay_is_manual_read_only_and_does_not_claim_live_collaboration():
    workflow = PINGPONG.read_text(encoding="utf-8")
    trigger_block = workflow.split("permissions:", 1)[0]

    assert "workflow_dispatch:" in trigger_block
    assert "schedule:" not in trigger_block
    assert "push:" not in trigger_block
    assert "permissions: {}" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "actions/checkout" not in workflow
    assert "secrets." not in workflow
    assert "contents: write" not in workflow
    assert "issues: write" not in workflow
    assert "pull-requests: write" not in workflow
    assert "git push" not in workflow
    assert "git commit" not in workflow
    assert "Signal strength: High" not in workflow
    assert "Response quality: Optimal" not in workflow


def test_cognitive_relay_artifact_reports_unverified_adapters_truthfully():
    workflow = PINGPONG.read_text(encoding="utf-8")
    lines = workflow.splitlines()
    start = next(i for i, line in enumerate(lines) if "<<'JSON'" in line) + 1
    end = next(i for i in range(start, len(lines)) if lines[i].strip() == "JSON")
    status = json.loads(textwrap.dedent("\\n".join(lines[start:end])))

    assert status["status"] == "NOT_IMPLEMENTED"
    assert status["live_collaboration_verified"] is False
    assert status["external_calls_made"] is False
    assert status["persistent_research_state_written"] is False
    assert status["verified_external_platform_adapters"] == []
    assert status["target_platforms"] == [
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks"
    ]


def test_disabled_privileged_workflows_retain_safe_manual_status_jobs():
    expectations = {
        "task-allocator.yml": "TASK_ALLOCATION_NOT_PERFORMED",
        "force-deploy-space.yml": "DEPLOYMENT_NOT_PERFORMED",
    }
    for filename, marker in expectations.items():
        workflow = (WORKFLOWS / filename).read_text(encoding="utf-8")
        trigger_block = workflow.split("permissions:", 1)[0]
        assert "workflow_dispatch:" in trigger_block
        assert "schedule:" not in trigger_block
        assert "push:" not in trigger_block
        assert "permissions: {}" in workflow
        assert "jobs:" in workflow
        assert "runs-on: ubuntu-latest" in workflow
        assert "if: ${{ false }}" not in workflow
        assert "secrets." not in workflow
        assert "actions/checkout" not in workflow
        assert "git push" not in workflow
        assert marker in workflow
