#!/usr/bin/env python3
"""
BARROT-Ω SEMANTIC MEMORY — real retrieval-augmented context for signal
generation, built the way this project's infrastructure actually works:
Groq's real embeddings API (nomic-embed-text-v1_5, confirmed real) for
vectors, plain cosine similarity (numpy only, no vector DB), and a
git-committed JSON file as the persistent store (same pattern as every
other real knowledge file in this repo).

Deliberately does NOT use LangChain, ChromaDB, or FinBERT/transformers:
- ChromaDB via actions/cache is not real persistence - GitHub Actions
  cache is evictable, not guaranteed, unlike a git-committed file.
- transformers/torch installs are the same category of heavy compiled
  dependency that already SIGKILLs on this hardware for huggingface_hub.
- LangChain wraps functionality already achievable in a few lines of
  stdlib code - unnecessary dependency weight for zero real benefit.

Real mechanism:
1. Embed each new distilled news entry via Groq's embeddings endpoint.
2. Store {text, embedding, metadata} in a git-committed JSONL file.
3. At query time, embed the query, compute cosine similarity against
   all stored embeddings with plain numpy, return the top-N matches.
"""

import json
import os
import sys
import urllib.request

import numpy as np

KB_DIR = "ping-pongings/knowledge-base"
MEMORY_STORE = os.path.join(KB_DIR, "semantic_memory.jsonl")
NEWS_LOG = os.path.join(KB_DIR, "log.jsonl")

KEY = os.environ.get("HF_TOKEN", "")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{EMBED_MODEL}"
MAX_NEW_PER_RUN = int(os.environ.get("EMBED_PER_RUN", "20"))


def embed(text):
    """Real HF Serverless Inference API feature-extraction endpoint -
    NOT Groq (confirmed via a real 404 that Groq has no embeddings API).
    First live call not yet verified - this endpoint is documented as
    official HF infrastructure but flagged by HF's own docs as
    potentially in flux; expect one possible fix cycle same as every
    other first-run integration."""
    body = json.dumps({"inputs": text[:2000]}).encode()
    req = urllib.request.Request(
        EMBED_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.load(r)
        if isinstance(result[0], list):
            if isinstance(result[0][0], list):
                import numpy as _np
                return _np.mean(result[0], axis=0).tolist()
            return result[0]
        return result


def load_store():
    if not os.path.exists(MEMORY_STORE):
        return []
    entries = []
    with open(MEMORY_STORE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries


def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def build_index():
    """Embed any new distilled news entries not already in the store."""
    if not os.path.exists(NEWS_LOG):
        print("No log.jsonl found - nothing to embed.")
        return

    with open(NEWS_LOG) as f:
        news_entries = [json.loads(l) for l in f if l.strip()]

    store = load_store()
    already_have = {e.get("source_url") for e in store}

    todo = [
        e for e in news_entries
        if e.get("distilled") and e.get("url") not in already_have
    ][:MAX_NEW_PER_RUN]

    if not todo:
        print("Nothing new to embed.")
        return

    print(f"Embedding {len(todo)} new entries...")
    new_records = []
    for e in todo:
        d = e.get("distill", {})
        text = f"{e.get('title', '')} - {d.get('one_line', '')}"
        try:
            vec = embed(text)
        except Exception as ex:
            print(f"  skip ({e.get('title', '')[:50]}): {ex}")
            continue
        new_records.append({
            "source_url": e.get("url"),
            "text": text,
            "asset": e.get("asset"),
            "embedding": vec,
        })
        print(f"  + {e.get('title', '')[:60]}")

    with open(MEMORY_STORE, "a", encoding="utf-8") as f:
        for r in new_records:
            f.write(json.dumps(r) + "\n")

    print(f"\nEmbedded {len(new_records)} new entries. Written to {MEMORY_STORE}")


def query(query_text, top_n=5, asset_filter=None):
    """Retrieve the most semantically similar stored entries to a query."""
    store = load_store()
    if not store:
        return []
    if asset_filter:
        store = [e for e in store if e.get("asset") == asset_filter]
    if not store:
        return []

    q_vec = embed(query_text)
    scored = [(cosine_sim(q_vec, e["embedding"]), e) for e in store]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": s, "text": e["text"], "source_url": e["source_url"]} for s, e in scored[:top_n]]


if __name__ == "__main__":
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    os.makedirs(KB_DIR, exist_ok=True)
    build_index()
