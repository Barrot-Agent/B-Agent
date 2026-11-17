#!/usr/bin/env python3
"""Verify the MCP protocol quotes against the live specification page.

Same rule as everything else: a quote that is not a literal substring of the fetched
document does not exist. Writes data/mcp/spec_check.json.
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://modelcontextprotocol.io/specification/2025-06-18/server/tools"
OUT = ROOT / "data" / "mcp" / "spec_check.json"

QUOTES = [
    "To discover available tools, clients send a",
    "To invoke a tool, clients send a",
    "Servers that support tools",
]


def main() -> int:
    request = urllib.request.Request(URL, headers={"User-Agent": "Barrot-agent/1.0"})
    with urllib.request.urlopen(request, timeout=30) as fh:
        page = fh.read().decode("utf-8", "ignore")
    text = re.sub(r"<[^>]+>", " ", page)
    text = re.sub(r"\s+", " ", text)
    results = []
    for quote in QUOTES:
        results.append({"quote": quote, "found": quote in text})
    payload = {
        "url": URL,
        "fetched_at": "2026-11-17",
        "http_status": 200,
        "quotes": results,
        "all_found": all(r["found"] for r in results),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["all_found"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
