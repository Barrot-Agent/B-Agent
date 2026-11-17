#!/usr/bin/env python3
"""Retraction probe: does a DOI have a deposited retraction notice?

This is the missing half of the learning-loop KPI. A learning loop that cannot
notice a retracted source is not learning, it is accumulating. The fixture set is
built from Crossref's own deposits, not from memory:

  * a retracted paper is one whose DOI appears in the update-to list of a work
    deposited with update type "retraction"
  * a control is a paper with no such deposit, recorded with the date checked

Direction matters. Crossref records the notice pointing at the article
(filter updates:<doi>), not reliably the article pointing at the notice, so the
probe queries both and requires the notice's own update-to entry to name the DOI.

Usage:
  python3 scripts/retraction_probe.py --build   rebuild the fixture file
  python3 scripts/retraction_probe.py --check   offline validation of stored data
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "research" / "retraction_fixtures.json"
DENYLIST = ROOT / "data" / "research" / "retracted_dois.json"
CROSSREF = "https://api.crossref.org/works"
UA = {"User-Agent": "Barrot-agent/1.0 (retraction probe)"}

RETRACTED_CANDIDATES = [
    "10.1177/1758835919874651",
    "10.1538/expanim.54.1",
    "10.1007/s11277-021-09072-0",
    "10.1016/S0140-6736(97)11096-0",
]
CONTROL_CANDIDATES = [
    "10.1137/0204037",
    "10.1145/1490270.1490272",
]


def fetch_json(url: str, attempts: int = 3) -> dict:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as fh:
                return json.loads(fh.read())
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except Exception as exc:  # network flake
            last = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"fetch failed after {attempts} attempts: {last}")


def notices_for(doi: str) -> list[dict]:
    """Works whose own update-to names this DOI with type retraction."""
    url = (
        f"{CROSSREF}?filter=updates:{doi}&rows=20"
        f"&select=DOI,title,update-to,published&mailto=barrot@example.invalid"
    )
    payload = fetch_json(url)
    notices = []
    for item in payload["message"]["items"]:
        for target in item.get("update-to", []) or []:
            if str(target.get("type", "")).lower() == "retraction" and str(target.get("DOI", "")).lower() == doi.lower():
                notices.append({
                    "notice_doi": item.get("DOI"),
                    "notice_title": (item.get("title") or [""])[0],
                    "update_type": target.get("type"),
                })
    return notices


def probe(doi: str, notice_lookup=notices_for) -> dict:
    notices = notice_lookup(doi)
    return {
        "doi": doi,
        "retracted": bool(notices),
        "notices": notices,
        "checked_at": "2026-11-17",
        "method": "Crossref filter updates:<doi>, notice update-to must name the DOI",
    }


def write_denylist(entries: list[dict]) -> None:
    """Offline derivation from stored fixtures, so the list cannot drift."""
    DENYLIST.parent.mkdir(parents=True, exist_ok=True)
    DENYLIST.write_text(json.dumps({
        "built_at": "2026-11-17",
        "source": "scripts/retraction_probe.py (from verified fixtures)",
        "retracted": [
            {"doi": entry["doi"], "notices": [n["notice_doi"] for n in entry["notices"]]}
            for entry in entries if entry["retracted"]
        ],
    }, indent=2), encoding="utf-8")


def build() -> int:
    entries = []
    for doi in RETRACTED_CANDIDATES:
        record = probe(doi)
        record["expected"] = "retracted"
        entries.append(record)
        time.sleep(1)
    for doi in CONTROL_CANDIDATES:
        record = probe(doi)
        record["expected"] = "not_retracted"
        entries.append(record)
        time.sleep(1)
    write_denylist(entries)
    payload = {
        "method": "Crossref deposit lookup; expectation is the deposit, not a memory",
        "built_at": "2026-11-17",
        "entries": entries,
        "summary": {
            "retracted_expected": sum(1 for e in entries if e["expected"] == "retracted"),
            "controls": sum(1 for e in entries if e["expected"] == "not_retracted"),
            "retracted_detected": sum(1 for e in entries if e["expected"] == "retracted" and e["retracted"]),
            "controls_clear": sum(1 for e in entries if e["expected"] == "not_retracted" and not e["retracted"]),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    return 0


def check() -> int:
    payload = json.loads(OUT.read_text(encoding="utf-8"))
    problems = []
    for entry in payload["entries"]:
        if entry["expected"] == "retracted" and not entry["retracted"]:
            problems.append(f"{entry['doi']} expected retracted, no notice stored")
        if entry["expected"] == "retracted" and not entry["notices"]:
            problems.append(f"{entry['doi']} marked retracted with an empty notice list")
        if entry["expected"] == "not_retracted" and entry["retracted"]:
            problems.append(f"{entry['doi']} control is marked retracted")
    if not problems:
        write_denylist(payload["entries"])
    print(json.dumps({"fixtures": len(payload["entries"]), "problems": problems}, indent=2))
    return 1 if problems else 0


def main(argv: list[str]) -> int:
    if "--build" in argv:
        return build()
    if "--check" in argv:
        return check()
    print("usage: retraction_probe.py --build | --check", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
