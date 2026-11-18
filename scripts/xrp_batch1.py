#!/usr/bin/env python3
"""Batch 1 from Sean's 2026-11-18 snapshot. Paper only, no orders.

    python scripts/xrp_batch1.py            write XRP_BATCH1.csv and report
    python scripts/xrp_batch1.py --check    verify the ledger is internally honest

The snapshot supplies entry prices. It supplies nothing about the future, so
every accepted entry is written with `exit_status=PENDING` and every realised
field is empty. `--check` fails if that ever stops being true.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from barrot_agent.trading.paper_sandbox import live_credentials_present  # noqa: E402
from barrot_agent.trading.xrp_batch import (  # noqa: E402
    Candidate,
    MarketSnapshot,
    batch_rows,
    read_batch_csv,
    summarize,
    write_batch_csv,
)
from barrot_agent.trading.xrp_rotation import (  # noqa: E402
    StrategyConfig,
    confidence,
    load_config,
)

SNAPSHOT = ROOT / "market/2026-11-18-sean-feed.json"
LEDGER = ROOT / "XRP_BATCH1.csv"
LESSONS = ROOT / "XRP_LESSONS.jsonl"

CANDIDATES = (
    Candidate(
        candidate_id="B1-01",
        asset="USDT",
        thesis=(
            "XRP is the only green asset on 24h (+1.70%) in a market that is down 15% on "
            "7d. Hypothesis: the bounce fades and XRP gives back part of it. Defensive "
            "leg, expected 3.0% depreciation in XRP terms."
        ),
        expected_move_pct=3.0,
        stop_pct=5.0,
    ),
    Candidate(
        candidate_id="B1-02",
        asset="USDT",
        thesis=(
            "Same thesis with a wider 12% stop, accepting a smaller position. Proves the "
            "sizing rule: backstop width changes size, never the risk budget."
        ),
        expected_move_pct=3.0,
        stop_pct=12.0,
    ),
    Candidate(
        candidate_id="B1-03",
        asset="USDT",
        thesis=(
            "Same defensive leg with a 0.5% expected move. Tests whether the cost gate "
            "rejects an edge that is smaller than the round trip."
        ),
        expected_move_pct=0.5,
        stop_pct=5.0,
    ),
    Candidate(
        candidate_id="B1-04",
        asset="USDT",
        thesis=(
            "Defensive leg with news state not supplied. Tests fail-closed behaviour when "
            "the scan is incomplete."
        ),
        expected_move_pct=3.0,
        stop_pct=5.0,
        news="UNKNOWN",
    ),
    Candidate(
        candidate_id="B1-05",
        asset="BTC",
        thesis="Sean's read: XRP strength against BTC weakness makes XRP->BTC a bad rotation.",
        expected_move_pct=3.0,
        stop_pct=5.0,
    ),
    Candidate(
        candidate_id="B1-06",
        asset="ETH",
        thesis="ETH is down 15% on 7d and 27% on 30d, roughly tracking BTC. Same rotation logic.",
        expected_move_pct=3.0,
        stop_pct=5.0,
    ),
    Candidate(
        candidate_id="B1-07",
        asset="SOL",
        thesis=(
            "SOL is the weakest of the majors (-30% on 30d). "
            "Tests whether weakness alone is a signal."
        ),
        expected_move_pct=3.0,
        stop_pct=5.0,
    ),
    Candidate(
        candidate_id="B1-08",
        asset="XLM",
        thesis=(
            "XLM fell 6% on 7d against XRP's 7%, so it is the only major that gained on XRP. "
            "Tests whether a favourable ratio is enough without volume."
        ),
        expected_move_pct=3.0,
        stop_pct=5.0,
    ),
    Candidate(
        candidate_id="B1-09",
        asset="BTC",
        thesis=(
            "Contrarian: BTC fell 15% on 7d, so a bounce is possible. Tests whether the "
            "system allows a counter-trend entry it has no rule for."
        ),
        expected_move_pct=4.0,
        stop_pct=5.0,
    ),
    Candidate(
        candidate_id="B1-10",
        asset="XRP",
        thesis=(
            "Hold the base asset. In a bearish tape where XRP is outperforming, holding is "
            "a position, not a non-decision. Recorded so it can be scored against the rest."
        ),
        expected_move_pct=0.0,
        stop_pct=5.0,
    ),
)

REQUIRED_EMPTY = (
    "exit_ratio", "xrp_out", "xrp_delta",
    "usd_in", "usd_out", "usd_delta", "r_multiple",
)


def abort_if_live_keys() -> None:
    found = live_credentials_present()
    if found:
        print(f"ABORT: live exchange credentials present: {found}")
        print("Unset them and re-run. Paper only.")
        raise SystemExit(2)


def run() -> int:
    abort_if_live_keys()
    snapshot = MarketSnapshot.from_json(SNAPSHOT)
    stack = float(snapshot.balances_start["xrp"])
    base_config = StrategyConfig(disabled_assets=snapshot.disabled_assets)
    config, applied = load_config(LESSONS, snapshot.provenance, base=base_config)

    print(f"snapshot   {snapshot.snapshot_id}  provenance={snapshot.provenance}")
    print(f"captured   {snapshot.captured_at_utc}")
    print(f"stack      {stack:.2f} XRP  (${snapshot.balances_start['usd_value']:.2f})")
    print(f"regime     {snapshot.market_trend}  XRP dominance {snapshot.xrp_dominance_pct()}%")
    print(f"lessons    {len(applied)} applied for provenance {snapshot.provenance}")
    print()
    print("signal table (all derived from the supplied numbers)")
    header = (
        f"  {'asset':<6}{'ratio':>14}{'ratio 7d':>11}"
        f"{'cf 7d':>9}{'trend':>8}{'ratio':>9}{'vol':>9}"
    )
    print(header)
    for asset in ("BTC", "ETH", "SOL", "USDT", "XLM"):
        ratio_7d = snapshot.ratio_change_pct(asset, "7d")
        cf = snapshot.counterfactual_pct(asset, "7d")
        print(
            f"  {asset:<6}{snapshot.ratio(asset):>14.8f}"
            f"{'n/a' if ratio_7d is None else f'{ratio_7d:+.2f}%':>11}"
            f"{'n/a' if cf is None else f'{cf:+.2f}%':>9}"
            f"{snapshot.trend(asset):>8}{snapshot.ratio_signal(asset):>9}"
            f"{snapshot.volume_signal(asset):>9}"
        )
    print()

    rows, log = batch_rows(snapshot, list(CANDIDATES), stack, config)
    for line in log:
        print("  " + line)
    print()

    summary = summarize(rows, stack)
    write_batch_csv(rows, LEDGER)

    print(f"wrote {LEDGER.name}: {summary['candidates']} candidates")
    print(
        f"accepted {summary['accepted']}  rejected {summary['rejected']}  "
        f"no_trade {summary['no_trade']}"
    )
    print(f"XRP allocated {summary['xrp_allocated']:.4f}  idle {summary['xrp_idle']:.4f}")
    print(
        f"XRP at risk   {summary['xrp_at_risk']:.4f}  "
        f"({summary['risk_pct_of_stack']:.3f}% of stack)"
    )
    print(f"exits pending {summary['exits_pending']}")
    print(f"realised XRP delta {summary['realised_xrp_delta']:.4f}  realised R  UNDEFINED")
    print("win rate / avg R / drawdown: UNDEFINED until exits exist")
    print()
    print("reject reasons")
    for reason, count in sorted(summary["reject_reasons"].items(), key=lambda kv: -kv[1]):
        print(f"  {count}x {reason}")
    print()

    report = confidence([], provenance=snapshot.provenance)
    print("confidence gate (no closed rotations, so it cannot pass)")
    for name, ok, detail in report["checks"]:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print(f"READY FOR REAL XRP: {'YES' if report['ready'] else 'NO'}")
    return 0


def check() -> int:
    rows = read_batch_csv(LEDGER)
    problems = []
    for row in rows:
        if row["exit_status"] != "PENDING":
            problems.append(f"{row['candidate_id']}: exit_status {row['exit_status']!r}")
        for field in REQUIRED_EMPTY:
            if row[field] != "":
                problems.append(
                    f"{row['candidate_id']}: {field} should be empty, got {row[field]!r}"
                )
        if row["decision"] == "ACCEPTED" and not row["xrp_allocated"]:
            problems.append(f"{row['candidate_id']}: accepted with no allocation")
        if row["decision"] == "REJECTED" and not row["reasons"]:
            problems.append(f"{row['candidate_id']}: rejected with no reason")
    if len(rows) != len(CANDIDATES):
        problems.append(f"expected {len(CANDIDATES)} rows, found {len(rows)}")

    snapshot = MarketSnapshot.from_json(SNAPSHOT)
    stack = float(snapshot.balances_start["xrp"])
    total = sum(float(row["xrp_allocated"]) for row in rows if row["xrp_allocated"])
    if total > stack + 1e-9:
        problems.append(f"allocated {total} exceeds stack {stack}")

    payload = {
        "check": "batch1_ledger",
        "rows": len(rows),
        "allocated_xrp": round(total, 8),
        "stack_xrp": stack,
        "problems": problems,
        "ok": not problems,
    }
    print(json.dumps(payload, indent=2))
    return 0 if not problems else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Batch 1 entry evaluation. Paper only.")
    parser.add_argument("--check", action="store_true", help="verify the written ledger")
    args = parser.parse_args(argv)
    return check() if args.check else run()


if __name__ == "__main__":
    raise SystemExit(main())
