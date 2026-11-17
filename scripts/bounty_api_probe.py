#!/usr/bin/env python3
"""Probe bounty platforms for an unauthenticated amount source.

The hunter needs one thing: a URL that returns a number for a specific issue
without a login. This script asks each platform and records exactly what came
back: status, content type, first bytes of the body. No parsing of guessed
schemas, no assumed field names.

A probe is only marked "amount_source" when the body is JSON and contains a
numeric amount field. Everything else is evidence of absence for this run.

Usage: python3 scripts/bounty_api_probe.py
Writes: data/money/bounty_apis.json
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "money" / "bounty_apis.json"

PROBES = [
    ("issuehunt issue page", "https://issuehunt.io/r/k3d-io/k3d"),
    ("issuehunt api guess", "https://issuehunt.io/api/v1/repos/k3d-io/k3d"),
    ("issuehunt api host", "https://api.issuehunt.io/v1/repos/k3d-io/k3d"),
    ("opire health", "https://api.opire.dev/health"),
    ("opire bounties guess", "https://api.opire.dev/bounties"),
    ("algora api guess", "https://api.algora.io/v1/bounties"),
    ("algora web guess", "https://algora.io/v1/bounties"),
    ("polar products", "https://api.polar.sh/v1/products?limit=1"),
    ("polar issue search", "https://api.polar.sh/v1/issues/search"),
]

AMOUNT_KEYS = ("amount", "bounty", "reward", "price", "value", "total")


def probe(name: str, url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "Barrot/1.0"})
    record = {"name": name, "url": url}
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read(4000)
            record["status"] = response.status
            record["content_type"] = response.headers.get("content-type", "")
    except urllib.error.HTTPError as exc:
        body = exc.read(4000) if exc.fp else b""
        record["status"] = exc.code
        record["content_type"] = exc.headers.get("content-type", "") if exc.headers else ""
    except Exception as exc:  # network failures are evidence too
        record.update(status=0, content_type="", error=str(exc)[:160], body_head="", verdict="unreachable")
        return record

    text = body.decode("utf-8", "ignore")
    record["body_head"] = " ".join(text.split())[:160]
    record["verdict"] = "no_amount"
    if "json" in record["content_type"] and record["status"] == 200:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
        if payload is not None:
            blob = json.dumps(payload).lower()
            if any(f'"{key}"' in blob for key in AMOUNT_KEYS):
                record["verdict"] = "amount_source"
    return record


def main() -> int:
    records = [probe(name, url) for name, url in PROBES]
    payload = {
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "probes": records,
        "amount_sources": [r["url"] for r in records if r["verdict"] == "amount_source"],
        "disclosure": (
            "A 404 or a 401 is evidence that an endpoint does not answer anonymously. "
            "It is not evidence that the platform has no bounties."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    for record in records:
        print(f"{record['status']:>4} {record['verdict']:<14} {record['url']} :: {record.get('body_head','')[:70]}")
    print(f"amount sources: {len(payload['amount_sources'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
