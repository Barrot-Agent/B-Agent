#!/usr/bin/env python3
"""Harvest public GitHub Actions workflows, gate them by licence, grade by evidence.

Rules:
  * only MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, CC0-1.0, Unlicense are usable
  * GPL/AGPL/LGPL, no licence, or NOASSERTION -> BLOCKED-LICENSE, nothing is pulled
  * a workflow is Q only if its YAML was fetched and parsed with name, on and jobs

Nothing is cloned. Only workflow YAML files under .github/workflows are read.

Usage: python3 scripts/workflow_harvest.py
Output: data/harvest/workflows.json
"""

from __future__ import annotations

import base64
import json
import subprocess
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "harvest" / "workflows.json"

QUERIES = [
    "topic:mcp-server stars:>800",
    "topic:ai-agent stars:>2000",
    "topic:automation stars:>3000",
    "github actions auto fix in:readme stars:>500",
    "topic:scraper stars:>2000",
    "topic:trading-bot stars:>1500",
]

ALLOWED = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "CC0-1.0", "Unlicense", "0BSD"}
MAX_REPOS_PER_QUERY = 6
MAX_WORKFLOWS_PER_REPO = 3


def gh(args: list[str]) -> str:
    completed = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=90)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip()[:160])
    return completed.stdout


def search(query: str) -> list[dict]:
    payload = json.loads(gh([
        "api",
        f"search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page={MAX_REPOS_PER_QUERY}",
        "--jq", "{items: [.items[] | {full_name, html_url, stars: .stargazers_count, description, archived}]}",
    ]))
    return payload["items"]


def license_of(full_name: str) -> str:
    try:
        return gh(["api", f"repos/{full_name}", "--jq", ".license.spdx_id // \"NONE\""]).strip()
    except Exception:
        return "NONE"


def workflow_files(full_name: str) -> list[dict]:
    try:
        raw = gh(["api", f"repos/{full_name}/contents/.github/workflows"])
        entries = json.loads(raw)
    except Exception:
        return []
    if isinstance(entries, dict):  # error payload
        return []
    return [e for e in entries if e.get("type") == "file" and e["name"].endswith((".yml", ".yaml"))][:MAX_WORKFLOWS_PER_REPO]


def workflow_yaml(download_url: str) -> str | None:
    try:
        return base64.b64decode(gh(["api", download_url.replace("https://api.github.com/", ""), "--jq", ".content"])).decode("utf-8", "ignore")
    except Exception:
        return None


def parse_simple(text: str) -> dict:
    """BaseLoader keeps `on` a string instead of turning it into True."""
    import yaml

    loaded = yaml.load(text, Loader=yaml.BaseLoader) or {}
    return loaded if isinstance(loaded, dict) else {}


def classify(text: str) -> list[str]:
    lowered = text.lower()
    tags = []
    for tag, needles in {
        "test": ("pytest", "npm test", "go test", "cargo test", "unittest"),
        "lint": ("lint", "eslint", "ruff", "flake8", "golangci"),
        "release": ("release", "publish", "upload", "pypi", "npm publish", "gh release"),
        "docker": ("docker/build-push", "docker build", "buildx"),
        "deploy": ("deploy", "pages", "vercel", "flyctl", "kubectl"),
        "security": ("codeql", "trivy", "dependabot", "semgrep", "bandit"),
        "schedule": ("schedule", "cron"),
        "summarize": ("summar", "openai", "llm", "gpt"),
        "scrape": ("scrape", "crawl", "playwright", "selenium"),
    }.items():
        if any(needle in lowered for needle in needles):
            tags.append(tag)
    return tags


def main() -> int:
    repos: dict[str, dict] = {}
    for query in QUERIES:
        try:
            for item in search(query):
                repos.setdefault(item["full_name"], {**item, "queries": []})
                repos[item["full_name"]]["queries"].append(query)
        except Exception as exc:
            print(f"search failed: {query}: {exc}")

    records = []
    blocked = []
    for full_name, meta in repos.items():
        spdx = license_of(full_name)
        entry = {
            "repo": full_name,
            "url": meta["html_url"],
            "stars": meta["stars"],
            "description": meta["description"],
            "license": spdx,
            "queries": meta["queries"],
            "workflows": [],
        }
        if spdx not in ALLOWED:
            entry["license_status"] = "BLOCKED-LICENSE"
            blocked.append(entry)
            records.append(entry)
            continue
        entry["license_status"] = "ALLOWED"
        for item in workflow_files(full_name):
            text = workflow_yaml(item["url"])
            if text is None:
                entry["workflows"].append({"file": item["name"], "status": "E", "reason": "fetch failed"})
                continue
            try:
                parsed = parse_simple(text)
            except Exception as exc:
                entry["workflows"].append({"file": item["name"], "status": "X", "reason": f"unparseable: {exc}"})
                continue
            has = all(key in parsed for key in ("name", "on", "jobs"))
            entry["workflows"].append({
                "file": item["name"],
                "path": item["path"],
                "html_url": item["html_url"],
                "status": "Q" if has else "E",
                "reason": "name, on and jobs present" if has else "missing one of name/on/jobs",
                "trigger": parsed.get("on") if isinstance(parsed.get("on"), str) else str(parsed.get("on"))[:120],
                "job_count": len(parsed.get("jobs") or {}),
                "tags": classify(text),
                "bytes": len(text),
            })
        records.append(entry)

    graded = {"Q": 0, "E": 0, "X": 0}
    for record in records:
        for workflow in record["workflows"]:
            graded[workflow["status"]] += 1

    payload = {
        "built_at": "2026-11-17",
        "queries": QUERIES,
        "allowed_licenses": sorted(ALLOWED),
        "repos_scanned": len(records),
        "workflows": sum(len(r["workflows"]) for r in records),
        "grades": graded,
        "blocked_license": len(blocked),
        "records": records,
        "disclosure": (
            "A workflow is quoted from its own YAML. Suitability for money is a separate "
            "judgment made in docs/money/TRANSMUTE.md, not a property of the file."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "repos": payload["repos_scanned"],
        "workflows": payload["workflows"],
        "grades": graded,
        "blocked_license": payload["blocked_license"],
        "blocked_repos": [b["repo"] for b in blocked][:12],
        "allowed_repos": [r["repo"] for r in records if r["license_status"] == "ALLOWED"][:12],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
