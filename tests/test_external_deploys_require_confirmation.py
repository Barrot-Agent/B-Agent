from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_WORKFLOWS = (
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/deploy-databricks.yml",
    ".github/workflows/sync-huggingface.yml",
    ".github/workflows/databricks-bundle.yml",
)


def test_external_deploy_workflows_are_disabled_pending_protected_environment():
    for relative_path in DEPLOY_WORKFLOWS:
        workflow = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "workflow_dispatch: {}" in workflow, relative_path
        assert "permissions: {}" in workflow, relative_path
        assert "if: false" in workflow, relative_path
        assert "secrets." not in workflow, relative_path
        assert "schedule:" not in workflow, relative_path
        assert "push:" not in workflow, relative_path
