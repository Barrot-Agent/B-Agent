#!/usr/bin/env python3
"""Reverse-engineering v2: TRACE-5.

  T  Target       a falsifiable sentence plus the title fragment it must resolve to
  R  Retrieve     by query or DOI, never by an identifier recalled from memory
  A  Assert-quote the quote must be a literal substring of the retrieved text
  C  Cross-check  a second independent document, or the record is marked single
  E  Exit         falsifier, what the source does not show, and an evidence grade

Grades: Q quoted primary, E existence only (content NOT verified), X rejected
mismatch. Only Q may support a claim, and a Q record may still be excluded when the
source is an unrefereed assertion rather than a result.

Usage:
  python3 scripts/re_v2.py build [p_vs_np|hodge]   fetch and write claims files
  python3 scripts/re_v2.py check [path]            re-validate offline
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


def retrieve(request: list) -> dict:
    kind, value = request
    return fetch_arxiv(value) if kind == "arxiv" else fetch_doi(value)


def grade(spec: dict, record: dict) -> dict:
    title_ok = spec["expected_title_fragment"].lower() in record["title"].lower()
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

    excluded = bool(spec.get("exclude"))
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
        "single_source": "cross_check" not in spec,
        "excluded_from_evidence": excluded,
        "exclusion_reason": spec.get("exclude_reason", "") if excluded else "",
    }


def cross_check_record(spec: dict) -> dict:
    check = spec["cross_check"]
    record = retrieve(check["request"])
    hit = check["quote"] in record["abstract"]
    return {
        "id": f"cross-check-{spec['id']}",
        "problem": spec["problem"],
        "claim": check["meaning"],
        "status": "Q" if hit else "X",
        "grade_reason": "secondary document quote matched" if hit else "quote not found",
        "evidence": {
            "kind": check["request"][0],
            "identifier": record["identifier"],
            "title": record["title"],
            "year": record["year"],
            "venue": record["venue"],
            "authors": record["authors"],
            "http_status": record["status"],
            "abstract": record["abstract"],
        },
        "quotes": [check["quote"]] if hit else [],
        "falsifier": check["falsifier"],
        "does_not_show": "that the original result is correct; this checks attribution only",
        "affirmed": hit,
        "single_source": False,
        "excluded_from_evidence": False,
        "exclusion_reason": "",
    }


P_VS_NP_SPECS = [
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
        "cross_check": {
            "request": ["arxiv", "2511.14038"],
            "quote": "proposed by Aaronson and Wigderson",
            "meaning": "an independent 2025 paper attributes the algebrization barrier to Aaronson and Wigderson, corroborating authorship and venue",
            "falsifier": "a primary source stating the barrier is not due to Aaronson and Wigderson",
        },
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

HODGE_SPECS = [
    {
        "id": "hodge-open-status",
        "problem": "Hodge Conjecture",
        "claim": "As of 2021, the Hodge conjecture is an open problem, not a settled result.",
        "request": ["arxiv", "2105.04695"],
        "expected_title_fragment": "Known cases of the Hodge conjecture",
        "quotes": ["The Hodge conjecture is a major open problem in complex algebraic geometry"],
        "falsifier": "a refereed proof accepted by the community, after which surveys stop calling it open",
        "does_not_show": "how much is known, or which cases are settled; only the general status as of 2021",
    },
    {
        "id": "integral-hodge-atiyah-hirzebruch",
        "problem": "Hodge Conjecture",
        "claim": "Atiyah and Hirzebruch (1962) produced the torsion obstruction that makes the integral form of the Hodge conjecture false.",
        "request": ["doi", "10.1016/0040-9383(62)90094-0"],
        "expected_title_fragment": "Analytic cycles on complex manifolds",
        "quotes": [],
        "falsifier": "a proof that every integral Hodge class is algebraic, which would remove the torsion obstruction",
        "does_not_show": "content is unverified: Topology 1962 is paywalled and exposes no abstract, so this is an existence record only",
    },
    {
        "id": "integral-hodge-counterexamples",
        "problem": "Hodge Conjecture",
        "claim": "Further counterexamples to the integral Hodge conjecture have been constructed in codimension 2 and 3 for approximations to the classifying space of groups of type A.",
        "request": ["arxiv", "1601.06170"],
        "expected_title_fragment": "Further counterexamples to the integral Hodge conjecture",
        "quotes": [
            "We study the integral Hodge conjecture in complex codimension $2$ and $3$",
            "extending his two counterexamples to a general family of groups",
        ],
        "falsifier": "a theorem that all integral Hodge classes in codimension 2 are algebraic on these spaces",
        "does_not_show": "the full classification of such counterexamples, nor whether the rational form fails",
    },
    {
        "id": "lefschetz-one-one",
        "problem": "Hodge Conjecture",
        "claim": "There is a Lefschetz (1,1) theorem characterizing classes of Cartier divisors, and it has an analogue for normal projective complex varieties.",
        "request": ["arxiv", "math/9904086"],
        "expected_title_fragment": "A Lefschetz (1,1) Theorem for normal projective complex varieties",
        "quotes": ["We prove an analogue of the Lefschetz (1,1) Theorem characterizing cohomology classes of Cartier divisors"],
        "falsifier": "a smooth projective variety with a (1,1) class that is not algebraic",
        "does_not_show": "nothing about codimension 2 and higher, which is where the conjecture is open",
    },
    {
        "id": "hypersurface-assertion",
        "problem": "Hodge Conjecture",
        "claim": "A 2023 arXiv preprint asserts a proof of the Hodge conjecture for smooth projective hypersurfaces.",
        "request": ["arxiv", "2312.09268"],
        "expected_title_fragment": "Hodge conjecture for projective hypersurface",
        "quotes": ["We deduce the Hodge conjecture for smooth projective hypersurfaces"],
        "falsifier": "refereeing or independent replication that fails to reproduce the argument",
        "does_not_show": "whether the argument is correct. Unrefereed assertion, no replication fetched, therefore excluded from evidence",
        "exclude": True,
        "exclude_reason": "unrefereed preprint asserting a solution to an open problem; excluded until independent verification exists",
    },
]

BUILDS = {
    "p_vs_np": ("p_vs_np.json", "P vs NP", P_VS_NP_SPECS),
    "hodge": ("hodge_conjecture.json", "Hodge Conjecture", HODGE_SPECS),
}


def build(name: str) -> int:
    filename, problem, specs = BUILDS[name]
    records = [grade(spec, retrieve(spec["request"])) for spec in specs]
    for spec in specs:
        if "cross_check" in spec:
            records.append(cross_check_record(spec))

    payload = {"problem": problem, "method": "reverse-engineering v2 (TRACE-5)", "built_at": "2026-11-17", "records": records}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / filename
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    usable = sum(1 for r in records if r["status"] == "Q" and not r["excluded_from_evidence"])
    print(json.dumps({"file": str(path.relative_to(ROOT)), "grades": counts, "usable_claims": usable}, indent=2))
    return 0


def validate(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    problems: list[str] = []
    for record in payload["records"]:
        abstract = record["evidence"]["abstract"]
        if record["evidence"]["http_status"] != 200:
            problems.append(f"{record['id']}: non-200 evidence")
        if record["status"] == "Q":
            if not record["quotes"]:
                problems.append(f"{record['id']}: Q with no quote")
            for quote in record["quotes"]:
                if quote not in abstract:
                    problems.append(f"{record['id']}: quote absent from stored abstract")
        if record["status"] == "E" and record["affirmed"]:
            problems.append(f"{record['id']}: existence-only record marked affirmed")
        if record["status"] == "X" and record["affirmed"]:
            problems.append(f"{record['id']}: rejected record marked affirmed")
        if record["status"] not in {"Q", "E", "X"}:
            problems.append(f"{record['id']}: unknown status")
        if record["excluded_from_evidence"] and not record["exclusion_reason"]:
            problems.append(f"{record['id']}: excluded without a reason")
    return problems


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "check"
    if command == "build":
        targets = sys.argv[2:] or list(BUILDS)
        for target in targets:
            build(target)
        raise SystemExit(0)
    path = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DIR / "p_vs_np.json"
    issues = validate(path)
    print(json.dumps({"file": str(path), "valid": not issues, "issues": issues}, indent=2))
    raise SystemExit(0 if not issues else 1)
