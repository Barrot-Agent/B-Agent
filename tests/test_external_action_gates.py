from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_destructive_or_secret_input_workflows_are_disabled() -> None:
    disabled = (
        "force-deploy-space.yml",
        "barrot-hf-admin.yml",
        "rotate-databricks-token.yml",
        "gumroad-metrics.yml",
        "barrot-merge-manual.yml",
    )
    for name in disabled:
        content = _read(name)
        assert "permissions: {}" in content
        assert "if: ${{ false }}" in content
        assert "secrets." not in content
        assert "schedule:" not in content
        assert "git push" not in content
        assert "curl " not in content
        assert "gh secret set" not in content


def test_databricks_pat_is_not_a_workflow_dispatch_input() -> None:
    content = _read("rotate-databricks-token.yml")
    assert "new_token" not in content
    assert "DATABRICKS_TOKEN" not in content
    assert "gh workflow run" not in content


def test_model_upload_requires_approval_and_validated_destination() -> None:
    content = _read("barrot-merge.yml")
    assert "confirm_external_change" in content
    assert "default: NO" in content
    assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in content
    assert "MODEL_NAME: ${{ inputs.model_name }}" in content
    assert '[[ ! "$MODEL_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]]' in content
    assert "${{ github.event.inputs.model_name }}" not in content
    assert "--trust-remote-code" not in content


def test_self_upgrade_requires_explicit_approval_and_main_base() -> None:
    content = _read("barrot-self-upgrade.yml")
    assert "confirm_external_change" in content
    assert "default: NO" in content
    assert "inputs.confirm_external_change == 'YES'" in content
    assert "github.ref == 'refs/heads/main'" in content
    assert "ref: main" in content
    assert "python3 scripts/barrot_self_upgrade.py" in content
    assert "--persist-audit-report" not in content
    assert "gh pr merge" not in content


def test_factory_restart_requires_explicit_approval() -> None:
    content = _read("barrot-restart-space.yml")
    assert "confirm_external_change" in content
    assert "default: NO" in content
    assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in content
    assert "restart?factory=true" in content


def test_existing_safe_external_deploys_keep_per_run_confirmation() -> None:
    for name in ("deploy-databricks.yml", "sync-huggingface.yml"):
        content = _read(name)
        assert "confirm_external_change" in content
        assert "default: NO" in content
        assert "if: ${{ inputs.confirm_external_change == 'YES' }}" in content


def test_controlled_pr_approval_is_not_a_merge_action() -> None:
    content = _read("barrot-approve-pr.yml")
    assert "expected_head_sha" in content
    assert "APPROVAL_REASON" in content
    assert "MERGE_PERFORMED=FALSE" in content
    assert "gh pr merge" not in content
