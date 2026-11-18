#!/usr/bin/env python3
"""Run one cycle of the rotating feedback loop. Paper only.

    python3 scripts/xrp_cycle.py --snapshot market/live-2026-11-18T193754Z.json

Order of operations, which is the whole point:
    mark the positions opened at earlier snapshots
    review those decisions, refusals included
    open this cycle's candidates
    write the playbook rule, the confidence score, the pattern

Nothing is graded against the snapshot it was decided on.
"""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from barrot_agent.trading.paper_sandbox import live_credentials_present  # noqa: E402
from barrot_agent.trading.xrp_batch import MarketSnapshot  # noqa: E402
from barrot_agent.trading.xrp_cycle import (  # noqa: E402
    WEIGHTS,
    confidence_score,
    focus_for,
    import_batch1,
    mark_row,
    next_cycle,
    open_positions,
    patterns,
    read_ledger,
    review,
    write_ledger,
)
from barrot_agent.trading.xrp_rotation import StrategyConfig, max_drawdown_pct  # noqa: E402

LEDGER = ROOT / "PAPER_XRP_TRADES.csv"
BATCH1 = ROOT / "XRP_BATCH1.csv"
PLAYBOOK = ROOT / "XRP_PLAYBOOK.md"
CONFIDENCE_LOG = ROOT / "CONFIDENCE_LOG.md"
PATTERN_MEMORY = ROOT / "PATTERN_MEMORY.md"
STARTING_XRP = 102.27


def latest_snapshot() -> Path | None:
    files = sorted(glob.glob(str(ROOT / "market" / "live-*.json")))
    return Path(files[-1]) if files else None


def append_block(path: Path, header: str, block: str) -> None:
    if not path.exists():
        path.write_text(header, encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(block if block.endswith("\n") else block + "\n")


def realised_series(rows: list[dict]) -> list[float]:
    equity = [STARTING_XRP]
    for row in rows:
        if row.get("exit_status") == "CLOSED" and row.get("realised_xrp"):
            equity.append(equity[-1] + float(row["realised_xrp"]))
    return equity


def recent_expectancy(rows: list[dict], window: int = 30) -> float:
    closed = [row for row in rows if row.get("exit_status") == "CLOSED" and row.get("r_multiple")]
    tail = closed[-window:]
    return round(sum(float(r["r_multiple"]) for r in tail) / len(tail), 6) if tail else 0.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One cycle of the XRP feedback loop.")
    parser.add_argument("--snapshot", help="path to a snapshot json; default newest live-*")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    found = live_credentials_present()
    if found:
        print(f"ABORT: live credentials present: {found}")
        return 2

    path = Path(args.snapshot) if args.snapshot else latest_snapshot()
    if path is None:
        print("no snapshot available. Run: python3 scripts/ingest_live.py")
        return 2
    snapshot = MarketSnapshot.from_json(path)

    rows = read_ledger(LEDGER)
    if not rows:
        entry_price = 0.9778
        seed = ROOT / "market" / "2026-11-18-sean-feed.json"
        if seed.exists():
            entry_price = MarketSnapshot.from_json(seed).prices_usd["XRP"]
        rows = import_batch1(BATCH1, rows, xrp_usd_entry=entry_price)

    cycle = next_cycle(rows)
    prior = [r for r in rows if int(r["cycle"]) < cycle]
    current = [r for r in rows if int(r["cycle"]) == cycle]

    print(f"snapshot  {snapshot.snapshot_id}  provenance={snapshot.provenance}")
    print(f"cycle     {cycle}  focus {focus_for(cycle)}  prior rows {len(prior)}")

    marked = [mark_row(row, snapshot) for row in prior]
    rows = marked + current

    review_rows = []
    if marked:
        last_cycle = max(int(r["cycle"]) for r in marked)
        review_rows = [r for r in marked if int(r["cycle"]) == last_cycle]
        report = review(review_rows, snapshot, last_cycle)
        print()
        print(f"REVIEW of cycle {last_cycle}, graded against {snapshot.snapshot_id}")
        print(f"  accepted {report['accepted']}  rejected {report['rejected']}  "
              f"closed {report['closed']}  still open {report['open']}")
        win_rate = ("UNDEFINED" if report["win_rate_pct"] is None
                    else report["win_rate_pct"])
        print(f"  win rate {win_rate}"
              f"  realised {report['realised_xrp']:+.4f} XRP  "
              f"unrealised {report['unrealised_xrp']:+.4f} XRP")
        for asset, pct in sorted(report["refused_return_pct"].items()):
            verdict = "gate cost" if pct > 0 else "gate saved"
            print(f"  refused {asset:<5} would have returned {pct:+.3f}%  ({verdict})")
        print(f"  lesson: {report['top_lesson']}")

        append_block(
            PATTERN_MEMORY,
            "# PATTERN MEMORY\n\nOne measured entry per cycle. Only patterns the data\n"
            "produced, never patterns that sounded good.\n\n",
            f"- cycle {last_cycle} ({snapshot.snapshot_id}): "
            f"{patterns(report, snapshot)}\n",
        )
        rule, evidence = report["rule"]
        lesson_block = (
            f"\n## Cycle {last_cycle} — graded at {snapshot.snapshot_id}\n"
            f"- Focus {report['focus']}; accepted {report['accepted']}, "
            f"rejected {report['rejected']}, closed {report['closed']}.\n"
            f"- Refused-rotation cost: "
            + ", ".join(f"{a} {p:+.2f}%" for a, p in sorted(report['refused_return_pct'].items()))
            + ".\n"
            f"- Evidence: {evidence}.\n"
            f"- **Rule added:** {rule}\n"
            f"- Rule removed or fixed: none — this is the first graded cycle.\n"
        )
        append_block(
            PLAYBOOK,
            "# XRP PLAYBOOK\n\nRules added only after a cycle measured them. A rule that\n"
            "fails gets removed in a later cycle, not quietly ignored.\n",
            lesson_block,
        )

    stack = STARTING_XRP + sum(
        float(r["realised_xrp"]) for r in rows
        if r.get("exit_status") == "CLOSED" and r.get("realised_xrp")
    )
    open_rows = [r for r in rows if r.get("exit_status") == "OPEN"]
    committed = sum(float(r["xrp_in"]) for r in open_rows if r.get("xrp_in"))
    available = max(0.0, stack - committed)

    config = StrategyConfig(disabled_assets=tuple(snapshot.disabled_assets))
    new_rows, available_after = open_positions(snapshot, cycle, stack, available, config)
    rows = rows + new_rows

    print()
    print(f"TRADE cycle {cycle}  focus {focus_for(cycle)}")
    for row in new_rows:
        size = f"{float(row['xrp_in']):.4f} XRP" if row["xrp_in"] else "-"
        detail = row["reasons"].split(";")[0] if row["reasons"] else "entry recorded"
        print(f"  {row['trade_id']:<18} {row['asset']:<5} {row['decision']:<9} "
              f"{size:>14}  {detail}")
    print(f"  committed {committed:.4f}  available {available:.4f} -> {available_after:.4f}")

    closed = [r for r in rows if r.get("exit_status") == "CLOSED"]
    equity = realised_series(rows)
    score = confidence_score(
        closed_count=len(closed),
        provenance=snapshot.provenance,
        stack_delta=stack - STARTING_XRP,
        drawdown_pct=max_drawdown_pct(equity),
        recent_expectancy=recent_expectancy(rows),
        violations=0,
    )

    usd_value = stack * snapshot.prices_usd["XRP"]
    print()
    print("EVOLVE")
    print(f"  confidence {score['score']}/100")
    for name, points in score["parts"].items():
        print(f"    {name:<22} {points:>5.2f} / {WEIGHTS[name]}")
    print(f"  stack {stack:.4f} XRP  = ${usd_value:.2f} at ${snapshot.prices_usd['XRP']}")

    if not args.dry_run:
        write_ledger(rows, LEDGER)
        append_block(
            CONFIDENCE_LOG,
            "# CONFIDENCE LOG\n\nScore 0-100, six weighted facts. It moves only when the\n"
            "facts move.\n\n| time | cycle | score | closed | provenance | why |\n"
            "|---|---|---|---|---|---|\n",
            f"| {snapshot.captured_at_utc} | {cycle} | {score['score']} | "
            f"{len(closed)} | {snapshot.provenance} | "
            f"{'no closed rotations yet' if not closed else 'scored from closed rotations'}"
            f" |\n",
        )
        print(f"\nwrote {LEDGER.name}, {PLAYBOOK.name}, "
              f"{CONFIDENCE_LOG.name}, {PATTERN_MEMORY.name}")

    top_lesson = (
        review_rows and review(review_rows, snapshot, int(review_rows[0]["cycle"]))["top_lesson"]
    ) or "no graded cycle yet; cycle 1 is open"
    print()
    print(
        f"FEEDBACK LOOP CYCLE {cycle} COMPLETE. REQUESTING SNAPSHOT {cycle + 1}. "
        f"Ready for next feed. Current XRP: {stack:.4f} XRP | USD: ${usd_value:.2f} | "
        f"Confidence: {score['score']}/100 | Top Lesson: {top_lesson}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
