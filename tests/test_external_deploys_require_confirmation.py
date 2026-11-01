from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXTERNAL_MUTATION_WORKFLOWS = (
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/deploy-databricks.yml",
    ".github/workflows/databricks-bundle.yml",
    ".github/workflows/sync-huggingface.yml",
    ".github/workflows/barrot-restart-space.yml",
    ".github/workflows/barrot-merge.yml",
    ".github/workflows/barrot-merge-manual.yml",
    ".github/workflows/barrot-self-upgrade.yml",
)

FORBIDDEN_MARKERS = (
    "secrets.",
    "HF_TOKEN",
    "GROQ_API_KEY",
    "DATABRICKS_TOKEN",
    "KAGGLE_JSON",
    "git push",
    "databricks bundle deploy",
    "databricks workspace import",
    "api.upload_folder",
    "api.add_space_secret",
    "hf upload",
    "mergekit-yaml",
    "scripts/barrot_self_upgrade.py",
)


def test_external_mutation_workflows_are_inert_until_protected_environment_is_verified() -> None:
    for relative_path in EXTERNAL_MUTATION_WORKFLOWS:
        workflow = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "workflow_dispatch:" in workflow, relative_path
        assert "permissions: {}" in workflow, relative_path
        assert "if: ${{ false }}" in workflow, relative_path
        for marker in FORBIDDEN_MARKERS:
            assert marker not in workflow, (relative_path, marker)
