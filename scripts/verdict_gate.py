#!/usr/bin/env python3
"""Gate a verdict document: a verdict letter, a falsifier, an upgrade condition.

Iteration 2 of the indefinite loop. Iteration 1 produced a verdict whose weakest
property was that nothing enforced its structure: the "would become A if" sentence
was voluntary. A verdict without an upgrade condition cannot be revisited, so it is
a paragraph, not a gate.

Checks, each independent:
  1. exactly one declared verdict line, of the form  **C: ...**
  2. a falsifier line: a line containing "falsifier"
  3. an upgrade condition: "would become <letter> if" (case-insensitive)
  4. a stated limit: "does not claim" or "does not show"

Usage:
  python3 scripts/verdict_gate.py FILE [FILE ...]   exit 1 if any file fails
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DECLARATION = re.compile(r"^\s*\*\*([ABCD]):\s*\S", re.MULTILINE)
UPGRADE = re.compile(r"would become\s+([ABCD])\s+if", re.IGNORECASE)


def check_text(text: str) -> list[str]:
    problems: list[str] = []

    declared = DECLARATION.findall(text)
    if not declared:
        problems.append("no verdict declaration (expected a line like '**C: ...**')")
    elif len(declared) > 1:
        problems.append(f"multiple verdict declarations: {declared}")

    if not re.search(r"^.*falsifier.*$", text, re.IGNORECASE | re.MULTILINE):
        problems.append("no falsifier line")

    upgrades = UPGRADE.findall(text)
    if not upgrades:
        problems.append("no upgrade condition ('would become X if ...')")
    elif len(upgrades) > 1:
        problems.append(f"multiple upgrade targets: {upgrades}")

    if not re.search(r"does not (claim|show)", text, re.IGNORECASE):
        problems.append("no stated limit ('does not claim' / 'does not show')")

    if declared and upgrades and declared[0] == upgrades[0].upper():
        problems.append(f"verdict {declared[0]} cannot upgrade to itself")

    return problems


def check_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"unreadable: {exc}"]
    problems = check_text(text)
    return [f"{path}: {problem}" for problem in problems]


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: verdict_gate.py FILE [FILE ...]", file=sys.stderr)
        return 2
    failures: list[str] = []
    for name in argv:
        problems = check_file(Path(name))
        if problems:
            failures.extend(problems)
            print(f"FAIL {name}")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"PASS {name}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
