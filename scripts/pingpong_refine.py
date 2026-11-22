#!/usr/bin/env python3
"""Safe CLI for classified derived-data refinement. Offline mode is default."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from barrot_agent.refinement import (
    REFINABLE_DATA_CLASSES, HeuristicRefiner, RefinementPipeline, load_run,
    refine_document,
)

def _build_refiners(args):
    if args.live:
        raise PermissionError(
            "live external refinement has been decommissioned; use deterministic offline mode"
        )
    if args.allow_external_data:
        raise PermissionError(
            "--allow-external-data is unsupported because external refinement is decommissioned"
        )
    return [HeuristicRefiner(), HeuristicRefiner("heuristic-2")]

def _write_or_print(document, args, input_path=None):
    payload = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    if not args.out:
        sys.stdout.write(payload)
        return
    dest = Path(args.out)
    if input_path and input_path != "-" and dest.resolve() == Path(input_path).resolve():
        raise ValueError("refinement output must not overwrite its source file")
    if dest.exists() and not args.force_output:
        raise FileExistsError("output exists; pass --force-output to replace it")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(payload, encoding="utf-8")

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="?", help="JSON file path, or '-' for stdin")
    ap.add_argument("-o", "--out", help="new output path; default prints JSON")
    ap.add_argument("--force-output", action="store_true")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true")
    mode.add_argument("--live", action="store_true")
    ap.add_argument("--allow-external-data", action="store_true")
    ap.add_argument("--classification", required=True, choices=sorted(REFINABLE_DATA_CLASSES))
    ap.add_argument("--objective", default="")
    ap.add_argument("--max-rounds", type=int, default=12)
    ap.add_argument("--no-ledger", action="store_true")
    ap.add_argument("--resume", metavar="RUN_ID")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    try:
        refiners = _build_refiners(args)
        ledger = None if args.no_ledger else "ping-pongings/knowledge-base/refinement_log.jsonl"
        if args.resume:
            if args.input:
                raise ValueError("omit input when using --resume")
            state = load_run(args.resume)
            if state.data_classification != args.classification:
                raise PermissionError("resume classification does not match saved run")
            pipe = RefinementPipeline(
                refiners, ledger=ledger, data_classification=args.classification,
                allow_external=False)
            outcome = pipe.resume(args.resume)
            state = load_run(args.resume)
            if outcome.get("disposition") not in (
                    "complete", "already_converged", "nothing_to_resume"):
                print(f"[refine] disposition={outcome.get('disposition')}; output withheld",
                      file=sys.stderr)
                return 1
            _write_or_print(state.document, args)
            print(f"[refine] disposition={outcome.get('disposition')} run={args.resume}",
                  file=sys.stderr)
            return 0
        if not args.input:
            raise ValueError("input is required unless --resume is used")
        data = json.load(sys.stdin) if args.input == "-" else json.loads(
            Path(args.input).read_text(encoding="utf-8"))
        outcome = refine_document(
            data, objective=args.objective, refiners=refiners,
            source_identity=str(args.input), force=args.force, ledger=ledger,
            max_rounds=args.max_rounds, data_classification=args.classification,
            allow_external=False)
        if outcome.get("mode") == "classic":
            document = outcome["report"].data
            disposition = outcome["disposition"]
        else:
            disposition = outcome.get("disposition")
            if disposition not in ("complete", "already_converged"):
                print(f"[refine] disposition={disposition}; output withheld",
                      file=sys.stderr)
                return 1
            document = load_run(outcome["run_id"]).document
        _write_or_print(document, args, args.input)
        print(f"[refine] disposition={disposition} mode={outcome.get('mode')} "
              f"run={outcome.get('run_id')}", file=sys.stderr)
        return 0
    except (OSError, ValueError, PermissionError, TypeError) as exc:
        print(f"[refine] blocked: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
