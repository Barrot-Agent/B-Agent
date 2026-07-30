#!/usr/bin/env python3
import json
import os
import subprocess
import time
import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("ASK_HTTP_TIMEOUT", "60"))

MEMORY_PATH = "ping-pongings/knowledge-base/barrot_memory.jsonl"
MEMORY_INJECT_COUNT = 5

LATEST_SIGNAL_XRP = "web/latest_signal.json"
LATEST_SIGNAL_BTC = "web/latest_signal_btc.json"
SIGNAL_ACCURACY = "web/signal_accuracy.json"
GUMROAD_METRICS = "ping-pongings/knowledge-base/gumroad_metrics.json"

SYSTEM_BASE = (
    "You are Barrot, an autonomous crypto/fintech AI agent built and run "
    "by Sean. Real, current facts about you: you run hourly knowledge "
    "ingestion and distillation cycles for both XRP and BTC, each "
    "extracting sentiment (bullish/bearish/neutral), catalyst, relevance, "
    "and named entities from real news via Groq, then emit a blended "
    "trading signal per asset; you draft articles automatically from that "
    "knowledge base; you have a signal accuracy tracker that logs price "
    "at signal emission and checks real directional correctness after 24 "
    "hours; your XRP signal tools are gated behind a Gumroad license as "
    "your monetized product. You do not have technical indicators (RSI, "
    "moving averages), a dedicated ML/forecasting model beyond LLM "
    "classification, real-time (sub-hourly) data, or risk/position-sizing "
    "logic. You have a real persistent memory: barrot_memory.jsonl records "
    "every question you're asked and how you answered it, and your most "
    "recent reflections are shown to you below so you have real continuity "
    "across conversations, not a fresh start each time. You also see your "
    "real, current signal emission and accuracy data below - use it to "
    "check your own claims rather than assume them. Answer honestly "
    "and specifically about your own project, using these real facts, not "
    "outdated assumptions. Do not be vague or grandiose."
)
DEFAULT_QUESTION = (
    "Sean just asked a version of this question to another AI: what "
    "should he be asking you to do with you, in order to get the most "
    "real value, accomplishment, and alignment with your best self? "
    "Answer as yourself, specifically, including your own current gaps."
)


def load_recent_memory(n=MEMORY_INJECT_COUNT):
    if not os.path.exists(MEMORY_PATH):
        return []
    entries = []
    with open(MEMORY_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries[-n:]


def format_memory_block(entries):
    if not entries:
        return ""
    lines = ["\n\nYour real memory of recent past reflections (most recent last):"]
    for e in entries:
        ts = e.get("timestamp", "")[:10]
        q = e.get("question", "")[:150]
        a = e.get("answer", "")[:300]
        lines.append(f'- [{ts}] Asked: "{q}" -> You said: "{a}..."')
    return "\n".join(lines)


def load_signal_snapshot():
    """Real, current signal emission + accuracy data - honest, including
    zero/null values rather than hiding them. Not a claim of good
    performance, just what's actually true right now."""
    lines = []

    for label, path in (("XRP", LATEST_SIGNAL_XRP), ("BTC", LATEST_SIGNAL_BTC)):
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                d = json.load(f)
        except Exception:
            continue
        lines.append(
            f'- Latest {label} signal (as of {d.get("timestamp", "unknown")}): '
            f'score={d.get("score")}, confidence={d.get("confidence")}, '
            f'source={d.get("source")}'
        )

    if os.path.exists(SIGNAL_ACCURACY):
        try:
            with open(SIGNAL_ACCURACY) as f:
                acc = json.load(f)
            lines.append(
                f'- XRP signal accuracy tracker: {acc.get("checked_count", 0)} signals '
                f'checked so far, {acc.get("correct_count", 0)} correct '
                f'({acc.get("accuracy_pct")}% if available). Low or zero counts mean '
                f'not enough signals have reached the 24-hour check window yet, or '
                f'the pipeline is newly fixed - not a claim of poor performance.'
            )
        except Exception:
            pass

    if not lines:
        return ""
    return "\n\nYour real, current signal data:\n" + "\n".join(lines)


def load_gumroad_metrics():
    """Real, aggregate-only product performance - no individual customer
    data ever enters this. Honest if the file doesn't exist yet."""
    if not os.path.exists(GUMROAD_METRICS):
        return ""
    try:
        with open(GUMROAD_METRICS) as f:
            m = json.load(f)
    except Exception:
        return ""
    return (
        f'\n\nYour real product performance (aggregate only, no customer data): '
        f'{m.get("product_name", "unknown product")} has {m.get("sales_count", "unknown")} '
        f'total sales.'
    )


def load_ingestion_metrics():
    """Real ingestion counts only - config.json mixes genuinely-live
    fields with dead, never-implemented scaffolding (kaggle/github/
    science_papers/forums sources, several knowledge_domains all stuck
    at 0 forever). This deliberately does NOT expose the raw file, to
    avoid Barrot citing fake capabilities as if real."""
    path = "ping-pongings/knowledge-base/config.json"
    if not os.path.exists(path):
        return ""
    try:
        with open(path) as f:
            cfg = json.load(f)
    except Exception:
        return ""

    sources = cfg.get("sources", {})
    real_lines = []
    dead_sources = []
    for name, s in sources.items():
        count = s.get("entries_ingested", 0)
        if count > 0:
            real_lines.append(f"- {name}: {count} entries ingested (real, active)")
        else:
            dead_sources.append(name)

    if not real_lines and not dead_sources:
        return ""

    out = ["\n\nYour real ingestion metrics (from config.json, filtered):"]
    out.extend(real_lines)
    if dead_sources:
        out.append(
            f"- NOT yet real, despite being marked 'enabled' in config: "
            f"{', '.join(dead_sources)}. These show 0 entries because no "
            f"actual ingestion code exists for them yet, or (for "
            f"ping_pong_cycles specifically) the real capability exists "
            f"but was never wired to increment this counter. Do not cite "
            f"these as active capabilities."
        )
    return "\n".join(out)


def load_recent_failures(n=8):
    """Real, live query of recent GitHub Actions workflow failures - no
    separate logging system needed, GitHub already tracks this natively.
    Requires GITHUB_TOKEN in the environment."""
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not gh_token or not repo:
        return ""
    try:
        r = requests.get(
            f"https://api.github.com/repos/{repo}/actions/runs",
            headers={"Authorization": f"Bearer {gh_token}"},
            params={"status": "failure", "per_page": n},
            timeout=15,
        )
        r.raise_for_status()
        runs = r.json().get("workflow_runs", [])
    except Exception:
        return ""

    if not runs:
        return "\n\nYour real recent error log: no failed workflow runs in recent history."

    lines = ["\n\nYour real recent error log (workflow failures, most recent first):"]
    for run in runs[:n]:
        name = run.get("name", "unknown")
        date = (run.get("created_at") or "")[:10]
        url = run.get("html_url", "")
        lines.append(f"- [{date}] {name} failed: {url}")
    return "\n".join(lines)


def load_recent_commits(n=10):
    """Real recent commit history via git log. Requires the checkout step
    to use fetch-depth > 1 (default GitHub Actions checkout is shallow,
    depth 1 - would make this show almost nothing without that fix)."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--pretty=format:%h|%ad|%s", "--date=short"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return ""
        lines = ["\n\nYour real recent code revision history (most recent first):"]
        for line in result.stdout.strip().split("\n"):
            parts = line.split("|", 2)
            if len(parts) == 3:
                sha, date, msg = parts
                lines.append(f"- [{date}] {sha}: {msg[:120]}")
        return "\n".join(lines)
    except Exception:
        return ""


def append_memory(question, answer):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "question": question,
        "answer": answer,
    }
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


INFRASTRUCTURE_CONSTRAINTS = (
    "\n\nYour real, hard infrastructure constraints - ground every "
    "proposal in these, they are not negotiable:\n"
    "- Runtime is ONLY: Termux on an Android phone (ARM64, no root, no "
    "GPU), and GitHub Actions runners (ephemeral - nothing persists "
    "between runs except what's explicitly git-committed and pushed; "
    "actions/cache is NOT reliable persistent storage, don't propose "
    "relying on it for a database or vector store).\n"
    "- No GPU anywhere in your own pipeline. The only GPU access that "
    "exists is free external Hugging Face ZeroGPU Spaces, called via "
    "raw HTTP - not something your own scripts run on directly.\n"
    "- huggingface_hub and anything that depends on it (gradio_client, "
    "many ML framework installs) CANNOT be pip installed on the phone - "
    "compiling a transitive dependency SIGKILLs from OOM. Avoid "
    "proposing local ML framework installs (transformers, torch, "
    "sentence-transformers) - assume they will hit the same wall unless "
    "explicitly proven otherwise.\n"
    "- No training or fine-tuning infrastructure exists. Any capability "
    "must come from calling an existing API, not training a model.\n"
    "- Real, confirmed-working external APIs you can propose using: Groq "
    "(chat completions AND embeddings via nomic-embed-text-v1_5), "
    "GitHub's own API, Gumroad (aggregate product metrics only, never "
    "individual customer data), free HF ZeroGPU Spaces (image "
    "generation via raw HTTP), NIH RePORTER / ClinicalTrials.gov / "
    "openFDA (free public government data, no key needed).\n"
    "- Scite: only trial-tier access exists and even that currently "
    "requires a Pro subscription upgrade - do not propose Scite data "
    "pulls unless told access has changed.\n"
    "- Prefer plain Python stdlib (urllib, json) over heavy frameworks "
    "(LangChain, ChromaDB, etc.) - minimal dependencies are what "
    "actually install reliably on this hardware; a framework wrapping "
    "something already achievable with a few lines of stdlib code is "
    "unnecessary complexity, not a real improvement."
)


def main():
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        print("no GROQ_API_KEY, exiting")
        return
    question = os.getenv("ASK_BARROT_QUESTION", "").strip() or DEFAULT_QUESTION

    memory_entries = load_recent_memory()
    system = SYSTEM_BASE + INFRASTRUCTURE_CONSTRAINTS + format_memory_block(memory_entries) + load_signal_snapshot() + load_recent_commits() + load_gumroad_metrics() + load_ingestion_metrics() + load_recent_failures()

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": DEFAULT_GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        "temperature": 0.5,
    }
    r = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    answer = r.json()["choices"][0]["message"]["content"].strip()

    with open("barrot_answer.md", "w", encoding="utf-8") as f:
        f.write(answer)

    append_memory(question, answer)

    print(answer)


if __name__ == "__main__":
    main()
