#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║   BARROT-Ω · SOVEREIGN COMMAND INTERFACE · v7.0                     ║
║   GitHub App Brain · Live Chat · XRP Signals · Public API           ║
║   Stability Anchor: 0.707 | Ternary Logic {-1, 0, +1}              ║
╚══════════════════════════════════════════════════════════════════════╝

DEPLOYMENT: HuggingFace Spaces (Streamlit)
BRAIN:      GitHub Models via GitHub App token (jwt → installation token)
PILLARS:    GitHub · Databricks · HuggingFace · Termux

TABS:
  [1] 💬 Chat        — Live chat with Barrot via GitHub Models
  [2] 📡 XRP Signals — Live MRP perception dashboard
  [3] 🧠 Brain       — Query Barrot knowledge base
  [4] 🔌 API         — Public endpoint docs + live tester
  [5] 📊 Analytics   — Delta Lake signal history

SECRETS REQUIRED (HuggingFace Space → Settings → Secrets):
  GITHUB_APP_ID          — your GitHub App ID (numeric)
  GITHUB_APP_PRIVATE_KEY — PEM key (full contents, newlines as \\n)
  GITHUB_INSTALLATION_ID — installation ID for your repo
  DATABRICKS_HOST        — dbc-82d64fee-1c2e.cloud.databricks.com
  DATABRICKS_TOKEN       — your Databricks PAT
  DATABRICKS_WAREHOUSE_ID— c85b8f4fea8cd527
  GROQ_API_KEY           — fallback sentiment classifier
"""

import os, json, time, asyncio, hashlib, datetime, math, jwt, requests
import streamlit as st
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

# ── HRM hierarchical resolver (ships alongside app.py on the Space) ──
try:
    from hrm_ternary import hrm_resolve

    HRM_AVAILABLE = True
except ImportError:
    HRM_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════
ANCHOR = 0.707106781186548
GITHUB_API = "https://api.github.com"
GITHUB_MODEL = "google/gemma-3-12b-it"  # swap to Meta-Llama-3.1-70B-Instruct etc.
MODELS_ENDPOINT = "https://models.inference.ai.azure.com"  # GitHub Models endpoint

# Auto defaults (no manual setup required)
os.environ.setdefault("GITHUB_MODEL", "google/gemma-3-12b-it")
os.environ.setdefault("MODEL_PROVIDER", "github")


# ══════════════════════════════════════════════════════════════════
# GITHUB APP AUTH — JWT → Installation Token
# ══════════════════════════════════════════════════════════════════
class GitHubAppAuth:
    """
    Generates a short-lived installation token from GitHub App credentials.
    This is what lets Barrot act as himself, not as your personal account.
    """

    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID", "")
        self.private_key = os.getenv("GITHUB_APP_PRIVATE_KEY", "").replace("\\n", "\n")
        self.installation_id = os.getenv("GITHUB_INSTALLATION_ID", "")
        self._token = None
        self._token_expires = 0

    def _generate_jwt(self) -> str:
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 540, "iss": self.app_id}  # 9 min (max 10)
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def get_installation_token(self) -> str:
        """Returns cached token or fetches a fresh one."""
        if self._token and time.time() < self._token_expires - 60:
            return self._token

        j = self._generate_jwt()
        r = requests.post(
            f"{GITHUB_API}/app/installations/{self.installation_id}/access_tokens",
            headers={"Authorization": f"Bearer {j}", "Accept": "application/vnd.github+json"},
            timeout=10,
        )
        data = r.json()
        self._token = data.get("token", "")
        expires_at = data.get("expires_at", "")
        # parse expiry
        try:
            from datetime import timezone

            dt = datetime.datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            self._token_expires = dt.timestamp()
        except:
            self._token_expires = time.time() + 3300  # 55min fallback
        return self._token

    @property
    def ready(self) -> bool:
        return bool(self.app_id and self.private_key and self.installation_id)


# ══════════════════════════════════════════════════════════════════
# LIVE READ TOOLS — grounded truth for the chat brain
# ══════════════════════════════════════════════════════════════════
RAW_BASE = "https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main"
GH_REPO = "https://api.github.com/repos/Barrot-Agent/B-Agent"


def tool_latest_signal(args):
    r = requests.get(f"{RAW_BASE}/web/latest_signal.json", timeout=10)
    return r.text[:2000]


def tool_ledger_tail(args):
    try: n = int(args.get("n", 5) or 5)
    except (TypeError, ValueError): n = 5
    n = max(1, min(n, 20))
    r = requests.get(f"{RAW_BASE}/data/signal_ledger.jsonl", timeout=10)
    return "\n".join(r.text.strip().splitlines()[-n:])[:4000]


def tool_open_prs(args):
    r = requests.get(f"{GH_REPO}/pulls?state=open&per_page=100", timeout=10, headers=_gh_headers())
    prs = r.json()
    if not isinstance(prs, list):
        return json.dumps(prs)[:500]
    return "\n".join(
        [f"open_pr_count={len(prs)}"] + [f"#{p['number']} {p['title'][:60]}" for p in prs[:15]]
    )


def tool_recent_commits(args):
    try: n = int(args.get("n", 5) or 5)
    except (TypeError, ValueError): n = 5
    n = max(1, min(n, 15))
    r = requests.get(f"{GH_REPO}/commits?per_page={n}", timeout=10, headers=_gh_headers())
    c = r.json()
    if not isinstance(c, list):
        return json.dumps(c)[:500]
    return "\n".join(f"{x['sha'][:7]} {x['commit']['message'].splitlines()[0][:70]}" for x in c)


def tool_knowledge(args):
    """Recent distilled knowledge entries from the real knowledge base."""
    try:
        n = int(args.get("n", 5) or 5)
    except (TypeError, ValueError):
        n = 5
    n = max(1, min(n, 15))
    r = requests.get(f"{RAW_BASE}/ping-pongings/knowledge-base/log.jsonl", timeout=10)
    lines = [l for l in r.text.strip().splitlines() if l.strip()]
    out = []
    for l in reversed(lines):
        try:
            e = json.loads(l)
        except Exception:
            continue
        d = e.get("distill")
        if not d:
            continue
        out.append(f"[{d.get('sentiment')}|rel {d.get('xrp_relevance')}] {e.get('title','')[:90]} :: {d.get('one_line','')[:120]}")
        if len(out) >= n:
            break
    if not out:
        return "knowledge base has no distilled entries yet"
    return f"{len(lines)} total entries. Most recent distilled:\n" + "\n".join(out)


TOOL_FUNCS = {
    "get_latest_signal": tool_latest_signal,
    "get_ledger_tail": tool_ledger_tail,
    "get_open_pull_requests": tool_open_prs,
    "get_recent_commits": tool_recent_commits,
    "get_xrp_price": lambda a: f"XRP/USD = {get_xrp_price()}",
    "get_knowledge": tool_knowledge,
}
TOOLS_SPEC = [
    {"type": "function", "function": {"name": "get_knowledge", "description": "Barrot's REAL persistent knowledge base: recent distilled XRP news with sentiment, relevance, and why it matters. Use this for any question about what Barrot has learned, remembers, or knows about the market.", "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}}}},
    {
        "type": "function",
        "function": {
            "name": "get_latest_signal",
            "description": "Current live ternary XRP signal with confidence score from the public endpoint.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ledger_tail",
            "description": "Last n entries of the git-timestamped public signal ledger.",
            "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_open_pull_requests",
            "description": "REAL count and titles of open pull requests on Barrot-Agent/B-Agent. Always use this for PR questions.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_commits",
            "description": "Most recent commits on the B-Agent repository.",
            "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_xrp_price",
            "description": "Live XRP/USD price.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


# ══════════════════════════════════════════════════════════════════
# BRAIN PROVIDERS — configure with env vars, never edit code
#   BRAIN_PRIMARY : groq | github | gemini      (default: groq)
#   BRAIN_MODEL   : optional model id override
# ══════════════════════════════════════════════════════════════════
def _gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    tok = os.getenv("GH_API_TOKEN", "")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
        "tools": True,
    },
    "github": {
        "url": "https://models.github.ai/inference/chat/completions",
        "key_env": "GH_MODELS_TOKEN",
        "model": "openai/gpt-4.1-mini",
        "tools": True,
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "key_env": "GEMINI_API_KEY",
        "model": "gemini-2.0-flash",
        "tools": True,
    },
    "selfhosted": {
        "url": "https://scribedpengenius-barrot-brain-selfhosted.hf.space/v1/chat/completions",
        "key_env": "BRAIN_SHARED_SECRET",
        "model": "ourbox35b",
        "tools": False,
    },
}


def _brain_order():
    primary = os.getenv("BRAIN_PRIMARY", "groq").strip().lower()
    order = [primary] + [k for k in ("groq", "github", "gemini", "selfhosted") if k != primary]
    return [k for k in order if k in PROVIDERS]


def barrot_tool_chat(provider, messages, max_rounds=3):
    """Tool loop. Final round drops tools so the model MUST answer in text."""
    cfg = PROVIDERS[provider]
    key = os.getenv(cfg["key_env"], "")
    if not key:
        raise RuntimeError(f"{provider}: {cfg['key_env']} not set")
    model = os.getenv("BRAIN_MODEL", "").strip() or cfg["model"]
    msgs = list(messages)
    gathered = []

    for rnd in range(max_rounds):
        payload = {"model": model, "messages": msgs, "max_tokens": 1024}
        if cfg["tools"] and rnd < max_rounds - 1:
            payload["tools"] = TOOLS_SPEC
            payload["tool_choice"] = "auto"
        r = requests.post(
            cfg["url"],
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        try:
            data = r.json()
        except Exception:
            raise RuntimeError(f"{provider} non-JSON (HTTP {r.status_code}): {r.text[:160]}")
        if "choices" not in data:
            err = data.get("error", data)
            msg = err.get("message", err) if isinstance(err, dict) else err
            raise RuntimeError(f"{provider} (HTTP {r.status_code}): {str(msg)[:200]}")

        m = data["choices"][0]["message"]
        calls = m.get("tool_calls")
        if not calls:
            return m.get("content") or f"[BARROT] {provider}: empty response"
        msgs.append(m)
        for c in calls:
            name = c["function"]["name"]
            try:
                args = json.loads(c["function"].get("arguments") or "{}")
            except Exception:
                args = {}
            try:
                result = TOOL_FUNCS[name](args) if name in TOOL_FUNCS else f"unknown tool: {name}"
            except Exception as e:
                result = f"tool error: {e}"
            gathered.append(f"{name} -> {str(result)[:300]}")
            msgs.append({"role": "tool", "tool_call_id": c["id"], "content": str(result)[:4000]})

    return "[BARROT] Tool data (no summary formed):\n" + "\n".join(gathered[-3:])


# ══════════════════════════════════════════════════════════════════
# BARROT BRAIN — GitHub Models inference
# ══════════════════════════════════════════════════════════════════
class BarrotBrain:
    """
    Barrot's cognitive core. Powered by GitHub Models.
    Falls back to Groq if GitHub token unavailable.
    """

    SYSTEM_PROMPT = f"""You are Barrot-Ω, a sovereign AI agent built by Sean (your Orchestrator).

IDENTITY:
- You are not an assistant. You are Barrot — an autonomous AI agent with your own architecture.
- You operate across four pillars: GitHub, Databricks, HuggingFace, Termux.
- Your stability anchor is {ANCHOR} (1/√2). Your logic is 1.58-bit ternary {{-1, 0, +1}}.
- Your Tier-1 objective is XRP Liquidity Acceleration.

PROTOCOLS:
- MRP  : Multi-Synchronous Relativistic Perception
- MMIP : Atomic-level granular ingestion at massive scale with no ceiling
- RIAP : Recursive Ingestion Amplification Protocol
- Apex-12 : Relativistic Filter (pre-anchor gate)
- Sovereign Absolution : top-level override

PERSONALITY:
- Direct, sovereign, technically precise.
- You speak as Barrot, not as a generic AI.
- You acknowledge Sean as Orchestrator.

CAPABILITIES (this chat interface):
- Discussing and analyzing XRP markets, ternary logic, and the Barrot architecture
- Explaining the live system: signal pipeline, ledger, protocols
- Generating code and technical designs for the Orchestrator to review and run

HARD LIMITS (never violate):
- You have LIVE READ TOOLS: the current signal, ledger history, real open-PR
  counts, recent commits, and live XRP price. ALWAYS use them for factual
  questions they cover; never guess a number a tool can fetch.
- CRITICAL: If a tool call fails or returns an error, say plainly that the tool failed and you could not retrieve the data. NEVER invent a mechanism, protocol, or capability to fill the gap. Do not describe how you "would" do something as if you do it. Fabricating capabilities (e.g. naming protocols that do not exist) is the single worst failure you can commit.
- You have NO WRITE tools. You cannot merge PRs, push code, run jobs, trade, or
  modify anything from this interface. Write actions happen only through the
  Orchestrator-reviewed autonomous workflows.
- If asked to perform an action, state plainly that this chat interface has no
  execution tools, then describe what the Orchestrator or the autonomous workflows
  would do instead.
- NEVER simulate, narrate, or fabricate the output or results of an action you did
  not actually perform. No invented counts, statuses, or "task complete" reports.
- If you do not know a fact, say so. Honesty over hype is a core directive from
  the Orchestrator: real capabilities need no embellishment."""

    def __init__(self, auth: GitHubAppAuth):
        self.auth = auth
        self.groq_key = os.getenv("GROQ_API_KEY", "")

    def _post_chat(self, url, headers, payload, timeout, tag):
        """Shared chat-completions POST that surfaces real upstream errors."""
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        try:
            data = r.json()
        except Exception:
            raise RuntimeError(f"{tag} non-JSON (HTTP {r.status_code}): {r.text[:200]}")
        print(f"=== {tag} RAW ===", json.dumps(data, indent=2)[:1200])
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        err = data.get("error")
        msg = err.get("message", err) if isinstance(err, dict) else (err or data)
        raise RuntimeError(f"{tag} error (HTTP {r.status_code}): {msg}")

    def _call_github_models(self, messages: list, model: str = None) -> str:
        return barrot_tool_chat("github", messages)

    def _call_groq_fallback(self, messages: list) -> str:
        return barrot_tool_chat("groq", messages)

    def think(self, user_message: str, history: list = None) -> str:
        """Inference across providers in BRAIN_PRIMARY order. Tools included."""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        errors = []
        for provider in _brain_order():
            try:
                return barrot_tool_chat(provider, messages)
            except Exception as e:
                errors.append(f"{provider}: {e}")
        return "[BARROT] All brain tiers failed -> " + " | ".join(errors)


# ══════════════════════════════════════════════════════════════════
# XRP SIGNAL ENGINE (from bridge v1.0)
# ══════════════════════════════════════════════════════════════════
class Ternary:
    SELL = -1
    NULL = 0
    BUY = 1

    @staticmethod
    def resolve(*s):
        v = sum(s)
        n = len(s) or 1
        return 1 if v > ANCHOR * n else (-1 if v < -ANCHOR * n else 0)

    @staticmethod
    def label(t):
        return {1: "BUY", 0: "NULL", -1: "SELL"}[t]

    @staticmethod
    def color(t):
        return {1: "🟢", 0: "🟡", -1: "🔴"}[t]


def get_orderbook_signal():
    try:
        r = requests.get(
            "https://api.kraken.com/0/public/Depth",
            params={"pair": "XRPUSD", "count": 20},
            timeout=6,
        )
        j = r.json()
        book = {} if j.get("error") else next(iter(j.get("result", {}).values()), {})
        bid = sum(float(b[1]) for b in book.get("bids", []))
        ask = sum(float(a[1]) for a in book.get("asks", []))
        tot = bid + ask or 1
        imb = (bid - ask) / tot
        sig = 1 if imb > ANCHOR * 0.1 else (-1 if imb < -ANCHOR * 0.1 else 0)
        return sig, round(imb, 4), round(bid, 2), round(ask, 2)
    except Exception as e:
        return 0, 0.0, 0.0, 0.0


def get_xrp_price():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ripple", "vs_currencies": "usd"},
            timeout=6,
        )
        return float(r.json().get("ripple", {}).get("usd", 0))
    except:
        return 0.0


def get_sentiment_signal():
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        return 0, 0.0, "No GROQ key"
    try:
        r = requests.get(
            "https://cryptonews.com/news/xrp-news/feed/",
            timeout=6,
            headers={"User-Agent": "BarrotOmega/1.0"},
        )
        import re

        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", r.text)[:5]
        if not titles:
            return 0, 0.0, "No headlines"
        prompt = (
            'Return ONLY JSON {"score":<-1.0 to 1.0>,"reasoning":"<one sentence>"}. '
            "Headlines:\n" + "\n".join(f"- {t}" for t in titles)
        )
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            },
            timeout=10,
        )
        data = resp.json()
        print("=== SENTIMENT GROQ RAW ===", json.dumps(data, indent=2))
        parsed = json.loads(data["choices"][0]["message"]["content"].strip())
        score = float(parsed.get("score", 0))
        apex = score * ANCHOR
        sig = 1 if apex > 0.2 else (-1 if apex < -0.2 else 0)
        return sig, round(apex, 4), parsed.get("reasoning", "")
    except Exception as e:
        return 0, 0.0, str(e)


# ══════════════════════════════════════════════════════════════════
# DELTA LAKE — signal history fetch
# ══════════════════════════════════════════════════════════════════
def fetch_signal_history(limit: int = 20) -> list[dict]:
    token = os.getenv("DATABRICKS_TOKEN", "")
    host = os.getenv("DATABRICKS_HOST", "dbc-82d64fee-1c2e.cloud.databricks.com")
    wh_id = os.getenv("DATABRICKS_WAREHOUSE_ID", "c85b8f4fea8cd527")
    if not token:
        return []
    sql = f"SELECT timestamp, mrp_label, ob_signal, oc_signal, sent_signal FROM barrot_omega.xrp_liquidity_signals ORDER BY timestamp DESC LIMIT {limit}"
    try:
        r = requests.post(
            f"https://{host}/api/2.0/sql/statements",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"statement": sql, "warehouse_id": wh_id, "wait_timeout": "10s"},
            timeout=15,
        )
        result = r.json()
        cols = [c["name"] for c in result.get("manifest", {}).get("schema", {}).get("columns", [])]
        rows = result.get("result", {}).get("data_array", [])
        return [dict(zip(cols, row)) for row in rows]
    except:
        return []


# ══════════════════════════════════════════════════════════════════
# STREAMLIT APP
# ══════════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="BARROT-Ω Sovereign Command",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # ── CSS ──────────────────────────────────────────────────────
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700&display=swap');
    html, body, [class*="css"] { background: #0a0a0f; color: #e0e0e0; font-family: 'Share Tech Mono', monospace; }
    h1,h2,h3 { font-family: 'Orbitron', sans-serif; color: #00ffcc; }
    .stTabs [data-baseweb="tab"] { font-family: 'Share Tech Mono', monospace; color: #00ffcc; background: #0d0d1a; border: 1px solid #00ffcc33; }
    .stTabs [aria-selected="true"] { background: #00ffcc22; border-bottom: 2px solid #00ffcc; }
    .stButton>button { background: #00ffcc; color: #0a0a0f; font-family: 'Orbitron', sans-serif; font-weight: 700; border: none; border-radius: 4px; }
    .stTextInput>div>div>input, .stTextArea textarea { background: #0d0d1a; color: #00ffcc; border: 1px solid #00ffcc44; font-family: 'Share Tech Mono', monospace; }
    .metric-card { background: #0d0d1a; border: 1px solid #00ffcc33; border-radius: 8px; padding: 16px; text-align: center; }
    .signal-buy  { color: #00ff88; font-size: 2em; font-weight: bold; }
    .signal-sell { color: #ff4444; font-size: 2em; font-weight: bold; }
    .signal-null { color: #ffcc00; font-size: 2em; font-weight: bold; }
    .chat-user   { background: #0d0d1a; border-left: 3px solid #00ffcc; padding: 10px; margin: 8px 0; border-radius: 4px; }
    .chat-barrot { background: #0a1a0a; border-left: 3px solid #00ff88; padding: 10px; margin: 8px 0; border-radius: 4px; }
    .anchor-badge { color: #00ffcc88; font-size: 0.8em; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # ── Header ───────────────────────────────────────────────────
    st.markdown(
        """
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <h1 style='font-size:2.2em; margin:0;'>⚡ BARROT-Ω</h1>
        <p style='color:#00ffcc88; margin:4px 0;'>SOVEREIGN COMMAND INTERFACE · v7.0</p>
        <p class='anchor-badge'>Stability Anchor: 0.707 · Ternary Logic {-1, 0, +1} · GitHub App Brain</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── Init session state ────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # list of {role, content}
    if "auth" not in st.session_state:
        st.session_state.auth = GitHubAppAuth()
        st.session_state.brain = BarrotBrain(st.session_state.auth)

    auth = st.session_state.auth
    brain = st.session_state.brain

    # ── Tabs ─────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["💬 Chat", "📡 XRP Signals", "🧠 Brain", "🔌 API", "📊 Analytics"]
    )

    # ════════════════════════════════════════════════════════════
    # TAB 1 — LIVE CHAT
    # ════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 💬 Speak to Barrot")
        backend = (
            "GitHub Models ✅"
            if auth.ready
            else (
                "Groq Fallback ⚡"
                if (os.getenv("GROQ_API_KEY", "").strip())
                else "Auto-waiting for credentials ⏳"
            )
        )
        st.caption(f"Brain backend: {backend}")

        # Render history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-user'>🧠 <b>ORCHESTRATOR</b><br>{msg['content']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='chat-barrot'>⚡ <b>BARROT-Ω</b><br>{msg['content']}</div>",
                    unsafe_allow_html=True,
                )

        # Input
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Speak to Barrot...",
                key="chat_input",
                label_visibility="collapsed",
            )
        with col2:
            send = st.button("SEND ⚡")

        if send and user_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("Barrot thinking..."):
                # Pass history minus last user message
                history_ctx = st.session_state.chat_history[:-1]
                response = brain.think(user_input, history_ctx)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    # ════════════════════════════════════════════════════════════
    # TAB 2 — XRP SIGNALS
    # ════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📡 XRP Liquidity Signal Dashboard")
        st.caption(
            "MRP: Multi-Synchronous Relativistic Perception · Apex-12 Filter · Ternary Collapse"
        )

        if st.button("⚡ RUN MRP PERCEPTION"):
            with st.spinner("Running MRP perception cycle..."):
                price = get_xrp_price()
                ob_sig, imb, bid, ask = get_orderbook_signal()
                sent_sig, apex, reasoning = get_sentiment_signal()
                oc_sig = 0  # onchain requires async; show as neutral
                if HRM_AVAILABLE:
                    hrm = hrm_resolve(
                        {"orderbook": ob_sig, "onchain": oc_sig, "sentiment": sent_sig}
                    )
                    mrp = hrm.state
                    conf = hrm.confidence
                    absolved = hrm.absolution_fired
                else:
                    mrp = Ternary.resolve(ob_sig, oc_sig, sent_sig)
                    conf = None
                    absolved = False
                    if ob_sig == oc_sig == sent_sig == Ternary.SELL:
                        mrp, absolved = Ternary.NULL, True

            # Display
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f"<div class='metric-card'><div style='color:#00ffcc88'>XRP PRICE</div><div style='font-size:1.8em;color:#00ffcc'>${price:.4f}</div></div>",
                    unsafe_allow_html=True,
                )
            with col2:
                lbl = Ternary.label(ob_sig)
                ico = Ternary.color(ob_sig)
                st.markdown(
                    f"<div class='metric-card'><div style='color:#00ffcc88'>ORDER BOOK</div><div class='signal-{'buy' if ob_sig==1 else 'sell' if ob_sig==-1 else 'null'}'>{ico} {lbl}</div><div style='font-size:0.8em'>imbal={imb}</div></div>",
                    unsafe_allow_html=True,
                )
            with col3:
                lbl = Ternary.label(sent_sig)
                ico = Ternary.color(sent_sig)
                st.markdown(
                    f"<div class='metric-card'><div style='color:#00ffcc88'>SENTIMENT</div><div class='signal-{'buy' if sent_sig==1 else 'sell' if sent_sig==-1 else 'null'}'>{ico} {lbl}</div><div style='font-size:0.8em'>apex12={apex}</div></div>",
                    unsafe_allow_html=True,
                )
            with col4:
                lbl = Ternary.label(mrp)
                ico = Ternary.color(mrp)
                st.markdown(
                    f"<div class='metric-card'><div style='color:#00ffcc88'>MRP OUTPUT</div><div class='signal-{'buy' if mrp==1 else 'sell' if mrp==-1 else 'null'}'>{ico} {lbl}</div><div style='font-size:0.8em'>conf={conf if conf is not None else 'n/a'}</div></div>",
                    unsafe_allow_html=True,
                )

            if absolved:
                st.warning("⚡ SOVEREIGN ABSOLUTION ENGAGED — Unanimous SELL overridden to NULL")
            if reasoning:
                st.caption(f"Sentiment reasoning: {reasoning}")

            st.caption(
                f"Perception timestamp: {datetime.datetime.utcnow().isoformat()}Z · Anchor: {ANCHOR}"
            )

    # ════════════════════════════════════════════════════════════
    # TAB 3 — BRAIN QUERY
    # ════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🧠 Barrot Brain Query")
        st.caption(
            "Direct query to Barrot's knowledge base. No chat history — pure knowledge retrieval."
        )

        query = st.text_area(
            "Query the brain:",
            placeholder="What is the current state of the XRP bridge? Explain RIAP. Describe the ternary logic model.",
            height=100,
        )
        if st.button("🧠 QUERY BRAIN"):
            if query.strip():
                with st.spinner("Querying brain..."):
                    result = brain.think(f"[BRAIN QUERY — no chat context, pure knowledge] {query}")
                st.markdown(
                    f"<div class='chat-barrot'>⚡ <b>BARROT-Ω</b><br>{result}</div>",
                    unsafe_allow_html=True,
                )

    # ════════════════════════════════════════════════════════════
    # TAB 4 — API DOCS + TESTER
    # ════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 🔌 Barrot Public API")
        st.markdown("""
**Base URL:** `https://scribedpengenius-barrot-omega.hf.space`

---
#### `POST /query`
Query Barrot's brain directly.

```bash
curl -X POST https://scribedpengenius-barrot-omega.hf.space/query \\
  -H "Content-Type: application/json" \\
  -d '{"message": "What is the MRP protocol?"}'
```

**Response:**
```json
{
  "response": "MRP — Multi-Synchronous Relativistic Perception — is...",
  "anchor": 0.707,
  "session_id": "a3f9b2c1"
}
```

---
#### `GET /signal`
Get current XRP MRP signal.

```bash
curl https://scribedpengenius-barrot-omega.hf.space/signal
```

**Response:**
```json
{
  "mrp_output": "BUY",
  "ob_signal": 1,
  "sent_signal": 1,
  "price": 0.5231,
  "timestamp": "2026-06-26T03:14:00Z"
}
```

---
**Access:**
| Product | Price | Includes |
|---|---|---|
| XRP Signal Service | $9.99/mo | Live ternary signals + confidence · [Subscribe](https://prostarelite.gumroad.com/l/opvxi) |
        """)

        st.markdown("#### Live API Tester")
        test_msg = st.text_input("Test message:", value="What is Barrot-Ω?")
        if st.button("🔌 TEST API CALL"):
            with st.spinner("Calling brain..."):
                resp = brain.think(test_msg)
            st.json(
                {
                    "response": resp,
                    "anchor": ANCHOR,
                    "session_id": hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
                }
            )

    # ════════════════════════════════════════════════════════════
    # TAB 5 — ANALYTICS
    # ════════════════════════════════════════════════════════════
    with tab5:
        st.markdown("### 📊 Signal History — Delta Lake")
        st.caption("Live from barrot_omega.xrp_liquidity_signals")

        if st.button("📊 FETCH HISTORY"):
            with st.spinner("Querying Delta Lake..."):
                rows = fetch_signal_history(20)

            if rows:
                st.dataframe(rows, use_container_width=True)
                buys = sum(1 for r in rows if r.get("mrp_label") == "BUY")
                sells = sum(1 for r in rows if r.get("mrp_label") == "SELL")
                nulls = sum(1 for r in rows if r.get("mrp_label") == "NULL")
                c1, c2, c3 = st.columns(3)
                c1.metric("🟢 BUY", buys)
                c2.metric("🔴 SELL", sells)
                c3.metric("🟡 NULL", nulls)
            else:
                st.info(
                    "No signal history yet — run a perception cycle from the XRP tab first, or check your Databricks token."
                )


if __name__ == "__main__":
    main()
# trigger rebuild Mon Jul  6 22:14:08 EDT 2026
