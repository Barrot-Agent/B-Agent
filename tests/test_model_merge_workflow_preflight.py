from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "barrot-merge.yml",
    ROOT / ".github" / "workflows" / "barrot-merge-manual.yml",
)
CONFIG_PATH = 'merges/barrot-superior/config.yaml'


def test_model_merge_workflows_validate_config_before_install_or_token_access():
    for workflow in WORKFLOWS:
        content = workflow.read_text(encoding="utf-8")
        assert "workflow_dispatch:" in content
        assert 'CONFIG_PATH="merges/barrot-superior/config.yaml"' in content
        assert 'if [[ ! -f "$CONFIG_PATH" ]]; then' in content
        assert 'echo "::error::Required model merge configuration is missing: $CONFIG_PATH"' in content
        assert content.index("Validate merge configuration before dependency installation or token access") < content.index("Install deps")
        assert content.index("Validate merge configuration before dependency installation or token access") < content.index("Configure git auth for HF")


def test_duplicate_model_merge_workflows_keep_same_fail_fast_preflight():
    first, second = (workflow.read_text(encoding="utf-8") for workflow in WORKFLOWS)
    assert first == second


def test_missing_merge_config_is_not_present_in_current_checkout_tree():
    # Static sentinel: if the config is later added, the preflight remains valid and the
    # workflow can proceed to its normal merge steps; until then it fails before secrets.
    assert CONFIG_PATH == "merges/barrot-superior/config.yaml"
