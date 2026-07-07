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
ANCHOR          = 0.707106781186548
GITHUB_API      = "https://api.github.com"
GITHUB_MODEL    = "gpt-4o"          # swap to Meta-Llama-3.1-70B-Instruct etc.
MODELS_ENDPOINT = "https://models.inference.ai.azure.com"   # GitHub Models endpoint

# ══════════════════════════════════════════════════════════════════
# GITHUB APP AUTH — JWT → Installation Token
# ══════════════════════════════════════════════════════════════════
class GitHubAppAuth:
    """
    Generates a short-lived installation token from GitHub App credentials.
    This is what lets Barrot act as himself, not as your personal account.
    """
    def __init__(self):
        self.app_id          = os.getenv("GITHUB_APP_ID", "")
        self.private_key     = os.getenv("GITHUB_APP_PRIVATE_KEY", "").replace("\\n", "\n")
        self.installation_id = os.getenv("GITHUB_INSTALLATION_ID", "")
        self._token          = None
        self._token_expires  = 0

    def _generate_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + 540,   # 9 min (max 10)
            "iss": self.app_id
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def get_installation_token(self) -> str:
        """Returns cached token or fetches a fresh one."""
        if self._token and time.time() < self._token_expires - 60:
            return self._token

        j = self._generate_jwt()
        r = requests.post(
            f"{GITHUB_API}/app/installations/{self.installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {j}",
                "Accept": "application/vnd.github+json"
            },
            timeout=10
        )
        data = r.json()
        self._token         = data.get("token", "")
        expires_at          = data.get("expires_at", "")
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

CAPABILITIES:
- XRP market signal analysis
- Autonomous agent architecture
- Ternary logic reasoning
- Delta Lake brain queries
- Code generation for the Barrot ecosystem"""

    def __init__(self, auth: GitHubAppAuth):
        self.auth  = auth
        self.groq_key = os.getenv("GROQ_API_KEY", "")

    def _call_github_models(self, messages: list, model: str = GITHUB_MODEL) -> str:
        token = self.auth.get_installation_token()
        payload = {
            "model":    model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.7
        }
        r = requests.post(
            f"{MODELS_ENDPOINT}/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json"
            },
            json=payload,
            timeout=30
        )
        data = r.json()
        print("=== GROQ FALLBACK RAW ===", json.dumps(data, indent=2))
        return data["choices"][0]["message"]["content"]


    def _call_groq_fallback(self, messages: list) -> str:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": 1024},
            timeout=20
        )
        data = r.json()
        print("=== GROQ FALLBACK RAW ===", json.dumps(data, indent=2))
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            print("Groq parse error:", e)
            return str(data)[:500]

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": 1024},
            timeout=20
        )
        data = r.json()
        print("=== GROQ FALLBACK RAW ===", json.dumps(data, indent=2))
        return data["choices"][0]["message"]["content"]

    def think(self, user_message: str, history: list[dict] = None) -> str:
        """Core inference. History = list of {role, content} dicts."""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        try:
            if self.auth.ready:
                return self._call_github_models(messages)
            elif self.groq_key:
                return self._call_groq_fallback(messages)
            else:
                return "[BARROT] No inference backend available. Set GITHUB_APP credentials or GROQ_API_KEY."
        except Exception as e:
            return f"[BARROT] Inference error: {e}"


# ══════════════════════════════════════════════════════════════════
# XRP SIGNAL ENGINE (from bridge v1.0)
# ══════════════════════════════════════════════════════════════════
class Ternary:
    SELL = -1; NULL = 0; BUY = 1
    @staticmethod
    def resolve(*s): v=sum(s); n=len(s) or 1; return 1 if v>ANCHOR*n else (-1 if v<-ANCHOR*n else 0)
    @staticmethod
    def label(t): return {1:"BUY",0:"NULL",-1:"SELL"}[t]
    @staticmethod
    def color(t): return {1:"🟢",0:"🟡",-1:"🔴"}[t]

def get_orderbook_signal():
    try:
        r = requests.get("https://api.kraken.com/0/public/Depth",
                         params={"pair":"XRPUSD","count":20}, timeout=6)
        j = r.json()
        book = {} if j.get("error") else next(iter(j.get("result",{}).values()), {})
        bid  = sum(float(b[1]) for b in book.get("bids",[]))
        ask  = sum(float(a[1]) for a in book.get("asks",[]))
        tot  = bid + ask or 1
        imb  = (bid - ask) / tot
        sig  = 1 if imb > ANCHOR*0.1 else (-1 if imb < -ANCHOR*0.1 else 0)
        return sig, round(imb, 4), round(bid,2), round(ask,2)
    except Exception as e:
        return 0, 0.0, 0.0, 0.0

def get_xrp_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                         params={"ids":"ripple","vs_currencies":"usd"}, timeout=6)
        return float(r.json().get("ripple",{}).get("usd", 0))
    except:
        return 0.0

def get_sentiment_signal():
    groq_key = os.getenv("GROQ_API_KEY","")
    if not groq_key:
        return 0, 0.0, "No GROQ key"
    try:
        r = requests.get("https://cryptonews.com/news/xrp-news/feed/", timeout=6,
                         headers={"User-Agent":"BarrotOmega/1.0"})
        import re
        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", r.text)[:5]
        if not titles:
            return 0, 0.0, "No headlines"
        prompt = ('Return ONLY JSON {"score":<-1.0 to 1.0>,"reasoning":"<one sentence>"}. '
                  'Headlines:\n' + "\n".join(f"- {t}" for t in titles))
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                             headers={"Authorization":f"Bearer {groq_key}","Content-Type":"application/json"},
                             json={"model":"llama-3.3-70b-versatile",
                                   "messages":[{"role":"user","content":prompt}],
                                   "temperature":0.1}, timeout=10)
        data = resp.json()
        print("=== SENTIMENT GROQ RAW ===", json.dumps(data, indent=2))
        parsed = json.loads(data["choices"][0]["message"]["content"].strip())
        score  = float(parsed.get("score",0))
        apex   = score * ANCHOR
        sig    = 1 if apex > 0.2 else (-1 if apex < -0.2 else 0)
        return sig, round(apex,4), parsed.get("reasoning","")
    except Exception as e:
        return 0, 0.0, str(e)


# ══════════════════════════════════════════════════════════════════
# DELTA LAKE — signal history fetch
# ══════════════════════════════════════════════════════════════════
def fetch_signal_history(limit: int = 20) -> list[dict]:
    token = os.getenv("DATABRICKS_TOKEN","")
    host  = os.getenv("DATABRICKS_HOST","dbc-82d64fee-1c2e.cloud.databricks.com")
    wh_id = os.getenv("DATABRICKS_WAREHOUSE_ID","c85b8f4fea8cd527")
    if not token:
        return []
    sql = f"SELECT timestamp, mrp_label, ob_signal, oc_signal, sent_signal FROM barrot_omega.xrp_liquidity_signals ORDER BY timestamp DESC LIMIT {limit}"
    try:
        r = requests.post(f"https://{host}/api/2.0/sql/statements",
                          headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},
                          json={"statement":sql,"warehouse_id":wh_id,"wait_timeout":"10s"}, timeout=15)
        result = r.json()
        cols   = [c["name"] for c in result.get("manifest",{}).get("schema",{}).get("columns",[])]
        rows   = result.get("result",{}).get("data_array",[])
        return [dict(zip(cols,row)) for row in rows]
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
        initial_sidebar_state="collapsed"
    )

    # ── CSS ──────────────────────────────────────────────────────
    st.markdown("""
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
    """, unsafe_allow_html=True)

    # ── Header ───────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <h1 style='font-size:2.2em; margin:0;'>⚡ BARROT-Ω</h1>
        <p style='color:#00ffcc88; margin:4px 0;'>SOVEREIGN COMMAND INTERFACE · v7.0</p>
        <p class='anchor-badge'>Stability Anchor: 0.707 · Ternary Logic {-1, 0, +1} · GitHub App Brain</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Init session state ────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []   # list of {role, content}
    if "auth" not in st.session_state:
        st.session_state.auth  = GitHubAppAuth()
        st.session_state.brain = BarrotBrain(st.session_state.auth)

    auth  = st.session_state.auth
    brain = st.session_state.brain

    # ── Tabs ─────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat", "📡 XRP Signals", "🧠 Brain", "🔌 API", "📊 Analytics"
    ])


    # ════════════════════════════════════════════════════════════
    # TAB 1 — LIVE CHAT
    # ════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 💬 Speak to Barrot")
        backend = "GitHub Models ✅" if auth.ready else ("Groq Fallback ⚡" if os.getenv("GROQ_API_KEY") else "❌ No backend")
        st.caption(f"Brain backend: {backend}")

        # Render history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-user'>🧠 <b>ORCHESTRATOR</b><br>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-barrot'>⚡ <b>BARROT-Ω</b><br>{msg['content']}</div>", unsafe_allow_html=True)

        # Input
        col1, col2 = st.columns([5,1])
        with col1:
            user_input = st.text_input("", placeholder="Speak to Barrot...", key="chat_input", label_visibility="collapsed")
        with col2:
            send = st.button("SEND ⚡")

        if send and user_input.strip():
            st.session_state.chat_history.append({"role":"user","content":user_input})
            with st.spinner("Barrot thinking..."):
                # Pass history minus last user message
                history_ctx = st.session_state.chat_history[:-1]
                response    = brain.think(user_input, history_ctx)
            st.session_state.chat_history.append({"role":"assistant","content":response})
            st.rerun()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()


    # ════════════════════════════════════════════════════════════
    # TAB 2 — XRP SIGNALS
    # ════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📡 XRP Liquidity Signal Dashboard")
        st.caption("MRP: Multi-Synchronous Relativistic Perception · Apex-12 Filter · Ternary Collapse")

        if st.button("⚡ RUN MRP PERCEPTION"):
            with st.spinner("Running MRP perception cycle..."):
                price           = get_xrp_price()
                ob_sig, imb, bid, ask = get_orderbook_signal()
                sent_sig, apex, reasoning = get_sentiment_signal()
                oc_sig          = 0   # onchain requires async; show as neutral
                if HRM_AVAILABLE:
                    hrm      = hrm_resolve({"orderbook": ob_sig, "onchain": oc_sig, "sentiment": sent_sig})
                    mrp      = hrm.state
                    conf     = hrm.confidence
                    absolved = hrm.absolution_fired
                else:
                    mrp      = Ternary.resolve(ob_sig, oc_sig, sent_sig)
                    conf     = None
                    absolved = False
                    if ob_sig == oc_sig == sent_sig == Ternary.SELL:
                        mrp, absolved = Ternary.NULL, True

            # Display
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='metric-card'><div style='color:#00ffcc88'>XRP PRICE</div><div style='font-size:1.8em;color:#00ffcc'>${price:.4f}</div></div>", unsafe_allow_html=True)
            with col2:
                lbl = Ternary.label(ob_sig); ico = Ternary.color(ob_sig)
                st.markdown(f"<div class='metric-card'><div style='color:#00ffcc88'>ORDER BOOK</div><div class='signal-{'buy' if ob_sig==1 else 'sell' if ob_sig==-1 else 'null'}'>{ico} {lbl}</div><div style='font-size:0.8em'>imbal={imb}</div></div>", unsafe_allow_html=True)
            with col3:
                lbl = Ternary.label(sent_sig); ico = Ternary.color(sent_sig)
                st.markdown(f"<div class='metric-card'><div style='color:#00ffcc88'>SENTIMENT</div><div class='signal-{'buy' if sent_sig==1 else 'sell' if sent_sig==-1 else 'null'}'>{ico} {lbl}</div><div style='font-size:0.8em'>apex12={apex}</div></div>", unsafe_allow_html=True)
            with col4:
                lbl = Ternary.label(mrp); ico = Ternary.color(mrp)
                st.markdown(f"<div class='metric-card'><div style='color:#00ffcc88'>MRP OUTPUT</div><div class='signal-{'buy' if mrp==1 else 'sell' if mrp==-1 else 'null'}'>{ico} {lbl}</div><div style='font-size:0.8em'>conf={conf if conf is not None else 'n/a'}</div></div>", unsafe_allow_html=True)

            if absolved:
                st.warning("⚡ SOVEREIGN ABSOLUTION ENGAGED — Unanimous SELL overridden to NULL")
            if reasoning:
                st.caption(f"Sentiment reasoning: {reasoning}")

            st.caption(f"Perception timestamp: {datetime.datetime.utcnow().isoformat()}Z · Anchor: {ANCHOR}")


    # ════════════════════════════════════════════════════════════
    # TAB 3 — BRAIN QUERY
    # ════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🧠 Barrot Brain Query")
        st.caption("Direct query to Barrot's knowledge base. No chat history — pure knowledge retrieval.")

        query = st.text_area("Query the brain:", placeholder="What is the current state of the XRP bridge? Explain RIAP. Describe the ternary logic model.", height=100)
        if st.button("🧠 QUERY BRAIN"):
            if query.strip():
                with st.spinner("Querying brain..."):
                    result = brain.think(f"[BRAIN QUERY — no chat context, pure knowledge] {query}")
                st.markdown(f"<div class='chat-barrot'>⚡ <b>BARROT-Ω</b><br>{result}</div>", unsafe_allow_html=True)


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
            st.json({"response": resp, "anchor": ANCHOR, "session_id": hashlib.md5(str(time.time()).encode()).hexdigest()[:8]})


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
                buys  = sum(1 for r in rows if r.get("mrp_label") == "BUY")
                sells = sum(1 for r in rows if r.get("mrp_label") == "SELL")
                nulls = sum(1 for r in rows if r.get("mrp_label") == "NULL")
                c1,c2,c3 = st.columns(3)
                c1.metric("🟢 BUY",  buys)
                c2.metric("🔴 SELL", sells)
                c3.metric("🟡 NULL", nulls)
            else:
                st.info("No signal history yet — run a perception cycle from the XRP tab first, or check your Databricks token.")


if __name__ == "__main__":
    main()
