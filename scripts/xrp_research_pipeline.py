#!/usr/bin/env python3
"""Fetch permitted XRP research feeds and produce a provenance-aware evidence summary.

The pipeline uses public RSS/Atom endpoints, not unrestricted page scraping. It is
rate limited, idempotent by URL, and treats Reddit observations as low-quality
leads rather than verified facts.
"""

import hashlib
import html
import json
import os
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

KB_DIR = Path(os.getenv("BARROT_KB_DIR", "ping-pongings/knowledge-base"))
LOG_PATH = KB_DIR / "xrp_research_log.jsonl"
SUMMARY_PATH = KB_DIR / "xrp_research_summary.json"
WEB_SUMMARY_PATH = Path(os.getenv("BARROT_WEB_DIR", "web")) / "xrp_research_summary.json"
RATE_LIMIT_SECONDS = float(os.getenv("XRP_RESEARCH_INTERVAL", "1.0"))
MAX_PER_FEED = int(os.getenv("XRP_RESEARCH_MAX_PER_FEED", "20"))

FEEDS = {
    "reddit_xrp": ("https://www.reddit.com/r/XRP/.rss", "reddit", 0.35),
    "reddit_crypto": (
        "https://www.reddit.com/r/CryptoCurrency/search.rss?q=XRP&restrict_sr=1",
        "reddit", 0.35,
    ),
    "clarity_act": (
        "https://news.google.com/rss/search?q=%22CLARITY+Act%22+crypto+when%3A30d",
        "news", 0.70,
    ),
    "sbic_japan": (
        "https://news.google.com/rss/search?q=SBIC+Japan+blockchain+payments+when%3A30d",
        "news", 0.70,
    ),
    "xrp_official": (
        "https://news.google.com/rss/search?q=XRP+XRPL+Ripple+when%3A30d",
        "news", 0.70,
    ),
}

QUALITY_BY_SOURCE = {"official": 1.0, "academic": 0.9, "regulator": 0.95, "news": 0.7, "reddit": 0.35}


def fetch(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "Barrot-XRPResearch/1.0 (research feed reader)"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def _text(value):
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def parse_feed(raw, feed_name, feed_url, source, quality):
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return []
    entries = []
    for item in root.iter():
        if item.tag.rsplit("}", 1)[-1] not in {"item", "entry"}:
            continue
        fields = {}
        for child in item:
            fields[child.tag.rsplit("}", 1)[-1]] = _text(child.text)
        link = fields.get("link", "")
        if not link:
            for child in item:
                if child.tag.rsplit("}", 1)[-1] == "link":
                    link = child.attrib.get("href", "")
                    break
        title = fields.get("title", "")
        summary = fields.get("description") or fields.get("summary", "")
        if title and link:
            entries.append({
                "source": source, "feed": feed_name, "feed_url": feed_url,
                "title": title[:300], "summary": summary[:1000], "url": link,
                "published": fields.get("pubDate") or fields.get("published", ""),
                "quality_score": quality,
            })
        if len(entries) >= MAX_PER_FEED:
            break
    return entries


def claim_key(entry):
    words = re.findall(r"[a-z0-9]{4,}", f"{entry['title']} {entry['summary']}".lower())
    ignored = {"about", "after", "could", "from", "have", "into", "that", "this", "with"}
    return hashlib.sha256(" ".join(sorted(set(words) - ignored)).encode()).hexdigest()[:16]


def load_seen():
    seen = set()
    if LOG_PATH.exists():
        for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
            try:
                seen.add(json.loads(line).get("url"))
            except json.JSONDecodeError:
                continue
    return seen


def load_entries():
    entries = []
    if LOG_PATH.exists():
        for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("url"):
                entries.append(entry)
    return entries


def summarize(entries):
    claims = defaultdict(list)
    for entry in entries:
        claims[entry["claim_key"]].append(entry)
    corroborated = []
    conflicts = []
    for key, records in claims.items():
        sources = sorted({record["source"] for record in records})
        if len(sources) > 1:
            corroborated.append({"claim_key": key, "source_count": len(sources), "sources": sources})
        if len(records) > 1 and len(sources) == 1:
            conflicts.append({"claim_key": key, "status": "single-source", "sources": sources})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_count": len(entries),
        "source_counts": {source: sum(e["source"] == source for e in entries)
                          for source in sorted({e["source"] for e in entries})},
        "corroborated_claims": corroborated,
        "uncorroborated_or_conflicting_claims": conflicts,
        "provenance": {
            "curriculum": "data/xrp_study_curriculum.json",
            "pipeline": "scripts/xrp_research_pipeline.py",
            "feeds": "Public RSS/Atom endpoints; Reddit is treated as low-confidence evidence.",
        },
        "limitations": [
            "RSS summaries are leads and may omit context.",
            "Reddit entries are low-confidence user-generated observations.",
            "Claim matching is lexical, not a substitute for expert fact checking.",
        ],
    }


def main():
    KB_DIR.mkdir(parents=True, exist_ok=True)
    seen = load_seen()
    new_entries = []
    last_fetch = 0.0
    for feed_name, (url, source, quality) in FEEDS.items():
        wait = RATE_LIMIT_SECONDS - (time.monotonic() - last_fetch)
        if wait > 0:
            time.sleep(wait)
        try:
            raw = fetch(url)
            last_fetch = time.monotonic()
            for entry in parse_feed(raw, feed_name, url, source, quality):
                if entry["url"] in seen:
                    continue
                seen.add(entry["url"])
                entry["ingested_at"] = datetime.now(timezone.utc).isoformat()
                entry["claim_key"] = claim_key(entry)
                new_entries.append(entry)
        except (OSError, urllib.error.URLError) as exc:
            print(f"fetch failed {feed_name}: {exc}")

    if new_entries:
        with LOG_PATH.open("a", encoding="utf-8") as output:
            for entry in new_entries:
                output.write(json.dumps(entry, ensure_ascii=False) + "\n")
    summary = summarize(load_entries())
    summary["new_entries_this_run"] = len(new_entries)
    rendered = json.dumps(summary, indent=2) + "\n"
    SUMMARY_PATH.write_text(rendered, encoding="utf-8")
    WEB_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEB_SUMMARY_PATH.write_text(rendered, encoding="utf-8")
    print(f"Ingested {len(new_entries)} new entries; summary written to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
