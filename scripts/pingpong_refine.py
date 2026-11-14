#!/usr/bin/env python3
"""CLI for optional, classified derived-data refinement.

Offline heuristic refinement is the default. External LunaRoute use requires
--live, --allow-external-data, a public data classification, an API key, and
BARROT_ALLOW_EXTERNAL_REFINEMENT=1. Canonical evidence is rejected.
"""
from __future__ import annotations

import argparse
import json
import os
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
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true",
                      help="deterministic heuristic refiners only (default)")
    mode.add_argument("--live", action="store_true",
                      help="request external LunaRoute refinement; disabled by default")
    ap.add_argument("--allow-external-data", action="store_true",
                    help="second explicit opt-in for public derived-data transfer")
    ap.add_argument("--classification", required=True, choices=[
        "derived_summary", "public_derived_summary", "public_documentation", "public_research_note",
    ])
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

    if args.live:
        if not args.allow_external_data or os.environ.get("BARROT_ALLOW_EXTERNAL_REFINEMENT") != "1":
            print("[refine] blocked: --allow-external-data and BARROT_ALLOW_EXTERNAL_REFINEMENT=1 are required", file=sys.stderr)
            return 2
        if args.classification not in {"public_derived_summary", "public_documentation", "public_research_note"}:
            print("[refine] blocked: classification is not eligible for external transfer", file=sys.stderr)
            return 2
        refiners = make_model_refiners(allow_external=True, data_classification=args.classification)
        if not refiners:
            print("[refine] blocked: no authorized LunaRoute model/key available", file=sys.stderr)
            return 2
    else:
        if args.allow_external_data:
            print("[refine] blocked: --allow-external-data requires --live", file=sys.stderr)
            return 2
        refiners = [HeuristicRefiner(), HeuristicRefiner("heuristic-2")]

    report = refine_data(
        data, refiners=refiners,
        ledger=None if args.no_ledger else "ping-pongings/knowledge-base/refinement_log.jsonl",
        max_rounds=args.max_rounds, data_classification=args.classification,
        allow_external=args.live,
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
