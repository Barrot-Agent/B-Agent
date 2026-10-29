#!/usr/bin/env python3
"""Entity co-occurrence with global descriptive and asset-scoped weighted views."""
import json
import os
from collections import Counter, defaultdict
from itertools import combinations

KB_DIR = "ping-pongings/knowledge-base"
XRP_LOG = os.path.join(KB_DIR, "log.jsonl")
BTC_LOG = os.path.join(KB_DIR, "log_btc.jsonl")
OUT_PATH = os.path.join(KB_DIR, "entity_cooccurrence.json")
ASSET_RELEVANCE_FIELD = {"XRP": "xrp_relevance", "BTC": "btc_relevance"}


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except (json.JSONDecodeError, TypeError):
                continue
    return out


def relevance_weight(distill, field):
    try:
        return max(0.0, float(distill.get(field, 0) or 0))
    except (TypeError, ValueError):
        return 0.0


def build_cooccurrence(xrp_entries, btc_entries):
    all_entries = [(entry, "XRP") for entry in xrp_entries] + [(entry, "BTC") for entry in btc_entries]
    pair_counts = Counter()
    pair_context = defaultdict(list)
    asset_counts = {asset: Counter() for asset in ASSET_RELEVANCE_FIELD}
    asset_weights = {asset: defaultdict(float) for asset in ASSET_RELEVANCE_FIELD}
    asset_context = {asset: defaultdict(list) for asset in ASSET_RELEVANCE_FIELD}

    for entry, asset in all_entries:
        distill = entry.get("distill", {})
        entities = sorted({value.strip() for value in distill.get("entities", []) if isinstance(value, str) and value.strip()})
        if len(entities) < 2:
            continue
        weight = relevance_weight(distill, ASSET_RELEVANCE_FIELD[asset])
        for pair in combinations(entities, 2):
            title = entry.get("title", "")[:100]
            pair_counts[pair] += 1
            if len(pair_context[pair]) < 2:
                pair_context[pair].append({"title": title, "asset": asset, "pipeline_asset": asset})
            if weight <= 0:
                continue
            asset_counts[asset][pair] += 1
            asset_weights[asset][pair] += weight
            if len(asset_context[asset][pair]) < 2:
                asset_context[asset][pair].append({"title": title, "pipeline_asset": asset, "relevance_weight": weight})

    pairs = [
        {"entity_a": a, "entity_b": b, "cooccurrence_count": count, "example_headlines": pair_context[(a, b)]}
        for (a, b), count in pair_counts.most_common()
    ]
    pairs_by_asset = {}
    for asset in ASSET_RELEVANCE_FIELD:
        ranked = sorted(asset_counts[asset].items(), key=lambda item: (-item[1], -asset_weights[asset][item[0]], item[0]))
        pairs_by_asset[asset] = [
            {"entity_a": pair[0], "entity_b": pair[1], "cooccurrence_count": count,
             "relevance_weight_sum": round(asset_weights[asset][pair], 6),
             "example_headlines": asset_context[asset][pair]}
            for pair, count in ranked
        ]
    return {
        "generated_from": {"xrp_entries": len(xrp_entries), "btc_entries": len(btc_entries)},
        "unique_pairs_found": len(pairs),
        "pairs": pairs,
        "pairs_by_asset": pairs_by_asset,
    }


def main():
    out = build_cooccurrence(load_jsonl(XRP_LOG), load_jsonl(BTC_LOG))
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Unique entity pairs found: {out['unique_pairs_found']}")


if __name__ == "__main__":
    main()
