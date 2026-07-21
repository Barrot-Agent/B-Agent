#!/usr/bin/env python3
"""
Cross-source corroboration pass.
Reads the knowledge base, groups entries by shared topic keywords,
and reports where sources agree, where they conflict, and where a
topic has coverage from only one source (a gap).
Read-only -- writes a report entry back, never rewrites existing entries.
"""
import json, sys, re
from collections import defaultdict

LOG = "ping-pongings/knowledge-base/log.jsonl"

TOPIC_KEYWORDS = {
    "settlement": ["settlement", "cross-border", "correspondent banking", "swift"],
    "cbdc": ["cbdc", "central bank digital"],
    "liquidity": ["liquidity", "market microstructure", "price discovery"],
    "sentiment": ["sentiment", "twitter", "fear and greed", "social"],
    "consensus": ["consensus protocol", "byzantine", "validator", "xrpl"],
}

def load_entries():
    entries = []
    with open(LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries

def classify(entry):
    text = (entry.get("title", "") + " " + entry.get("summary", "") + " " + entry.get("final", "")).lower()
    hits = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            hits.append(topic)
    return hits

def main():
    entries = load_entries()
    by_topic = defaultdict(lambda: defaultdict(list))
    for e in entries:
        source = e.get("source", "unknown")
        for topic in classify(e):
            by_topic[topic][source].append(e.get("title", "")[:80])

    report_lines = []
    all_sources = set()
    for e in entries:
        all_sources.add(e.get("source", "unknown"))

    for topic, sources in by_topic.items():
        covered_by = set(sources.keys())
        missing = all_sources - covered_by
        report_lines.append(f"TOPIC: {topic}")
        for src, titles in sources.items():
            report_lines.append(f"  {src}: {len(titles)} entries")
        if missing:
            report_lines.append(f"  GAP -- no coverage from: {', '.join(sorted(missing))}")
        report_lines.append("")

    report = "\n".join(report_lines)
    print(report)

    entry = {
        "source": "corroboration_report",
        "title": "Cross-source topic coverage report",
        "summary": report[:2000],
        "topics_covered": list(by_topic.keys()),
        "sources_seen": sorted(all_sources),
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print("Appended corroboration_report entry to", LOG)

if __name__ == "__main__":
    main()
