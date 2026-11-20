"""Command line interface for the paid-issue kit.

    python3 -m paid_issue_kit score --input candidates.json --out ledger.csv
    python3 -m paid_issue_kit pr --plan plan.json --out-dir out/
    python3 -m paid_issue_kit timebox start --state run.json --mission "..."
    python3 -m paid_issue_kit timebox checkpoint --state run.json --phase triage
    python3 -m paid_issue_kit timebox status --state run.json
    python3 -m paid_issue_kit phases
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any

from .ledger import Candidate, Policy, audit, summarize, to_csv
from .pack import build_evidence_pack, build_pr_body, validate_evidence_plan, validate_pr_body
from .timebox import PHASES, Timebox


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def candidates_from(data: Any) -> list[Candidate]:
    if isinstance(data, dict):
        data = data.get("candidates", data)
    if not isinstance(data, list):
        raise ValueError("input must be a list of candidates or {'candidates': [...]}")
    return [Candidate.from_dict(item) for item in data]


def cmd_score(args: argparse.Namespace) -> int:
    try:
        candidates = candidates_from(load_json(args.input))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    policy = Policy(min_effective_hourly_usd=args.min_hourly)
    now = datetime.fromisoformat(args.now) if args.now else None
    verdicts = audit(candidates, policy=policy, now=now)
    csv_text = to_csv(verdicts)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(csv_text)
        print(json.dumps(summarize(verdicts), indent=2))
    else:
        sys.stdout.write(csv_text)
    return 0


def cmd_pr(args: argparse.Namespace) -> int:
    try:
        plan = load_json(args.plan)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not isinstance(plan, dict):
        print("ERROR: plan must be a JSON object", file=sys.stderr)
        return 2

    try:
        body = build_pr_body(plan)
        evidence = build_evidence_pack(plan)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    problems = validate_pr_body(body) + validate_evidence_plan(plan)
    if problems:
        for problem in problems:
            print(f"BLOCKED: {problem}", file=sys.stderr)
        return 1

    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        body_path = os.path.join(args.out_dir, "PR_BODY.md")
        evidence_path = os.path.join(args.out_dir, "EVIDENCE_PACK.md")
        with open(body_path, "w", encoding="utf-8") as handle:
            handle.write(body)
        with open(evidence_path, "w", encoding="utf-8") as handle:
            handle.write(evidence)
        print(f"wrote {body_path}")
        print(f"wrote {evidence_path}")
    else:
        sys.stdout.write(body)
    return 0


def cmd_timebox(args: argparse.Namespace) -> int:
    try:
        if args.action == "start":
            box = Timebox(args.mission or "")
            box.start()
            box.save(args.state)
        else:
            box = Timebox.load(args.state)
            if args.action == "checkpoint":
                box.checkpoint(args.phase, note=args.note or "")
                box.save(args.state)
        print(box.report())
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_phases(_: argparse.Namespace) -> int:
    print(f"{'phase':<12}{'minutes':>8}  purpose")
    for name, minutes, purpose in PHASES:
        print(f"{name:<12}{minutes:>8}  {purpose}")
    print(f"{'total':<12}{sum(m for _, m, _ in PHASES):>8}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paid_issue_kit",
        description="Score paid issues, package a PR, and keep a 120-minute timebox.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    score = sub.add_parser("score", help="score candidates into a CSV ledger")
    score.add_argument("--input", required=True, help="JSON file with candidates")
    score.add_argument("--out", help="CSV output path; stdout when omitted")
    score.add_argument("--min-hourly", type=float, default=30.0, help="minimum USD per hour")
    score.add_argument("--now", help="ISO timestamp for the repo-idle check")
    score.set_defaults(func=cmd_score)

    pr = sub.add_parser("pr", help="build and validate a PR body and evidence pack")
    pr.add_argument("--plan", required=True, help="JSON plan file")
    pr.add_argument("--out-dir", help="write PR_BODY.md and EVIDENCE_PACK.md here")
    pr.set_defaults(func=cmd_pr)

    box = sub.add_parser("timebox", help="run the 120-minute phase gate")
    box.add_argument("--state", required=True, help="JSON state file")
    box.add_argument("--mission", help="mission text (start only)")
    box.add_argument("--phase", choices=[name for name, _, _ in PHASES],
                     help="phase to complete (checkpoint only)")
    box.add_argument("--note", help="optional note for the checkpoint")
    box.add_argument("action", choices=("start", "checkpoint", "status"))
    box.set_defaults(func=cmd_timebox)

    phases = sub.add_parser("phases", help="print the phase budget")
    phases.set_defaults(func=cmd_phases)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "timebox" and args.action == "start" and not args.mission:
        parser.error("timebox start requires --mission")
    if args.command == "timebox" and args.action == "checkpoint" and not args.phase:
        parser.error("timebox checkpoint requires --phase")
    return int(args.func(args))
