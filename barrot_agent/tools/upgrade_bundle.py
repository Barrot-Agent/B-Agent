#!/usr/bin/env python3
"""Disabled legacy upgrade bundle.

The historical bundle overwrote files under ~/barrot, generated an hourly
workflow that committed and pushed to main, and emitted uncalibrated BUY/SELL
signals from unsynchronized provider responses. It is intentionally disabled.
"""
from __future__ import annotations


def main() -> int:
    print("DISABLED: legacy upgrade bundle performs unsafe overwrites and creates an automatic main-branch push workflow.")
    print("It also contains unvalidated directional heuristics. No files were written and no network calls were made.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
