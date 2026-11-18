#!/usr/bin/env python3
"""Paper-trading sandbox CLI. No network, no keys, no orders.

    python scripts/paper_trade.py demo      evaluate 3 simulated setups -> CSV
    python scripts/paper_trade.py report    summarise the closed rows

Every price below is simulated. There is no market feed in this runtime, so the
numbers are fixtures for the rule gate, not a market view. The file records that
in the data_source column on every row.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from barrot_agent.trading.paper_sandbox import (  # noqa: E402
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

LEDGER = ROOT / "PAPER_TRADES.csv"
TS = "2026-11-18T00:00:00Z"

# Simulated fixtures. Round numbers on purpose so the arithmetic is checkable by
# hand. Do not read these as current prices.
SETUPS = (
    Setup(
        trade_id="P-001",
        timestamp_utc=TS,
        pair="BTC/USDT",
        side="long",
        entry=62000.00,
        stop=61250.00,
        target=63500.00,
        thesis="1h uptrend, pullback held above prior swing low; simulated fixture",
        news="UNKNOWN",
        contract_check="N/A_NATIVE",
    ),
    Setup(
        trade_id="P-002",
        timestamp_utc=TS,
        pair="ETH/USDT",
        side="long",
        entry=3050.00,
        stop=2980.00,
        target=3155.00,
        thesis="Range low reclaim; target too close, kept as the negative control",
        news="UNKNOWN",
        contract_check="N/A_NATIVE",
    ),
    Setup(
        trade_id="P-003",
        timestamp_utc=TS,
        pair="SOL/USDT",
        side="long",
        entry=142.50,
        stop=138.90,
        target=149.70,
        thesis="15m higher low after 1h base; simulated fixture",
        news="UNKNOWN",
        contract_check="N/A_NATIVE",
    ),
)


def abort_if_live_keys() -> None:
    found = live_credentials_present()
    if found:
        print(f"ABORT: live exchange credentials present in environment: {found}")
        print("Unset them and re-run. The sandbox never runs beside a live key.")
        raise SystemExit(2)


def cmd_demo(force: bool) -> int:
    abort_if_live_keys()
    if LEDGER.exists() and not force:
        print(f"refusing to overwrite {LEDGER.name}; pass --force to rebuild")
        return 1

    rows = []
    balance = STARTING_BALANCE
    trades_today = 0
    print(f"starting paper balance: {balance:.2f} USDT (fake)")
    print(f"{'id':<6}{'pair':<10}{'verdict':<9}{'risk':<8}{'units':<14}{'notional':<11}{'R':<5}")
    for setup in SETUPS:
        verdict = evaluate(setup, balance=balance, risk_pct=1.0, trades_today=trades_today)
        row = to_row(verdict, balance_before=balance)
        rows.append(row)
        if verdict.approved:
            trades_today += 1
        print(
            f"{setup.trade_id:<6}{setup.pair:<10}"
            f"{('ACCEPT' if verdict.approved else 'REJECT'):<9}"
            f"{verdict.risk_amount:<8.2f}{verdict.units:<14.6f}"
            f"{verdict.notional:<11.2f}{verdict.r_multiple:<5.2f}"
        )
        for reason in verdict.reasons:
            print(f"       - {reason}")

    write_csv(rows, LEDGER)
    approved = sum(1 for row in rows if row["status"] in ("OPEN", "CLOSED"))
    print(f"wrote {LEDGER.name}: {len(rows)} evaluated, {approved} approved")
    print(f"daily cap: {trades_today}/{MAX_TRADES_PER_DAY} used")
    print("status: PAPER ONLY. No order was sent; no exchange was contacted.")
    return 0


def cmd_report() -> int:
    if not LEDGER.exists():
        print(f"{LEDGER.name} not found; run `demo` first")
        return 1
    rows = read_csv(LEDGER)
    summary = summarise(rows)
    print(f"closed trades      {summary['closed_trades']}")
    print(f"win rate           {summary['win_rate']:.2%}")
    print(f"avg R              {summary['avg_r']:.2f}")
    print(f"max drawdown       {summary['max_drawdown_pct']:.2f}%")
    print(f"ending balance     {summary['ending_balance']:.2f} USDT (fake)")
    if summary["top_mistakes"]:
        for tag, count in summary["top_mistakes"]:
            print(f"mistake            {tag} x{count}")
    else:
        print("mistake tags       none recorded")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Paper-trading sandbox. No real money.")
    parser.add_argument("command", choices=("demo", "report"))
    parser.add_argument("--force", action="store_true", help="rebuild PAPER_TRADES.csv")
    args = parser.parse_args(argv)
    return cmd_demo(args.force) if args.command == "demo" else cmd_report()


if __name__ == "__main__":
    raise SystemExit(main())
