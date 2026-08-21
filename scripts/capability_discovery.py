#!/usr/bin/env python3
"""Capability discovery: given a real gap from barrot_capability_audit.py,
search for tools/libraries/APIs that could close it, evaluate each against
this project's real, repeatedly-confirmed hardware constraints. Extends the
anti-fabrication discipline already in frontier_gap_analysis.py from
research findings to tooling. Applies to primary brain AND ping-pong chain."""
import os, json, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

KNOWN_HARD_WALLS = [
    "requires huggingface_hub (SIGKILL/OOM compiling cryptography on Termux/Moto G7)",
    "requires compiling C extensions with heavy build deps (torch, tensorflow from source)",
    "requires a persistent always-on server (GitHub Actions is ephemeral-only)",
    "requires Wrangler/workerd on Android ARM64 (no prebuilt binary exists)",
    "requires a paid tier with no free quota and no budget approved",
]

def call_groq(prompt, max_tokens=1200):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}",
                 "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                 "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
        return ""

def search_pypi(query):
    url = f"https://pypi.org/pypi/{urllib.parse.quote(query)}/json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
            return {"exists": True, "summary": data.get("info", {}).get("summary", "")}
    except Exception:
        return {"exists": False, "summary": None}

def evaluate_candidate(candidate_name, candidate_description, consumer="primary_brain"):
    walls_str = "\n".join(f"- {w}" for w in KNOWN_HARD_WALLS)
    prompt = f"""Candidate tool/capability: {candidate_name}
Description: {candidate_description}
Target consumer: {consumer} (primary Groq-based brain, or a ping-pong chain member model)

Known hard infrastructure walls for this project (Termux on Moto G7 + GitHub Actions only, no GPU, no persistent server):
{walls_str}

Evaluate: does this candidate hit any wall above? Cite the wall verbatim if one applies.
If none apply, say so explicitly. Give a real implementation sketch IF viable.

Output ONLY JSON: {{"viable": true/false, "wall_hit": "verbatim wall text or null", "implementation_sketch": "...", "consumer_fit": "primary_brain|ping_pong_chain|both"}}"""
    response = call_groq(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        return json.loads(response[start:end])
    except Exception:
        return {"viable": False, "wall_hit": "PARSE_FAILURE", "implementation_sketch": "", "consumer_fit": "unknown"}

def discover_for_gap(gap_name):
    prompt = f"""Capability gap: {gap_name}

Propose up to 3 REAL, currently-existing tools, libraries, or free APIs that could help close this gap.
Only name things you can describe a specific, checkable mechanism for (a real endpoint, a real package name, a real API).
Do not invent plausible-sounding names.

Output ONLY JSON: {{"candidates": [{{"name": "...", "description": "...", "type": "pypi_package|free_api|github_repo"}}]}}"""
    response = call_groq(prompt, max_tokens=800)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        candidates = json.loads(response[start:end]).get("candidates", [])
    except Exception:
        candidates = []

    results = []
    for c in candidates:
        name, desc, ctype = c.get("name", ""), c.get("description", ""), c.get("type", "")
        pypi_check = search_pypi(name) if ctype == "pypi_package" else None
        eval_result = evaluate_candidate(name, desc)
        results.append({
            "name": name, "description": desc, "type": ctype,
            "pypi_verification": pypi_check, "evaluation": eval_result,
        })
    return results

def generate_usage_doc(gap_name, viable_candidate):
    prompt = f"""New validated capability: {viable_candidate['name']} (closes gap: {gap_name})
Implementation sketch: {viable_candidate['evaluation'].get('implementation_sketch', '')}

Write a 4-6 sentence usage doc: what it does, when to reach for it, one concrete example call, one real limitation.
Plain text, no headers."""
    doc = call_groq(prompt, max_tokens=300)
    kb_dir = Path("ping-pongings/knowledge-base")
    kb_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "capability": viable_candidate["name"], "closes_gap": gap_name,
        "usage_doc": doc, "added": datetime.now(timezone.utc).isoformat(),
    }
    log_file = kb_dir / "capability_usage_docs.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Usage doc appended to {log_file}")
    return entry

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        raise SystemExit(1)
    gap = os.environ.get("GAP_NAME", "")
    if not gap:
        print("No GAP_NAME provided")
        raise SystemExit(1)
    results = discover_for_gap(gap)
    out = f"capability_discovery_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    Path(out).write_text(json.dumps(results, indent=2))
    print(f"Saved: {out}")
    for r in results:
        if r["evaluation"].get("viable"):
            generate_usage_doc(gap, r)
        else:
            print(f"REJECTED {r['name']}: {r['evaluation'].get('wall_hit')}")
