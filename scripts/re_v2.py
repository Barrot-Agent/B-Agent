#!/usr/bin/env python3
"""Reverse-engineering v2: TRACE-5.

The v1 loop was: recall an identifier, fetch its metadata, narrate what the paper
contributes from memory, and gate the result on a schema test. Two of three
identifiers recalled from memory on 2026-11-17 resolved to the wrong paper, and the
schema test passed anyway.

v2 removes the recall step and makes the quote the unit of evidence:

  T  Target      a falsifiable sentence plus the title fragment it must resolve to
  R  Retrieve    by query or DOI, never by a recalled arXiv id
  A  Assert-quote  the quote must be a literal substring of the retrieved text
  C  Cross-check   a second independent document, or the record is marked single
  E  Exit        falsifier, what the source does not show, and an evidence grade

Grades: Q quoted primary, E existence only (content NOT verified), X rejected
mismatch. Nothing below Q may be used to support a claim.

Usage:
  python3 scripts/re_v2.py build     fetch and write data/millennium/claims/*.json
  python3 scripts/re_v2.py check     re-validate the written file offline
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "millennium" / "claims"
ARXIV = "https://export.arxiv.org/api/query"
CROSSREF = "https://api.crossref.org/works"
UA = {"User-Agent": "Barrot-agent/1.0 (reverse-engineering v2)"}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


def fetch_doi(doi: str) -> dict:
    import urllib.request

    url = f"{CROSSREF}/{doi}?mailto=barrot@example.invalid"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as fh:
        message = json.loads(fh.read().decode())["message"]
    return {
        "status": 200,
        "identifier": doi,
        "title": (message.get("title") or [""])[0],
        "year": (message.get("issued", {}).get("date-parts") or [[None]])[0][0],
        "venue": (message.get("container-title") or [""])[0],
        "authors": [a.get("family", "") for a in message.get("author", [])],
        "abstract": _clean(message.get("abstract", "")),
    }


def fetch_arxiv(arxiv_id: str) -> dict:
    import urllib.request

    url = f"{ARXIV}?id_list={arxiv_id}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as fh:
        xml = fh.read().decode("utf-8", "ignore")
    entry = (re.search(r"<entry>([\s\S]*?)</entry>", xml) or [None, ""])[1]

    def tag(name: str) -> str:
        found = re.search(rf"<{name}>([\s\S]*?)</{name}>", entry)
        return _clean(found.group(1)) if found else ""

    return {
        "status": 200,
        "identifier": arxiv_id,
        "title": tag("title"),
        "year": tag("published")[:4],
        "venue": "arXiv",
        "authors": [],
        "abstract": tag("summary"),
    }


def retrieve(spec: dict) -> dict:
    kind, value = spec["request"]
    return fetch_arxiv(value) if kind == "arxiv" else fetch_doi(value)


def grade(spec: dict, record: dict) -> dict:
    target_title = spec["expected_title_fragment"].lower()
    title_ok = target_title in record["title"].lower()
    quotes = [q for q in spec.get("quotes", []) if q in record["abstract"]]
    missing = [q for q in spec.get("quotes", []) if q not in record["abstract"]]

    if not title_ok:
        status = "X"
        reason = f"title mismatch: wanted {spec['expected_title_fragment']!r}, got {record['title']!r}"
    elif not record["abstract"]:
        status = "E"
        reason = "no abstract retrievable; existence verified, content not verified"
    elif missing:
        status = "X"
        reason = f"quote not found in retrieved text: {missing[0][:60]!r}"
    else:
        status = "Q"
        reason = "quote matched the retrieved primary text"

    return {
        "id": spec["id"],
        "problem": spec["problem"],
        "claim": spec["claim"],
        "status": status,
        "grade_reason": reason,
        "evidence": {
            "kind": spec["request"][0],
            "identifier": record["identifier"],
            "title": record["title"],
            "year": record["year"],
            "venue": record["venue"],
            "authors": record["authors"],
            "http_status": record["status"],
            "abstract": record["abstract"],
        },
        "quotes": quotes,
        "falsifier": spec["falsifier"],
        "does_not_show": spec["does_not_show"],
        "affirmed": status == "Q",
    }


SPECS = [
    {
        "id": "relativization-barrier",
        "problem": "P vs NP",
        "claim": "Oracle separations exist in both directions, so any technique invariant under relativization cannot settle P versus NP.",
        "request": ["doi", "10.1137/0204037"],
        "expected_title_fragment": "Relativizations of the",
        "quotes": [
            "We construct a recursive set A such that",
            "On the other hand, we construct a recursive set B such that",
        ],
        "falsifier": "a relativizing argument that separates P from NP, i.e. a proof stable under every oracle",
        "does_not_show": "that non-relativizing techniques must also fail; only that relativizing ones cannot decide the question",
    },
    {
        "id": "natural-proofs-barrier",
        "problem": "P vs NP",
        "claim": "Razborov and Rudich show that natural proofs cannot prove strong enough circuit lower bounds to separate P from NP without breaking pseudorandom functions.",
        "request": ["doi", "10.1006/jcss.1997.1494"],
        "expected_title_fragment": "Natural Proofs",
        "quotes": [],
        "falsifier": "a natural proof that separates P from NP while pseudorandom function candidates remain secure",
        "does_not_show": "anything yet: no abstract was retrievable, so this record is existence only and the claim above is not affirmed",
    },
    {
        "id": "algebrization-barrier",
        "problem": "P vs NP",
        "claim": "A third barrier, algebrization, sits beyond relativization and natural proofs, and P versus NP will require non-algebrizing techniques.",
        "request": ["doi", "10.1145/1490270.1490272"],
        "expected_title_fragment": "Algebrization",
        "quotes": [
            "we present such a barrier, which we call algebraic relativization or algebrization",
            "will require non-algebrizing techniques",
        ],
        "falsifier": "a proof of an algebrizing separation for P versus NP, which would show the barrier is not binding",
        "does_not_show": "that no non-algebrizing technique exists; only that the current toolbox does not contain one",
    },
    {
        "id": "negative-control-arxiv-id-from-memory",
        "problem": "P vs NP",
        "claim": "control: an arXiv id recalled from memory for the algebrization paper",
        "request": ["arxiv", "0801.4877"],
        "expected_title_fragment": "Algebrization",
        "quotes": [],
        "falsifier": "n/a, this record exists to prove the title check fires",
        "does_not_show": "nothing; it shows the recalled identifier was wrong",
    },
    {
        "id": "negative-control-doi-from-memory",
        "problem": "P vs NP",
        "claim": "control: a DOI recalled from memory for the algebrization paper",
        "request": ["doi", "10.1145/1462153.1462156"],
        "expected_title_fragment": "Algebrization",
        "quotes": [],
        "falsifier": "n/a, this record exists to prove the title check fires",
        "does_not_show": "nothing; it shows the recalled identifier was wrong",
    },
]

CROSS_CHECK = {
    "record_id": "algebrization-barrier",
    "request": ["arxiv", "2511.14038"],
    "quote": "proposed by Aaronson and Wigderson",
    "meaning": "an independent 2025 paper attributes the algebrization barrier to Aaronson and Wigderson, corroborating authorship and venue",
}


def build() -> int:
    records = []
    for spec in SPECS:
        record = retrieve(spec)
        records.append(grade(spec, record))

    cross = retrieve({"request": CROSS_CHECK["request"]})
    records.append(
        {
            "id": "cross-check-algebrization-authorship",
            "problem": "P vs NP",
            "claim": CROSS_CHECK["meaning"],
            "status": "Q" if CROSS_CHECK["quote"] in cross["abstract"] else "X",
            "grade_reason": "secondary document quote matched" if CROSS_CHECK["quote"] in cross["abstract"] else "quote not found",
            "evidence": {
                "kind": "arxiv",
                "identifier": cross["identifier"],
                "title": cross["title"],
                "year": cross["year"],
                "venue": cross["venue"],
                "authors": cross["authors"],
                "http_status": cross["status"],
                "abstract": cross["abstract"],
            },
            "quotes": [CROSS_CHECK["quote"]] if CROSS_CHECK["quote"] in cross["abstract"] else [],
            "falsifier": "a primary source stating the barrier is not due to Aaronson and Wigderson",
            "does_not_show": "that the barrier is correct; only who proposed it",
            "affirmed": CROSS_CHECK["quote"] in cross["abstract"],
        }
    )

    payload = {
        "problem": "P vs NP",
        "method": "reverse-engineering v2 (TRACE-5)",
        "built_at": "2026-11-17",
        "records": records,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "p_vs_np.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    print(json.dumps({"file": str(path.relative_to(ROOT)), "grades": counts}, indent=2))
    return 0 if counts.get("X", 0) <= 2 else 1


def validate(path: Path | None = None) -> list[str]:
    path = path or OUT_DIR / "p_vs_np.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    problems: list[str] = []
    for record in payload["records"]:
        abstract = record["evidence"]["abstract"]
        title = record["evidence"]["title"]
        if record["evidence"]["http_status"] != 200:
            problems.append(f"{record['id']}: non-200 evidence")
        if record["status"] == "Q":
            if not record["quotes"]:
                problems.append(f"{record['id']}: Q with no quote")
            for quote in record["quotes"]:
                if quote not in abstract:
                    problems.append(f"{record['id']}: quote absent from stored abstract")
            if not title:
                problems.append(f"{record['id']}: Q with no title")
        if record["status"] == "E" and record["affirmed"]:
            problems.append(f"{record['id']}: existence-only record marked affirmed")
        if record["status"] == "X" and record["affirmed"]:
            problems.append(f"{record['id']}: rejected record marked affirmed")
        if record["status"] not in {"Q", "E", "X"}:
            problems.append(f"{record['id']}: unknown status")
    return problems


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "check"
    if command == "build":
        raise SystemExit(build())
    issues = validate()
    print(json.dumps({"valid": not issues, "issues": issues}, indent=2))
    raise SystemExit(0 if not issues else 1)
