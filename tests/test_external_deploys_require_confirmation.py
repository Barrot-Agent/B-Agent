from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_WORKFLOWS = (
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/deploy-databricks.yml",
)

QUARANTINED_DEPLOY_WORKFLOWS = (
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
        assert "inputs.confirm_external_change == 'YES'" in workflow, relative_path
        assert re.search(r"(?m)^\s*(contents|pull-requests):\s*write\b", workflow) is None, relative_path
        if relative_path.endswith("deploy-databricks.yml"):
            assert "expected_source_sha" in workflow, relative_path
            assert "github.ref == 'refs/heads/main'" in workflow, relative_path
        if relative_path.endswith("sync-huggingface.yml"):
            assert "permissions:\n  contents: read" in workflow, relative_path



def test_unreviewed_external_deploy_workflows_are_quarantined() -> None:
    forbidden = ("secrets.", "uses:", "run: databricks bundle deploy", "run: databricks bundle run", "api.upload_folder", "api.add_space_secret")
    for relative_path in QUARANTINED_DEPLOY_WORKFLOWS:
        workflow = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "workflow_dispatch: {}" in workflow, relative_path
        assert "permissions: {}" in workflow, relative_path
        assert "if: ${{ false }}" in workflow, relative_path
        for token in forbidden:
            assert token not in workflow.lower(), (relative_path, token)


def test_space_and_worker_secret_mutations_require_separate_explicit_approval() -> None:
    for relative_path in (
        ".github/workflows/deploy-a2a-worker.yml",
        ".github/workflows/sync-self-hosted-brain.yml",
    ):
        workflow = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "confirm_secret_rotation:" in workflow, relative_path
        assert 'options: ["NO", "YES"]' in workflow, relative_path
        assert "inputs.confirm_secret_rotation == 'YES'" in workflow, relative_path
        assert "expected_main_sha:" in workflow, relative_path
        assert "github.ref == 'refs/heads/main'" in workflow, relative_path
        assert "persist-credentials: false" in workflow, relative_path


def test_barrot_ops_external_writes_require_independent_yes_inputs():
    workflow = (REPO_ROOT / ".github/workflows/barrot-ops.yml").read_text(encoding="utf-8")
    for input_name in ("confirm_databricks_workspace_import", "confirm_kaggle_dataset_download"):
        assert f"{input_name}:" in workflow
        assert "default: NO" in workflow
        assert f"inputs.{input_name} == 'YES'" in workflow
    assert "if: ${{ inputs.confirm_databricks_workspace_import == 'YES' }}" in workflow
    assert "if: ${{ inputs.confirm_kaggle_dataset_download == 'YES' }}" in workflow
    assert "databricks workspace import" in workflow
    assert "kaggle datasets download" in workflow


def test_databricks_setup_cli_uses_a_verified_immutable_commit():
    workflow = (REPO_ROOT / ".github/workflows/barrot-ops.yml").read_text(encoding="utf-8")
    assert "uses: databricks/setup-cli@9625fdde9ba2607df0087e0d3ec7449198bf2180" in workflow
    assert "uses: databricks/setup-cli@main" not in workflow
    assert "inputs.confirm_external_change == 'YES'" in workflow
    assert "expected_source_sha" in workflow


def test_lean_installer_script_uses_the_verified_v4_2_4_commit():
    workflow = (REPO_ROOT / ".github/workflows/formal-verification-benchmarks.yml").read_text(encoding="utf-8")
    assert "raw.githubusercontent.com/leanprover/elan/227caca133724d5516bee25c2aeb3e609478f2d8/elan-init.sh" in workflow
    assert "raw.githubusercontent.com/leanprover/elan/master/elan-init.sh" not in workflow
    assert 'sh "$RUNNER_TEMP/elan-init.sh" -y' in workflow
