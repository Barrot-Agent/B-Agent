from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_WORKFLOWS = (
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/deploy-databricks.yml",
    ".github/workflows/sync-huggingface.yml",
    ".github/workflows/databricks-bundle.yml",
)


def test_external_deploy_workflows_are_manual_and_fail_closed() -> None:
    for relative_path in DEPLOY_WORKFLOWS:
        workflow = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert re.search(r"(?m)^  push:", workflow) is None, relative_path
        assert re.search(r"(?m)^  schedule:", workflow) is None, relative_path
        assert "workflow_dispatch:" in workflow, relative_path
        assert "default: NO" in workflow, relative_path
        assert "options:" in workflow and "- YES" in workflow, relative_path
        if relative_path == ".github/workflows/barrot-ops.yml":
            assert "inputs.confirm_databricks_workspace_create == 'YES'" in workflow
            assert "inputs.confirm_kaggle_dataset_download == 'YES'" in workflow
            assert "confirm_external_change" not in workflow
            assert "github.ref == 'refs/heads/main'" in workflow
            assert "workspace/get-status" in workflow
            assert "--overwrite" not in workflow
            assert "databricks/setup-cli@4f41a4c5291b531c1bb1e5760d677999cd484f89" in workflow
            assert "kaggle datasets submit" not in workflow
        else:
            assert "inputs.confirm_external_change == 'YES'" in workflow, relative_path
        assert re.search(r"(?m)^\s*(contents|pull-requests):\s*write\b", workflow) is None, relative_path
        if relative_path.endswith(("sync-huggingface.yml", "deploy-databricks.yml")):
            assert "expected_source_sha" in workflow, relative_path
            assert "github.ref == 'refs/heads/main'" in workflow, relative_path
        if relative_path.endswith("sync-huggingface.yml"):
            assert "permissions:\n  contents: read" in workflow, relative_path
