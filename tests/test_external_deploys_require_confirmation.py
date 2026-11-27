from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_WORKFLOWS = (
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/sync-huggingface.yml",
    ".github/workflows/databricks-bundle.yml",
)


def test_external_deploy_workflows_are_manual_and_fail_closed() -> None:
    for relative_path in DEPLOY_WORKFLOWS:
        workflow = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert re.search(r"(?m)^  push:", workflow) is None, relative_path
        assert re.search(r"(?m)^  schedule:", workflow) is None, relative_path
        assert "workflow_dispatch:" in workflow, relative_path
        if relative_path == ".github/workflows/barrot-ops.yml":
            assert "default: NO" in workflow
            assert "options:" in workflow and "- YES" in workflow
            assert "inputs.confirm_databricks_workspace_create == 'YES'" in workflow
            assert "inputs.confirm_kaggle_dataset_download == 'YES'" in workflow
            assert "github.ref == 'refs/heads/main'" in workflow
            assert "workspace/get-status" in workflow
            assert "--overwrite" not in workflow
            assert "databricks/setup-cli@12452ad4003a2dd61d5a7cee30bc068f750a2e00" in workflow
            assert "kaggle datasets submit" not in workflow
            assert "contents: read" in workflow
        else:
            assert "permissions: {}" in workflow, relative_path
            assert ("if: $" + "{{ false }}") in workflow, relative_path
            assert "secrets." not in workflow, relative_path
            assert "uses:" not in workflow, relative_path
        assert re.search(r"(?m)^\s*(contents|pull-requests):\s*write\b", workflow) is None, relative_path

def test_legacy_databricks_overwrite_workflow_is_quarantined() -> None:
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "deploy-databricks.yml"
    ).read_text(encoding="utf-8")
    assert "permissions: {}" in workflow
    assert "if: ${{ false }}" in workflow
    assert "secrets." not in workflow
    assert "scripts/deploy_databricks.py" not in workflow
