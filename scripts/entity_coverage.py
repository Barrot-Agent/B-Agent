#!/usr/bin/env python3
"""
BARROT-Ω ENTITY/TOPIC COVERAGE — cross-references entities extracted from
live XRP/BTC news against the 198 topics already researched in
topics_log.jsonl. Surfaces two real things:
  - entities recurring in news that already have research backing (context)
  - entities recurring in news with NO research backing (a real gap to
    consider for the next research_topics.py batch)
Pure string matching over existing files. No new infrastructure, no API
calls, no new dependencies.
"""

import json
import os
import re
from collections import Counter

KB_DIR = "ping-pongings/knowledge-base"
XRP_LOG = os.path.join(KB_DIR, "log.jsonl")
BTC_LOG = os.path.join(KB_DIR, "log_btc.jsonl")
TOPICS_LOG = os.path.join(KB_DIR, "topics_log.jsonl")
OUT_PATH = os.path.join(KB_DIR, "entity_coverage.json")


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def collect_entities(entries, asset_tag):
    """Returns Counter of entity -> mention count, plus which asset(s)
    each entity appeared under."""
    counts = Counter()
    assets = {}
    for e in entries:
        d = e.get("distill", {})
        for ent in d.get("entities", []):
            ent_norm = ent.strip()
            if not ent_norm:
                continue
            counts[ent_norm] += 1
            assets.setdefault(ent_norm, set()).add(asset_tag)
    return counts, assets


def topic_text_blob(topics):
    """One lowercased blob per topic entry for substring matching."""
    return [
        (t.get("topic", "") + " " + t.get("analysis", "")).lower()
        for t in topics
    ]


def entity_has_topic_coverage(entity, topic_blobs):
    """True if the entity string appears in any researched topic's
    topic+analysis text. Simple case-insensitive substring match -
    intentionally conservative, no fuzzy matching."""
    needle = entity.lower()
    if len(needle) < 3:
        return False  # too short to match meaningfully, avoid false hits
    return any(needle in blob for blob in topic_blobs)


def main():
    xrp_entries = load_jsonl(XRP_LOG)
    btc_entries = load_jsonl(BTC_LOG)
    topics = load_jsonl(TOPICS_LOG)

    if not topics:
        print("No topics_log.jsonl found or empty - nothing to cross-reference against.")
        return

    xrp_counts, xrp_assets = collect_entities(xrp_entries, "XRP")
    btc_counts, btc_assets = collect_entities(btc_entries, "BTC")

    combined_counts = xrp_counts + btc_counts
    combined_assets = {}
    for ent, a in xrp_assets.items():
        combined_assets.setdefault(ent, set()).update(a)
    for ent, a in btc_assets.items():
        combined_assets.setdefault(ent, set()).update(a)

    topic_blobs = topic_text_blob(topics)

    results = []
    for entity, count in combined_counts.most_common():
        has_coverage = entity_has_topic_coverage(entity, topic_blobs)
        results.append(
            {
                "entity": entity,
                "mention_count": count,
                "seen_in": sorted(combined_assets.get(entity, [])),
                "has_topic_research": has_coverage,
            }
        )

    covered = [r for r in results if r["has_topic_research"]]
    gaps = [r for r in results if not r["has_topic_research"]]

    out = {
        "generated_from": {
            "xrp_entries": len(xrp_entries),
            "btc_entries": len(btc_entries),
            "topics_researched": len(topics),
        },
        "summary": {
            "unique_entities_seen": len(results),
            "with_research_coverage": len(covered),
            "research_gaps": len(gaps),
        },
        "entities": results,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Unique entities seen in news: {len(results)}")
    print(f"  With existing topic research coverage: {len(covered)}")
    print(f"  Research gaps (recurring, no coverage):  {len(gaps)}")
    print("\nTop 10 recurring entities with NO research coverage (gap candidates):")
    for r in sorted(gaps, key=lambda x: -x["mention_count"])[:10]:
        print(f"  {r['mention_count']:3d}x  {r['entity']}  [{','.join(r['seen_in'])}]")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
