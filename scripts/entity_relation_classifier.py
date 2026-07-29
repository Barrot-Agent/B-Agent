#!/usr/bin/env python3
"""
BARROT-Ω ENTITY RELATION CLASSIFIER — the real, buildable version of the
"semantic relation" layer Barrot proposed for cross-domain synthesis
(issue #335). Turns raw co-occurrence counts (already real, already
running) into classified relationships between entities, grounded in the
actual headlines that mention them together.

Deliberately does NOT use vector embeddings (openai/text-embedding-3-large
isn't available - no OpenAI key exists in this project, only Groq) or a
fine-tuned classifier (no training infrastructure exists). Uses a direct
Groq classification prompt instead - same real mechanism as every other
distillation step in this project, zero new infrastructure.

Idempotent: only classifies pairs not already in entity_relations.json,
same pattern as research_topics.py.
"""

import json
import os
import time
import urllib.request

KB_DIR = "ping-pongings/knowledge-base"
COOCCURRENCE_PATH = os.path.join(KB_DIR, "entity_cooccurrence.json")
OUT_PATH = os.path.join(KB_DIR, "entity_relations.json")

KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "openai/gpt-oss-120b"

VALID_RELATIONS = {
    "causal",           # one plausibly drives/influences the other
    "regulatory",       # a regulator/legal action affecting the other
    "competitive",      # rivals, substitutes, or opposing market forces
    "complementary",    # reinforce or depend on each other
    "same_event",       # both are part of the same single news event
    "correlated_unclear",  # appear together but no clear real relation
}

MAX_PER_RUN = int(os.environ.get("RELATIONS_PER_RUN", "15"))


def ask(prompt):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.1,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def build_prompt(pair):
    headlines = "\n".join(f"- {h['title']}" for h in pair.get("example_headlines", []))
    return (
        f"Two entities appear together {pair['cooccurrence_count']} times in real "
        f"crypto news: \"{pair['entity_a']}\" and \"{pair['entity_b']}\".\n\n"
        f"Real example headlines where they co-occur:\n{headlines}\n\n"
        f"Classify their relationship using ONLY the headlines above - do not "
        f"invent context not shown. Reply with JSON only, no prose: "
        '{"relation_type": one of ["causal","regulatory","competitive",'
        '"complementary","same_event","correlated_unclear"], '
        '"justification": one sentence grounded strictly in the headlines above}'
    )


def parse(raw):
    a, b = raw.find("{"), raw.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json")
    d = json.loads(raw[a:b + 1])
    if d.get("relation_type") not in VALID_RELATIONS:
        raise ValueError(f"invalid relation_type: {d.get('relation_type')}")
    return d


def pair_key(pair):
    return f"{pair['entity_a']}|{pair['entity_b']}"


def main():
    if not KEY:
        import sys
        sys.exit("GROQ_API_KEY not set")
    if not os.path.exists(COOCCURRENCE_PATH):
        print("No entity_cooccurrence.json found - nothing to classify.")
        return

    with open(COOCCURRENCE_PATH) as f:
        cooc = json.load(f)
    pairs = cooc.get("pairs", [])

    existing = {}
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            existing_data = json.load(f)
        existing = {r["pair_key"]: r for r in existing_data.get("relations", [])}

    todo = [p for p in pairs if pair_key(p) not in existing]
    if not todo:
        print(f"All {len(pairs)} pairs already classified.")
        return

    batch = todo[:MAX_PER_RUN]
    print(f"Classifying {len(batch)}/{len(todo)} remaining pairs...")

    done = 0
    for pair in batch:
        try:
            parsed = parse(ask(build_prompt(pair)))
            existing[pair_key(pair)] = {
                "pair_key": pair_key(pair),
                "entity_a": pair["entity_a"],
                "entity_b": pair["entity_b"],
                "cooccurrence_count": pair["cooccurrence_count"],
                "relation_type": parsed["relation_type"],
                "justification": parsed["justification"],
                "classified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            done += 1
            print(f"  [{parsed['relation_type']}] {pair['entity_a']} <-> {pair['entity_b']}")
        except Exception as ex:
            print(f"  skip ({pair['entity_a']} <-> {pair['entity_b']}): {ex}")

    out = {
        "note": (
            "Relationships classified from real co-occurrence headlines via "
            "direct Groq classification - not embeddings, not a fine-tuned "
            "model (neither is available on this infrastructure). Grounded "
            "strictly in the actual headlines shown to the model."
        ),
        "total_classified": len(existing),
        "relations": list(existing.values()),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"\nClassified {done} new pairs. Total: {len(existing)}. Written to {OUT_PATH}")


if __name__ == "__main__":
    main()
