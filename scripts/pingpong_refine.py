#!/usr/bin/env python3
"""pingpong_refine.py — CLI for the ping-pong refinement baseline.

Refines a JSON document (or stdin JSON) by ping-ponging between models until
the data can be refined no further (measured fixed point). Every round is
ledgered to ping-pongings/knowledge-base/refinement_log.jsonl.

Usage:
    python3 scripts/pingpong_refine.py data.json              # in place
    python3 scripts/pingpong_refine.py in.json -o out.json    # to file
    echo '{"a": "x  x"}' | python3 scripts/pingpong_refine.py -
    python3 scripts/pingpong_refine.py data.json --offline    # deterministic
    python3 scripts/pingpong_refine.py data.json --max-rounds 6

Exit codes: 0 = converged, 1 = capped (max rounds / failures), 2 = input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from barrot_agent.refinement import (          # noqa: E402
    HeuristicRefiner,
    make_model_refiners,
    refine_data,
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", help="JSON file path, or '-' for stdin")
    ap.add_argument("-o", "--out", help="output path (default: in place)")
    ap.add_argument("--offline", action="store_true",
                    help="deterministic heuristic refiners only (no API)")
    ap.add_argument("--max-rounds", type=int, default=12)
    ap.add_argument("--no-ledger", action="store_true")
    args = ap.parse_args(argv)

    try:
        if args.input == "-":
            data = json.load(sys.stdin)
        else:
            data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[refine] input error: {exc}", file=sys.stderr)
        return 2

    if args.offline:
        refiners = [HeuristicRefiner(), HeuristicRefiner("heuristic-2")]
    else:
        refiners = make_model_refiners() or [HeuristicRefiner()]
        print(f"[refine] pool: {[r.name for r in refiners]}")

    report = refine_data(
        data, refiners=refiners,
        ledger=None if args.no_ledger
        else "ping-pongings/knowledge-base/refinement_log.jsonl",
        max_rounds=args.max_rounds,
    )

    dest = args.out or args.input
    if dest != "-":
        Path(dest).write_text(
            json.dumps(report.data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    else:
        json.dump(report.data, sys.stdout, indent=2, ensure_ascii=False)
        print()

    print(f"[refine] converged={report.converged} "
          f"stop={report.stop_reason} rounds={report.rounds} "
          f"score {report.score_start:.4f} -> {report.score_end:.4f} "
          f"(+{report.score_end - report.score_start:.4f})")
    print(f"[refine] models: {', '.join(report.models_used)}")
    return 0 if report.converged else 1


if __name__ == "__main__":
    sys.exit(main())
