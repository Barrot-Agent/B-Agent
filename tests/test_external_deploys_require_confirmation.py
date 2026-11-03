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
        assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in workflow, relative_path
        assert re.search(r"(?m)^\s*(contents|pull-requests):\s*write\b", workflow) is None, relative_path
        if relative_path.endswith("sync-huggingface.yml"):
            assert "permissions:\n  contents: read" in workflow, relative_path


EXTERNAL_WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"


def read_external_workflow(name: str) -> str:
    return (EXTERNAL_WORKFLOW_DIR / name).read_text(encoding="utf-8")


def test_model_upload_workflows_require_explicit_approval_and_safe_names() -> None:
    primary = read_external_workflow("barrot-merge.yml")
    manual = read_external_workflow("barrot-merge-manual.yml")
    assert primary == manual
    for workflow in (primary, manual):
        assert "default: NO" in workflow
        assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in workflow
        assert "MODEL_NAME: ${{ inputs.model_name }}" in workflow
        assert "^[a-z0-9][a-z0-9-]{0,63}$" in workflow
        assert "github.event.inputs.model_name" not in workflow
        assert "persist-credentials: false" in workflow
        assert "git push" not in workflow.lower()


def test_destructive_hugging_face_admin_workflow_is_inert() -> None:
    workflow = read_external_workflow("barrot-hf-admin.yml")
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    assert "HF_TOKEN" not in workflow
    assert "api/repos/delete" not in workflow
    assert "api/repos/create" not in workflow


def test_factory_restart_requires_explicit_approval() -> None:
    workflow = read_external_workflow("barrot-restart-space.yml")
    assert "default: NO" in workflow
    assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in workflow
    assert "permissions: {}" in workflow
    assert "factory=true" in workflow


def test_push_triggered_external_deployments_are_removed() -> None:
    for name in ("sync-self-hosted-brain.yml", "deploy-a2a-worker.yml"):
        workflow = read_external_workflow(name)
        assert re.search(r"(?m)^  push:", workflow) is None, name
        assert "workflow_dispatch:" in workflow, name
        assert "default: NO" in workflow, name
        assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in workflow, name
        assert "contents: write" not in workflow, name
        assert "persist-credentials: false" in workflow, name


def test_unverified_multi_platform_allocator_is_disabled() -> None:
    workflow = read_external_workflow("task-allocator.yml")
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    assert "CHATGPT_TOKEN" not in workflow
    assert "OPENAI_API_KEY" not in workflow
    assert "GROQ_API_KEY" not in workflow
    assert "gh secret list" not in workflow
    assert "git push" not in workflow


def test_capability_9_data_resolver_is_disabled_until_adapter_verification() -> None:
    workflow = read_external_workflow("capability-9-data-resolver.yml")
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    assert "GROQ_API_KEY" not in workflow
    assert "git push" not in workflow
    assert "api.groq.com" not in workflow
