"""Safety regression tests for the simulated Coinbase paper trader and workflow."""
import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "coinbase_paper_trader.py"
WORKFLOW = ROOT / ".github" / "workflows" / "coinbase-paper-trader.yml"
SPEC = importlib.util.spec_from_file_location("coinbase_paper_trader_safety", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(module)


def state():
    return {
        "cash_usd": 1000.0,
        "position_size": 2.0,
        "position_product": "BTC-USD",
        "avg_entry_price": 100.0,
        "trade_count": 3,
        "started_at": "2026-10-26T00:00:00Z",
    }


def test_invalid_decisions_do_not_mutate_simulated_state():
    invalid_amounts = (float("nan"), float("inf"), float("-inf"), "bad", True, None, -0.01)
    for amount in invalid_amounts:
        portfolio = state()
        before = portfolio.copy()
        result = module.execute_paper_trade(
            portfolio, {"action": "sell", "amount_usd": amount, "reasoning": "test"}, 100.0
        )
        assert result == "held -- invalid paper decision"
        assert portfolio == before


def test_unknown_action_and_non_object_decision_fail_closed():
    for decision in (
        {"action": "short", "amount_usd": 10, "reasoning": "unsupported"},
        ["buy", 10],
        None,
        {"action": "buy", "amount_usd": 10, "reasoning": 42},
    ):
        portfolio = state()
        before = portfolio.copy()
        result = module.execute_paper_trade(portfolio, decision, 100.0)
        assert result == "held -- invalid paper decision"
        assert portfolio == before


def test_invalid_price_does_not_mutate_state():
    for price in (0, -1, float("nan"), float("inf"), "bad", True):
        portfolio = state()
        before = portfolio.copy()
        result = module.execute_paper_trade(
            portfolio, {"action": "buy", "amount_usd": 100, "reasoning": "test"}, price
        )
        assert result == "held -- invalid current price"
        assert portfolio == before


def test_buy_is_capped_at_twenty_percent_of_cash_and_sell_is_position_capped():
    portfolio = state()
    result = module.execute_paper_trade(
        portfolio, {"action": "buy", "amount_usd": 99999, "reasoning": "test"}, 100.0
    )
    assert result == "bought $200.00 at $100.00"
    assert math.isclose(portfolio["cash_usd"], 800.0)
    assert math.isclose(portfolio["position_size"], 4.0)
    assert portfolio["trade_count"] == 4

    result = module.execute_paper_trade(
        portfolio, {"action": "sell", "amount_usd": 99999, "reasoning": "test"}, 100.0
    )
    assert result == "sold $400.00 at $100.00"
    assert portfolio["position_size"] == 0.0
    assert math.isclose(portfolio["cash_usd"], 1200.0)
    assert portfolio["trade_count"] == 5


def test_workflow_is_manual_read_only_and_does_not_push_simulation_state():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "git push" not in workflow
    assert "git commit" not in workflow
    assert "git add" not in workflow
    assert "actions/upload-artifact@" in workflow
