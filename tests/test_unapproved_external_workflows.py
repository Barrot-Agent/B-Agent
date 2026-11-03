from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_model_upload_workflows_require_explicit_approval_and_safe_names():
    primary = read("barrot-merge.yml")
    manual = read("barrot-merge-manual.yml")
    assert primary == manual
    for workflow in (primary, manual):
        assert "default: NO" in workflow
        assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in workflow
        assert "MODEL_NAME: ${{ inputs.model_name }}" in workflow
        assert '^[a-z0-9][a-z0-9-]{0,63}$' in workflow
        assert "github.event.inputs.model_name" not in workflow
        assert "persist-credentials: false" in workflow
        assert "git push" not in workflow.lower()


def test_destructive_hugging_face_admin_workflow_is_inert():
    workflow = read("barrot-hf-admin.yml")
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    assert "HF_TOKEN" not in workflow
    assert "api/repos/delete" not in workflow
    assert "api/repos/create" not in workflow


def test_factory_restart_requires_explicit_approval():
    workflow = read("barrot-restart-space.yml")
    assert "default: NO" in workflow
    assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in workflow
    assert "permissions: {}" in workflow
    assert "factory=true" in workflow


def test_push_triggered_external_deployments_are_removed():
    for name in ("sync-self-hosted-brain.yml", "deploy-a2a-worker.yml"):
        workflow = read(name)
        assert re.search(r"(?m)^  push:", workflow) is None, name
        assert "workflow_dispatch:" in workflow, name
        assert "default: NO" in workflow, name
        assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in workflow, name
        assert "contents: write" not in workflow, name
        assert "persist-credentials: false" in workflow, name


def test_unverified_multi_platform_allocator_is_disabled():
    workflow = read("task-allocator.yml")
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    assert "CHATGPT_TOKEN" not in workflow
    assert "OPENAI_API_KEY" not in workflow
    assert "GROQ_API_KEY" not in workflow
    assert "gh secret list" not in workflow
    assert "git push" not in workflow
