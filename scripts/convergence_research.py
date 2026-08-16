#!/usr/bin/env python3
"""Bounded, provenance-preserving convergence research.

This process is deliberately read-only with respect to source systems. It
creates review reports only; a human must approve any dependency, code, data,
or deployment change suggested by a report.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "convergence_sources.json"
KB = ROOT / "ping-pongings" / "knowledge-base"
REPORTS = KB / "convergence_reports.jsonl"
AUDIT = KB / "convergence_audit.jsonl"
MATH_STATUSES = {"open", "solved", "partial", "disproved", "speculative", "unknown"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                if line.strip():
                    rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def repo_text() -> str:
    names = []
    for directory in ("barrot_agent", "scripts", "data", "apex_lattice", "tests"):
        path = ROOT / directory
        if path.exists():
            names.extend(str(p.relative_to(ROOT)) for p in path.rglob("*") if p.is_file())
    return " ".join(names).lower()


def github_snapshot(full_name: str, token: str = "") -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "B-Agent-convergence-research",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(
        f"https://api.github.com/repos/{full_name}",
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)
    return {
        "full_name": data.get("full_name", full_name),
        "html_url": data.get("html_url", f"https://github.com/{full_name}"),
        "description": data.get("description") or "",
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "archived": bool(data.get("archived", False)),
        "license": (data.get("license") or {}).get("spdx_id"),
        "updated_at": data.get("updated_at"),
        "default_branch": data.get("default_branch"),
    }


def rank_repository(source: dict[str, Any], snapshot: dict[str, Any], internal: str) -> dict[str, Any]:
    text = " ".join(
        [source.get("domain", ""), source.get("full_name", ""), snapshot.get("description", "")]
        + source.get("keywords", [])
    ).lower()
    matches = sorted({word for word in source.get("keywords", []) if word.lower() in internal})
    score = min(100, len(matches) * 12 + min(30, int(snapshot.get("stars", 0)) // 10000))
    if snapshot.get("archived"):
        score = max(0, score - 40)
    return {
        "candidate": source["full_name"],
        "url": snapshot["html_url"],
        "domain": source.get("domain"),
        "license": snapshot.get("license") or source.get("license") or "unknown",
        "maintenance": {"updated_at": snapshot.get("updated_at"), "archived": snapshot.get("archived")},
        "internal_matches": matches,
        "integration_targets": source.get("integration_targets", []),
        "impact_score": score,
        "evidence": {
            "description": snapshot.get("description", ""),
            "stars": snapshot.get("stars", 0),
            "forks": snapshot.get("forks", 0),
        },
        "recommendation": "review" if score >= 20 and not snapshot.get("archived") else "monitor",
        "approval_required": True,
    }


def normalize_math_status(value: str) -> str:
    text = re.sub(r"[*_]", "", str(value or "")).strip().lower()
    if "solved" in text or "proved" in text:
        return "solved"
    if "disprov" in text or "counterexample" in text:
        return "disproved"
    if "partial" in text:
        return "partial"
    if "speculat" in text or "unverified" in text:
        return "speculative"
    if "open" in text or "unsolved" in text:
        return "open"
    return "unknown"


def validate_math_status(problems: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    for problem in problems.get("problems", []):
        declared = normalize_math_status(problem.get("official_status", ""))
        if declared not in MATH_STATUSES:
            declared = "unknown"
        findings.append(
            {
                "name": problem.get("name", "unnamed problem"),
                "status": declared,
                "status_source": "data/millennium_problems_unified.json",
                "claim_hash": hashlib.sha256(
                    f"{problem.get('name')}|{declared}".encode()
                ).hexdigest()[:16],
                "warning": (
                    "Treat as historical/solved; do not present as open."
                    if declared == "solved"
                    else None
                ),
            }
        )
    return findings


def source_claims() -> list[dict[str, Any]]:
    claims = []
    for row in load_jsonl(KB / "topics_log.jsonl")[-50:]:
        claims.append(
            {
                "source": row.get("source"),
                "topic": row.get("topic"),
                "claim": row.get("analysis", "")[:500],
                "url": row.get("url"),
            }
        )
    for row in load_jsonl(KB / "frontier_log.jsonl")[-50:]:
        claims.append(
            {
                "source": row.get("source"),
                "topic": row.get("title"),
                "claim": row.get("summary", "")[:500],
                "url": row.get("url"),
            }
        )
    return claims


def corroborate(reports: list[dict[str, Any]], claims: list[dict[str, Any]]) -> dict[str, Any]:
    indexed = {}
    for claim in claims:
        words = set(re.findall(r"[a-z0-9]{5,}", claim.get("claim", "").lower()))
        for word in words:
            indexed.setdefault(word, set()).add(claim.get("source", "unknown"))
    corroborated = []
    for report in reports:
        words = set(re.findall(r"[a-z0-9]{5,}", report.get("domain", "").lower()))
        sources = sorted({source for word in words for source in indexed.get(word, set())})
        corroborated.append({"candidate": report["candidate"], "supporting_sources": sources})
    return {"method": "normalized claim-term overlap", "matches": corroborated}


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    config = load_json(CONFIG)
    internal = repo_text()
    reports, failures = [], []
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN", "")
    for source in config.get("github_repositories", [])[: config.get("max_github_repositories", 12)]:
        try:
            reports.append(
                rank_repository(source, github_snapshot(source["full_name"], token), internal)
            )
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            failures.append({"source": source["full_name"], "error": str(exc)[:300]})

    problems = validate_math_status(load_json(ROOT / "data" / "millennium_problems_unified.json"))
    claims = source_claims()
    report = {
        "generated_at": now(),
        "schema_version": 1,
        "bounded": True,
        "approval_required": True,
        "repositories": reports,
        "mathematical_status": problems,
        "corroboration": corroborate(reports, claims),
        "failures": failures,
        "source_registry": str(CONFIG.relative_to(ROOT)),
        "next_action": "Human review only; no automatic adoption or mutation.",
    }
    append_jsonl(REPORTS, [report])
    append_jsonl(
        AUDIT,
        [
            {
                "timestamp": report["generated_at"],
                "report_hash": hashlib.sha256(
                    json.dumps(report, sort_keys=True).encode()
                ).hexdigest(),
                "repositories_seen": len(reports),
                "failures": len(failures),
                "claims_cross_checked": len(claims),
            }
        ],
    )
    print(f"Wrote convergence report: {len(reports)} repositories, {len(failures)} failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
