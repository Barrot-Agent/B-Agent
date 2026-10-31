from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "rotate-databricks-token.yml"


def test_token_rotation_workflow_is_disabled_and_accepts_no_secret_input():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "permissions: {}" in workflow
    assert "inputs:" not in workflow
    assert "new_token" not in workflow
    assert "secrets." not in workflow
    assert "${{ inputs." not in workflow


def test_token_rotation_workflow_cannot_mutate_secrets_or_trigger_deployment():
    workflow = WORKFLOW.read_text(encoding="utf-8").lower()

    assert "gh secret set" not in workflow
    assert "gh workflow run" not in workflow
    assert "contents: write" not in workflow
    assert "actions: write" not in workflow
    assert "ROTATION_NOT_PERFORMED".lower() in workflow
    assert "github_step_summary" in workflow
