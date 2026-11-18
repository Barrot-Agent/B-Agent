"""Tests for the paper-trading sandbox.

These lock the safety properties, not a strategy: no network, no live key,
1% risk ceiling, 2R floor, stop always, 3 trades a day, no leverage.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from barrot_agent.trading.paper_sandbox import (
    MAX_TRADES_PER_DAY,
    STARTING_BALANCE,
    Setup,
    evaluate,
    live_credentials_present,
    read_csv,
    summarise,
    to_row,
    write_csv,
)

MODULE = Path(__file__).resolve().parents[1] / "barrot_agent/trading/paper_sandbox.py"
FORBIDDEN_IMPORTS = {
    "socket",
    "ssl",
    "http",
    "urllib",
    "requests",
    "aiohttp",
    "httpx",
    "websocket",
    "websockets",
    "ccxt",
    "web3",
}


def setup(**overrides) -> Setup:
    base = dict(
        trade_id="T-001",
        timestamp_utc="2026-11-18T00:00:00Z",
        pair="BTC/USDT",
        side="long",
        entry=62_000.0,
        stop=61_250.0,
        target=63_500.0,
    )
    base.update(overrides)
    return Setup(**base)


def test_starting_balance_is_ten_thousand_paper_usdt():
    assert STARTING_BALANCE == 10_000.0


def test_valid_setup_sizes_to_one_percent_risk():
    verdict = evaluate(setup())
    assert verdict.approved
    assert verdict.risk_amount == pytest.approx(100.0)
    assert verdict.stop_distance == pytest.approx(750.0)
    assert verdict.units == pytest.approx(100.0 / 750.0)
    assert verdict.r_multiple == pytest.approx(2.0)


def test_reward_below_two_r_is_rejected():
    verdict = evaluate(setup(entry=3050.0, stop=2980.0, target=3155.0))
    assert not verdict.approved
    assert any("below" in reason for reason in verdict.reasons)


def test_long_stop_above_entry_is_rejected():
    verdict = evaluate(setup(stop=62_500.0))
    assert not verdict.approved
    assert any("long stop" in reason for reason in verdict.reasons)


def test_short_stop_below_entry_is_rejected():
    verdict = evaluate(setup(side="short", stop=61_000.0))
    assert not verdict.approved
    assert any("short stop" in reason for reason in verdict.reasons)


def test_risk_above_one_percent_is_rejected():
    verdict = evaluate(setup(), risk_pct=1.5)
    assert not verdict.approved
    assert any("risk_pct" in reason for reason in verdict.reasons)


def test_zero_risk_is_rejected():
    verdict = evaluate(setup(), risk_pct=0.0)
    assert not verdict.approved


def test_daily_cap_is_enforced():
    verdict = evaluate(setup(), trades_today=MAX_TRADES_PER_DAY)
    assert not verdict.approved
    assert any("daily trade cap" in reason for reason in verdict.reasons)


def test_implied_leverage_above_one_is_rejected():
    verdict = evaluate(setup(entry=100.0, stop=99.5, target=101.0))
    assert not verdict.approved
    assert any("exposure" in reason for reason in verdict.reasons)


def test_high_impact_news_blocks_trade():
    verdict = evaluate(setup(news="HIGH_IMPACT"))
    assert not verdict.approved
    assert any("news" in reason for reason in verdict.reasons)


def test_failed_contract_check_blocks_trade():
    verdict = evaluate(setup(contract_check="FAIL"))
    assert not verdict.approved
    assert any("contract" in reason for reason in verdict.reasons)


def test_unverified_contract_verdict_blocks_trade():
    verdict = evaluate(setup(contract_check="UNVERIFIED"))
    assert not verdict.approved


def test_non_finite_price_is_rejected():
    verdict = evaluate(setup(entry=float("nan")))
    assert not verdict.approved
    assert any("finite" in reason for reason in verdict.reasons)


def test_live_credentials_are_detected():
    env = {"BINANCE_API_KEY": "x", "COINBASE_API_SECRET": "y", "HOME": "/root"}
    assert live_credentials_present(env) == ["BINANCE_API_KEY", "COINBASE_API_SECRET"]


def test_non_exchange_keys_do_not_trip_the_guard():
    env = {"GROQ_API_KEY": "x", "OPENCODE_API_KEY": "public", "HOME": "/root"}
    assert live_credentials_present(env) == []


def test_module_has_no_network_imports():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(FORBIDDEN_IMPORTS), imported & FORBIDDEN_IMPORTS


def test_open_trade_keeps_balance_and_carries_no_pnl():
    row = to_row(evaluate(setup()), balance_before=10_000.0)
    assert row["status"] == "OPEN"
    assert row["pnl_usd"] == 0.0
    assert row["balance_after"] == 10_000.0
    assert row["data_source"] == "SIMULATED_NO_FEED"


def test_closed_trade_books_risk_times_r():
    row = to_row(evaluate(setup()), balance_before=10_000.0, exit_price=63_500.0, realised_r=2.0)
    assert row["status"] == "CLOSED"
    assert row["pnl_usd"] == pytest.approx(200.0)
    assert row["balance_after"] == pytest.approx(10_200.0)


def test_rejected_row_is_marked_rejected_with_reasons(tmp_path):
    row = to_row(evaluate(setup(target=62_500.0)))
    assert row["status"] == "REJECTED"
    assert row["reject_reasons"]


def test_csv_round_trip(tmp_path):
    rows = [to_row(evaluate(setup()), balance_before=10_000.0)]
    path = write_csv(rows, tmp_path / "ledger.csv")
    back = read_csv(path)
    assert len(back) == 1
    assert back[0]["pair"] == "BTC/USDT"
    assert back[0]["risk_amount_usd"] == "100.0"


def test_empty_ledger_is_refused(tmp_path):
    with pytest.raises(ValueError):
        write_csv([], tmp_path / "empty.csv")


def test_summary_computes_win_rate_average_r_and_drawdown():
    rows = [
        {"status": "CLOSED", "r_multiple_realised": "2", "pnl_usd": "200", "mistake_tag": ""},
        {
            "status": "CLOSED",
            "r_multiple_realised": "-1",
            "pnl_usd": "-100",
            "mistake_tag": "chased",
        },
        {"status": "CLOSED", "r_multiple_realised": "2", "pnl_usd": "200", "mistake_tag": "chased"},
        {"status": "OPEN", "r_multiple_realised": "", "pnl_usd": "0", "mistake_tag": ""},
    ]
    summary = summarise(rows)
    assert summary["closed_trades"] == 3
    assert summary["win_rate"] == pytest.approx(2 / 3, abs=1e-4)
    assert summary["avg_r"] == pytest.approx(1.0)
    assert summary["max_drawdown_pct"] == pytest.approx(0.9804, abs=1e-3)
    assert summary["top_mistakes"][0] == ("chased", 2)
