#!/usr/bin/env python3
"""
BARROT-Ω PING-PONG — real multi-model refinement chain.
GPT stage uses the real OpenAI API with a model auto-discovered from the
account's own /v1/models list -- no guessed model string.
IBM Bob stage writes a real task ticket -- no confirmed live completions
endpoint exists yet, so this doesn't fabricate one.
"""

import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("CHATGPT_TOKEN", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "")

KB = "ping-pongings/knowledge-base/log.jsonl"
TICKETS_DIR = Path("tasks/ibm_bob")

CHAIN = [
    ("qwen/qwen3-32b", "DRAFT", "Produce a first substantive answer. Be concrete and specific."),
    ("meta-llama/llama-4-scout-17b-16e-instruct", "CRITIQUE",
     "Critique the previous answer: what is wrong, missing, unsupported, or overclaimed? Then give an improved version."),
    ("openai/gpt-oss-120b", "REFINE",
     "Refine the previous answer. Remove any claim not supported by evidence. Tighten and improve."),
]
FINAL = ("openai/gpt-oss-120b", "BARROT",
    "You are Barrot-Omega. You receive the refined outcome LAST. Deliver the final answer and state plainly any remaining uncertainty. Never invent capabilities.")


def discover_openai_model(api_key):
    """Real /v1/models call -- picks a real chat-capable model from the
    authenticated account. No guessed names."""
    req = urllib.request.Request("https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"[model_discovery] HTTP {e.code}: {e.read().decode()[:300]}")
        return None
    except Exception as e:
        print(f"[model_discovery] error: {e}")
        return None
    ids = [m["id"] for m in data.get("data", [])]
    excluded = ("embedding", "whisper", "tts", "moderation", "dall-e", "davinci-002", "babbage")
    candidates = [i for i in ids if i.startswith("gpt-") and not any(x in i for x in excluded)]
    if not candidates:
        print(f"[model_discovery] No gpt-* chat models found. Full list: {ids[:20]}")
        return None
    candidates.sort(reverse=True)
    chosen = candidates[0]
    print(f"[model_discovery] Selected {chosen} from {len(candidates)} candidates: {candidates[:8]}")
    return chosen


if not OPENAI_MODEL and OPENAI_KEY:
    OPENAI_MODEL = discover_openai_model(OPENAI_KEY) or ""


def ask_groq(model, system, user, max_tokens=900):
    body = json.dumps({"model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": max_tokens, "temperature": 0.3}).encode()
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()


def ask_openai(system, user, max_tokens=900):
    if not OPENAI_KEY:
        raise RuntimeError("No OpenAI key found (checked OPENAI_API_KEY, CHATGPT_TOKEN)")
    if not OPENAI_MODEL:
        raise RuntimeError("OPENAI_MODEL could not be auto-discovered -- check key validity")
    body = json.dumps({"model": OPENAI_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": max_tokens, "temperature": 0.3}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI HTTP {e.code}: {e.read().decode()[:400]}")


def write_ibm_bob_ticket(task, current_output):
    TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    ticket_path = TICKETS_DIR / f"ticket_{stamp}.md"
    ticket_path.write_text(
        f"# IBM Bob Task Ticket -- {stamp}\n\n## Original task\n{task}\n\n"
        f"## Current chain output (for context)\n{current_output[:2000]}\n\n"
        f"## Instructions\nPaste this into IBM Bob's interface. No confirmed live "
        f"completions endpoint exists for this project yet.\n")
    print(f"  [IBM_BOB] ticket written -> {ticket_path}")
    return str(ticket_path)


def run_chain(task, include_gpt=True, include_ibm_bob=True):
    stages = []
    current = task
    for model, role, instruction in CHAIN:
        try:
            out = ask_groq(model, instruction, f"TASK:\n{task}\n\nPREVIOUS OUTPUT:\n{current}")
            stages.append({"model": model, "role": role, "ok": True, "chars": len(out)})
            current = out
            print(f"  [{role}] {model} -> {len(out)} chars")
        except Exception as e:
            stages.append({"model": model, "role": role, "ok": False, "error": str(e)[:200]})
            print(f"  [{role}] {model} FAILED: {str(e)[:120]}")

    if include_gpt:
        try:
            out = ask_openai(
                "Critique and refine the previous answer from a different model family's perspective. Flag anything the prior stages may have missed or overclaimed.",
                f"TASK:\n{task}\n\nPREVIOUS OUTPUT:\n{current}")
            stages.append({"model": OPENAI_MODEL or "openai:unset", "role": "GPT_CROSSCHECK", "ok": True, "chars": len(out)})
            current = out
            print(f"  [GPT_CROSSCHECK] {OPENAI_MODEL} -> {len(out)} chars")
        except Exception as e:
            stages.append({"model": OPENAI_MODEL or "openai:unset", "role": "GPT_CROSSCHECK", "ok": False, "error": str(e)[:200]})
            print(f"  [GPT_CROSSCHECK] FAILED: {str(e)[:200]}")

    if include_ibm_bob:
        try:
            ticket_path = write_ibm_bob_ticket(task, current)
            stages.append({"model": "ibm_bob", "role": "IBM_BOB_TICKET", "ok": True, "ticket": ticket_path})
        except Exception as e:
            stages.append({"model": "ibm_bob", "role": "IBM_BOB_TICKET", "ok": False, "error": str(e)[:200]})

    model, role, instruction = FINAL
    try:
        final = ask_groq(model, instruction, f"TASK:\n{task}\n\nREFINED OUTPUT FROM THE CHAIN:\n{current}")
        stages.append({"model": model, "role": role, "ok": True, "chars": len(final)})
        print(f"  [{role}] {model} -> {len(final)} chars (FINAL)")
    except Exception as e:
        stages.append({"model": model, "role": role, "ok": False, "error": str(e)[:200]})
        final = current
    return final, stages


def log_cycle(task, final, stages):
    os.makedirs(os.path.dirname(KB), exist_ok=True)
    entry = {"ingested_at": datetime.now(timezone.utc).isoformat(), "source": "ping_pong_cycles",
        "title": f"Ping-pong cycle: {task[:80]}", "url": f"pingpong://cycle/{int(datetime.now(timezone.utc).timestamp())}",
        "task": task[:500], "stages": stages, "final": final[:2000], "distilled": True,
        "distill": {"sentiment": "neutral", "catalyst": "ping_pong_refinement", "xrp_relevance": 0.0,
            "one_line": f"Multi-model refinement over {sum(1 for s in stages if s['ok'])}/{len(stages)} successful stages."}}
    with open(KB, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    task = os.environ.get("PINGPONG_TASK", "").strip()
    if not task:
        sys.exit("PINGPONG_TASK not set")
    if not GROQ_KEY:
        sys.exit("GROQ_API_KEY not set")
    include_gpt = os.environ.get("PINGPONG_INCLUDE_GPT", "1") != "0"
    include_ibm_bob = os.environ.get("PINGPONG_INCLUDE_IBM_BOB", "1") != "0"
    print(f"TASK: {task[:100]}\n")
    final, stages = run_chain(task, include_gpt, include_ibm_bob)
    log_cycle(task, final, stages)
    ok = sum(1 for s in stages if s["ok"])
    print(f"\n=== {ok}/{len(stages)} stages succeeded ===\n\n=== FINAL (Barrot) ===\n")
    print(final[:3000])


if __name__ == "__main__":
    main()
