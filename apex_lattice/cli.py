"""
CLI for the Apex Lattice sandbox analysis pipeline.

Usage
-----
    python -m apex_lattice               # run a single analysis cycle
    python -m apex_lattice --cycle       # explicit single cycle
    python -m apex_lattice --status      # show audit log tail
    python -m apex_lattice --schedule 3600  # recurring cycle every hour
    python -m apex_lattice --findings    # list persisted findings
    python -m apex_lattice --recs        # list persisted recommendations
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m apex_lattice",
        description="Apex Lattice — sandbox analysis pipeline for Barrot Agent",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--cycle",
        "-c",
        action="store_true",
        help="Run a single analysis cycle (default action)",
    )
    group.add_argument(
        "--schedule",
        "-s",
        type=float,
        metavar="SECONDS",
        help="Run recurring cycles at the given interval (seconds)",
    )
    group.add_argument(
        "--status",
        action="store_true",
        help="Show the tail of the audit log",
    )
    group.add_argument(
        "--findings",
        action="store_true",
        help="List all persisted findings",
    )
    group.add_argument(
        "--recs",
        "--recommendations",
        action="store_true",
        dest="recs",
        help="List all persisted recommendations",
    )
    parser.add_argument(
        "--apex-dir",
        default=".apex_lattice",
        metavar="DIR",
        help="Path to the apex lattice workspace (default: .apex_lattice)",
    )

    args = parser.parse_args(argv)

    apex_dir = Path(args.apex_dir)

    if args.status:
        return _cmd_status(apex_dir)
    if args.findings:
        return _cmd_findings(apex_dir)
    if args.recs:
        return _cmd_recs(apex_dir)
    if args.schedule is not None:
        return _cmd_schedule(apex_dir, args.schedule)

    # Default: single cycle
    return _cmd_cycle(apex_dir)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def _cmd_cycle(apex_dir: Path) -> int:
    from .cycle import CycleManager

    print("Apex Lattice — running analysis cycle…")
    manager = CycleManager(apex_dir)
    result = manager.run_cycle()
    print(result.summary())
    return 0 if result.error is None else 1


def _cmd_schedule(apex_dir: Path, interval: float) -> int:
    from .cycle import CycleManager

    print(f"Apex Lattice — starting scheduler (interval: {interval}s).")
    print("Press Ctrl-C to stop.")
    manager = CycleManager(apex_dir)
    manager.start_scheduler(interval)
    try:
        while manager.is_scheduler_running():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping scheduler…")
        manager.stop_scheduler()
    return 0


def _cmd_status(apex_dir: Path) -> int:
    from .audit import AuditTrail
    import json as _json

    trail = AuditTrail(apex_dir / "audit_logs")
    events = trail.tail(20)
    if not events:
        print("No audit events found.")
        return 0
    print(f"Last {len(events)} audit event(s):")
    print("-" * 60)
    for ev in events:
        ts = ev.get("ts", 0)
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        print(f"[{ts_str}] {ev.get('event', '?')}  {_json.dumps(ev.get('data', {}))}")
    return 0


def _cmd_findings(apex_dir: Path) -> int:
    from .findings import FindingGenerator

    gen = FindingGenerator(apex_dir / "findings")
    findings = gen.load_all()
    if not findings:
        print("No findings found. Run `python -m apex_lattice --cycle` first.")
        return 0
    print(f"Findings ({len(findings)} total):")
    print("-" * 60)
    for f in findings:
        print(f"[{f.severity.upper():>8}] [{f.category}] {f.title}")
    return 0


def _cmd_recs(apex_dir: Path) -> int:
    from .recommendations import RecommendationEngine

    engine = RecommendationEngine(apex_dir / "recommendations")
    recs = engine.load_all()
    if not recs:
        print("No recommendations found. Run `python -m apex_lattice --cycle` first.")
        return 0
    print(f"Recommendations ({len(recs)} total):")
    print("-" * 60)
    for r in recs:
        print(f"[{r.priority.upper():>8}] {r.title}")
        for item in r.action_items[:2]:
            print(f"             • {item}")
    return 0
