#!/usr/bin/env python3
"""
BARROT-Ω KNOWLEDGE DISTILL (BTC) — turns raw ingested headlines into
signal-relevant insight. Reads log_btc.jsonl entries not yet distilled,
sends each through Groq to extract sentiment/catalyst/relevance/entities.
Honest: if the brain fails on an entry, that entry is left undistilled.
"""

import json, os, sys, urllib.request

KB_DIR = "ping-pongings/knowledge-base"
LOG_PATH = os.path.join(KB_DIR, "log_btc.jsonl")
KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "llama-3.3-70b-versatile"


def ask(prompt):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
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


def build_prompt(e):
    return (
        f"Headline: {e['title']}\nSummary: {e.get('summary','')}\n\n"
        'Reply with JSON ONLY, no prose: {"sentiment": one of '
        '[bullish,bearish,neutral], "catalyst": short phrase or null, '
        '"btc_relevance": number 0.0-1.0, "entities": array of up to 5 '
        "key named entities mentioned (people, organizations, tickers, "
        'protocols - not generic words), "one_line": one sentence on why '
        "it matters for a Bitcoin trading signal}"
    )


def parse(raw):
    a, b = raw.find("{"), raw.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json")
    d = json.loads(raw[a : b + 1])
    if d.get("sentiment") not in ("bullish", "bearish", "neutral"):
        raise ValueError("bad sentiment")
    d["btc_relevance"] = max(0.0, min(float(d.get("btc_relevance", 0)), 1.0))
    entities = d.get("entities", [])
    if not isinstance(entities, list):
        entities = []
    d["entities"] = [str(x).strip() for x in entities if str(x).strip()][:5]
    return d


def main():
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    if not os.path.exists(LOG_PATH):
        sys.exit("no log to distill")
    with open(LOG_PATH) as f:
        entries = [json.loads(l) for l in f if l.strip()]

    todo = [e for e in entries if not e.get("distilled")]
    if not todo:
        print("All entries already distilled.")
        return

    done = 0
    for e in todo:
        try:
            d = parse(ask(build_prompt(e)))
            e["distill"] = d
            e["distilled"] = True
            done += 1
            ents = ", ".join(d["entities"]) or "none"
            print(f"  [{d['sentiment']}] {e['title'][:60]} | entities: {ents}")
        except Exception as ex:
            print(f"  skip (brain/parse fail): {e['title'][:50]} — {ex}")

    with open(LOG_PATH, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    print(f"Distilled {done}/{len(todo)} pending entries.")


if __name__ == "__main__":
    main()
