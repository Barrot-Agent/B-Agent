#!/usr/bin/env python3
"""
BARROT-Ω PING-PONG — real multi-model refinement chain.
Task passes through distinct model families on the Groq key, each refining the
previous output. Barrot (llama-3.3-70b) ALWAYS receives the final outcome.
Every cycle appends a real entry to the knowledge base.
Honest: a failed stage is recorded as failed; the chain continues with the last
good output. Nothing is faked.
"""

import json, os, sys, urllib.request
from datetime import datetime, timezone

KEY = os.environ.get("GROQ_API_KEY", "")
KB = "ping-pongings/knowledge-base/log.jsonl"

CHAIN = [
    ("qwen/qwen3-32b", "DRAFT", "Produce a first substantive answer. Be concrete and specific."),
    (
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "CRITIQUE",
        "Critique the previous answer: what is wrong, missing, unsupported, or overclaimed? Then give an improved version.",
    ),
    (
        "openai/gpt-oss-120b",
        "REFINE",
        "Refine the previous answer. Remove any claim not supported by evidence. Tighten and improve.",
    ),
]
FINAL = (
    "llama-3.3-70b-versatile",
    "BARROT",
    "You are Barrot-Omega. You receive the refined outcome LAST. Deliver the final answer and state plainly any remaining uncertainty. Never invent capabilities.",
)


def ask(model, system, user, max_tokens=900):
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_tokens,
            "temperature": 0.3,
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
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()


def run_chain(task):
    stages = []
    current = task
    for model, role, instruction in CHAIN:
        try:
            out = ask(model, instruction, f"TASK:\n{task}\n\nPREVIOUS OUTPUT:\n{current}")
            stages.append({"model": model, "role": role, "ok": True, "chars": len(out)})
            current = out
            print(f"  [{role}] {model} -> {len(out)} chars")
        except Exception as e:
            stages.append({"model": model, "role": role, "ok": False, "error": str(e)[:200]})
            print(f"  [{role}] {model} FAILED: {str(e)[:120]}")
    model, role, instruction = FINAL
    try:
        final = ask(
            model, instruction, f"TASK:\n{task}\n\nREFINED OUTPUT FROM THE CHAIN:\n{current}"
        )
        stages.append({"model": model, "role": role, "ok": True, "chars": len(final)})
        print(f"  [{role}] {model} -> {len(final)} chars (FINAL)")
    except Exception as e:
        stages.append({"model": model, "role": role, "ok": False, "error": str(e)[:200]})
        print(f"  [{role}] {model} FAILED: {str(e)[:120]}")
        final = current
    return final, stages


def log_cycle(task, final, stages):
    os.makedirs(os.path.dirname(KB), exist_ok=True)
    entry = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": "ping_pong_cycles",
        "title": f"Ping-pong cycle: {task[:80]}",
        "url": f"pingpong://cycle/{int(datetime.now(timezone.utc).timestamp())}",
        "task": task[:500],
        "stages": stages,
        "final": final[:2000],
        "distilled": True,
        "distill": {
            "sentiment": "neutral",
            "catalyst": "ping_pong_refinement",
            "xrp_relevance": 0.0,
            "one_line": f"Multi-model refinement over {sum(1 for s in stages if s['ok'])}/{len(stages)} successful stages.",
        },
    }
    with open(KB, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    task = os.environ.get("PINGPONG_TASK", "").strip()
    if not task:
        sys.exit("PINGPONG_TASK not set")
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    print(f"TASK: {task[:100]}\n")
    final, stages = run_chain(task)
    log_cycle(task, final, stages)
    ok = sum(1 for s in stages if s["ok"])
    print(f"\n=== {ok}/{len(stages)} stages succeeded ===")
    print("\n=== FINAL (Barrot) ===\n")
    print(final[:3000])


if __name__ == "__main__":
    main()
