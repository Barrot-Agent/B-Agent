#!/usr/bin/env python3
"""
Safe patcher: gates premium WebMCP tools in web/landing.html behind
Gumroad license verification. Fails closed - if expected patterns
aren't found, it changes nothing and reports exactly what's missing.

Usage:
  python3 scripts/patch_landing_monetization.py            # dry run, shows diff
  python3 scripts/patch_landing_monetization.py --apply    # writes the file
"""
import re
import sys
import difflib
from pathlib import Path

LANDING = Path("web/landing.html")
PREMIUM_TOOLS = ["getLatestXRPSignal", "getSignalAccuracy"]
SCRIPT_TAG = '<script src="webmcp_monetization.js"></script>\n'


def load_source():
    if not LANDING.exists():
        print(f"FAIL CLOSED: {LANDING} not found. No changes made.")
        sys.exit(1)
    return LANDING.read_text(encoding="utf-8")


def ensure_script_tag(src: str) -> str:
    if "webmcp_monetization.js" in src:
        return src
    if "</head>" in src:
        return src.replace("</head>", "  " + SCRIPT_TAG + "</head>", 1)
    print("FAIL CLOSED: no </head> tag found. No changes made.")
    sys.exit(1)


def main():
    apply = "--apply" in sys.argv
    src = load_source()
    original = src
    src = ensure_script_tag(src)

    any_gated = False
    for tool in PREMIUM_TOOLS:
        src, gated = gate_execute(src, tool)
        any_gated = any_gated or gated
        src = gate_schema(src, tool)

    if src == original:
        print("No changes made (already patched or nothing matched).")
        return

    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        src.splitlines(keepends=True),
        fromfile="web/landing.html (before)",
        tofile="web/landing.html (after)",
    )
    print("".join(diff))

    if not any_gated:
        print("\nFAIL CLOSED: no tool bodies matched. Nothing written.")
        return

    if apply:
        LANDING.write_text(src, encoding="utf-8")
        print(f"\nApplied. {LANDING} updated.")
    else:
        print("\nDry run only. Re-run with --apply to write these changes.")


if __name__ == "__main__":
    main()


def main():
    apply = "--apply" in sys.argv
    src = load_source()
    original = src
    src = ensure_script_tag(src)

    any_gated = False
    for tool in PREMIUM_TOOLS:
        src, gated = gate_execute(src, tool)
        any_gated = any_gated or gated
        src = gate_schema(src, tool)

    if src == original:
        print("No changes made (already patched or nothing matched).")
        return

    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        src.splitlines(keepends=True),
        fromfile="web/landing.html (before)",
        tofile="web/landing.html (after)",
    )
    print("".join(diff))

    if not any_gated:
        print("\nFAIL CLOSED: no tool bodies matched. Nothing written.")
        return

    if apply:
        LANDING.write_text(src, encoding="utf-8")
        print(f"\nApplied. {LANDING} updated.")
    else:
        print("\nDry run only. Re-run with --apply to write these changes.")


if __name__ == "__main__":
    main()
