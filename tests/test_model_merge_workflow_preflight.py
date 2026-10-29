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


def test_preflight_segment_does_not_install_dependencies_or_access_hf_token():
    for workflow in WORKFLOWS:
        content = workflow.read_text(encoding="utf-8")
        preflight_segment = content.split("      - name: Install deps", 1)[0]
        assert "HF_TOKEN" not in preflight_segment
        assert "pip install" not in preflight_segment
        assert "test -f" not in preflight_segment  # only the expected -f absence guard is present
        assert '[[ ! -f "$CONFIG_PATH" ]]' in preflight_segment
