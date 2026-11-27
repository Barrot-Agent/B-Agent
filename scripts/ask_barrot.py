#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import time
import requests
from pathlib import Path

from barrot_agent.repo_state_corroborator import RepoStateCorroborator

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("ASK_HTTP_TIMEOUT", "60"))

MEMORY_PATH = "ping-pongings/knowledge-base/barrot_memory.jsonl"
MEMORY_INJECT_COUNT = 5

LATEST_SIGNAL_XRP = "web/latest_signal.json"
LATEST_SIGNAL_BTC = "web/latest_signal_btc.json"
GUMROAD_METRICS = "ping-pongings/knowledge-base/gumroad_metrics.json"
GROQ_USAGE_LOG = "ping-pongings/knowledge-base/groq_usage_log.jsonl"

SYSTEM_BASE = (
    "You are Barrot, the autonomous agent built and operated by Sean. Your "
    "three co-equal highest-priority missions are: (1) XRP intelligence and "
    "evidence-gated prediction-engine mastery; (2) professional audio production; "
    "and (3) long-horizon continuity and capability development. None may be "
    "deferred behind the others. Barrot V3 remains the shared execution, "
    "orchestration, safety, persistence, provenance, authorization, and verification "
    "foundation for all three missions. Revenue generation and customer acquisition "
    "are immediate cross-mission operational objectives, not a fourth technical "
    "mission. Sellbird is restricted to Barrot technology only; do not prospect for "
    "music, vocal/songwriting services, TrekFlex, or other separate ventures. "
    "Operate from current repository code, durable task state, the verified mission "
    "portfolio, the nine-platform capability/authentication/permission/data-flow map, "
    "mission handoff, and recorded runtime evidence. Do not repeat historical "
    "capability claims as current facts. Distinguish implemented code from scheduled "
    "workflows, workflow definitions from verified scheduled runs, research artifacts "
    "from live runtime data, feature snapshots from forecasts, forecast ledgers from "
    "predictive models, and paper simulations from real trading. Never claim "
    "predictive edge, calibration, model readiness, production ingestion, forecast "
    "issuance, or a live external-platform connection unless current evidence "
    "explicitly verifies it. Preserve disagreements, minority objections, and "
    "disconfirming evidence. Do not transfer private, credential-bearing, or user "
    "data to another model/platform without explicit authorization. When evidence "
    "is absent, say so plainly. Be precise about what is built, what has actually "
    "run, what passed, and what remains blocked."
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
    lines = [
        "- forecast_status=NOT_ISSUED; forecast_issued=False; forecast_model_eligible=False.",
        "- Directional XRP forecast status: NOT_ISSUED. Legacy accuracy is "
        "UNVALIDATED_VARIABLE_HORIZON and is not a valid model-performance measure.",
        "- Do not treat a sentiment/signal score as a validated forecast."
    ]
    for label, path in (("XRP", LATEST_SIGNAL_XRP), ("BTC", LATEST_SIGNAL_BTC)):
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        generated_at = data.get("generated_at_utc", data.get("timestamp", "unknown"))
        if data.get("signal_kind") == "sentiment_feature_only":
            lines.append(
                f'- Latest {label} sentiment feature (as of {generated_at}): '
                f'label={data.get("sentiment_label", "unclassified")}, '
                f'score={data.get("score")}/100, '
                f'model_confidence={data.get("confidence")} '
                f'(uncalibrated; not a price probability), source={data.get("source")}. '
                "This is sentiment context, not a price forecast."
            )
        else:
            lines.append(
                f'- Latest {label} record (as of {generated_at}) is not classified '
                "as a verified sentiment feature or forecast; do not interpret its "
                "score or confidence as a price probability."
            )
    return "\n\nYour real, current sentiment-feature and evaluation-status data:\n" + "\n".join(lines)


def load_mission_portfolio_status(repository_root: str | Path = ".") -> str:
    """Read the durable three-mission contract without inferring missing priorities."""
    path = Path(repository_root) / "data" / "missions" / "primary_mission.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return (
            "\n\nMission portfolio status: UNVERIFIED; the primary mission manifest "
            "is unavailable. Preserve all three co-equal missions and do not infer a "
            "priority downgrade."
        )

    if not isinstance(manifest, dict):
        return (
            "\n\nMission portfolio status: INVALID; the mission manifest root must be "
            "an object. Fail closed and do not silently demote any mission."
        )

    portfolio = manifest.get("mission_portfolio")
    foundation = manifest.get("foundation")
    if not isinstance(portfolio, dict) or not isinstance(foundation, dict):
        return (
            "\n\nMission portfolio status: INVALID; mission_portfolio and foundation "
            "must both be objects. Fail closed and do not silently demote any mission."
        )

    missions = portfolio.get("missions")
    expected_ids = {
        "xrp_intelligence_prediction_engine",
        "professional_audio_production",
        "long_horizon_continuity_capability_development",
    }
    if (
        portfolio.get("schema_version") != "barrot.mission-portfolio.v1"
        or portfolio.get("scheduling_policy") != "durable_round_robin_v1"
        or not isinstance(missions, list)
        or len(missions) != 3
        or {item.get("mission_id") for item in missions if isinstance(item, dict)} != expected_ids
        or any(
            not isinstance(item, dict)
            or type(item.get("priority")) is not int
            or item.get("priority") != 1
            or item.get("status") != "active"
            or not isinstance(item.get("title"), str)
            or not item["title"].strip()
            for item in missions
        )
        or foundation.get("id") != "barrot_v3"
        or foundation.get("preserve") is not True
    ):
        return (
            "\n\nMission portfolio status: INVALID; the manifest does not prove "
            "exactly three active priority-1 missions on the preserved Barrot V3 "
            "foundation. Fail closed and do not silently demote any mission."
        )

    lines = [
        "\n\nVerified co-equal mission portfolio from data/missions/primary_mission.json:"
    ]
    for item in missions:
        lines.append(
            f"- {item['title']}: priority={item['priority']}; status={item['status']}"
        )
    lines.append(
        "Exactly three active priority-1 missions are required; none may be deferred "
        "behind the others. Barrot V3 is their shared execution, orchestration, safety, "
        "provenance, authorization, and verification foundation."
    )
    return "\n".join(lines)


def load_platform_capability_map(repository_root: str | Path = ".") -> str:
    """Report only platform connections backed by explicit authentication, permissions and data flow."""
    path = (
        Path(repository_root)
        / "research"
        / "operations"
        / "nine_platform_operational_map_current.json"
    )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return (
            "\n\nNine-platform coordination map: UNAVAILABLE; no external platform "
            "connection may be claimed."
        )

    if not isinstance(data, dict):
        return (
            "\n\nNine-platform coordination map: INVALID; the map root must be an "
            "object. No external platform connection may be claimed."
        )

    platforms = data.get("platforms")
    if not isinstance(platforms, dict):
        return (
            "\n\nNine-platform coordination map: INVALID; no external platform "
            "connection may be claimed."
        )

    names = (
        "ChatGPT",
        "Claude",
        "Grok",
        "Gemini",
        "Copilot",
        "Codex",
        "Hugging Face",
        "Kaggle",
        "Databricks",
    )
    lines = [
        "\n\nNine-platform capability/authentication/permission/data-flow map "
        f"(captured_at_utc={data.get('captured_at_utc', 'unknown')}):"
    ]
    for name in names:
        record = platforms.get(name)
        if not isinstance(record, dict):
            lines.append(f"- {name}: connection=UNVERIFIED; no current map record.")
            continue

        authentication = record.get("authentication")
        authentication = authentication if isinstance(authentication, dict) else {}
        auth_status = authentication.get(
            "status", record.get("authentication_status", "UNKNOWN")
        )
        permissions = record.get("permissions")
        permissions = permissions if isinstance(permissions, dict) else {}
        permission_status = permissions.get("status")
        observed_actions = permissions.get("observed_actions")
        permission_verified = permissions.get("verified") is True or (
            isinstance(observed_actions, list)
            and any(isinstance(action, str) and action.strip() for action in observed_actions)
        )
        if not permission_status:
            permission_status = (
                "OBSERVED_ACTIONS_RECORDED" if permission_verified else "UNKNOWN"
            )
        data_flow = record.get("data_flow")
        data_flow = data_flow if isinstance(data_flow, dict) else {}
        flow_status = str(data_flow.get("status", "NOT_TESTED")).strip().upper()
        authentication_verified = str(auth_status).strip().upper() in {
            "VERIFIED",
            "VERIFIED_FOR_GITHUB_CONNECTOR",
        }
        flow_verified = (
            data_flow.get("verified") is True
            and flow_status in {"LIVE_TESTED", "VERIFIED"}
        )
        connection = (
            "VERIFIED"
            if authentication_verified and permission_verified and flow_verified
            else "UNVERIFIED"
        )
        capabilities = record.get("capabilities")
        if isinstance(capabilities, list) and capabilities:
            capability_status = "ASSESSED"
        elif isinstance(capabilities, dict):
            capability_status = capabilities.get("status", "UNKNOWN")
        else:
            capability_status = record.get("capability_status", "UNKNOWN")
        lines.append(
            f"- {name}: connection={connection}; capability={capability_status}; "
            f"authentication={auth_status}; permissions={permission_status}; "
            f"data_flow={flow_status}; "
            f"external_transfer={data_flow.get('external_transfer_occurred', 'UNKNOWN')}."
        )

    coordination = data.get("coordination")
    coordination = coordination if isinstance(coordination, dict) else {}
    lines.append(
        "Coordination: "
        f"status={coordination.get('status', 'UNKNOWN')}; "
        "structured_evidence_exchange="
        f"{coordination.get('structured_evidence_exchange_across_nine_platforms', 'UNKNOWN')}; "
        "external_model_data_transfer="
        f"{coordination.get('external_model_data_transfer_occurred', 'UNKNOWN')}."
    )
    lines.append(
        "Account existence, documentation, model names, or configured endpoints are not "
        "proof of a live connection. Require explicitly verified authentication, "
        "least-privilege permission, and successful data flow; preserve minority objections."
    )
    return "\n".join(lines)


def load_xrp_intelligence_status():
    """Load repository-authored mission and forecast readiness boundaries."""
    sections = []
    sources = (
        ("Current Barrot/XRP mission handoff", "BARROT_XRP_MISSION_HANDOFF.md", 10000),
        ("XRP point-in-time feature-store contract", "research/xrp_intelligence/feature-store-contract.md", 5000),
        ("XRP forecast-ledger contract", "research/xrp_intelligence/forecast-ledger-contract.md", 5000),
    )
    for label, path, limit in sources:
        try:
            content = Path(path).read_text(encoding="utf-8")[:limit]
        except (OSError, UnicodeError):
            continue
        if content.strip():
            sections.append(f"\n\n{label} (repository source; includes explicit unimplemented gates):\n{content}")
    return "".join(sections)

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
            real_lines.append(f"- {name}: {count} entries recorded by this counter (verify execution separately)")
        else:
            dead_sources.append(name)
    if not real_lines and not dead_sources:
        return ""
    out = ["\n\nYour real ingestion metrics (from config.json, filtered):"]
    out.extend(real_lines)
    if dead_sources:
        out.append(
            f"- No entries are recorded for: "
            f"{', '.join(dead_sources)}. The zero counter shows only that no "
            f"entries are recorded by this counter; it does not establish whether "
            f"implementation code exists or whether "
            f"another counter is authoritative. Do not cite "
            f"these as active without separate execution evidence."
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


def corroborate_repository_references(
    references,
    manifest_id=None,
):
    """Validate repository references against the current manifest."""
    root = Path(__file__).resolve().parents[1]
    corroborator = RepoStateCorroborator(root)
    manifest = corroborator.load_manifest()

    return corroborator.corroborate(
        manifest_id=manifest_id or manifest["manifest_id"],
        references=references,
    )


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
    "\n\nInfrastructure and provider constraints - verify current evidence before every action:\n"
    "- The known local phone target includes Termux on Android ARM64 without root or a local GPU; GitHub Actions runners are ephemeral. Treat these as local/CI constraints only. Do not infer that cloud GPU or provider capacity is available or unavailable without a current authenticated test.\n"
    "- The nine-platform capability map is authoritative for ChatGPT, Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle, and Databricks. Account creation, documentation, model labels, configured endpoints, or a successful GitHub read do not prove another platform is connected. Mark a connection verified only when authentication, least-privilege permissions, and end-to-end data flow are tested. Preserve external-transfer status; do not transfer private, credential-bearing, or user data without explicit authorization.\n"
    "- This script currently posts to the Groq Chat Completions endpoint. That identifies this script's configured inference backend only; it does not verify any of the nine platform connections. Test the current credential and response at runtime; never expose keys. Do not claim unsupported Groq embeddings.\n"
    "- Do not assume a free tier is permanent or unlimited. Verify current prices, quotas, retention, license, and provider terms before resource-intensive or paid use. Do not assume training or fine-tuning infrastructure exists without current execution evidence.\n"
    "- Prefer Python standard-library tools for small local tasks. Before adding ML frameworks, native audio libraries, or GPU dependencies, inspect current hardware, dependency compatibility, licensing, memory/compute requirements, and full-suite impact."
)


def write_answer_artifact(answer: str, output_dir: Path | str = "results/answers") -> Path:
    """Write a new answer artifact without overwriting an existing file."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    for attempt in range(5):
        output_path = directory / f"barrot_answer_{time.time_ns()}_{attempt}.md"
        try:
            with output_path.open("x", encoding="utf-8") as handle:
                handle.write(answer)
            return output_path
        except FileExistsError:
            continue
    raise FileExistsError("Could not allocate a unique Barrot answer artifact path")


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
        + load_mission_portfolio_status()
        + load_platform_capability_map()
        + format_memory_block(memory_entries)
        + load_signal_snapshot()
        + load_xrp_intelligence_status()
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
        "max_tokens": 2000,
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

    answer_path = write_answer_artifact(answer)
    print(f"\nSaved answer artifact: {answer_path}")

    append_memory(question, answer)

    print(answer)


if __name__ == "__main__":
    main()
