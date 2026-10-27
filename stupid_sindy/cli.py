"""
Command-line interface for the Stupid Sindy episode generator.

Usage
-----
    python -m stupid_sindy                         # series overview
    python -m stupid_sindy --episode 1             # single episode (text)
    python -m stupid_sindy --episode 1 --md        # single episode (markdown)
    python -m stupid_sindy --act 1                 # full act
    python -m stupid_sindy --all                   # complete series
    python -m stupid_sindy --all --md              # complete series (markdown)
    python -m stupid_sindy --list                  # list all episodes
    python -m stupid_sindy --episode 1 --out ep1.md  # save to file
"""

import argparse
import sys
from pathlib import Path

from .generator import (
    generate_episode,
    generate_act,
    generate_full_series,
    format_series_overview,
    ACT_TITLES,
)
from .episodes import EPISODES, episode_count


def _list_episodes() -> str:
    lines = [
        "STUPID SINDY — Episode List",
        "-" * 50,
    ]
    current_act = None
    ep_ranges = {1: "Ep 1-8", 2: "Ep 9-10", 3: "Ep 11+"}
    for ep in EPISODES:
        if ep["act"] != current_act:
            current_act = ep["act"]
            act_label = ACT_TITLES.get(current_act, f"ACT {current_act}")
            ep_range = ep_ranges.get(current_act, "")
            lines.append(f"\n  {act_label} ({ep_range})")
        lines.append(f"    {ep['number']:>2}. {ep['title']:<38} [{ep['tone']}]")
    lines.append(f"\nTotal: {episode_count()} episodes")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m stupid_sindy",
        description="Stupid Sindy episodic comedy skit generator",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--episode", "-e",
        type=int,
        metavar="N",
        help="Generate script for episode N",
    )
    group.add_argument(
        "--act", "-a",
        type=int,
        metavar="N",
        help="Generate all scripts for act N (1, 2, or 3)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Generate the complete series",
    )
    group.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all episodes",
    )
    parser.add_argument(
        "--md", "--markdown",
        action="store_true",
        help="Output in Markdown format instead of plain text",
    )
    parser.add_argument(
        "--out", "-o",
        type=str,
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )

    args = parser.parse_args(argv)
    fmt = "markdown" if args.md else "text"

    try:
        if args.list:
            output = _list_episodes()
        elif args.episode is not None:
            output = generate_episode(args.episode, fmt=fmt)
        elif args.act is not None:
            output = generate_act(args.act, fmt=fmt)
        elif args.all:
            output = generate_full_series(fmt=fmt)
        else:
            output = format_series_overview(fmt=fmt)
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.out:
        path = Path(args.out)
        path.write_text(output, encoding="utf-8")
        print(f"Written to {path}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
