from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "barrot-ops.yml"


def test_external_deployment_workflow_is_manual_and_explicitly_gated() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "\n  push:\n" not in text
    assert "workflow_dispatch:" in text
    assert "confirm_external_deploy:" in text
    assert "required: true" in text
    assert "default: false" in text
    assert "type: boolean" in text
    assert "if: inputs.confirm_external_deploy == true" in text


def test_external_write_targets_remain_visible_behind_gate() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "git push hf origin/main:main" in text
    assert "databricks workspace import src/barrot_databricks_job.py" in text
    assert "--overwrite" in text
    assert "permissions:\n  contents: read" in text
