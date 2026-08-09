#!/usr/bin/env python3
"""
BARROT-Ω SEMANTIC MEMORY — real retrieval-augmented context for signal
generation, LLM-as-judge version. Real dead ends already ruled out
tonight: Groq has no embeddings API (confirmed 404), and HF's old free
embeddings endpoint is retired (confirmed DNS failure) - the new HF
Inference Providers system technically supports embeddings, but only
through the huggingface_hub Python library, which cannot be installed
on this hardware (same SIGKILL wall as everything else in that family).

Real mechanism instead: no vectors, no separate index, no new
dependencies. At query time, feed Groq (already proven, already used
everywhere) a batch of real recent distilled headlines and ask it
directly which are most relevant to a given query - structured JSON
output, grounded strictly in the real headlines shown, same discipline
as entity_relation_classifier.py.

This is less efficient at very large scale than true vector search
(re-reads/re-judges the pool each query rather than pre-computing once),
but it's real, working, and needs nothing beyond what's already proven.
"""

import json
import os
import sys
import urllib.request
from data.animal_research import search_records
from data.registry import load_animal_research

KB_DIR = "ping-pongings/knowledge-base"
NEWS_LOG = os.path.join(KB_DIR, "log.jsonl")

KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "openai/gpt-oss-120b"

POOL_SIZE = int(os.environ.get("MEMORY_POOL_SIZE", "50"))


def ask(prompt):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.1,
    }).encode()
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


def load_pool(asset_filter=None, pool_size=POOL_SIZE):
    """Real recent distilled entries from the existing news log - no
    separate index needed, this data already exists and is already real."""
    if not os.path.exists(NEWS_LOG):
        return []
    with open(NEWS_LOG) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    entries = [e for e in entries if e.get("distilled")]
    if asset_filter:
        entries = [e for e in entries if e.get("asset") == asset_filter]
    return entries[-pool_size:]


def build_prompt(query_text, pool):
    lines = []
    for i, e in enumerate(pool):
        d = e.get("distill", {})
        lines.append(f"{i}. {e.get('title', '')[:120]} - {d.get('one_line', '')[:150]}")
    headlines_block = "\n".join(lines)
    return (
        f"Query: {query_text}\n\n"
        f"Real recent headlines (numbered):\n{headlines_block}\n\n"
        f"Which of these numbered headlines are most relevant to the query? "
        f"Use ONLY the headlines shown - do not invent anything not listed. "
        f"Reply with JSON only, no prose: "
        '{"relevant_indices": [list of up to 5 integers, most relevant first], '
        '"reasoning": "one sentence explaining the top pick"}'
    )


def parse(raw, pool_len):
    a, b = raw.find("{"), raw.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json")
    d = json.loads(raw[a:b + 1])
    indices = d.get("relevant_indices", [])
    indices = [i for i in indices if isinstance(i, int) and 0 <= i < pool_len]
    d["relevant_indices"] = indices
    return d


def query_relevant(query_text, asset_filter=None, top_n=5):
    """Real, live retrieval - no pre-built index, judges the current
    real news pool directly against the query each time it's called."""
    if not KEY:
        raise RuntimeError("GROQ_API_KEY not set")
    pool = load_pool(asset_filter=asset_filter)
    if not pool:
        return {"reasoning": "No real news entries available to search.", "matches": []}

    raw = ask(build_prompt(query_text, pool))
    parsed = parse(raw, len(pool))

    matches = []
    for i in parsed["relevant_indices"][:top_n]:
        e = pool[i]
        d = e.get("distill", {})
        matches.append({
            "title": e.get("title"),
            "one_line": d.get("one_line"),
            "url": e.get("url"),
            "asset": e.get("asset"),
        })
    return {"reasoning": parsed.get("reasoning", ""), "matches": matches}


def query_animal_research(query_text, top_n=5):
    """Retrieve reviewed animal-research records without requiring an LLM key."""
    registry = load_animal_research()
    records = [record for record in registry.get("records", []) if record.get("status") == "approved"]
    return search_records(query_text, records, limit=top_n)


if __name__ == "__main__":
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    test_query = os.environ.get("MEMORY_TEST_QUERY", "regulatory action affecting XRP")
    result = query_relevant(test_query)
    print(f"Query: {test_query}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"\nMatches ({len(result['matches'])}):")
    for m in result["matches"]:
        print(f"  - [{m['asset']}] {m['title']}")
        print(f"    {m['one_line']}")
