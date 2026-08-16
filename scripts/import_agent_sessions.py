"""Merge a portable agent-session bundle into the local session store."""

from __future__ import annotations

import argparse
from pathlib import Path

from directive_platform.bundle import merge_sessions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--sessions-dir", type=Path, default=Path(".directive_platform/sessions"))
    parser.add_argument("--report", type=Path, default=Path(".directive_platform/session-merge-report.json"))
    parser.add_argument("--merge", action="store_true", help="Apply the import (required for safety).")
    args = parser.parse_args()
    if not args.merge:
        parser.error("--merge is required to modify the local session store")
    report = merge_sessions(args.sessions_dir, args.input, args.report)
    print(f"Merged {report['imported']} session(s); {len(report['conflicts'])} conflict(s)")


if __name__ == "__main__":
    main()
