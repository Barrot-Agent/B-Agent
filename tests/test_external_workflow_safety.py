from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

def read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")

def test_barrot_ops_is_manual_and_confirmation_gated():
    text = read("barrot-ops.yml")
    assert "\n  push:" not in text
    assert "workflow_dispatch:" in text
    assert "confirm_external_deploy:" in text
    assert "default: false" in text
    assert "if: inputs.confirm_external_deploy == true" in text
    assert "git push hf origin/main:main" in text
    assert "databricks workspace import" in text

def test_merge_queue_has_no_mutating_operations():
    text = read("merge-queue.yml").lower()
    assert "contents: read" in text and "contents: write" not in text
    assert "pull-requests: read" in text and "pull-requests: write" not in text
    for operation in ("gh pr merge", "update-branch", "git push", "git merge", "labels[]="):
        assert operation not in text
    assert "disabled" in text

def test_force_deploy_workflow_cannot_force_push_or_read_token():
    text = read("force-deploy-space.yml").lower()
    assert "git push -f" not in text
    assert "hf_token" not in text
    assert "huggingface.co/spaces/" not in text
    assert "contents: read" in text

def test_huggingface_sync_is_manual_additive_and_does_not_propagate_secrets():
    text = read("sync-huggingface.yml")
    assert "\n  push:" not in text
    assert "workflow_dispatch:" in text
    assert "confirm_external_deploy:" in text
    assert "if: inputs.confirm_external_deploy == true" in text
    assert "delete_patterns" not in text
    assert "api.delete_space_variable" not in text
    assert "api.add_space_secret" not in text
    assert "permissions:\n  contents: read" in text

def test_databricks_deploy_is_manual_gated_and_uses_real_script_path():
    text = read("deploy-databricks.yml")
    assert "\n  push:" not in text
    assert "workflow_dispatch:" in text
    assert "confirm_external_deploy:" in text
    assert "if: inputs.confirm_external_deploy == true" in text
    assert "run: python3 scripts/deploy_databricks.py" in text
    assert "run: python deploy_databricks.py" not in text
    assert (ROOT / "scripts" / "deploy_databricks.py").is_file()
