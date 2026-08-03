#!/usr/bin/env python3
"""
BARROT-Ω WEBMCP MONETIZATION ENRICHMENT — adds real market-validation
signals to candidate WebMCP tool ideas (from webmcp_trend_summary.json),
using APIs with no usage restrictions:
- GitHub repo search (real stars/forks for existing similar projects)
- NPM registry search (real package popularity for existing similar tools)

Deliberately excludes:
- Product Hunt: real API exists but its own terms explicitly disallow
  commercial use without prior permission - Sean is emailing to request
  this; do not build against it until/unless that's granted.
- PyPI: no official free-text search API exists (only exact-package-name
  lookup), so it can't answer "does something like this already exist."
- Google Trends: official API is still application-gated alpha, not
  generally available; the free unofficial route was deprecated in 2025.

This is a real signal, not a definitive one: existing GitHub/npm
activity suggests the underlying idea has real-world traction, but
absence of results doesn't mean an idea is bad - just that it hasn't
been built as open-source software yet, which says nothing about
demand for a hosted/paid version.
"""

import json
import os
import time
import urllib.parse
import urllib.request

KB_DIR = "ping-pongings/knowledge-base"
SUMMARY_PATH = os.path.join(KB_DIR, "webmcp_trend_summary.json")
OUT_PATH = os.path.join(KB_DIR, "webmcp_monetization_signals.json")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def github_search(query):
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode({
        "q": query, "sort": "stars", "order": "desc", "per_page": 3
    })
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def npm_search(query):
    url = "https://registry.npmjs.org/-/v1/search?" + urllib.parse.urlencode({
        "text": query, "size": 3
    })
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def enrich_candidate(idea_text):
    signals = {"github": [], "npm": []}

    try:
        gh = github_search(idea_text)
        for item in gh.get("items", [])[:3]:
            signals["github"].append({
                "name": item.get("full_name"),
                "stars": item.get("stargazers_count"),
                "forks": item.get("forks_count"),
                "url": item.get("html_url"),
            })
    except Exception as e:
        signals["github_error"] = str(e)

    try:
        npm = npm_search(idea_text)
        for obj in npm.get("objects", [])[:3]:
            pkg = obj.get("package", {})
            score = obj.get("score", {}).get("detail", {})
            signals["npm"].append({
                "name": pkg.get("name"),
                "description": pkg.get("description"),
                "popularity_score": score.get("popularity"),
                "url": pkg.get("links", {}).get("npm"),
            })
    except Exception as e:
        signals["npm_error"] = str(e)

    return signals


def main():
    if not os.path.exists(SUMMARY_PATH):
        print("No webmcp_trend_summary.json found - nothing to enrich.")
        return

    with open(SUMMARY_PATH) as f:
        summary = json.load(f)

    ideas = summary.get("ranked_candidate_tool_ideas", [])
    if not ideas:
        print("No candidate tool ideas to enrich.")
        return

    enriched = []
    for idea in ideas:
        name = idea["candidate_tool_idea"]
        print(f"Enriching: {name}")
        signals = enrich_candidate(name)
        gh_total_stars = sum(g.get("stars", 0) or 0 for g in signals["github"])
        npm_hit_count = len(signals["npm"])
        print(f"  GitHub: {len(signals['github'])} similar repos, {gh_total_stars} total stars")
        print(f"  NPM: {npm_hit_count} similar packages found")
        enriched.append({
            "candidate_tool_idea": name,
            "times_surfaced_in_discourse": idea.get("times_surfaced"),
            "monetization_signals": signals,
            "note": (
                "Real GitHub/npm activity for similar existing projects - "
                "a signal of real-world traction, not a definitive verdict. "
                "Product Hunt and Google Trends excluded - see script "
                "docstring for why."
            ),
        })
        time.sleep(1)

    out = {
        "generated_from": f"{len(ideas)} candidate ideas from webmcp_trend_summary.json",
        "enriched_candidates": enriched,
    }
    os.makedirs(KB_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"\nEnriched {len(enriched)} candidates. Written to {OUT_PATH}")


if __name__ == "__main__":
    main()
