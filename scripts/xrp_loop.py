#!/usr/bin/env python3
"""XRP-centric paper rotation loop. No network, no keys, no orders.

    python scripts/xrp_loop.py demo         20 simulated rotations, 2 lessons
    python scripts/xrp_loop.py lesson       review the ledger, propose one change
    python scripts/xrp_loop.py confidence   readiness checklist for real capital
    python scripts/xrp_loop.py scan FILE    evaluate plans from a dated snapshot

`demo` is a rehearsal on simulated scenarios. It cannot make you confident: the
confidence gate refuses any record whose provenance is SIMULATED_SCENARIO.
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
from barrot_agent.trading.xrp_rotation import (  # noqa: E402
    STARTING_XRP,
    RotationPlan,
    StrategyConfig,
    apply_lesson,
    auto_lesson,
    confidence,
    evaluate,
    from_row,
    read_csv,
    settle,
    to_row,
    write_csv,
)

LEDGER = ROOT / "XRP_ROTATIONS.csv"
LESSONS = ROOT / "XRP_LESSONS.jsonl"
TS = "2026-11-18T00:00:00Z"

# Simulated fixtures. ratio = units of the asset per 1 XRP. These are not
# current prices; they exist so the arithmetic can be re-checked by hand.
RATIOS = {"BTC": 0.00002, "ETH": 0.0004, "SOL": 0.0025, "USDT": 0.52, "XLM": 0.9}
XRP_USD = 0.52

# (asset, expected move %, realised favourable move %, notes)
BATCH_ONE = (
    ("BTC", 3.0, 2.5, ""),
    ("ETH", 3.0, 1.8, ""),
    ("XLM", 3.0, -3.0, "broke below the range"),
    ("SOL", 3.0, 4.0, ""),
    ("XLM", 3.0, -2.0, "broke below the range"),
    ("BTC", 3.0, 1.2, ""),
    ("XLM", 3.0, -3.5, "chased the entry"),
    ("ETH", 3.0, 2.2, ""),
    ("XLM", 3.0, -1.0, "chased the entry"),
    ("USDT", 3.0, 2.0, ""),
)
BATCH_TWO = (
    ("BTC", 3.0, 3.0, ""),
    ("ETH", 3.0, -1.5, "entered late"),
    ("SOL", 3.0, 2.5, ""),
    ("BTC", 3.0, 1.0, ""),
    ("ETH", 3.0, 2.0, ""),
    ("SOL", 3.0, -2.0, "entered late"),
    ("USDT", 3.0, 1.5, ""),
    ("BTC", 3.0, 2.0, ""),
    ("ETH", 3.0, 1.2, ""),
    ("SOL", 3.0, 3.0, ""),
)


def abort_if_live_keys() -> None:
    found = live_credentials_present()
    if found:
        print(f"ABORT: live exchange credentials present: {found}")
        print("Unset them and re-run. Paper only.")
        raise SystemExit(2)


def build_plan(index: int, asset: str, expected: float, source: str) -> RotationPlan:
    defensive = asset == "USDT"
    return RotationPlan(
        rotation_id=f"X-{index:03d}",
        timestamp_utc=TS,
        asset=asset,
        xrp_per_asset=RATIOS[asset],
        expected_move_pct=expected,
        stop_pct=5.0,
        trend="DOWN" if defensive else "UP",
        ratio_signal="AGAINST" if defensive else "FAVOURS",
        volume_signal="THIN" if defensive else "CONFIRMS",
        news="HIGH_IMPACT" if defensive else "CLEAR",
        xrp_dominance=55.0,
        bars_held=0,
        provenance=source,
    )


def run_batch(
    batch,
    start_index: int,
    stack: float,
    config: StrategyConfig,
    rows: list[dict],
    lessons: list[dict],
) -> tuple[float, StrategyConfig]:
    outcomes = []
    for offset, (asset, expected, realised, tag) in enumerate(batch):
        plan = build_plan(start_index + offset, asset, expected, "SIMULATED_SCENARIO")
        verdict = evaluate(plan, stack_xrp=stack, config=config)
        if not verdict.approved:
            print(f"  {plan.rotation_id} {asset:<4} REJECT: {verdict.reasons[0]}")
            continue
        exit_ratio = plan.xrp_per_asset * (1.0 - realised / 100.0)
        xrp_usd_exit = XRP_USD * (1.0 - realised / 100.0) if asset == "USDT" else XRP_USD
        outcome = settle(
            verdict,
            exit_ratio,
            xrp_usd_entry=XRP_USD,
            xrp_usd_exit=xrp_usd_exit,
            exit_reason="TARGET" if realised >= 0 else "STOP",
            mistake_tag=tag,
        )
        outcomes.append(outcome)
        stack += outcome.xrp_delta
        rows.append(to_row(outcome))
        print(
            f"  {plan.rotation_id} {asset:<4} {'WIN ' if outcome.xrp_delta > 0 else 'LOSS'}"
            f" xrp_delta {outcome.xrp_delta:+9.4f}  stack {stack:10.4f}"
        )

    lesson = auto_lesson(outcomes)
    print(f"  lesson over {lesson['window']} trades")
    for asset, stats in sorted(lesson["per_asset"].items()):
        print(
            f"    {asset:<5} n={stats['trades']:<3} win={stats['win_rate']:.0%}"
            f" xrp={stats['xrp_delta']:+.4f}"
        )
    if lesson["top_mistakes"]:
        print(f"    mistakes {lesson['top_mistakes']}")
    print(f"    proposal {lesson['proposal']}")
    config, applied = apply_lesson(config, lesson)
    lesson["applied"] = applied
    lessons.append(lesson)
    if applied:
        print(f"    applied: disabled {lesson['proposal']['asset']} from now on")
    return stack, config


def cmd_demo(force: bool) -> int:
    abort_if_live_keys()
    if LEDGER.exists() and not force:
        print(f"refusing to overwrite {LEDGER.name}; pass --force")
        return 1

    rows: list[dict] = []
    lessons: list[dict] = []
    stack = STARTING_XRP
    config = StrategyConfig()
    print(f"starting XRP stack: {stack:.2f} (fake)")
    print("batch 1")
    stack, config = run_batch(BATCH_ONE, 1, stack, config, rows, lessons)
    print("batch 2")
    stack, config = run_batch(BATCH_TWO, 11, stack, config, rows, lessons)

    # A rejected attempt proves the lesson changed behaviour: XLM is now off.
    blocked = build_plan(99, "XLM", 3.0, "SIMULATED_SCENARIO")
    verdict = evaluate(blocked, stack_xrp=stack, config=config)
    print(f"  X-099 XLM  {'ACCEPT' if verdict.approved else 'REJECT'} {verdict.reasons}")

    write_csv(rows, LEDGER)
    LESSONS.write_text(
        "\n".join(json.dumps(item, sort_keys=True) for item in lessons) + "\n", encoding="utf-8"
    )
    print(f"wrote {LEDGER.name}: {len(rows)} rotations")
    print(f"wrote {LESSONS.name}: {len(lessons)} lessons")
    print(f"stack after: {stack:.4f} XRP (fake)")
    print("provenance: SIMULATED_SCENARIO — rehearsal only, not performance")
    return 0


def cmd_lesson() -> int:
    if not LEDGER.exists():
        print(f"{LEDGER.name} not found")
        return 1
    outcomes = [from_row(row) for row in read_csv(LEDGER)]
    lesson = auto_lesson(outcomes)
    print(json.dumps(lesson, indent=2, sort_keys=True))
    return 0


def cmd_confidence() -> int:
    if not LEDGER.exists():
        print(f"{LEDGER.name} not found")
        return 1
    outcomes = [from_row(row) for row in read_csv(LEDGER)]
    provenance = outcomes[0].plan.provenance if outcomes else "UNKNOWN"
    report = confidence(outcomes, provenance=provenance)
    print(f"provenance: {provenance}")
    for name, ok, detail in report["checks"]:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print(f"READY FOR REAL XRP: {'YES' if report['ready'] else 'NO'}")
    return 0 if report["ready"] else 1


def cmd_scan(path: str) -> int:
    abort_if_live_keys()
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    provenance = payload.get("provenance", "UNKNOWN")
    if provenance not in ("SEAN_SUPPLIED", "RECORDED_FEED"):
        print(f"refusing: provenance {provenance!r} is not SEAN_SUPPLIED or RECORDED_FEED")
        return 2
    stack = float(payload.get("stack_xrp", STARTING_XRP))
    config = StrategyConfig(disabled_assets=tuple(payload.get("disabled_assets", ())))
    for index, item in enumerate(payload.get("plans", []), start=1):
        plan = RotationPlan(
            rotation_id=item.get("rotation_id", f"S-{index:03d}"),
            timestamp_utc=payload.get("captured_at_utc", "UNKNOWN"),
            asset=item["asset"].upper(),
            xrp_per_asset=float(item["xrp_per_asset"]),
            expected_move_pct=float(item["expected_move_pct"]),
            stop_pct=float(item["stop_pct"]),
            trend=item.get("trend", "UNKNOWN"),
            ratio_signal=item.get("ratio_signal", "UNKNOWN"),
            volume_signal=item.get("volume_signal", "UNKNOWN"),
            news=payload.get("news", "UNKNOWN"),
            xrp_dominance=payload.get("xrp_dominance"),
            bars_held=int(item.get("bars_held", 0)),
            provenance=provenance,
        )
        verdict = evaluate(plan, stack_xrp=stack, config=config)
        status = "ACCEPT" if verdict.approved else "REJECT"
        print(f"{plan.rotation_id} {plan.asset:<5} {status} {verdict.reasons}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="XRP paper rotation loop. No real money.")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--force", action="store_true")
    sub.add_parser("lesson")
    sub.add_parser("confidence")
    scan = sub.add_parser("scan")
    scan.add_argument("file")
    args = parser.parse_args(argv)
    if args.command == "demo":
        return cmd_demo(args.force)
    if args.command == "lesson":
        return cmd_lesson()
    if args.command == "confidence":
        return cmd_confidence()
    return cmd_scan(args.file)


if __name__ == "__main__":
    raise SystemExit(main())
