#!/usr/bin/env python3
"""Measure the paid-issue market with the GitHub API (read-only).

Two measurements:
  1. Open issues carrying the `bounty` label: how many state an amount, how many
     link a bounty platform, comment count and age.
  2. Open-to-merge latency for the 100 most recently updated merged pull requests
     in a few public repositories.

Requires `gh` authenticated. Writes JSON. No writes to GitHub, no claiming,
no commenting. Amounts are parsed from the issue title/body with a dollar or USD
regex; an amount that is not written down is not counted.

Usage:
    python3 measure_market.py --out market_measurement.json
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
from datetime import datetime, timezone

SEARCH_QUERY = "label:bounty is:issue is:open"
COUNT_QUERIES = (
    "label:bounty is:issue is:open",
    "algora in:body is:issue is:open",
    '"paid" "pull request" in:body is:issue is:open',
)
DEFAULT_REPOS = ("pallets/flask", "fastapi/fastapi", "encode/httpx")
AMOUNT_PATTERNS = (
    re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)"),
    re.compile(r"([0-9][0-9,]*)\s?(?:USD|usd)"),
)
PLATFORMS = ("algora.io", "opire.dev", "issuehunt.io")
SPAM_MARKERS = (
    "bounty-watcher",
    "bounty alert",
    "bounty plaza",
    "bounty radar",
    "[bounty] answer",
)


def gh(path: str) -> dict:
    proc = subprocess.run(
        ["gh", "api", path], capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh api {path} failed: {proc.stderr.strip()[:300]}")
    return json.loads(proc.stdout)


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_amount(text: str) -> float | None:
    for pattern in AMOUNT_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        try:
            amount = float(match.group(1).replace(",", ""))
        except ValueError:
            continue
        if 1.0 <= amount <= 100_000.0:
            return amount
    return None


def measure_bounties(pages: int, now: datetime) -> dict:
    items: list[dict] = []
    for page in range(1, pages + 1):
        data = gh(f"search/issues?q={SEARCH_QUERY.replace(' ', '+')}&per_page=50&page={page}")
        items.extend(data.get("items", []))
        if len(data.get("items", [])) < 50:
            break

    amounts: list[float] = []
    comments: list[int] = []
    ages_days: list[float] = []
    platform_hits = {name: 0 for name in PLATFORMS}
    with_platform = 0
    spam_like = 0
    for item in items:
        text = f"{item.get('title') or ''}\n{item.get('body') or ''}"
        amount = parse_amount(text)
        if amount is not None:
            amounts.append(amount)
        comments.append(int(item.get("comments", 0)))
        ages_days.append((now - parse_iso(item["created_at"])).total_seconds() / 86400)
        hit = False
        for name in PLATFORMS:
            if name in text:
                platform_hits[name] += 1
                hit = True
        with_platform += int(hit)
        lowered = text.lower()
        spam_like += int(any(marker in lowered for marker in SPAM_MARKERS))

    return {
        "query": SEARCH_QUERY,
        "issues_fetched": len(items),
        "issues_with_stated_amount": len(amounts),
        "issues_with_amount_pct": round(100 * len(amounts) / len(items), 1) if items else None,
        "issues_with_platform_link": with_platform,
        "platform_hits": platform_hits,
        "spam_marker_hits": spam_like,
        "amount_usd": _describe(amounts),
        "comments_median": statistics.median(comments) if comments else None,
        "age_days_median": round(statistics.median(ages_days), 1) if ages_days else None,
        "amounts_are_self_declared": True,
        "escrow_verified": False,
    }


def measure_merge_latency(repos: list[str], now: datetime) -> dict:
    out: dict[str, dict] = {}
    all_hours: list[float] = []
    for repo in repos:
        pulls = gh(f"repos/{repo}/pulls?state=closed&per_page=100&sort=updated&direction=desc")
        hours: list[float] = []
        for pull in pulls:
            if not pull.get("merged_at") or not pull.get("created_at"):
                continue
            hours.append(
                (parse_iso(pull["merged_at"]) - parse_iso(pull["created_at"])).total_seconds()
                / 3600
            )
        hours.sort()
        all_hours.extend(hours)
        out[repo] = {
            "merged_sampled": len(hours),
            "median_hours": round(statistics.median(hours), 2) if hours else None,
            "p75_hours": round(statistics.quantiles(hours, n=4)[2], 2) if len(hours) >= 4 else None,
            "pct_merged_within_2h": round(100 * sum(1 for h in hours if h <= 2) / len(hours), 1)
            if hours
            else None,
        }
    all_hours.sort()
    return {
        "repos": out,
        "pooled": {
            "merged_sampled": len(all_hours),
            "median_hours": round(statistics.median(all_hours), 2) if all_hours else None,
            "pct_merged_within_2h": round(
                100 * sum(1 for h in all_hours if h <= 2) / len(all_hours), 1
            )
            if all_hours
            else None,
        },
        "note": "Open-to-merge latency of the 100 most recently updated merged PRs per "
        "repository. It measures review latency, not contributor effort, and does not "
        "predict any single pull request.",
    }


def _describe(values: list[float]) -> dict:
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "p25": statistics.quantiles(values, n=4)[0] if len(values) >= 4 else None,
        "p75": statistics.quantiles(values, n=4)[2] if len(values) >= 4 else None,
    }


def measure_query_counts(queries: tuple[str, ...]) -> dict:
    counts: dict[str, int | None] = {}
    for query in queries:
        data = gh(f"search/issues?q={query.replace(' ', '+')}&per_page=1")
        counts[query] = data.get("total_count")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=int, default=2)
    parser.add_argument("--repos", nargs="*", default=list(DEFAULT_REPOS))
    parser.add_argument("--out", default="market_measurement.json")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    report = {
        "retrieved_at": now.isoformat().replace("+00:00", "Z"),
        "tool": "measure_market.py",
        "query_counts": measure_query_counts(COUNT_QUERIES),
        "bounties": measure_bounties(args.pages, now),
        "merge_latency": measure_merge_latency(args.repos, now),
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
