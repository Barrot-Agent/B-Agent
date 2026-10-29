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
        assert "if: \${{ inputs.confirm_external_change == 'YES' }}" in workflow, relative_path
        assert re.search(r"(?m)^\s*(contents|pull-requests):\s*write\b", workflow) is None, relative_path
        if relative_path.endswith("sync-huggingface.yml"):
            assert "permissions:\n  contents: read" in workflow, relative_path
