#!/usr/bin/env python3
"""
BARROT-Ω ENTITY CO-OCCURRENCE — finds which named entities appear together
in the same news item across both XRP and BTC pipelines. Pure counting over
existing distilled entries. No new infrastructure, no API calls.
"""

import json
import os
from collections import Counter
from itertools import combinations

KB_DIR = "ping-pongings/knowledge-base"
XRP_LOG = os.path.join(KB_DIR, "log.jsonl")
BTC_LOG = os.path.join(KB_DIR, "log_btc.jsonl")
OUT_PATH = os.path.join(KB_DIR, "entity_cooccurrence.json")


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


def main():
    xrp_entries = load_jsonl(XRP_LOG)
    btc_entries = load_jsonl(BTC_LOG)
    all_entries = [(e, "XRP") for e in xrp_entries] + [(e, "BTC") for e in btc_entries]

    pair_counts = Counter()
    pair_context = {}

    for e, asset in all_entries:
        d = e.get("distill", {})
        ents = sorted(set(x.strip() for x in d.get("entities", []) if x.strip()))
        if len(ents) < 2:
            continue
        for a, b in combinations(ents, 2):
            pair_counts[(a, b)] += 1
            pair_context.setdefault((a, b), []).append(
                {"title": e.get("title", "")[:100], "asset": asset}
            )

    results = []
    for (a, b), count in pair_counts.most_common():
        examples = pair_context[(a, b)][:2]
        results.append(
            {
                "entity_a": a,
                "entity_b": b,
                "cooccurrence_count": count,
                "example_headlines": examples,
            }
        )

    out = {
        "generated_from": {"xrp_entries": len(xrp_entries), "btc_entries": len(btc_entries)},
        "unique_pairs_found": len(results),
        "pairs": results,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Unique entity pairs found: {len(results)}")
    print("\nTop 10 co-occurring entity pairs:")
    for r in results[:10]:
        print(f"  {r['cooccurrence_count']:3d}x  {r['entity_a']} <-> {r['entity_b']}")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
