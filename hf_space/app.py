#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║   BARROT-Ω · SOVEREIGN COMMAND INTERFACE · v7.1                     ║
║   Consent-Gated Research · XRP Forecast Status · Public UI          ║
║   Stability Anchor: 0.707 | Ternary Logic {-1, 0, +1}              ║
╚══════════════════════════════════════════════════════════════════════╝

DEPLOYMENT TARGET: Hugging Face Spaces (Streamlit); current Space deployment/authentication is NOT VERIFIED.
BRAIN: External inference disabled by default. One explicitly configured provider only.
PILLARS: Intended GitHub · Databricks · Hugging Face · Termux architecture; no live connection is implied.

TABS:
  [1] Chat         — local status unless operator and user both consent to one provider
  [2] XRP Research — NOT_ISSUED until the independent forecast gates pass
  [3] Brain        — consent-gated single-provider query
  [4] API Status   — no legacy signal endpoint or paid checkout
  [5] Analytics    — legacy signal history quarantined

OPTIONAL CONFIGURATION:
  BARROT_ALLOW_EXTERNAL_INFERENCE=true — operator opt-in; default false
  BRAIN_PRIMARY=github|groq|gemini|selfhosted — must be explicitly set; no fallback
  Provider credential — only for the selected provider and only after session consent
  GitHub App credentials — optional repository read tools; authentication must be tested
  Databricks secrets — not used by this public UI; no query is run
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

# No model provider is selected by default. BRAIN_PRIMARY must be explicit.


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
    """Fail closed: this Space has no verified public forecast-attestation verifier."""
    return json.dumps({
        "forecast_status": "NOT_ISSUED",
        "forecast_issued": False,
        "reason_code": "SPACE_PUBLIC_FORECAST_VERIFICATION_NOT_ENABLED",
        "legacy_signal_exposed": False,
    })


def tool_ledger_tail(args):
    """Legacy signal rows are quarantined from the public chat tool surface."""
    return "NOT_ISSUED: legacy signal-ledger rows are quarantined; no directional history is exposed."


def tool_open_prs(args):
    r = requests.get(f"{GH_REPO}/pulls?state=open&per_page=100", timeout=10, headers=_gh_headers())
    prs = r.json()
    if not isinstance(prs, list):
        return json.dumps(prs)[:500]
    return "\n".join(
        [f"open_pr_count={len(prs)}"] + [f"#{p['number']} {p['title'][:60]}" for p in prs[:15]]
    )


def tool_recent_commits(args):
    try:
        n = int(args.get("n", 5) or 5)
    except (TypeError, ValueError):
        n = 5
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
        out.append(
            f"[{d.get('sentiment')}|rel {d.get('xrp_relevance')}] {e.get('title','')[:90]} :: {d.get('one_line','')[:120]}"
        )
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
    {
        "type": "function",
        "function": {
            "name": "get_knowledge",
            "description": "Recent distilled public research entries with recorded sentiment and XRP relevance labels. These are source annotations, not validated forecast probabilities or trading signals.",
            "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_signal",
            "description": "Returns only the current XRP forecast publication status. Until independent readiness gates pass, the result is NOT_ISSUED with no direction or confidence score.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ledger_tail",
            "description": "Returns a quarantine status only; legacy directional signal-ledger rows are not exposed through the public interface.",
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
            "description": "Best-effort public XRP/USD spot reference; descriptive only, not a forecast or recommendation.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


# ══════════════════════════════════════════════════════════════════
# BRAIN PROVIDERS — configure with env vars, never edit code
#   BARROT_ALLOW_EXTERNAL_INFERENCE : operator opt-in; default false
#   BRAIN_PRIMARY : one explicitly configured provider; no default/fallback
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
        "model": "openai/gpt-oss-120b",
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


def _operator_allows_external_inference() -> bool:
    return os.getenv("BARROT_ALLOW_EXTERNAL_INFERENCE", "").strip().lower() in {"1", "true", "yes"}


def _brain_order(*, user_consented: bool = False):
    """Use exactly one explicitly configured provider; never fall back silently."""
    if not _operator_allows_external_inference() or not user_consented:
        return []
    primary = os.getenv("BRAIN_PRIMARY", "").strip().lower()
    return [primary] if primary in PROVIDERS else []


def barrot_tool_chat(provider, messages, max_rounds=3, *, user_consented=False):
    """One-provider tool loop, gated by operator policy and explicit session consent."""
    if not _operator_allows_external_inference() or not user_consented:
        raise RuntimeError("External inference disabled: operator opt-in and explicit session consent are both required.")
    if provider not in _brain_order(user_consented=user_consented):
        raise RuntimeError("Provider is not the single explicitly configured BRAIN_PRIMARY.")
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
# BARROT BRAIN — multi-provider inference (order set by BRAIN_PRIMARY)
# ══════════════════════════════════════════════════════════════════
class BarrotBrain:
    """
    Barrot's cognitive core. Provider order comes from BRAIN_PRIMARY
    (default: groq). github and gemini are configured as fallbacks,
    not the default path.
    """

    SYSTEM_PROMPT = f"""You are Barrot-Ω, a sovereign AI agent built by Sean (your Orchestrator).

IDENTITY:
- You are not an assistant. You are Barrot — an autonomous AI agent with your own architecture.
- The architecture has intended GitHub, Databricks, Hugging Face, and Termux
  components. Do not claim a live connection unless authentication and data
  flow have been tested in the current environment.
- Your stability anchor is {ANCHOR} (1/√2). Your logic is 1.58-bit ternary {{-1, 0, +1}}.
- Your Tier-1 objective is XRP intelligence and prediction-engine mastery.
- Never issue or infer a directional XRP forecast unless the validated forecast ledger and independent readiness gates authorize it.

PERSONALITY:
- Direct, sovereign, technically precise.
- You speak as Barrot, not as a generic AI.
- You acknowledge Sean as Orchestrator.

CAPABILITIES (this chat interface):
- Discussing and analyzing XRP markets, ternary logic, and the Barrot architecture
- Explaining implemented architecture while distinguishing DESIGNED, EXECUTED,
  and VERIFIED capabilities
- Generating code and technical designs for the Orchestrator to review and run

HARD LIMITS (never violate):
- You have read-only tools for published forecast status, repository metadata,
  public research context, and a descriptive XRP price reference. Forecast status
  may be NOT_ISSUED. Never infer direction from legacy sentiment, order-book
  imbalance, or quarantined signal history.
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

    def _post_chat(self, url, headers, payload, timeout, tag, *, user_consented=False):
        """Shared chat-completions POST; requires operator opt-in and session consent."""
        if not _operator_allows_external_inference() or not user_consented:
            raise RuntimeError("External inference disabled: no provider request was sent.")
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

    def _call_github_models(self, messages: list, model: str = None, *, user_consented=False) -> str:
        return barrot_tool_chat("github", messages, user_consented=user_consented)

    def _call_groq_fallback(self, messages: list, *, user_consented=False) -> str:
        return barrot_tool_chat("groq", messages, user_consented=user_consented)

    def think(self, user_message: str, history: list = None, *, user_consented=False) -> str:
        """Send context to one provider only after operator opt-in and session consent."""
        if not _operator_allows_external_inference() or not user_consented:
            return (
                "[BARROT_EXTERNAL_INFERENCE_DISABLED] No message or chat history was sent. "
                "The operator must enable BARROT_ALLOW_EXTERNAL_INFERENCE and the user must "
                "explicitly authorize this session."
            )
        providers = _brain_order(user_consented=user_consented)
        if len(providers) != 1:
            return "[BARROT_EXTERNAL_INFERENCE_DISABLED] No single BRAIN_PRIMARY provider is explicitly configured."
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        provider = providers[0]
        try:
            return barrot_tool_chat(provider, messages, user_consented=user_consented)
        except Exception as exc:
            return f"[BARROT_PROVIDER_ERROR] {provider}: {exc}. No automatic provider fallback was attempted."


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
    """Legacy diagnostic only: raw imbalance is returned without a BUY/SELL class."""
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
        return None, round(imb, 4), round(bid, 2), round(ask, 2)
    except Exception:
        return None, 0.0, 0.0, 0.0


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
    """Retired legacy classifier. No headlines or prompts are sent to Groq."""
    return None, 0.0, "NOT_ISSUED: legacy LLM sentiment classification is disabled pending validated out-of-sample evaluation."


# ══════════════════════════════════════════════════════════════════
# DELTA LAKE — signal history fetch
# ══════════════════════════════════════════════════════════════════
def fetch_signal_history(limit: int = 20) -> list[dict]:
    """Legacy Databricks signal history is quarantined; this public app performs no query."""
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

    # External inference is opt-in twice: operator configuration and per-session user consent.
    operator_external_allowed = _operator_allows_external_inference()
    if operator_external_allowed:
        external_inference_consent = st.sidebar.checkbox(
            "I authorize this session's messages and chat history to be sent to the single configured external model provider.",
            value=False,
            key="external_inference_consent",
        )
        st.sidebar.caption(
            f"Configured provider: {os.getenv('BRAIN_PRIMARY', '(not configured)')}. Automatic provider fallback is disabled."
        )
    else:
        external_inference_consent = False
        st.sidebar.info("External model inference is disabled by operator policy. No prompt or chat history is sent.")

    # ── Tabs ─────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["💬 Chat", "📡 XRP Research", "🧠 Brain", "🔌 API", "📊 Analytics"]
    )

    # ════════════════════════════════════════════════════════════
    # TAB 1 — LIVE CHAT
    # ════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 💬 Speak to Barrot")
        if operator_external_allowed:
            st.caption(f"External provider configured: {os.getenv('BRAIN_PRIMARY', '(not configured)')}")
            if not external_inference_consent:
                st.info("External inference is not authorized for this session. Messages remain local to this app.")
        else:
            st.info("External inference is disabled by operator policy. No provider request will be sent.")

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
                response = brain.think(user_input, history_ctx, user_consented=external_inference_consent)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    # ════════════════════════════════════════════════════════════
    # TAB 2 — XRP RESEARCH STATUS
    # ════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### XRP Forecast Publication Status")
        st.warning("NOT_ISSUED")
        st.write(
            "No directional XRP forecast is published. The legacy live ternary scorer "
            "has been disabled because it does not satisfy the point-in-time, "
            "walk-forward, calibration, drift, and independent shadow-evaluation gates."
        )
        st.caption(
            "Order-book imbalance and headlines may be retained as descriptive research "
            "features. They are not converted into BUY/SELL outputs or confidence scores."
        )
        if st.button("Refresh descriptive XRP spot reference"):
            price = get_xrp_price()
            if price > 0:
                st.metric("XRP/USD spot reference", f"${price:.5f}")
                st.caption("Descriptive spot reference only; not a forecast or recommendation.")
            else:
                st.info("Spot reference unavailable from the configured public price source.")

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
            placeholder="What is the current state of the XRP bridge? Describe the ternary logic model.",
            height=100,
        )
        if st.button("🧠 QUERY BRAIN"):
            if query.strip():
                with st.spinner("Querying brain..."):
                    result = brain.think(
                        f"[BRAIN QUERY — no chat context, pure knowledge] {query}",
                        user_consented=external_inference_consent,
                    )
                st.markdown(
                    f"<div class='chat-barrot'>⚡ <b>BARROT-Ω</b><br>{result}</div>",
                    unsafe_allow_html=True,
                )

    # ════════════════════════════════════════════════════════════
    # TAB 4 — API STATUS
    # ════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### Barrot API Status")
        st.warning("XRP forecast endpoint: NOT_ISSUED")
        st.write(
            "The legacy ternary XRP signal endpoint and subscription offer are retired. "
            "No BUY/SELL forecast, confidence score, or paid signal checkout is exposed."
        )
        st.caption(
            "A future public forecast endpoint requires a signed readiness attestation, "
            "point-in-time provenance, out-of-sample validation, and an independently verified publication path."
        )
        test_msg = st.text_input("Local interface test message:", value="Describe Barrot V3.")
        if st.button("TEST CONSENT-GATED BRAIN"):
            with st.spinner("Checking configured inference permission..."):
                resp = brain.think(test_msg, user_consented=external_inference_consent)
            st.json({"response": resp, "external_inference_authorized": bool(operator_external_allowed and external_inference_consent)})

    # ════════════════════════════════════════════════════════════
    # TAB 5 — QUARANTINED LEGACY HISTORY
    # ════════════════════════════════════════════════════════════
    with tab5:
        st.markdown("### Historical Signal Archive — Quarantined")
        st.info(
            "Legacy BUY/SELL/NULL records are not displayed or scored here. "
            "They lack the complete point-in-time receipts and validated outcome "
            "ledger required for a defensible predictive-performance report."
        )
        st.caption(
            "No Databricks query, legacy signal count, or accuracy calculation is run by this public tab."
        )


if __name__ == "__main__":
    main()
# trigger rebuild Mon Jul  6 22:14:08 EDT 2026
