from pathlib import Path

WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "coinbase-paper-trader.yml"
)


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _assert_quarantined() -> str:
    content = _workflow_text()
    assert "workflow_dispatch:" in content
    assert "permissions: {}" in content
    assert "if: ${{ false }}" in content
    assert "secrets." not in content
    assert "uses:" not in content
    assert "schedule:" not in content
    assert "push:" not in content
    assert "workflow_run:" not in content
    assert "git push" not in content
    assert "actions/upload-artifact" not in content
    assert "GROQ_API_KEY" not in content
    assert "Disabled:" in content
    return content


def test_paper_trader_workflow_is_quarantined_until_xrp_shadow_evaluation_exists():
    content = _assert_quarantined()
    assert "legacy BTC-USD paper trader" in content
    assert "not the XRP shadow-evaluation engine" in content
    assert "No credentials are read" in content


def test_paper_trader_is_artifact_only_and_never_writes_to_main():
    content = _assert_quarantined()
    assert "contents: write" not in content
    assert "git commit" not in content
    assert "GITHUB_TOKEN" not in content
    assert "actions/upload-artifact" not in content


def test_model_secret_is_not_exposed_while_quarantined():
    content = _assert_quarantined()
    assert "secrets." not in content
    assert "GROQ_API_KEY" not in content
    assert "simulate:" not in content


def test_simulation_refuses_stale_or_unpinned_main_revision_while_quarantined():
    content = _assert_quarantined()
    assert "expected_main_sha" not in content
    assert "ref:" not in content
    assert "python" not in content.lower()
