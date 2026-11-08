#!/usr/bin/env python3
"""
COINBASE PAPER TRADER -- real live prices, zero real capital, zero custody risk.
Uses Coinbase Exchange's real public market data API (api.exchange.coinbase.com).
Barrot (Groq) makes a real buy/sell/hold decision against real current prices.
All positions and cash are SIMULATED. No Coinbase API key used or needed here.
"""

import os, json, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
PRODUCT_ID = os.environ.get("PRODUCT_ID", "BTC-USD")
STARTING_BALANCE_USD = float(os.environ.get("STARTING_BALANCE_USD", "10000"))

STATE_FILE = Path("web/paper_trading_state.json")
LOG_FILE = Path("web/paper_trading_log.jsonl")


def fetch_ticker(product_id):
    url = f"https://api.exchange.coinbase.com/products/{product_id}/ticker"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Coinbase ticker HTTP {e.code}: {e.read().decode()[:300]}")
        return None
    except Exception as e:
        print(f"Coinbase ticker error: {e}")
        return None


def fetch_recent_trades(product_id, limit=20):
    url = f"https://api.exchange.coinbase.com/products/{product_id}/trades"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            trades = json.loads(r.read().decode())
            return trades[:limit]
    except Exception as e:
        print(f"Coinbase trades error: {e}")
        return []


def call_groq(prompt):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        print(f"Groq HTTP {e.code}: {e.read().decode()[:300]}")
        return None


def extract_json(text):
    start = text.find('{')
    end = text.rfind('}') + 1
    if start == -1:
        return None
    try:
        return json.loads(text[start:end])
    except Exception:
        return None


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {
        "cash_usd": STARTING_BALANCE_USD, "position_size": 0.0,
        "position_product": None, "avg_entry_price": None,
        "trade_count": 0, "started_at": datetime.now(timezone.utc).isoformat(),
    }


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def log_decision(entry):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def decide(product_id, ticker, recent_trades, state):
    trade_summary = ", ".join(f"${float(t['price']):.2f}" for t in recent_trades[:10])
    prompt = f"""Real current {product_id} data from Coinbase (live, right now):
Best bid: {ticker.get('bid')}
Best ask: {ticker.get('ask')}
Last price: {ticker.get('price')}
24h volume: {ticker.get('volume')}
Last 10 real trade prices (most recent first): {trade_summary}

Current SIMULATED paper position: cash=${state['cash_usd']:.2f}, position_size={state['position_size']}, avg_entry={state['avg_entry_price']}

This is PAPER TRADING -- no real money moves. Decide: buy, sell, or hold.
If buying, use at most 20% of available cash on this single decision.
If selling, you may only sell up to the current position_size.
Be honest about uncertainty -- if the data doesn't support a clear edge, hold.

Output ONLY JSON: {{"action": "buy|sell|hold", "amount_usd": 0, "reasoning": "..."}}"""
    response = call_groq(prompt)
    if not response:
        return {"action": "hold", "amount_usd": 0, "reasoning": "Groq call failed"}
    parsed = extract_json(response)
    if not parsed:
        return {"action": "hold", "amount_usd": 0, "reasoning": "failed to parse decision"}
    return parsed


def execute_paper_trade(state, decision, current_price):
    action = decision.get("action", "hold")
    amount_usd = float(decision.get("amount_usd", 0) or 0)

    if action == "buy" and amount_usd > 0:
        amount_usd = min(amount_usd, state["cash_usd"] * 0.2, state["cash_usd"])
        if amount_usd < 1:
            return "hold -- insufficient cash for a meaningful buy"
        qty = amount_usd / current_price
        total_qty = state["position_size"] + qty
        prev_cost = (state["avg_entry_price"] or 0) * state["position_size"]
        state["avg_entry_price"] = (prev_cost + amount_usd) / total_qty if total_qty else None
        state["position_size"] = total_qty
        state["cash_usd"] -= amount_usd
        state["trade_count"] += 1
        return f"bought ${amount_usd:.2f} at ${current_price:.2f}"

    if action == "sell" and state["position_size"] > 0:
        sell_qty = min(state["position_size"], amount_usd / current_price if amount_usd else state["position_size"])
        proceeds = sell_qty * current_price
        state["cash_usd"] += proceeds
        state["position_size"] -= sell_qty
        if state["position_size"] <= 0.00000001:
            state["position_size"] = 0.0
            state["avg_entry_price"] = None
        state["trade_count"] += 1
        return f"sold ${proceeds:.2f} at ${current_price:.2f}"

    return "held -- no action taken"


def portfolio_value(state, current_price):
    return state["cash_usd"] + (state["position_size"] * current_price)


def run():
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        raise SystemExit(1)

    ticker = fetch_ticker(PRODUCT_ID)
    if not ticker:
        print("Could not fetch real ticker data -- aborting this cycle")
        raise SystemExit(1)
    current_price = float(ticker["price"])
    recent_trades = fetch_recent_trades(PRODUCT_ID)

    state = load_state()
    starting_value = portfolio_value(state, current_price)

    decision = decide(PRODUCT_ID, ticker, recent_trades, state)
    result = execute_paper_trade(state, decision, current_price)

    ending_value = portfolio_value(state, current_price)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(), "product": PRODUCT_ID,
        "price": current_price, "decision": decision, "result": result,
        "portfolio_value_usd": round(ending_value, 2),
        "portfolio_change_this_cycle": round(ending_value - starting_value, 2),
        "cumulative_return_pct": round(((ending_value - STARTING_BALANCE_USD) / STARTING_BALANCE_USD) * 100, 3),
    }
    log_decision(entry)
    save_state(state)

    print(f"Price: ${current_price:.2f}")
    print(f"Decision: {decision.get('action')} -- {decision.get('reasoning', '')[:150]}")
    print(f"Result: {result}")
    print(f"Portfolio value: ${ending_value:.2f} ({entry['cumulative_return_pct']:+.3f}% since start)")


if __name__ == "__main__":
    run()
