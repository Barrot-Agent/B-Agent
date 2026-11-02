from __future__ import annotations

import importlib.util
import json
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


def test_run_aborts_before_provider_calls_for_unidentified_open_position(monkeypatch):
    trader = load_trader()
    monkeypatch.setattr(trader, "GROQ_KEY", "test-key")
    monkeypatch.setattr(trader, "PRODUCT_ID", "BTC-USD")
    monkeypatch.setattr(
        trader, "fetch_ticker",
        lambda product: (_ for _ in ()).throw(AssertionError("ticker provider must not run")),
    )
    monkeypatch.setattr(
        trader, "fetch_recent_trades",
        lambda product: (_ for _ in ()).throw(AssertionError("trade provider must not run")),
    )
    monkeypatch.setattr(trader, "load_state", lambda: make_state(size=0.25, avg=40000.0))
    monkeypatch.setattr(
        trader, "decide",
        lambda *args: (_ for _ in ()).throw(AssertionError("model must not run")),
    )

    try:
        trader.run(allow_state_mutation=True)
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("run must stop when an open position lacks product identity")


def test_non_finite_position_size_fails_closed():
    trader = load_trader()
    for bad_size in (float("nan"), float("inf"), float("-inf")):
        error = trader.validate_position_product(make_state(size=bad_size), "BTC-USD")
        assert error == "aborted -- non-finite position size"


def test_existing_unreadable_state_fails_closed_without_reset(tmp_path, monkeypatch):
    trader = load_trader()
    state_path = tmp_path / "paper_state.json"
    original = "{invalid json"
    state_path.write_text(original, encoding="utf-8")
    monkeypatch.setattr(trader, "STATE_FILE", state_path)
    try:
        trader.load_state()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("unreadable existing state must fail closed")
    assert state_path.read_text(encoding="utf-8") == original


def test_state_validation_rejects_invalid_cash_and_average_entry():
    trader = load_trader()
    for cash in (float("nan"), float("inf"), -1.0):
        error = trader.validate_position_product(make_state(cash=cash), "BTC-USD")
        assert error is not None
    for avg in (None, 0.0, float("nan"), float("inf")):
        error = trader.validate_position_product(
            make_state(size=0.25, product="BTC-USD", avg=avg), "BTC-USD"
        )
        assert error is not None


def test_flat_position_rejects_stale_product_identity():
    trader = load_trader()
    state = make_state(size=0.0, product="BTC-USD", avg=None)
    assert "stale product identity" in trader.validate_position_product(state, "BTC-USD")


def test_non_finite_decision_amount_does_not_mutate_state():
    trader = load_trader()
    state = make_state()
    before = state.copy()
    result = trader.execute_paper_trade(
        state, {"action": "buy", "amount_usd": float("nan")}, 10.0, "BTC-USD"
    )
    assert result == "hold -- invalid decision amount"
    assert state == before


def test_invalid_current_price_does_not_mutate_state():
    trader = load_trader()
    for price in (0.0, float("nan"), float("inf")):
        state = make_state()
        before = state.copy()
        result = trader.execute_paper_trade(
            state, {"action": "buy", "amount_usd": 100}, price, "BTC-USD"
        )
        assert result == "hold -- invalid current price"
        assert state == before


def test_run_requires_explicit_mutation_authorization_before_state_or_network(monkeypatch):
    trader = load_trader()
    monkeypatch.setattr(
        trader, "load_state",
        lambda: (_ for _ in ()).throw(AssertionError("state must not be read before authorization")),
    )
    try:
        trader.run()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("run must require explicit mutation authorization")


def test_save_state_uses_atomic_replace(tmp_path, monkeypatch):
    trader = load_trader()
    state_path = tmp_path / "paper_state.json"
    monkeypatch.setattr(trader, "STATE_FILE", state_path)
    trader.save_state(make_state())
    assert json.loads(state_path.read_text(encoding="utf-8"))["position_size"] == 0.0
    assert not list(tmp_path.glob("*.tmp"))


def test_state_preflight_rejects_trade_count_exceeding_log_entries(tmp_path, monkeypatch):
    trader = load_trader()
    state_path = tmp_path / "paper_state.json"
    log_path = tmp_path / "paper_log.jsonl"
    state_path.write_text(json.dumps(make_state(trades=2)), encoding="utf-8")
    log_path.write_text(json.dumps({"timestamp": "2026-11-02T00:00:00Z"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(trader, "STATE_FILE", state_path)
    monkeypatch.setattr(trader, "LOG_FILE", log_path)
    try:
        trader.validate_state_only()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("state trade count greater than log entries must fail closed")
    assert json.loads(state_path.read_text(encoding="utf-8"))["trade_count"] == 2
    assert len(log_path.read_text(encoding="utf-8").splitlines()) == 1


def test_state_preflight_rejects_malformed_decision_log(tmp_path, monkeypatch):
    trader = load_trader()
    state_path = tmp_path / "paper_state.json"
    log_path = tmp_path / "paper_log.jsonl"
    state_path.write_text(json.dumps(make_state()), encoding="utf-8")
    log_path.write_text("{not json}\n", encoding="utf-8")
    monkeypatch.setattr(trader, "STATE_FILE", state_path)
    monkeypatch.setattr(trader, "LOG_FILE", log_path)
    try:
        trader.validate_state_only()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("malformed decision log must fail closed")


def test_state_preflight_allows_flat_zero_trade_state_without_log(tmp_path, monkeypatch):
    trader = load_trader()
    state_path = tmp_path / "paper_state.json"
    log_path = tmp_path / "paper_log.jsonl"
    state_path.write_text(json.dumps(make_state()), encoding="utf-8")
    monkeypatch.setattr(trader, "STATE_FILE", state_path)
    monkeypatch.setattr(trader, "LOG_FILE", log_path)
    state = trader.validate_state_only()
    assert state["trade_count"] == 0
    assert not log_path.exists()
