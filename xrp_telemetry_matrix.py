#!/usr/bin/env python3
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
            r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                             params={"ids": "ripple", "vs_currencies": "usd"}, timeout=5)
            return float(r.json()["ripple"]["usd"])
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
                      '"reasoning":"<one sentence>"}. Headlines:\n' +
                      "\n".join(f"- {t}" for t in titles))
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
