#!/usr/bin/env python3
"""pingpong_refine.py — CLI for the ping-pong refinement baseline.

Refines a JSON document (or stdin JSON) by ping-ponging between models until
the data can be refined no further (measured fixed point). Every round is
ledgered to ping-pongings/knowledge-base/refinement_log.jsonl.

Documents above the segmentation threshold (24K chars) are routed through
the patch pipeline: sections are refined independently, changes land as
validated patches, an independent judge evaluates semantics, the result is
regression-tested against the original, and the run is resumable:

    python3 scripts/pingpong_refine.py big.json --objective "tighten and verify"
    python3 scripts/pingpong_refine.py big.json --resume ref-<id>

Usage:
    python3 scripts/pingpong_refine.py data.json              # in place
    python3 scripts/pingpong_refine.py in.json -o out.json    # to file
    echo '{"a": "x  x"}' | python3 scripts/pingpong_refine.py -
    python3 scripts/pingpong_refine.py data.json --offline    # deterministic
    python3 scripts/pingpong_refine.py data.json --max-rounds 6

Exit codes: 0 = converged/complete, 1 = capped/incomplete, 2 = input error.
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
    refine_document,
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", help="JSON file path, or '-' for stdin")
    ap.add_argument("-o", "--out", help="output path (default: in place)")
    ap.add_argument("--offline", action="store_true",
                    help="deterministic heuristic refiners only (no API)")
    ap.add_argument("--max-rounds", type=int, default=12)
    ap.add_argument("--no-ledger", action="store_true")
    ap.add_argument("--objective", default="",
                    help="refinement objective (patch pipeline)")
    ap.add_argument("--resume", metavar="RUN_ID",
                    help="resume an interrupted pipeline run")
    ap.add_argument("--force", action="store_true",
                    help="re-refine even if the learning history says done")
    args = ap.parse_args(argv)

    if args.resume:
        from barrot_agent.refinement import RefinementPipeline, load_run
        from barrot_agent.refinement.pipeline import DEFAULT_RUNS_DIR
        state = load_run(args.resume, DEFAULT_RUNS_DIR)
        refiners = ([HeuristicRefiner(), HeuristicRefiner("heuristic-2")]
                    if args.offline else make_model_refiners())
        pipe = RefinementPipeline(refiners, ledger=None if args.no_ledger
                                  else "ping-pongings/knowledge-base/"
                                       "refinement_log.jsonl")
        outcome = pipe.resume(args.resume)
        return _report(outcome, args, state.document)

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

    ledger = None if args.no_ledger \
        else "ping-pongings/knowledge-base/refinement_log.jsonl"
    outcome = refine_document(
        data, objective=args.objective, refiners=refiners,
        source_identity=str(args.input), force=args.force,
        ledger=ledger, max_rounds=args.max_rounds)
    return _report(outcome, args, data)


def _report(outcome: dict, args, source_doc) -> int:
    if outcome.get("mode") == "classic":
        report = outcome["report"]
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

    # patch pipeline outcome
    disposition = outcome.get("disposition")
    if disposition == "already_converged":
        print(f"[refine] already converged (learning history): "
              f"run={outcome.get('run_id')} — nothing to redo "
              f"(use --force to re-refine)")
        return 0
    dest = args.out or args.input
    final_doc = None
    if disposition in ("complete", "incomplete"):
        run_id = outcome["run_id"]
        from barrot_agent.refinement import load_run
        from barrot_agent.refinement.pipeline import DEFAULT_RUNS_DIR
        final_doc = load_run(run_id, DEFAULT_RUNS_DIR).document
    if final_doc is not None and dest != "-":
        Path(dest).write_text(
            json.dumps(final_doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    mech = outcome.get("mechanical", {})
    sem = outcome.get("semantic") or {}
    ver = outcome.get("verification") or {}
    print(f"[refine] disposition={disposition} run={outcome.get('run_id')}")
    print(f"[refine] mechanical {mech.get('before', 0):.4f} -> "
          f"{mech.get('after', 0):.4f} | semantic={sem.get('status')} "
          f"({sem.get('semantic', 0):.3f}, judge={sem.get('judge')}, "
          f"calibrated={sem.get('calibrated')}) | "
          f"regression={sem.get('regression', 1):.3f}")
    print(f"[refine] verification ok={ver.get('ok')} "
          f"missing={len(ver.get('missing_paths', []))} "
          f"smuggled={len(ver.get('smuggled_changes', []))}")
    failed = [s["id"] for s in outcome.get("sections", [])
              if s.get("status") != "refined"]
    if failed:
        print(f"[refine] INCOMPLETE — sections not refined: {failed}")
    if outcome.get("unresolved_conflicts"):
        print(f"[refine] unresolved conflicts: "
              f"{outcome['unresolved_conflicts'][:3]}")
    ok = disposition in ("complete", "already_converged")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
