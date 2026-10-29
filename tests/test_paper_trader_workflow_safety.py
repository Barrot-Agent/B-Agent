from pathlib import Path


WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "coinbase-paper-trader.yml"
)


def test_paper_trader_workflow_is_manual_only_while_state_is_unreconciled():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in content
    assert "schedule:" not in content
    assert "Validate persisted paper position before execution" in content


def test_workflow_fails_closed_on_unknown_or_mismatched_position_identity():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "position_size" in content
    assert "position_product" in content
    assert 'os.environ["PRODUCT_ID"]' in content
    assert "open paper position has no product identity" in content
    assert "does not match open position" in content
    assert "state preserved" in content
