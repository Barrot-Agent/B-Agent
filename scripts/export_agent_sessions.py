"""Export local directive-platform sessions as a portable JSON bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

from directive_platform.bundle import export_sessions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-dir", type=Path, default=Path(".directive_platform/sessions"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bundle = export_sessions(args.sessions_dir, args.output)
    print(f"Exported {len(bundle['sessions'])} session(s) to {args.output}")


if __name__ == "__main__":
    main()
