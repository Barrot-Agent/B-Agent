from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TRADER_PATH = REPO_ROOT / "scripts" / "coinbase_paper_trader.py"


def load_trader():
    spec = importlib.util.spec_from_file_location("coinbase_paper_trader_product_state_test", TRADER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_state(*, cash=1000.0, size=0.0, product=None, avg=None, count=0):
    return {
        "cash_usd": cash,
        "position_size": size,
        "position_product": product,
        "avg_entry_price": avg,
        "trade_count": count,
        "started_at": "2026-01-01T00:00:00+00:00",
    }


def test_empty_position_accepts_any_configured_product():
    trader = load_trader()
    assert trader.validate_position_product(make_state(), "BTC-USD") is None
    assert trader.validate_position_product(make_state(), "XRP-USD") is None


def test_legacy_open_position_without_product_identity_fails_closed():
    trader = load_trader()
    state = make_state(size=0.25, avg=40000.0)
    error = trader.validate_position_product(state, "BTC-USD")
    assert error is not None
    assert "no product identity" in error


def test_open_position_for_different_product_fails_closed():
    trader = load_trader()
    state = make_state(size=0.25, product="BTC-USD", avg=40000.0)
    error = trader.validate_position_product(state, "XRP-USD")
    assert error is not None
    assert "does not match open position BTC-USD" in error


def test_buy_records_product_identity():
    trader = load_trader()
    state = make_state()
    result = trader.execute_paper_trade(
        state, {"action": "buy", "amount_usd": 100}, 10.0, "BTC-USD"
    )
    assert result == "bought $100.00 at $10.00"
    assert state["position_product"] == "BTC-USD"
    assert state["position_size"] == 10.0
    assert state["cash_usd"] == 900.0


def test_mismatched_product_trade_does_not_mutate_state():
    trader = load_trader()
    state = make_state(cash=500.0, size=2.0, product="BTC-USD", avg=100.0, count=4)
    before = state.copy()
    result = trader.execute_paper_trade(
        state, {"action": "buy", "amount_usd": 100}, 10.0, "XRP-USD"
    )
    assert "does not match open position BTC-USD" in result
    assert state == before


def test_full_sell_clears_product_identity():
    trader = load_trader()
    state = make_state(cash=800.0, size=2.0, product="BTC-USD", avg=100.0, count=4)
    result = trader.execute_paper_trade(
        state, {"action": "sell", "amount_usd": 0}, 100.0, "BTC-USD"
    )
    assert result == "sold $200.00 at $100.00"
    assert state["position_size"] == 0.0
    assert state["position_product"] is None
    assert state["avg_entry_price"] is None


def test_partial_sell_preserves_product_identity():
    trader = load_trader()
    state = make_state(cash=800.0, size=2.0, product="BTC-USD", avg=100.0, count=4)
    result = trader.execute_paper_trade(
        state, {"action": "sell", "amount_usd": 50}, 100.0, "BTC-USD"
    )
    assert result == "sold $50.00 at $100.00"
    assert state["position_size"] == 1.5
    assert state["position_product"] == "BTC-USD"


def test_run_aborts_before_model_call_for_unidentified_open_position(monkeypatch):
    trader = load_trader()
    monkeypatch.setattr(trader, "GROQ_KEY", "test-key")
    monkeypatch.setattr(trader, "PRODUCT_ID", "BTC-USD")
    monkeypatch.setattr(trader, "fetch_ticker", lambda product: {"price": "100", "bid": "99", "ask": "101"})
    monkeypatch.setattr(trader, "fetch_recent_trades", lambda product: [])
    monkeypatch.setattr(trader, "load_state", lambda: make_state(size=0.25, avg=40000.0))
    monkeypatch.setattr(trader, "decide", lambda *args: (_ for _ in ()).throw(AssertionError("model must not run")))

    try:
        trader.run()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("run must stop when an open position lacks product identity")
