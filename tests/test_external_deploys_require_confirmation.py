from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_WORKFLOWS = (
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/deploy-databricks.yml",
    ".github/workflows/sync-huggingface.yml",
    ".github/workflows/databricks-bundle.yml",
    ".github/workflows/barrot-restart-space.yml",
    ".github/workflows/barrot-merge.yml",
    ".github/workflows/barrot-merge-manual.yml",
)


def test_external_deploy_workflows_are_manual_and_fail_closed() -> None:
    for relative_path in DEPLOY_WORKFLOWS:
        workflow = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert re.search(r"(?m)^  push:", workflow) is None, relative_path
        assert re.search(r"(?m)^  schedule:", workflow) is None, relative_path
        assert "workflow_dispatch:" in workflow, relative_path
        assert "default: NO" in workflow, relative_path
        assert "options:" in workflow and "- YES" in workflow, relative_path
        assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in workflow, relative_path
        assert re.search(r"(?m)^\s*(contents|pull-requests):\s*write\b", workflow) is None, relative_path
        if relative_path.endswith("sync-huggingface.yml"):
            assert "permissions:\n  contents: read" in workflow, relative_path


def test_force_deploy_and_unverified_task_allocator_are_inert() -> None:
    force_deploy = (REPO_ROOT / ".github/workflows/force-deploy-space.yml").read_text(encoding="utf-8")
    task_allocator = (REPO_ROOT / ".github/workflows/task-allocator.yml").read_text(encoding="utf-8")

    for relative_path, workflow in (
        (".github/workflows/force-deploy-space.yml", force_deploy),
        (".github/workflows/task-allocator.yml", task_allocator),
    ):
        assert "permissions: {}" in workflow, relative_path
        assert "if: ${{ false }}" in workflow, relative_path
        assert "git push" not in workflow.lower(), relative_path
        assert "HF_TOKEN" not in workflow, relative_path
        assert "GROQ_API_KEY" not in workflow, relative_path
        assert "OPENAI_API_KEY" not in workflow, relative_path


def test_self_upgrade_requires_explicit_non_main_branch_approval() -> None:
    workflow = (REPO_ROOT / ".github/workflows/barrot-self-upgrade.yml").read_text(encoding="utf-8")
    assert "confirm_repository_write:" in workflow
    assert "default: NO" in workflow
    assert "options:" in workflow and "- YES" in workflow
    assert "if: ${{ inputs.confirm_repository_write == 'YES' && github.ref_type == 'branch' && github.ref != 'refs/heads/main' }}" in workflow
    assert "pull-requests: write" not in workflow
