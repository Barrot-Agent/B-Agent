#!/usr/bin/env python3
"""Market scan for digital products: fetch competition and demand, rank, do not recall.

Demand and competition are fetched numbers, never estimates:

  competition = GitHub repository count for the niche query
  demand      = npm weekly downloads of the closest comparable package, or a GitHub
                repository count for the adjacent tooling when no package exists

Score = log10(demand + 1) * speed_factor / log10(competition + 10)
  speed_factor = 1.0 for under 4 hours, 0.7 for under 12, 0.4 for longer

A low competition count with high adjacent demand ranks first. Hours are judgment and
labelled as such; every other number below is fetched at build time.

Usage: python3 scripts/market_scan.py
Output: data/money/market.json
"""

from __future__ import annotations

import json
import math
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "money" / "market.json"

PRODUCTS = [
    {
        "id": "evidence-audit-mcp",
        "name": "Evidence Audit MCP",
        "format": "MCP server, source licence plus hosted tier",
        "problem": "agents cite sources without checking that quotes exist or that a DOI is retracted",
        "buyer": "AI engineering teams shipping research features",
        "competition_query": "claims verification",
        "demand_package": "@modelcontextprotocol/sdk",
        "hours": 6,
    },
    {
        "id": "workflow-doctor",
        "name": "Workflow Doctor",
        "format": "CLI plus GitHub Action",
        "problem": "CI failures caused by optional imports and Jekyll-hostile markdown",
        "buyer": "maintainers of Python repos with docs builds",
        "competition_query": "github actions lint",
        "demand_package": "action-validator",
        "hours": 4,
    },
    {
        "id": "trace5-template-pack",
        "name": "TRACE-5 Research Kit",
        "format": "markdown templates, CLI, worked examples",
        "problem": "research notes that cannot be audited or reproduced",
        "buyer": "analysts and technical writers who must show sources",
        "competition_query": "claims verification",
        "demand_package": None,
        "demand_query": "llm eval",
        "hours": 3,
    },
    {
        "id": "retraction-watchlist",
        "name": "Retracted DOI Watchlist",
        "format": "dataset plus refresh script",
        "problem": "pipelines cite retracted papers with no detection",
        "buyer": "research tooling and literature-review products",
        "competition_query": "retraction",
        "demand_package": None,
        "demand_query": "claims verification",
        "hours": 2,
    },
    {
        "id": "mcp-starter-audit",
        "name": "MCP Server Audit Template",
        "format": "template repo, tests, checklist",
        "problem": "MCP servers shipped without startup, refusal or path-escape tests",
        "buyer": "developers publishing MCP servers",
        "competition_query": "mcp server",
        "demand_package": "@modelcontextprotocol/sdk",
        "hours": 5,
    },
]


def gh_count(query: str) -> int:
    url = "search/repositories?q=" + urllib.parse.quote(query) + "&per_page=1"
    completed = subprocess.run(["gh", "api", url, "--jq", ".total_count"], capture_output=True, text=True, timeout=60)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip()[:120])
    return int(completed.stdout.strip())


def npm_downloads(package: str) -> int | None:
    url = f"https://api.npmjs.org/downloads/point/last-week/{package}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Barrot-agent/1.0"}), timeout=30) as fh:
        payload = json.loads(fh.read())
    return payload.get("downloads")


def speed_factor(hours: float) -> float:
    if hours <= 4:
        return 1.0
    if hours <= 12:
        return 0.7
    return 0.4


def main() -> int:
    records = []
    for product in PRODUCTS:
        competition = gh_count(product["competition_query"])
        if product["demand_package"]:
            demand = npm_downloads(product["demand_package"])
            demand_source = f"npm last-week downloads: {product['demand_package']}"
        else:
            demand = gh_count(product["demand_query"])
            demand_source = f"github repository count proxy: {product['demand_query']}"
        score = (math.log10((demand or 1) + 1) * speed_factor(product["hours"])) / math.log10(competition + 10)
        records.append({
            **{k: v for k, v in product.items() if k not in {"competition_query", "demand_query"}},
            "competition_repos": competition,
            "competition_source": f"github repository count: {product['competition_query']}",
            "demand": demand,
            "demand_source": demand_source,
            "score": round(score, 4),
            "status": "Q" if (competition and demand) else "E",
        })

    ranked = sorted(records, key=lambda r: -r["score"])
    for index, record in enumerate(ranked, start=1):
        record["rank"] = index

    payload = {
        "built_at": "2026-11-17",
        "formula": "log10(demand+1) * speed_factor(hours) / log10(competition+10)",
        "disclosure": (
            "Competition and demand are fetched counts, not market size. npm downloads "
            "measure the adjacent ecosystem, not willingness to pay. Hours are estimates."
        ),
        "unreachable_sources": [
            "Product Hunt: needs an API token",
            "Etsy: needs an API key",
            "Gumroad search: client-rendered, no public count",
            "Kaggle: needs credentials",
        ],
        "products": ranked,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"ranked": [(p["rank"], p["name"], p["score"], p["competition_repos"], p["demand"]) for p in ranked]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
