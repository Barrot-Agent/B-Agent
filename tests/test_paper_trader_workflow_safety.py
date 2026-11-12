from pathlib import Path

WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "coinbase-paper-trader.yml"
)


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_paper_trader_workflow_is_manual_and_requires_explicit_sha_confirmation():
    content = _workflow_text()
    assert "workflow_dispatch:" in content
    assert "schedule:" not in content
    assert "confirm:" in content
    assert "expected_main_sha:" in content
    assert 'CONFIRM: ${{ inputs.confirm }}' in content
    assert 'EXPECTED_MAIN_SHA: ${{ inputs.expected_main_sha }}' in content
    assert '[[ "$CONFIRM" == "YES" ]]' in content
    assert "A full 40-character main SHA is required" in content
    assert "github.ref == 'refs/heads/main'" in content


def test_paper_trader_is_artifact_only_and_never_writes_to_main():
    content = _workflow_text()
    assert "  persist:" not in content
    assert "contents: write" not in content
    assert "git push" not in content
    assert "gh auth setup-git" not in content
    assert "GITHUB_TOKEN" not in content
    assert "actions/download-artifact" not in content
    assert "actions/upload-artifact@v7" in content
    assert "web/paper_trading_state.json" in content
    assert "web/paper_trading_log.jsonl" in content
    assert "retention-days: 7" in content


def test_model_secret_is_scoped_only_to_the_manual_simulation_job():
    content = _workflow_text()
    assert content.count("GROQ_API_KEY:") == 1
    assert "secrets.GROQ_API_KEY" in content
    assert content.count("  simulate:") == 1
    assert "permissions:\n  contents: read" in content
    assert "persist-credentials: false" in content


def test_simulation_refuses_a_stale_or_unpinned_main_revision():
    content = _workflow_text()
    assert "ref: ${{ inputs.expected_main_sha }}" in content
    assert '[[ "$GITHUB_REF" == "refs/heads/main" ]]' in content
    assert '[[ "$CONFIRM" == "YES" ]]' in content
    assert '[[ "$EXPECTED_MAIN_SHA" =~ ^[0-9a-f]{40}$ ]]' in content
    assert '[[ "$current_main" == "$EXPECTED_MAIN_SHA" && "$checked_out" == "$EXPECTED_MAIN_SHA" ]]' in content
