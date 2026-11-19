"""Quarantined prototype: the original implementation mutated live targets and deleted losing variants.

Do not re-enable until a non-destructive isolated-copy evaluator has been designed,
implemented, and independently tested. This module intentionally performs no I/O.
"""
from __future__ import annotations

import sys
from pathlib import Path

QUARANTINE_MESSAGE = (
    "TRANSMUTE QUARANTINED: the former implementation overwrote the target and "
    "deleted losing variants in the live workspace. No files were read, written, "
    "moved, or deleted. Use an isolated-copy evaluator that preserves every original."
)


def transmute(
    target: Path,
    variants: list[Path],
    tests: list[Path],
    runner: str,
    log_path: Path,
    keep_losers: bool = False,
    interactive: bool = False,
    cwd: Path | None = None,
    repeats: int = 1,
):
    """Refuse all live-workspace transmutation until a safe evaluator exists."""
    raise RuntimeError(QUARANTINE_MESSAGE)


def main(argv=None) -> int:
    """The command-line entry point is intentionally fail-closed."""
    print(QUARANTINE_MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
