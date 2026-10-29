"""Safety tests for the Coinbase paper-trader decision boundary."""
import importlib.util
import math
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "coinbase_paper_trader.py"
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


def test_negative_sell_amount_cannot_increase_position_or_reduce_cash():
    portfolio = state()
    before = portfolio.copy()
    result = module.execute_paper_trade(
        portfolio, {"action": "sell", "amount_usd": -50, "reasoning": "bad output"}, 100.0
    )
    assert result == "held -- invalid paper decision"
    assert portfolio == before


def test_nonfinite_and_malformed_amounts_fail_closed():
    for amount in (float("nan"), float("inf"), float("-inf"), "not-a-number", True, None, -0.01):
        portfolio = state()
        before = portfolio.copy()
        result = module.execute_paper_trade(
            portfolio, {"action": "buy", "amount_usd": amount, "reasoning": "test"}, 100.0
        )
        assert result == "held -- invalid paper decision"
        assert portfolio == before


def test_unknown_action_and_non_object_decision_fail_closed():
    for decision in (
        {"action": "short", "amount_usd": 10, "reasoning": "unsupported"},
        ["buy", 10],
        None,
    ):
        portfolio = state()
        before = portfolio.copy()
        result = module.execute_paper_trade(portfolio, decision, 100.0)
        assert result == "held -- invalid paper decision"
        assert portfolio == before


def test_invalid_current_price_cannot_mutate_state():
    for price in (0, -1, float("nan"), float("inf"), "bad"):
        portfolio = state()
        before = portfolio.copy()
        result = module.execute_paper_trade(
            portfolio, {"action": "buy", "amount_usd": 100, "reasoning": "test"}, price
        )
        assert result == "held -- invalid current price"
        assert portfolio == before


def test_buy_is_capped_at_twenty_percent_of_available_cash():
    portfolio = state()
    result = module.execute_paper_trade(
        portfolio, {"action": "buy", "amount_usd": 99999, "reasoning": "test"}, 100.0
    )
    assert result == "bought $200.00 at $100.00"
    assert math.isclose(portfolio["cash_usd"], 800.0)
    assert math.isclose(portfolio["position_size"], 4.0)
    assert portfolio["trade_count"] == 4


def test_sell_cannot_exceed_position_size():
    portfolio = state()
    result = module.execute_paper_trade(
        portfolio, {"action": "sell", "amount_usd": 99999, "reasoning": "test"}, 100.0
    )
    assert result == "sold $200.00 at $100.00"
    assert portfolio["position_size"] == 0.0
    assert math.isclose(portfolio["cash_usd"], 1200.0)
    assert portfolio["trade_count"] == 4
