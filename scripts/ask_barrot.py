#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
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
GROQ_USAGE_LOG = "ping-pongings/knowledge-base/groq_usage_log.jsonl"

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


CURRENT_QUESTION_PRIORITY = (
    "\n\nCURRENT QUESTION PRIORITY: Answer the current user question directly "
    "before anything else. The current question overrides recent memory, previous "
    "answers, default tasks, and background context. Memory is reference material "
    "only and must never cause you to continue or repeat an earlier task. Follow "
    "explicit length and format instructions in the current question exactly."
)

ANTI_FABRICATION = (
    "\n\nCRITICAL, NON-NEGOTIABLE RULE: never state a specific number, "
    "percentage, function name, file path, class name, or capability as "
    "fact unless it appears explicitly in the real data sections of this "
    "prompt. If you are asked about something not shown to you here - "
    "including exact usage figures, exact code structure, or exact API "
    "signatures - say plainly 'I don't have real data on that in my "
    "current context' rather than inventing a plausible-sounding answer. "
    "This applies with extra force to code: if a file's real content is "
    "not shown to you verbatim below, do not invent or guess its "
    "function names, signatures, or behavior, even if a similar-sounding "
    "function would make sense. A specific-sounding wrong answer is "
    "worse than an honest 'I don't know.'"
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


def load_last_groq_usage():
    if not os.path.exists(GROQ_USAGE_LOG):
        return ""
    try:
        with open(GROQ_USAGE_LOG) as f:
            lines = [l for l in f if l.strip()]
        if not lines:
            return ""
        last = json.loads(lines[-1])
    except Exception:
        return ""
    return (
        f'\n\nYour real Groq API usage, as of the last logged call '
        f'({last.get("timestamp", "unknown")}): '
        f'{last.get("remaining_tokens", "unknown")} tokens remaining this minute '
        f'(limit {last.get("limit_tokens", "unknown")}), '
        f'{last.get("remaining_requests", "unknown")} requests remaining today '
        f'(limit {last.get("limit_requests", "unknown")}). Groq does not expose '
        f'a live daily-token-remaining count in headers - only the figures above '
        f'are real. Never state a specific daily-token-usage percentage unless '
        f'it is derivable from these real numbers.'
    )


def log_groq_usage(response):
    try:
        h = response.headers
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "remaining_tokens": h.get("x-ratelimit-remaining-tokens"),
            "limit_tokens": h.get("x-ratelimit-limit-tokens"),
            "remaining_requests": h.get("x-ratelimit-remaining-requests"),
            "limit_requests": h.get("x-ratelimit-limit-requests"),
        }
        os.makedirs(os.path.dirname(GROQ_USAGE_LOG), exist_ok=True)
        with open(GROQ_USAGE_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def extract_referenced_files(question, repo_root="."):
    candidates = set(re.findall(r"[\w\-/\.]+\.(?:py|yml|yaml|json|md)\b", question))
    found = []
    for c in candidates:
        direct = os.path.join(repo_root, c)
        if os.path.isfile(direct):
            found.append(direct)
            continue
        base = os.path.basename(c)
        for root, dirs, files in os.walk(repo_root):
            if ".git" in root:
                continue
            if base in files:
                found.append(os.path.join(root, base))
                break
    return found


def load_referenced_file_contents(question, max_chars=6000):
    paths = extract_referenced_files(question)
    if not paths:
        return ""
    out = [
        "\n\nThe question references specific file(s). Here is their REAL, "
        "current content - ground your answer in this exact code. Do not "
        "invent function names or behavior beyond what is shown here:"
    ]
    for p in paths[:3]:
        try:
            content = open(p, encoding="utf-8").read()
        except Exception:
            continue
        if len(content) > max_chars:
            content = content[:max_chars] + "\n... [truncated]"
        out.append(f"\n--- REAL CONTENT OF {p} ---\n{content}")
    return "\n".join(out)


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
    "(chat completions ONLY - it does NOT have a real embeddings API, "
    "confirmed via a real 404 on the endpoint; never propose Groq "
    "embeddings again), "
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
    question = (
        " ".join(sys.argv[1:]).strip()
        or os.getenv("ASK_BARROT_QUESTION", "").strip()
        or DEFAULT_QUESTION
    )

    memory_entries = load_recent_memory()
    system = (
        SYSTEM_BASE
        + CURRENT_QUESTION_PRIORITY
        + ANTI_FABRICATION
        + INFRASTRUCTURE_CONSTRAINTS
        + format_memory_block(memory_entries)
        + load_signal_snapshot()
        + load_recent_commits()
        + load_gumroad_metrics()
        + load_ingestion_metrics()
        + load_recent_failures()
        + load_last_groq_usage()
        + load_referenced_file_contents(question)
    )

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": DEFAULT_GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content":
                "BACKEND IDENTITY: The API endpoint used by this script is api.groq.com, "
                "therefore the inference backend is Groq. A model name containing OpenAI, "
                "such as openai/gpt-oss-120b, does not mean OpenAI is the API backend. "
                "Report Groq as the backend when this script is using the Groq endpoint.\n\n"
                "CURRENT QUESTION — ANSWER ONLY THIS QUESTION. Do not answer any "
                "previous question from memory or background context. Follow all "
                "exact format, sentence-count, and length instructions exactly.\n\n"
                + question},
        ],
        "temperature": 0.5,
    }
    r = None
    for attempt in range(6):
        r = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT)
        if r.status_code == 429 and attempt < 5:
            wait = min(60, 2 ** attempt)
            print(f"Groq rate-limited. Retrying in {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        break
    log_groq_usage(r)
    response_data = r.json()
    answer = response_data["choices"][0]["message"]["content"].strip()
    actual_model = response_data.get("model", DEFAULT_GROQ_MODEL)
    print(f"[BARROT BACKEND: Groq | MODEL: {actual_model}]")

    with open("barrot_answer.md", "w", encoding="utf-8") as f:
        f.write(answer)

    append_memory(question, answer)

    print(answer)


if __name__ == "__main__":
    main()
