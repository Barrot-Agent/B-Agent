#!/usr/bin/env python3
"""
BARROT-Omega | SIGNAL LEDGER EMITTER | v1.0
Runs one full perception cycle and appends the result to the public,
git-timestamped signal ledger. Every emission is a permanent, tamper-
evident record: the commit timestamp proves when the call was made.

Outputs:
  data/signal_ledger.jsonl  - append-only ledger (one JSON record/line)
  web/latest_signal.json    - public endpoint, current signal state

Degrades gracefully: any source that fails contributes 0 (neutral)
and the failure is recorded in the ledger entry. Honesty over hype:
a NULL from missing data is still a real, auditable emission.
Stability Anchor: 0.707106781186548
"""
import json, os, re, sys, datetime
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))
from hrm_ternary import hrm_resolve, ANCHOR

def get_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                         params={"ids": "ripple", "vs_currencies": "usd"}, timeout=10)
        return float(r.json()["ripple"]["usd"]), ""
    except Exception as e:
        return 0.0, f"price: {e}"

def get_orderbook():
    try:
        r = requests.get("https://api.kraken.com/0/public/Depth",
                         params={"pair": "XRPUSD", "count": 20}, timeout=10)
        j = r.json()
        if j.get("error"):
            return 0, 0.0, f"orderbook: {j['error']}"
        book = next(iter(j.get("result", {}).values()), {})
        bid = sum(float(b[1]) for b in book.get("bids", []))
        ask = sum(float(a[1]) for a in book.get("asks", []))
        tot = bid + ask or 1
        imb = (bid - ask) / tot
        sig = 1 if imb > ANCHOR * 0.1 else (-1 if imb < -ANCHOR * 0.1 else 0)
        return sig, round(imb, 4), ""
    except Exception as e:
        return 0, 0.0, f"orderbook: {e}"

def get_sentiment():
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        return 0, 0.0, "", "sentiment: no GROQ_API_KEY"
    try:
        feeds = [
            "https://cointelegraph.com/rss/tag/xrp",
            "https://cryptonews.com/news/xrp-news/feed/",
        ]
        titles = []
        for url in feeds:
            try:
                fr = requests.get(url, timeout=10,
                                  headers={"User-Agent": "Mozilla/5.0 (compatible; BarrotOmega/1.1)"})
                found = re.findall(r"<title>(?:<!\[CDATA\[)?\s*(.*?)\s*(?:\]\]>)?</title>",
                                   fr.text, re.S)
                cleaned = [t.strip() for t in found[1:] if t.strip()][:5]
                if cleaned:
                    titles = cleaned
                    break
            except Exception:
                continue
        if not titles:
            return 0, 0.0, "", "sentiment: no headlines (all feeds)"
        prompt = ('Return ONLY JSON {"score":<-1.0 to 1.0>,"reasoning":"<one sentence>"}. '
                  "Headlines:\n" + "\n".join(f"- {t}" for t in titles))
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                             headers={"Authorization": f"Bearer {key}",
                                      "Content-Type": "application/json"},
                             json={"model": "llama-3.3-70b-versatile",
                                   "messages": [{"role": "user", "content": prompt}],
                                   "temperature": 0.1}, timeout=25)
        parsed = json.loads(resp.json()["choices"][0]["message"]["content"].strip())
        score = float(parsed.get("score", 0))
        apex = score * ANCHOR
        sig = 1 if apex > 0.2 else (-1 if apex < -0.2 else 0)
        return sig, round(apex, 4), str(parsed.get("reasoning", ""))[:200], ""
    except Exception as e:
        return 0, 0.0, "", f"sentiment: {e}"

def main():
    price, e1 = get_price()
    ob_sig, imb, e2 = get_orderbook()
    sent_sig, apex, reasoning, e3 = get_sentiment()
    oc_sig = 0  # onchain source reserved; neutral until wired

    res = hrm_resolve({"orderbook": ob_sig, "onchain": oc_sig, "sentiment": sent_sig})
    errors = [e for e in (e1, e2, e3) if e]

    record = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "asset": "XRP/USD",
        "price": price,
        "state": res.state,
        "label": res.label,
        "raw_state": res.raw_state,
        "confidence": res.confidence,
        "agreement": res.agreement,
        "convergence": res.convergence,
        "absolution": res.absolution_fired,
        "sources": {
            "orderbook": {"signal": ob_sig, "imbalance": imb},
            "sentiment": {"signal": sent_sig, "apex12": apex, "reasoning": reasoning},
            "onchain": {"signal": oc_sig},
        },
        "anchor": ANCHOR,
        "degraded": errors,
    }

    ledger = ROOT / "data" / "signal_ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")

    latest = dict(record)
    latest["ledger_url"] = "https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main/data/signal_ledger.jsonl"
    (ROOT / "web" / "latest_signal.json").write_text(json.dumps(latest, indent=2))

    print(f"EMITTED {record['ts']} {res.label} conf={res.confidence} "
          f"price=${price} degraded={len(errors)}")
    for e in errors:
        print("  WARN", e)

if __name__ == "__main__":
    main()
