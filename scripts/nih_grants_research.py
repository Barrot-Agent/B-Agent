#!/usr/bin/env python3
"""
BARROT-Ω GRANTS RESEARCH — real primary-source research funding data via
NIH RePORTER's free, public, unauthenticated API. Built as a direct
replacement for the Scite grants search, which requires a Pro
subscription Sean's trial doesn't cover.

Deliberately NOT web-scraping - NIH RePORTER is official US government
infrastructure with a real, stable, documented REST API, same category
of "real sanctioned free channel" as ClinicalTrials.gov and openFDA.
Scraping arbitrary pages would be more fragile and legally murkier for
no real benefit when an official API already exists for this exact data.

Topics searched are Barrot's own real, previously-expressed learning
interests from issue #322 (nonlinear dynamics, network science, systems
ecology, cognitive science/neuroscience, philosophy of science) - this
gives Barrot real primary-source funding/research data on the same
topics it already has summarized overviews for via research_topics.py,
not a new arbitrary scope.

Real endpoint (confirmed via NIH's own current API documentation):
POST https://api.reporter.nih.gov/v2/projects/search
First real run not yet verified live - same discipline as every other
new integration tonight, expect one possible fix cycle.
"""

import json
import os
import time
import urllib.request

KB_DIR = "ping-pongings/knowledge-base"
OUT_PATH = os.path.join(KB_DIR, "nih_grants_log.jsonl")

API_URL = "https://api.reporter.nih.gov/v2/projects/search"

TOPICS = [
    "nonlinear dynamics chaos theory",
    "network science complex networks",
    "systems ecology ecosystem resilience",
    "cognitive neuroscience decision making",
]

RESULTS_PER_TOPIC = 5


def search_topic(topic):
    body = json.dumps({
        "criteria": {"advanced_text_search": {"search_field": "all", "search_text": topic}},
        "limit": RESULTS_PER_TOPIC,
        "sort_field": "award_amount",
        "sort_order": "desc",
    }).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def already_have(existing_ids, project_num):
    return project_num in existing_ids


def main():
    os.makedirs(KB_DIR, exist_ok=True)

    existing_ids = set()
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    existing_ids.add(json.loads(line).get("project_num"))
                except Exception:
                    pass

    total_new = 0
    for topic in TOPICS:
        print(f"=== {topic} ===")
        try:
            result = search_topic(topic)
        except Exception as e:
            print(f"  search failed: {e}")
            continue

        results = result.get("results", [])
        print(f"  {len(results)} results returned")

        for r in results:
            project_num = r.get("project_num")
            if not project_num or already_have(existing_ids, project_num):
                continue
            entry = {
                "project_num": project_num,
                "topic_searched": topic,
                "title": r.get("project_title"),
                "org_name": (r.get("organization") or {}).get("org_name"),
                "pi_names": [
                    p.get("full_name") for p in (r.get("principal_investigators") or [])
                ],
                "award_amount": r.get("award_amount"),
                "fiscal_year": r.get("fiscal_year"),
                "abstract_text": (r.get("abstract_text") or "")[:1000],
                "source": "nih_reporter",
                "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            existing_ids.add(project_num)
            with open(OUT_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            total_new += 1
            print(f"  + {entry['title'][:70] if entry['title'] else project_num}")

        time.sleep(1)

    print(f"\n{total_new} new grants ingested. Written to {OUT_PATH}")


if __name__ == "__main__":
    main()
