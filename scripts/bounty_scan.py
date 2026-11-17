#!/usr/bin/env python3
"""Scan open GitHub issues that state a cash bounty, and grade the claim.

Same rule as the research track: an amount is only Q if it appears literally in the
fetched issue body and the repository is old enough and starred enough that the
bounty is not same-day spam. Amounts on throwaway repos are E at best, and obvious
auto-generated bounty farms are X.

Usage: python3 scripts/bounty_scan.py
Output: data/money/bounties.json
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "money" / "bounties.json"

QUERIES = [
    "is:issue is:open label:bounty",
    "is:issue is:open bounty in:body",
    "is:issue is:open bounty language:Go",
    "is:issue is:open bounty language:Python",
    "is:issue is:open \"USDC\" bounty",
]

AMOUNT = re.compile(r"(?:\$|USD\s?|USDC\s?)([0-9][0-9,]{1,6})")
SPAM_TITLE = ("bounty-watcher", "radar", "[bounty] answer the", "bounty alert")

# Skills this repository can actually demonstrate: Go, Python, CI/workflow repair,
# auditable research tooling.
SKILL_HINTS = ("go ", "golang", "python", "workflow", "ci ", "github action", "test", "cli", "audit")


def gh(args: list[str]) -> dict | list:
    completed = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=90)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip()[:200])
    return json.loads(completed.stdout)


def repo_meta(full_name: str, cache: dict) -> dict:
    if full_name in cache:
        return cache[full_name]
    try:
        data = gh(["api", f"repos/{full_name}", "--jq",
                   "{stars: .stargazers_count, created: .created_at, pushed: .pushed_at, archived: .archived, forks: .forks_count}"])
    except Exception:
        data = {"stars": 0, "created": "", "pushed": "", "archived": True, "forks": 0}
    cache[full_name] = data
    return data


def days_since(iso: str) -> int:
    if not iso:
        return 0
    try:
        then = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return 0
    return (datetime.now(timezone.utc) - then).days


def amount_of(body: str) -> tuple[int | None, str]:
    match = AMOUNT.search(body or "")
    if not match:
        return None, ""
    raw = match.group(0)
    value = int(match.group(1).replace(",", ""))
    return value, raw


def cjk_chars(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def repetitive(text: str) -> float:
    words = text.split()
    return len(set(words)) / len(words) if words else 1.0


def grade(item: dict, meta: dict, amount: int | None) -> tuple[str, str]:
    title = item["title"].lower()
    body = item.get("body") or ""
    if any(marker in title for marker in SPAM_TITLE):
        return "X", "auto-generated bounty feed title"
    # Found by inspection: the only 10k issue was a propaganda dump with a dollar
    # sign in front of it. Age and stars do not catch that; content has to.
    if cjk_chars(body) > 100:
        return "X", f"off-topic body: {cjk_chars(body)} CJK characters, not a task description"
    if repetitive(body) < 0.25 and len(body.split()) > 40:
        return "X", f"stuffed body: unique-word ratio {repetitive(body):.2f}"
    if title.count("bounty") > 2:
        return "X", "keyword-stuffed title"
    if days_since(meta["created"]) < 30 or meta["stars"] < 3:
        return "X", f"repo unproven: {meta['stars']} stars, created {days_since(meta['created'])} days ago"
    if amount is None:
        return "E", "no literal amount in the fetched body"
    if meta["stars"] >= 20 and days_since(meta["created"]) >= 180 and not meta["archived"]:
        return "Q", f"amount literal in body; repo {meta['stars']} stars, {days_since(meta['created'])} days old"
    return "E", f"amount literal, but repo only {meta['stars']} stars / {days_since(meta['created'])} days old"


def main() -> int:
    seen: dict[str, dict] = {}
    cache: dict[str, dict] = {}
    for query in QUERIES:
        try:
            payload = gh(["api", f"search/issues?q={query.replace(' ', '+')}&per_page=30",
                          "--jq", "{total: .total_count, items: [.items[] | {url: .html_url, title, body, number, repo: .repository_url, labels: [.labels[].name], created: .created_at}]}"])
        except Exception as exc:
            print(f"query failed: {query}: {exc}")
            continue
        for item in payload["items"]:
            if item["url"] in seen:
                continue
            full_name = item["repo"].split("/repos/")[-1]
            meta = repo_meta(full_name, cache)
            amount, literal = amount_of((item["title"] or "") + " " + (item["body"] or ""))
            source = "title" if amount_of(item["title"] or "")[0] is not None else ("body" if amount else "")
            status, reason = grade(item, meta, amount)
            lowered = (item["title"] + " " + (item["body"] or "")).lower()
            seen[item["url"]] = {
                "repo": full_name,
                "number": item["number"],
                "title": item["title"],
                "url": item["url"],
                "labels": item["labels"],
                "created": item["created"],
                "amount_usd": amount,
                "amount_literal": literal,
                "amount_source": source,
                "repo_stars": meta["stars"],
                "repo_age_days": days_since(meta["created"]),
                "archived": meta["archived"],
                "skill_match": [hint.strip() for hint in SKILL_HINTS if hint in lowered],
                "status": status,
                "grade_reason": reason,
                "query": query,
            }

    records = sorted(seen.values(), key=lambda r: ({"Q": 0, "E": 1, "X": 2}[r["status"]], -(r["amount_usd"] or 0)))
    grades = {grade: sum(1 for r in records if r["status"] == grade) for grade in ("Q", "E", "X")}
    payload = {
        "built_at": "2026-11-17",
        "queries": QUERIES,
        "records": len(records),
        "grades": grades,
        "records_list": records,
        "disclosure": (
            "A stated amount is not escrow. None of these payouts is verified; only the "
            "literal amount string and the repository age/size are verified."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"records": len(records), "grades": grades,
                      "top": [(r["repo"], r["amount_usd"], r["status"]) for r in records[:8]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
