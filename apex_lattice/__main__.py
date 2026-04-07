"""
Apex Lattice CLI entry point.

Usage:
    python -m apex_lattice [--once | --schedule SECONDS] [--repo-root PATH]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    _configure_logging()

    parser = argparse.ArgumentParser(
        prog="python -m apex_lattice",
        description="Apex Lattice – sandbox-based infrastructure analysis pipeline",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the repository root to analyse (default: current directory)",
    )
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Directory under which .apex_lattice/ storage is created (default: current directory)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--once",
        action="store_true",
        default=True,
        help="Run a single analysis cycle (default)",
    )
    mode.add_argument(
        "--schedule",
        type=float,
        metavar="SECONDS",
        help="Run on a recurring schedule every SECONDS seconds",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Stop after this many cycles when using --schedule",
    )
    parser.add_argument(
        "--github-repo",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="GitHub repository in owner/repo format for PR creation",
    )
    parser.add_argument(
        "--github-token",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub token for PR creation (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--base-branch",
        default="Main",
        help="Target base branch for created PRs (default: Main)",
    )

    args = parser.parse_args(argv)

    from apex_lattice.cycle import CycleManager  # noqa: PLC0415

    mgr = CycleManager(
        repo_root=Path(args.repo_root),
        base_dir=Path(args.base_dir),
        github_token=args.github_token or None,
        github_repo=args.github_repo or None,
        base_branch=args.base_branch,
    )

    if args.schedule:
        mgr.run_scheduled(interval=args.schedule, max_cycles=args.max_cycles)
    else:
        summary = mgr.run_once()
        print(json.dumps(summary, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())
