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


def test_model_secret_is_isolated_from_the_write_job():
    content = _workflow_text()
    simulate = content.split("  simulate:", 1)[1].split("  persist:", 1)[0]
    persist = content.split("  persist:", 1)[1]
    assert "GROQ_API_KEY" in simulate
    assert "GROQ_API_KEY" not in persist
    assert "contents: read" in simulate
    assert "contents: write" in persist
    assert "persist-credentials: false" in simulate
    assert "persist-credentials: false" in persist
    assert "actions/download-artifact" in persist
    assert "gh auth setup-git" in persist


def test_persist_job_rechecks_main_and_limits_writes_to_two_state_files():
    content = _workflow_text()
    persist = content.split("  persist:", 1)[1]
    assert persist.count("git fetch --no-tags --depth=1 origin main") == 1
    assert '[[ "$(git rev-parse HEAD)" == "$EXPECTED_MAIN_SHA" && "$current_main" == "$EXPECTED_MAIN_SHA" ]]' in persist
    assert "git status --porcelain" in persist
    assert "web/paper_trading_state.json" in persist
    assert "web/paper_trading_log.jsonl" in persist
    assert "git push origin HEAD:main" in persist
    assert "needs: simulate" in content



def test_paper_trader_jobs_require_main_ref_and_explicit_confirmation():
    content = _workflow_text()
    required = "if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main' && inputs.confirm == 'YES'"
    assert content.count(required) == 2
    assert '[[ "$GITHUB_REF" == "refs/heads/main" ]]' in content
