#!/usr/bin/env python3
"""Data value triage: score ingested content for novelty/relevance/density
before it consumes prompt budget. Real mechanism, not a renamed label --
directly extends the existing file_ctx/dir_ctx budgeting discipline
(barrot_agent.py) to the ingestion side instead of just the injection side."""
import os, json, urllib.request, hashlib
from pathlib import Path
from datetime import datetime, timezone

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
KB_DIR = Path("ping-pongings/knowledge-base")
SEEN_HASHES_FILE = KB_DIR / "seen_content_hashes.json"

def call_groq(prompt, max_tokens=400):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}",
                 "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                 "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
        return ""

def load_seen_hashes():
    if SEEN_HASHES_FILE.exists():
        return set(json.loads(SEEN_HASHES_FILE.read_text()))
    return set()

def save_seen_hashes(hashes):
    KB_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_HASHES_FILE.write_text(json.dumps(list(hashes)))

def content_hash(text):
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()[:16]

def novelty_score(text, seen_hashes):
    h = content_hash(text)
    return (1.0, h) if h not in seen_hashes else (0.0, h)

def relevance_and_density(text, active_goals):
    goals_str = ", ".join(active_goals) if active_goals else "general capability building"
    prompt = f"""Active goals: {goals_str}

Content to evaluate:
{text[:1500]}

Score this content 0.0-1.0 on:
- relevance: does it materially connect to the active goals above?
- density: is the information-to-length ratio high, or mostly padding/repetition?

You MUST quote the specific phrase (under 15 words) that justifies your relevance score, or say "no relevant content found" if none exists.
Output ONLY JSON: {{"relevance": 0.0, "density": 0.0, "justifying_quote": "..."}}"""
    response = call_groq(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        result = json.loads(response[start:end])
        return result.get("relevance", 0.0), result.get("density", 0.0), result.get("justifying_quote", "")
    except Exception:
        return 0.0, 0.0, "SCORING_FAILED"

def triage(text, active_goals=None, seen_hashes=None):
    if seen_hashes is None:
        seen_hashes = load_seen_hashes()
    novelty, h = novelty_score(text, seen_hashes)
    if novelty == 0.0:
        return {"admit": False, "reason": "exact_duplicate", "hash": h,
                "novelty": 0.0, "relevance": None, "density": None}
    relevance, density, quote = relevance_and_density(text, active_goals or [])
    composite = (novelty * 0.2) + (relevance * 0.5) + (density * 0.3)
    admit = composite >= 0.4
    seen_hashes.add(h)
    return {
        "admit": admit, "composite_score": round(composite, 3),
        "novelty": novelty, "relevance": relevance, "density": density,
        "justifying_quote": quote, "hash": h,
    }

def triage_batch(items, active_goals=None):
    seen_hashes = load_seen_hashes()
    results = []
    for item in items:
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        r = triage(text, active_goals, seen_hashes)
        r["source_id"] = item.get("id") if isinstance(item, dict) else None
        results.append(r)
    save_seen_hashes(seen_hashes)
    admitted = sum(1 for r in results if r["admit"])
    print(f"Triage: {admitted}/{len(results)} admitted")
    return results

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        raise SystemExit(1)
    raw = os.environ.get("TRIAGE_INPUT", "")
    goals = os.environ.get("ACTIVE_GOALS", "").split(",") if os.environ.get("ACTIVE_GOALS") else []
    if raw:
        items = json.loads(raw)
        results = triage_batch(items, goals)
        out = f"triage_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        Path(out).write_text(json.dumps(results, indent=2))
        print(f"Saved: {out}")
    else:
        print("No TRIAGE_INPUT provided")
