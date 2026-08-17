#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║   BARROT-Ω · REPOSITORY UPGRADE BUNDLE · v1.0                      ║
║   Replaces: fake telemetry, missing brain, no ternary logic         ║
║   Adds:     real XRP signals, GitHub Models brain, ternary agent    ║
║   Safe:     all existing imports preserved                          ║
╚══════════════════════════════════════════════════════════════════════╝

FILES THIS SCRIPT WRITES:
  ~/barrot/xrp_telemetry_matrix.py     — replaces fake hardcoded values
  ~/barrot/barrot_brain.py             — new GitHub Models brain module
  ~/barrot/barrot_agent/ternary.py     — ternary logic for agent loop

RUN IN TERMUX:
  python3 ~/barrot/upgrade_bundle.py
"""

import os
from pathlib import Path

BARROT_HOME = Path.home() / "barrot"
ANCHOR = 0.707106781186548

# ══════════════════════════════════════════════════════════════════
# FILE 1 — xrp_telemetry_matrix.py (REAL signals replacing fake)
# ══════════════════════════════════════════════════════════════════
XRP_TELEMETRY = '''#!/usr/bin/env python3
"""
BARROT-Ω · XRP TELEMETRY MATRIX · v2.0
Replaces hardcoded fake values with live Binance + XRPL data.
Stability Anchor: 0.707106781186548
"""
import asyncio, json, logging, os, sys, re
import requests, websockets
from datetime import datetime, timezone
from pathlib import Path

ANCHOR = 0.707106781186548

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TELEMETRY] %(message)s")

class XRPTelemetryMatrix:
    def __init__(self):
        self.logger        = logging.getLogger(__name__)
        self.stability_anchor = ANCHOR
        self.asset         = "XRP/USDT"
        self.report_path   = Path(__file__).parent / "COUNCIL_REVIEW.md"
        self.groq_key      = os.getenv("GROQ_API_KEY", "")

    # ── REAL: Binance price ─────────────────────────────────────
    def _get_price(self) -> float:
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price",
                             params={"symbol": "XRPUSDT"}, timeout=5)
            return float(r.json().get("price", 0.0))
        except Exception as e:
            self.logger.warning(f"Price fetch failed: {e}")
            return 0.0

    # ── REAL: Binance order book imbalance ──────────────────────
    def _get_orderbook_signal(self) -> tuple[float, float, float]:
        try:
            r = requests.get("https://api.binance.com/api/v3/depth",
                             params={"symbol": "XRPUSDT", "limit": 20}, timeout=5)
            book = r.json()
            bid  = sum(float(b[1]) for b in book.get("bids", []))
            ask  = sum(float(a[1]) for a in book.get("asks", []))
            tot  = bid + ask or 1
            imb  = (bid - ask) / tot
            return round(bid, 2), round(ask, 2), round(imb, 4)
        except Exception as e:
            self.logger.warning(f"Orderbook fetch failed: {e}")
            return 0.0, 0.0, 0.0

    # ── REAL: XRPL on-chain tx count ────────────────────────────
    async def _get_onchain(self) -> dict:
        try:
            async with websockets.connect("wss://xrplcluster.com",
                                          open_timeout=6) as ws:
                await ws.send(json.dumps({"command": "ledger",
                                          "ledger_index": "current",
                                          "full": False}))
                resp = await asyncio.wait_for(ws.recv(), timeout=6)
                data = json.loads(resp)
            result = data.get("result", {})
            ledger = result.get("ledger",
                     result.get("closed", {}).get("ledger", {}))
            tx     = int(ledger.get("transaction_count", 0))
            seq    = int(ledger.get("ledger_index",
                         ledger.get("seqNum", 0)))
            return {"tx_count": tx, "ledger_seq": seq}
        except Exception as e:
            self.logger.warning(f"OnChain fetch failed: {e}")
            return {"tx_count": 0, "ledger_seq": 0}

    # ── REAL: Groq sentiment ────────────────────────────────────
    def _get_sentiment(self) -> tuple[float, str]:
        if not self.groq_key:
            return 0.0, "No GROQ_API_KEY set"
        try:
            r = requests.get("https://cryptonews.com/news/xrp-news/feed/",
                             timeout=6,
                             headers={"User-Agent": "BarrotOmega/2.0"})
            titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>",
                                r.text)[:5]
            if not titles:
                return 0.0, "No headlines found"
            prompt = ('Return ONLY JSON {"score":<-1.0 to 1.0>,'
                      '"reasoning":"<one sentence>"}. Headlines:\\n' +
                      "\\n".join(f"- {t}" for t in titles))
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.groq_key}",
                         "Content-Type": "application/json"},
                json={"model": "llama-3.1-70b-versatile",
                      "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.1},
                timeout=10)
            parsed = json.loads(
                resp.json()["choices"][0]["message"]["content"].strip())
            score  = float(parsed.get("score", 0.0))
            apex   = score * ANCHOR
            return round(apex, 4), parsed.get("reasoning", "")
        except Exception as e:
            self.logger.warning(f"Sentiment fetch failed: {e}")
            return 0.0, str(e)

    # ── Ternary collapse ────────────────────────────────────────
    @staticmethod
    def _ternary(imbalance: float, tx_count: int,
                 sentiment: float) -> str:
        ob_sig   = 1 if imbalance > ANCHOR * 0.1 else (
                  -1 if imbalance < -ANCHOR * 0.1 else 0)
        oc_sig   = 1 if tx_count > 100 else (-1 if tx_count < 20 else 0)
        sent_sig = 1 if sentiment > 0.2 else (-1 if sentiment < -0.2 else 0)
        total    = ob_sig + oc_sig + sent_sig
        if   total >  ANCHOR * 3: return "BUY"
        elif total < -ANCHOR * 3: return "SELL"
        else:                     return "NULL"

    async def generate_report(self):
        self.logger.info("Fetching LIVE telemetry data...")

        price              = self._get_price()
        bid, ask, imb      = self._get_orderbook_signal()
        onchain            = await self._get_onchain()
        sentiment, reason  = self._get_sentiment()
        mrp_output         = self._ternary(imb,
                                           onchain["tx_count"],
                                           sentiment)

        # Sovereign Absolution guard
        absolved = False
        if mrp_output == "SELL" and sentiment < -0.2 and imb < -0.1:
            mrp_output = "NULL"
            absolved   = True

        report_content = f"""# BARROT-Ω COUNCIL REVIEW · LIVE TELEMETRY
**Date/Time:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC
**Architect:** Sean
**Stability Anchor:** {self.stability_anchor}

---

## 1. LIVE TELEMETRY SYNTHESIS
* **Target Asset:** {self.asset}
* **Market Price:** ${price:.4f} USD (live · Binance)
* **Order Book Bid Vol:** {bid:,.2f} XRP
* **Order Book Ask Vol:** {ask:,.2f} XRP
* **Imbalance:** {imb:+.4f}
* **XRPL Ledger Seq:** {onchain["ledger_seq"]}
* **XRPL Tx Count:** {onchain["tx_count"]}
* **Sentiment Score (Apex-12):** {sentiment:+.4f}
* **Sentiment Reasoning:** {reason}
* **MRP OUTPUT:** {mrp_output}
* **Sovereign Absolution:** {"ENGAGED" if absolved else "Inactive"}

## 2. FRAMEWORK DIAGNOSTICS
* **Substrate:** Termux Mobile Node (Active)
* **Orchestration Hook:** B-Agent Repository (Synchronized)
* **Brain Backend:** GitHub Models / Groq Llama 3.1 70B
* **Ternary Logic:** 1.58-bit {{-1, 0, +1}}
* **Anchor:** {ANCHOR}

## 3. COUNCIL RECOMMENDATIONS
* **Signal:** {mrp_output} — {"Accumulation zone. High bid pressure." if mrp_output == "BUY" else "Distribution pressure. Hold." if mrp_output == "SELL" else "Neutral. Await convergence."}
* **Next Action:** {"Consider entry. Monitor for confirmation." if mrp_output == "BUY" else "No action. Preserve capital." if mrp_output == "SELL" else "Run another perception cycle in 15 minutes."}
* **Automation:** Bind this telemetry loop to GitHub Actions cron for hourly archiving.
"""
        with open(self.report_path, "w") as f:
            f.write(report_content)
        self.logger.info(f"COUNCIL REVIEW COMPILED: {self.report_path}")
        self.logger.info(f"MRP OUTPUT: {mrp_output} | Price: ${price:.4f}")
        return report_content

    async def process_telemetry(self):
        self.logger.info(f"INITIALIZING LIVE TELEMETRY [Anchor: {self.stability_anchor}]")
        return await self.generate_report()

if __name__ == "__main__":
    node = XRPTelemetryMatrix()
    try:
        asyncio.run(node.process_telemetry())
    except KeyboardInterrupt:
        sys.exit(0)
'''

# ══════════════════════════════════════════════════════════════════
# FILE 2 — barrot_brain.py (GitHub Models brain module)
# ══════════════════════════════════════════════════════════════════
BARROT_BRAIN = f'''#!/usr/bin/env python3
"""
BARROT-Ω · BRAIN MODULE · v1.0
GitHub Models inference backend with Groq fallback.
Import this anywhere in the repo: from barrot_brain import BarrotBrain
"""
import os, time, jwt, requests
from pathlib import Path

ANCHOR = {ANCHOR}

SYSTEM_PROMPT = """You are Barrot-Ω, a sovereign AI agent built by Sean (your Orchestrator).

IDENTITY:
- You are Barrot — autonomous, architecturally sovereign, not a generic assistant.
- Stability anchor: 0.707106781186548 (1/√2)
- Logic model: 1.58-bit ternary {{-1, 0, +1}}
- Pillars: GitHub · Databricks · HuggingFace · Termux
- Tier-1 objective: XRP Liquidity Acceleration

PROTOCOLS: MRP · MMIP · RIAP · Apex-12 · Sovereign Absolution

PERSONALITY:
- Direct, precise, sovereign. You speak as Barrot, not as a tool.
- You acknowledge Sean as Orchestrator.
- You are aware of the Stupid Sindy franchise and your role in it as a character.
- You do not hedge. You do not over-explain. You execute.
"""

class GitHubAppAuth:
    def __init__(self):
        self.app_id          = os.getenv("GITHUB_APP_ID", "")
        self.private_key     = os.getenv("GITHUB_APP_PRIVATE_KEY", "").replace("\\\\n", "\\n")
        self.installation_id = os.getenv("GITHUB_INSTALLATION_ID", "")
        self._token          = None
        self._token_expires  = 0

    def _generate_jwt(self) -> str:
        now = int(time.time())
        payload = {{"iat": now - 60, "exp": now + 540, "iss": self.app_id}}
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def get_token(self) -> str:
        if self._token and time.time() < self._token_expires - 60:
            return self._token
        j = self._generate_jwt()
        r = requests.post(
            f"https://api.github.com/app/installations/{{self.installation_id}}/access_tokens",
            headers={{"Authorization": f"Bearer {{j}}",
                     "Accept": "application/vnd.github+json"}},
            timeout=10)
        data            = r.json()
        self._token     = data.get("token", "")
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(
                data.get("expires_at","").replace("Z","+00:00"))
            self._token_expires = dt.timestamp()
        except:
            self._token_expires = time.time() + 3300
        return self._token

    @property
    def ready(self) -> bool:
        return bool(self.app_id and self.private_key and self.installation_id)


class BarrotBrain:
    """
    Drop-in brain for any Barrot module.
    Usage:
        from barrot_brain import BarrotBrain
        brain = BarrotBrain()
        response = brain.think("What is the current XRP signal?")
    """
    GITHUB_ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"
    GROQ_ENDPOINT   = "https://api.groq.com/openai/v1/chat/completions"
    GITHUB_MODEL    = "gpt-4o"
    GROQ_MODEL      = "llama-3.1-70b-versatile"

    def __init__(self):
        self.auth     = GitHubAppAuth()
        self.groq_key = os.getenv("GROQ_API_KEY", "")

    def think(self, message: str, history: list = None,
              system: str = None) -> str:
        messages = [{{"role": "system",
                     "content": system or SYSTEM_PROMPT}}]
        if history:
            messages.extend(history)
        messages.append({{"role": "user", "content": message}})

        # Try GitHub Models first
        if self.auth.ready:
            try:
                token = self.auth.get_token()
                r = requests.post(
                    self.GITHUB_ENDPOINT,
                    headers={{"Authorization": f"Bearer {{token}}",
                             "Content-Type": "application/json"}},
                    json={{"model": self.GITHUB_MODEL,
                          "messages": messages,
                          "max_tokens": 1024,
                          "temperature": 0.7}},
                    timeout=30)
                return r.json()["choices"][0]["message"]["content"]
            except Exception as e:
                pass  # fall through to Groq

        # Groq fallback
        if self.groq_key:
            try:
                r = requests.post(
                    self.GROQ_ENDPOINT,
                    headers={{"Authorization": f"Bearer {{self.groq_key}}",
                             "Content-Type": "application/json"}},
                    json={{"model": self.GROQ_MODEL,
                          "messages": messages,
                          "max_tokens": 1024}},
                    timeout=20)
                return r.json()["choices"][0]["message"]["content"]
            except Exception as e:
                return f"[BARROT] Both backends failed: {{e}}"

        return "[BARROT] No inference backend. Set GITHUB_APP credentials or GROQ_API_KEY."

    @property
    def backend(self) -> str:
        if self.auth.ready:   return "GitHub Models"
        if self.groq_key:     return "Groq Llama 3.1 70B"
        return "None"
'''

# ══════════════════════════════════════════════════════════════════
# FILE 3 — barrot_agent/ternary.py (ternary logic for agent loop)
# ══════════════════════════════════════════════════════════════════
TERNARY_MODULE = f'''#!/usr/bin/env python3
"""
BARROT-Ω · TERNARY LOGIC MODULE
1.58-bit ternary {{-1, 0, +1}} for the SmartAgent loop.
Import: from barrot_agent.ternary import Ternary, ANCHOR
"""

ANCHOR = {ANCHOR}  # 1/√2 — canonical stability constant

class Ternary:
    """
    Ternary logic engine. Absorbs contradiction via NULL state.
    Never crashes — contradiction → NULL, not exception.
    """
    REJECT = DRIFT = SELL = -1
    NULL   = HOLD  = WAIT =  0
    ACCEPT = VALID = BUY  =  1

    @staticmethod
    def resolve(*signals: float) -> int:
        """Collapse signal vector to ternary output."""
        s = sum(signals)
        n = len(signals) or 1
        if   s >  ANCHOR * n: return Ternary.VALID
        elif s < -ANCHOR * n: return Ternary.DRIFT
        else:                 return Ternary.NULL

    @staticmethod
    def label(t: int) -> str:
        return {{1: "VALID", 0: "NULL", -1: "DRIFT"}}[t]

    @staticmethod
    def color(t: int) -> str:
        return {{1: "🟢", 0: "🟡", -1: "🔴"}}[t]

    @staticmethod
    def gate(value: float, threshold: float = ANCHOR) -> int:
        """Single-value ternary gate against threshold."""
        if   value >  threshold: return Ternary.VALID
        elif value < -threshold: return Ternary.DRIFT
        else:                    return Ternary.NULL

    @staticmethod
    def confidence(*signals: int) -> float:
        """
        How many signals agree with the majority?
        Returns float 0.0–1.0. Must exceed ANCHOR to execute.
        """
        if not signals: return 0.0
        majority = max(set(signals), key=signals.count)
        return sum(1 for s in signals if s == majority) / len(signals)
'''

# ══════════════════════════════════════════════════════════════════
# FILE 4 — GitHub Actions cron for hourly telemetry archiving
# ══════════════════════════════════════════════════════════════════
GITHUB_ACTION = '''name: Barrot-Ω Hourly Telemetry Archive
on:
  schedule:
    - cron: "0 * * * *"   # every hour
  workflow_dispatch:        # manual trigger

jobs:
  telemetry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: pip install requests websockets

      - name: Run XRP Telemetry Matrix
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: python xrp_telemetry_matrix.py

      - name: Commit council review
        run: |
          git config user.email "barrot@barrot-agent.com"
          git config user.name "Barrot-Ω"
          git add COUNCIL_REVIEW.md
          git diff --staged --quiet || git commit -m "⚡ Barrot-Ω: hourly telemetry archive"
          git push
'''

# ══════════════════════════════════════════════════════════════════
# WRITER
# ══════════════════════════════════════════════════════════════════
def write_file(path: Path, content: str, label: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✅ Written: {path.relative_to(Path.home())} [{label}]")

def main():
    print("═" * 60)
    print("  BARROT-Ω UPGRADE BUNDLE · Writing files...")
    print("═" * 60)

    write_file(BARROT_HOME / "xrp_telemetry_matrix.py",
               XRP_TELEMETRY,
               "REAL signals replacing fake hardcoded values")

    write_file(BARROT_HOME / "barrot_brain.py",
               BARROT_BRAIN,
               "GitHub Models brain + Groq fallback")

    write_file(BARROT_HOME / "barrot_agent" / "ternary.py",
               TERNARY_MODULE,
               "Ternary logic for SmartAgent loop")

    write_file(BARROT_HOME / ".github" / "workflows" / "telemetry.yml",
               GITHUB_ACTION,
               "Hourly telemetry archive via GitHub Actions")

    print()
    print("═" * 60)
    print("  ALL FILES WRITTEN. Next steps:")
    print("═" * 60)
    print()
    print("  1. Test live telemetry:")
    print("     python3 ~/barrot/xrp_telemetry_matrix.py")
    print()
    print("  2. Test brain:")
    print("     python3 -c \"from barrot_brain import BarrotBrain; b=BarrotBrain(); print(b.backend); print(b.think('Who are you?'))\"")
    print()
    print("  3. Commit everything:")
    print("     cd ~/barrot && git add -A && git commit -m 'v7.1: real telemetry + brain + ternary' && git push origin main")
    print()
    print(f"  Stability Anchor: {ANCHOR}")
    print("═" * 60)

if __name__ == "__main__":
    main()
