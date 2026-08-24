#!/usr/bin/env python3
"""
Barrot Ω — Riemann Hypothesis Research Harvesting

Harvests candidate research metadata from public scholarly feeds, normalizes
evidence, and persists append-safe structured findings.

This subsystem does NOT claim to prove the Riemann Hypothesis. Computational
evidence, conjectures, claims, and established results remain explicitly
separated.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "research" / "riemann_hypothesis_harvest.json"

QUERY = '"Riemann Hypothesis" OR "Riemann zeta function"'
ARXIV_URL = (
    "https://export.arxiv.org/api/query?"
    + urllib.parse.urlencode({
        "search_query": 'all:"Riemann Hypothesis"',
        "start": 0,
        "max_results": 25,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
)

EVIDENCE_CLASSES = {
    "established_result",
    "computational_evidence",
    "published_claim",
    "conjecture_or_hypothesis",
    "barrot_research_lead",
}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def classify_evidence(title: str, summary: str) -> str:
    """Classify evidence conservatively without treating claims as proof."""
    text = f"{title} {summary}".lower()

    # Explicit computational evidence takes precedence.
    if any(x in text for x in (
        "numerical verification",
        "computed zero",
        "computational verification",
        "zeros up to",
    )):
        return "computational_evidence"

    # A counterexample is evidence/claim territory, never automatically proof.
    if "counterexample" in text:
        return "published_claim"

    # Proof/disproof language describes a published claim until independently verified.
    if any(x in text for x in ("proof", "prove", "disproof")):
        return "published_claim"

    # Only classify as conjectural when no stronger claim is present.
    if any(x in text for x in (
        "conjecture", "hypothesis", "heuristic", "speculation"
    )):
        return "conjecture_or_hypothesis"

    return "barrot_research_lead"

def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()

def parse_arxiv_atom(xml: str) -> List[Dict[str, Any]]:
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.S)
    records = []

    for entry in entries:
        def tag(name: str) -> str:
            match = re.search(
                rf"<{name}[^>]*>(.*?)</{name}>", entry, re.S
            )
            return clean(re.sub(r"<[^>]+>", "", match.group(1))) if match else ""

        title = tag("title")
        summary = tag("summary")
        identifier = tag("id")
        published = tag("published")
        authors = [
            clean(re.sub(r"<[^>]+>", "", a))
            for a in re.findall(r"<author>.*?<name>(.*?)</name>.*?</author>", entry, re.S)
        ]

        if not title:
            continue

        records.append({
            "id": identifier,
            "title": title,
            "summary": summary,
            "authors": authors,
            "published": published,
            "source": "arXiv",
            "url": identifier,
            "evidence_class": classify_evidence(title, summary),
            "verification_status": "unverified_candidate",
            "harvested_at": utcnow(),
        })

    return records

def harvest_arxiv() -> List[Dict[str, Any]]:
    request = urllib.request.Request(
        ARXIV_URL,
        headers={"User-Agent": "Barrot-Omega-Riemann-Research/1.0"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return parse_arxiv_atom(response.read().decode("utf-8", errors="replace"))

def load_existing() -> Dict[str, Any]:
    if OUTPUT.exists():
        try:
            return json.loads(OUTPUT.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "domain": "Riemann Hypothesis",
        "schema_version": "1.0",
        "records": [],
    }

def merge_records(existing: List[Dict[str, Any]],
                  incoming: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = {r.get("id") or r.get("url") or r.get("title"): r for r in existing}
    for record in incoming:
        key = record.get("id") or record.get("url") or record.get("title")
        merged[key] = record
    return sorted(
        merged.values(),
        key=lambda r: r.get("published", ""),
        reverse=True,
    )

def run() -> Dict[str, Any]:
    payload = load_existing()
    try:
        harvested = harvest_arxiv()
        source_status = "success"
    except Exception as exc:
        harvested = []
        source_status = f"error: {type(exc).__name__}"

    payload["records"] = merge_records(payload.get("records", []), harvested)
    payload["last_harvested_at"] = utcnow()
    payload["last_source_status"] = source_status
    payload["evidence_policy"] = {
        "rule": (
            "No harvested publication, computational result, conjecture, "
            "or model output is treated as a proof without independent "
            "mathematical validation."
        ),
        "classes": sorted(EVIDENCE_CLASSES),
    }
    payload["statistics"] = {
        "total_records": len(payload["records"]),
        "by_evidence_class": {
            kind: sum(
                1 for r in payload["records"]
                if r.get("evidence_class") == kind
            )
            for kind in sorted(EVIDENCE_CLASSES)
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload

if __name__ == "__main__":
    result = run()
    print(json.dumps(result["statistics"], indent=2))
