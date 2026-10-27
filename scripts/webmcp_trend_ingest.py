#!/usr/bin/env python3
"""
BARROT-Ω WEBMCP TREND INGEST — real, minimal, honest.

Tracks public developer discourse about WebMCP / agentic browsing / AI
agent-website interaction, so Barrot's "what tools should we build next"
answers are grounded in real published discourse instead of invented
predictions. Same pattern as frontier_ingest.py: fetch real RSS, dedupe
by URL, append to a separate log. Every entry has a real URL.

Honest expectation going in: prior research this session confirmed real
WebMCP adoption is near-zero as of July 2026, so results here may be
thin. That is itself an honest finding, not a failure of this script.
"""

import json, os, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

KB_DIR = "ping-pongings/knowledge-base"
LOG_PATH = os.path.join(KB_DIR, "webmcp_trend_log.jsonl")

FEEDS = {
    "webmcp_news": [
        "https://news.google.com/rss/search?q=WebMCP+OR+%22Model+Context+Protocol%22+web+when:14d",
    ],
    "agentic_browsing_news": [
        "https://news.google.com/rss/search?q=%22agentic+browsing%22+OR+%22AI+agent+website%22+when:14d",
    ],
    "agent_web_discourse": [
        "https://news.google.com/rss/search?q=%22AI+shopping+agent%22+OR+%22MCP+client%22+adoption+when:14d",
    ],
}


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def parse_rss(raw, source, feed_url, limit=10):
    out = []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return out
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if not title or not link:
            continue
        out.append(
            {
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "source": source,
                "feed": feed_url,
                "title": title[:300],
                "url": link,
                "published": pub,
                "summary": desc[:800],
            }
        )
        if len(out) >= limit:
            break
    return out


def load_seen():
    seen = set()
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            for line in f:
                try:
                    seen.add(json.loads(line)["url"])
                except Exception:
                    pass
    return seen


def main():
    os.makedirs(KB_DIR, exist_ok=True)
    seen = load_seen()
    new, per_source = [], {}
    for source, urls in FEEDS.items():
        for u in urls:
            try:
                raw = fetch(u)
            except Exception as e:
                print(f"fetch failed {u}: {e}")
                continue
            for e in parse_rss(raw, source, u):
                if e["url"] in seen:
                    continue
                seen.add(e["url"])
                new.append(e)
                per_source[source] = per_source.get(source, 0) + 1
    if not new:
        print("No new entries.")
        return
    with open(LOG_PATH, "a") as f:
        for e in new:
            f.write(json.dumps(e) + "\n")
    print(f"Ingested {len(new)} new entries: {per_source}")
    for e in new[:5]:
        print(f"  - [{e['source']}] {e['title'][:70]}")


if __name__ == "__main__":
    main()
