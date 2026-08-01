#!/usr/bin/env python3
"""
BARROT-Ω FRONTIER GAP ANALYSIS
Compares real ingested frontier findings (frontier_log.jsonl) against our
real current stack, via a grounded Groq call - not keyword heuristics.
Read/recommend-only: never auto-switches or auto-adopts anything.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

KB_ROOT = Path(__file__).resolve().parents[1] / "ping-pongings" / "knowledge-base"
FRONTIER_LOG = KB_ROOT / "frontier_log.jsonl"
BENCHMARK_LOG = KB_ROOT / "benchmark_log.jsonl"
UPGRADE_RECS = KB_ROOT / "upgrade_recommendations.jsonl"

KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "openai/gpt-oss-120b"

CURRENT_STACK = {
    "inference": "Groq openai/gpt-oss-120b (free/low-cost API inference, no owned GPU)",
    "image_gen": "HF ZeroGPU black-forest-labs/FLUX.1-dev + yanze/PuLID-FLUX (free, shared GPU queue)",
}


def _now():
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path):
    if not path.is_file():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def ask_groq(system, user):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": 1200,
        "temperature": 0.1,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"[frontier_gap_analysis] Groq HTTP {e.code}: {err[:500]}")
        return ""


SYSTEM = """You compare real recent AI/ML developments against a real current tech stack.
You output ONLY JSON: {"findings": [{"entry_title": "...", "entry_url": "...", "reason": "..."}]}
A finding means: this specific real entry describes a genuinely free-tier or low-cost option
that could concretely replace or improve one of the listed current stack components.
CRITICAL ANTI-FABRICATION RULES:
- entry_title and entry_url MUST be copied verbatim from one of the real entries provided below.
  Never invent an entry that was not given to you.
- If nothing in the batch is a real, concrete, actionable improvement, return {"findings": []}.
  This is the expected, honest result most of the time - do not force a finding.
- Do not claim any option replicates large-corporation-scale training or owned compute. We run
  entirely on free/cheap borrowed inference and GPU-sharing tiers, not owned hardware."""


def build_batch_text(entries, budget=3500):
    lines = []
    used = 0
    for e in entries:
        d = e.get("distill", {}) or {}
        snippet = (
            f"- TITLE: {e.get('title','')}\n"
            f"  URL: {e.get('url','')}\n"
            f"  CLAIM_TYPE: {d.get('claim_type','')}\n"
            f"  CLAIM: {d.get('concrete_claim','')[:300]}\n"
        )
        if used + len(snippet) > budget:
            break
        lines.append(snippet)
        used += len(snippet)
    return "\n".join(lines)


def main():
    frontier_entries = [
        e for e in load_jsonl(FRONTIER_LOG)
        if e.get("distill", {}).get("claim_type") in {"benchmark_result", "proposed_method"}
    ]
    frontier_entries = frontier_entries[-25:]

    recs = []
    if not KEY:
        print("no GROQ_API_KEY set - skipping this cycle")
        sys.exit(0)

    if not frontier_entries:
        recs.append({
            "generated_at": _now(),
            "recommendation": "No benchmark_result/proposed_method entries available this cycle.",
            "grounded_on": None,
        })
    else:
        stack_desc = "\n".join(f"- {k}: {v}" for k, v in CURRENT_STACK.items())
        batch_text = build_batch_text(frontier_entries)
        user = (
            f"CURRENT REAL STACK:\n{stack_desc}\n\n"
            f"REAL RECENT FINDINGS (use ONLY these, never invent others):\n{batch_text}\n\n"
            "Which, if any, describe a free-tier or low-cost option that could concretely "
            "improve one of the current stack components?"
        )
        raw = ask_groq(SYSTEM, user).strip()
        try:
            a, b = raw.find("{"), raw.rfind("}")
            data = json.loads(raw[a:b + 1]) if a != -1 else {"findings": []}
        except json.JSONDecodeError:
            data = {"findings": []}

        findings = data.get("findings", []) or []
        real_titles = {e.get("title", "") for e in frontier_entries}
        for f in findings:
            if f.get("entry_title") in real_titles:
                recs.append({
                    "generated_at": _now(),
                    "recommendation": f.get("reason", ""),
                    "grounded_on": {"title": f.get("entry_title"), "url": f.get("entry_url")},
                })
        if not recs:
            recs.append({
                "generated_at": _now(),
                "recommendation": "No actionable free-tier or low-cost findings this cycle.",
                "grounded_on": None,
            })

    UPGRADE_RECS.parent.mkdir(parents=True, exist_ok=True)
    with UPGRADE_RECS.open("a", encoding="utf-8") as f:
        for rec in recs:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(recs)} recommendation(s)")


if __name__ == "__main__":
    main()
