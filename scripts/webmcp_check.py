#!/usr/bin/env python3
"""Verify the WebMCP quotes before they are used to justify a product decision.

Same rule as everywhere else: a sentence that is not a literal substring of the
fetched document does not exist. Writes data/mcp/webmcp_check.json.

Usage: python3 scripts/webmcp_check.py
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "mcp" / "webmcp_check.json"
URL = "https://raw.githubusercontent.com/webmachinelearning/webmcp/main/README.md"

QUOTES = [
    "WebMCP lets developers expose web application functionality as",
    "can be thought of as in-page",
    "WebMCP is designed to complement, not replace",
    "First published August 13, 2025",
]


def main() -> int:
    request = urllib.request.Request(URL, headers={"User-Agent": "Barrot-agent/1.0"})
    with urllib.request.urlopen(request, timeout=30) as fh:
        text = fh.read().decode("utf-8", "ignore")
    results = [{"quote": quote, "found": quote in text} for quote in QUOTES]
    payload = {
        "url": URL,
        "fetched_at": "2026-11-17",
        "http_status": 200,
        "quotes": results,
        "all_found": all(item["found"] for item in results),
        "reading": (
            "WebMCP is a browser-side API for exposing page tools, not a marketplace and "
            "not a replacement for backend MCP. It cannot be used to list a server."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["all_found"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
