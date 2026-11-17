#!/usr/bin/env python3
"""Find accessible paid GitHub issues and write PAID-ISSUES.md.

Read-only on purpose. This script never comments, never claims, never labels. It
searches, filters, scores, and writes two files:

  PAID-ISSUES.md            top 10, status READY, quoted from the issue itself
  data/money/paid_issues.json  machine record with the same rows

Filters: amount > $50 literal in title or body, issue open, repository pushed within
120 days and not archived, and at least one skill keyword (Go, Python, workflow,
GitHub Actions, MCP, audit, CLI, test).

Accessibility score = amount_usd / difficulty, where difficulty comes from labels:
  1.0  good first issue, docs, documentation, typo
  2.0  bug, test, tests
  3.0  feature, enhancement, refactor
  2.5  anything else
Higher score = more money for less ambiguity. The heuristic is stated so the reader
can reject it.

Usage: python3 scripts/paid_issue_hunter.py [--limit 10]
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = ROOT / "PAID-ISSUES.md"
RECORD = ROOT / "data" / "money" / "paid_issues.json"

QUERIES = [
    "label:bounty",
    "bounty in:body",
    "algora in:body",
    "polar.sh in:body",
    "issuehunt in:body",
    "gitcoin in:body",
    "opire in:body",
]

SKILLS = (
    "go ", "golang", "python", "workflow", "github action", "mcp",
    "audit", "cli", "pytest", "test",
)

AMOUNT = re.compile(r"(?:\$|USD\s?|USDC\s?)([0-9][0-9,]{0,6}(?:\.[0-9]{1,2})?)")
# An amount is only a bounty if a bounty word sits in the same sentence and the
# number is plausible for open-source work. The first run of this script picked up
# $600,000 from a funding table; these two rules are the fix.
BOUNTY_WORD = re.compile(r"bount(y|ies)|reward|payout|escrow|prize", re.IGNORECASE)
MAX_PLAUSIBLE = 50_000
MIN_STARS = 20
SPAM_TITLE = ("bounty-watcher", "radar", "bounty alert", "bounty plaza", "[bounty] answer")
# Repositories whose whole purpose is to resell or farm bounties. They are not
# accessible work; they are listings of uncertain escrow.
DENY_REPOS = {"zhangjiayang6835-cyber/bounty-plaza"}
# Most real bounties keep the amount on the platform, not in the issue text. Those
# rows are listed with amount UNKNOWN, never invented.
#
# A platform mention is not a bounty. The first run of this rule matched a bug
# template that says "consider sponsoring this issue via issuehunt.io/r/owner/repo"
# and a documentation link. Both are repo-level or docs-level, not issue-level. Only
# an issue-specific URL counts, and only the shapes below are accepted.
PLATFORM_PATTERNS = (
    re.compile(r"https?://algora\.io/[\w.-]+/[\w.-]+/issue/\d+"),
    re.compile(r"https?://issuehunt\.io/r/[\w.-]+/[\w.-]+/issues/\d+"),
    re.compile(r"https?://opire\.dev/bounty/[\w.-]+"),
    re.compile(r"https?://polar\.sh/[\w.-]+/[\w.-]+/issues?/\d+"),
)


def full_name_from(item: dict) -> str:
    return item["repo"].split("/repos/")[-1]


DIFFICULTY = (
    (("good first issue", "docs", "documentation", "typo"), 1.0),
    (("bug", "test", "tests"), 2.0),
    (("feature", "enhancement", "refactor"), 3.0),
)


def gh(args: list[str]) -> str:
    completed = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=120)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip()[:200])
    return completed.stdout


def search(query: str) -> list[dict]:
    payload = json.loads(gh([
        "api",
        f"search/issues?q={query.replace(' ', '+')}+is:issue+is:open&per_page=40"
        "&sort=created&order=desc&advanced_search=true",
        "--jq",
        "{items: [.items[] | {url: .html_url, title, body, number, repo: .repository_url,"
        " labels: [.labels[].name], created: .created_at, comments: .comments}]}",
    ]))
    return payload["items"]


def repo_meta(full_name: str, cache: dict) -> dict:
    if full_name in cache:
        return cache[full_name]
    try:
        cache[full_name] = json.loads(gh([
            "api", f"repos/{full_name}", "--jq",
            "{stars: .stargazers_count, pushed: .pushed_at, archived: .archived, open_issues: .open_issues_count}",
        ]))
    except Exception:
        cache[full_name] = {"stars": 0, "pushed": "", "archived": True, "open_issues": 0}
    return cache[full_name]


def platform_bounty_link(body: str) -> str:
    """Return an issue-specific bounty URL, or empty. Repo-level and docs links are noise."""
    for pattern in PLATFORM_PATTERNS:
        match = pattern.search(body)
        if match:
            return match.group(0)
    return ""


def amount_of(text: str) -> int | None:
    best = None
    for line in text.splitlines():
        if not BOUNTY_WORD.search(line):
            continue
        for match in AMOUNT.finditer(line):
            value = float(match.group(1).replace(",", ""))
            if 1 <= value <= MAX_PLAUSIBLE:
                best = max(best or 0, int(value))
    return best


def difficulty_of(labels: list[str]) -> float:
    lowered = " ".join(labels).lower()
    for needles, value in DIFFICULTY:
        if any(needle in lowered for needle in needles):
            return value
    return 2.5


def quote_for(text: str) -> str:
    for line in text.splitlines():
        if AMOUNT.search(line):
            return " ".join(line.split())[:160]
    return ""


def active(meta: dict) -> bool:
    if meta["archived"] or meta["stars"] < MIN_STARS:
        return False
    # Thousands of open issues on a small repo is a queue, not a task board.
    if meta.get("open_issues", 0) > 400:
        return False
    try:
        pushed = datetime.fromisoformat(meta["pushed"].replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(timezone.utc) - pushed < timedelta(days=120)


def collect(limit: int) -> list[dict]:
    seen: dict[str, dict] = {}
    cache: dict[str, dict] = {}
    for query in QUERIES:
        try:
            items = search(query)
        except Exception as exc:
            print(f"query failed: {query}: {exc}")
            continue
        for item in items:
            url = item["url"]
            if url in seen:
                continue
            title = (item["title"] or "").lower()
            if full_name_from(item) in DENY_REPOS:
                continue
            if any(marker in title for marker in SPAM_TITLE):
                continue
            body = item["body"] or ""
            amount = amount_of(item["title"] + "\n" + body)
            platform_link = platform_bounty_link(body)
            if amount is None and not platform_link:
                continue
            labels = item["labels"]
            difficulty = difficulty_of(labels)
            full_name = item["repo"].split("/repos/")[-1]
            meta = repo_meta(full_name, cache)
            if not active(meta):
                continue
            haystack = (item["title"] + " " + body).lower()
            skills = sorted({skill.strip() for skill in SKILLS if skill in haystack})
            if not skills:
                continue
            seen[url] = {
                "url": url,
                "title": item["title"],
                "repo": full_name,
                "number": item["number"],
                "amount_usd": amount,
                "platform_link": platform_link,
                "labels": labels,
                "skills": skills,
                "difficulty": difficulty,
                "score": round(amount / difficulty, 2) if amount else None,
                "stars": meta["stars"],
                "last_push": meta["pushed"][:10],
                "quote": quote_for(item["title"] + "\n" + body),
                "status": "READY" if amount else "READY-UNPRICED",
            }
    priced = sorted((r for r in seen.values() if r["amount_usd"]), key=lambda r: -r["score"])
    unpriced = sorted((r for r in seen.values() if not r["amount_usd"]), key=lambda r: -r["stars"])
    return (priced + unpriced)[:limit]


def render(rows: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Paid issues: READY, never claimed",
        "",
        f"Last run: {now}. Schedule: every 6 hours, indefinitely, plus manual dispatch.",
        "",
        "Rules enforced by `scripts/paid_issue_hunter.py`:",
        "",
        "- read-only: no comment, no claim, no label, no assignment",
        "- amount must sit in the same line as a bounty word, exceed $50 and not exceed $50,000",
        "- repository must be active: pushed within 120 days, not archived, at least 20 stars",
        "- at least one skill keyword must appear: Go, Python, workflow, Actions, MCP, audit, CLI, test",
        "- a platform link counts only if it is issue-specific; repo-level sponsor links and docs links are noise",
        "- score = amount / difficulty, difficulty from labels (docs 1.0, bug 2.0, feature 3.0, else 2.5)",
        "",
        f"Rows: {len(rows)}. Every row is READY. Nothing here is claimed or verified escrow.",
        "",
    ]
    priced = [row for row in rows if row["amount_usd"]]
    unpriced = [row for row in rows if not row["amount_usd"]]
    if not rows:
        lines += ["No issue passed the filters this run. That is a result, not a failure.", ""]
    if priced:
        lines += [
            "## Priced by the issue text",
            "",
            "| # | Issue | Bounty | Score | Skills | Difficulty | Repo stars | Quote |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for index, row in enumerate(priced, start=1):
            quote = row["quote"].replace("|", "\\|")
            lines.append(
                f"| {index} | [{row['repo']}#{row['number']}]({row['url']}) | ${row['amount_usd']} "
                f"| {row['score']} | {', '.join(row['skills'][:3])} | {row['difficulty']} "
                f"| {row['stars']} | {quote} |"
            )
        lines.append("")
    if unpriced:
        lines += [
            "## Platform-linked, amount not in the text",
            "",
            "The body links a bounty platform but states no amount. Amount is UNKNOWN and",
            "is not guessed. These are candidates to open by hand, not priced work.",
            "",
            "| # | Issue | Platform | Skills | Difficulty | Repo stars |",
            "|---|---|---|---|---|---|",
        ]
        for index, row in enumerate(unpriced, start=1):
            lines.append(
                f"| {index} | [{row['repo']}#{row['number']}]({row['url']}) | {row['platform_link']} "
                f"| {', '.join(row['skills'][:3])} | {row['difficulty']} | {row['stars']} |"
            )
        lines.append("")
    lines += [
        "## What this file does not claim",
        "",
        "- A stated bounty is not escrow. None of these payouts was verified.",
        "- No issue was claimed, commented on, or started by the automation.",
        "- Approval to start any row must come from the user.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    import sys

    limit = 10
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    rows = collect(limit)
    MARKDOWN.write_text(render(rows), encoding="utf-8")
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "queries": QUERIES,
        "limit": limit,
        "rows": rows,
        "status_values": sorted({row["status"] for row in rows}),
        "mutations_performed": 0,
    }, indent=2), encoding="utf-8")
    print(json.dumps({
        "rows": len(rows),
        "top": [(row["repo"], row["amount_usd"], row["score"]) for row in rows[:5]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
