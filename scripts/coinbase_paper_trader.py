#!/usr/bin/env python3
"""
COINBASE PAPER TRADER -- real live prices, zero real capital, zero custody risk.
Uses Coinbase Exchange's real public market data API (api.exchange.coinbase.com).
Barrot (Groq) makes a real buy/sell/hold decision against real current prices.
All positions and cash are SIMULATED. No Coinbase API key used or needed here.
"""

import os, json, math, sys, urllib.request, urllib.error
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


def reject_nonfinite_json_constant(value):
    raise ValueError(f"non-finite JSON number is not permitted: {value}")


def extract_json(text):
    start = text.find('{')
    end = text.rfind('}') + 1
    if start == -1:
        return None
    try:
        return json.loads(text[start:end], parse_constant=reject_nonfinite_json_constant)
    except Exception:
        return None


def load_state():
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"ABORT: existing paper state is unreadable ({type(exc).__name__}); state preserved")
            raise SystemExit(2)
        if not isinstance(state, dict):
            print("ABORT: existing paper state is not a JSON object; state preserved")
            raise SystemExit(2)
        return state

    if not math.isfinite(STARTING_BALANCE_USD) or STARTING_BALANCE_USD <= 0:
        print("ABORT: STARTING_BALANCE_USD must be finite and positive")
        raise SystemExit(2)
    return {
        "cash_usd": STARTING_BALANCE_USD, "position_size": 0.0,
        "position_product": None, "avg_entry_price": None,
        "trade_count": 0, "started_at": datetime.now(timezone.utc).isoformat(),
    }


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_path = STATE_FILE.with_name(f".{STATE_FILE.name}.{os.getpid()}.tmp")
    try:
        temp_path.write_text(json.dumps(state, indent=2, allow_nan=False), encoding="utf-8")
        os.replace(temp_path, STATE_FILE)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def log_decision(entry):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, allow_nan=False) + "\n")


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


def validate_position_product(state, product_id):
    """Validate persisted simulated portfolio identity and numeric invariants."""
    if not isinstance(state, dict):
        return "aborted -- invalid paper state object"
    try:
        cash = float(state.get("cash_usd"))
        position_size = float(state.get("position_size"))
    except (TypeError, ValueError):
        return "aborted -- invalid cash or position size"
    if not math.isfinite(cash) or cash < 0:
        return "aborted -- non-finite or negative cash balance"
    if not math.isfinite(position_size) or position_size < 0:
        return "aborted -- non-finite or negative position size"

    trade_count = state.get("trade_count")
    if isinstance(trade_count, bool) or not isinstance(trade_count, int) or trade_count < 0:
        return "aborted -- invalid trade count"

    position_product = state.get("position_product")
    avg_entry = state.get("avg_entry_price")
    if position_size > 1e-8:
        if not isinstance(position_product, str) or not position_product.strip():
            return "aborted -- open position has no product identity"
        if position_product != product_id:
            return (
                f"aborted -- configured product {product_id} does not match "
                f"open position {position_product}"
            )
        try:
            avg_entry_value = float(avg_entry)
        except (TypeError, ValueError):
            return "aborted -- open position has invalid average entry price"
        if not math.isfinite(avg_entry_value) or avg_entry_value <= 0:
            return "aborted -- open position has invalid average entry price"
    else:
        if position_product not in (None, ""):
            return "aborted -- flat position has stale product identity"
        if avg_entry not in (None, 0, 0.0):
            return "aborted -- flat position has stale average entry price"
    return None


def validate_state_only():
    state = load_state()
    error = validate_position_product(state, PRODUCT_ID)
    if error:
        print(f"ABORT: {error}; state preserved")
        raise SystemExit(2)
    print("Persisted paper state validation passed; no provider or model calls made.")
    return state


def execute_paper_trade(state, decision, current_price, product_id):
    if not isinstance(decision, dict):
        return "hold -- invalid decision object"
    identity_error = validate_position_product(state, product_id)
    if identity_error:
        return identity_error
    try:
        price = float(current_price)
    except (TypeError, ValueError):
        return "hold -- invalid current price"
    if not math.isfinite(price) or price <= 0:
        return "hold -- invalid current price"
    raw_amount = decision.get("amount_usd", 0)
    if isinstance(raw_amount, bool):
        return "hold -- invalid decision amount"
    try:
        amount_usd = float(raw_amount or 0)
    except (TypeError, ValueError):
        return "hold -- invalid decision amount"
    if not math.isfinite(amount_usd) or amount_usd < 0:
        return "hold -- invalid decision amount"

    action = decision.get("action", "hold")
    if not isinstance(action, str):
        return "hold -- invalid decision action"
    action = action.strip().lower()

    if action == "buy" and amount_usd > 0:
        amount_usd = min(amount_usd, state["cash_usd"] * 0.2, state["cash_usd"])
        if amount_usd < 1:
            return "hold -- insufficient cash for a meaningful buy"
        if state["position_size"] <= 1e-8:
            state["position_product"] = product_id
        qty = amount_usd / price
        total_qty = state["position_size"] + qty
        prev_cost = (state["avg_entry_price"] or 0) * state["position_size"]
        state["avg_entry_price"] = (prev_cost + amount_usd) / total_qty if total_qty else None
        state["position_size"] = total_qty
        state["cash_usd"] -= amount_usd
        state["trade_count"] += 1
        return f"bought ${amount_usd:.2f} at ${price:.2f}"

    if action == "sell" and state["position_size"] > 0:
        sell_qty = min(state["position_size"], amount_usd / price if amount_usd else state["position_size"])
        proceeds = sell_qty * price
        state["cash_usd"] += proceeds
        state["position_size"] -= sell_qty
        if state["position_size"] <= 0.00000001:
            state["position_size"] = 0.0
            state["avg_entry_price"] = None
            state["position_product"] = None
        state["trade_count"] += 1
        return f"sold ${proceeds:.2f} at ${price:.2f}"

    return "held -- no action taken"


def portfolio_value(state, current_price):
    return state["cash_usd"] + (state["position_size"] * current_price)


def run(allow_state_mutation=False):
    if not allow_state_mutation:
        print("ABORT: explicit --execute confirmation is required for a paper-state mutation")
        raise SystemExit(2)

    # Validate persisted identity and numeric invariants before any provider/model call.
    state = validate_state_only()
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        raise SystemExit(1)

    ticker = fetch_ticker(PRODUCT_ID)
    if not ticker:
        print("Could not fetch real ticker data -- aborting this cycle")
        raise SystemExit(1)
    try:
        current_price = float(ticker["price"])
    except (KeyError, TypeError, ValueError):
        print("ABORT: Coinbase ticker returned an invalid price")
        raise SystemExit(1)
    if not math.isfinite(current_price) or current_price <= 0:
        print("ABORT: Coinbase ticker price must be finite and positive")
        raise SystemExit(1)
    recent_trades = fetch_recent_trades(PRODUCT_ID)

    starting_value = portfolio_value(state, current_price)
    decision = decide(PRODUCT_ID, ticker, recent_trades, state)
    result = execute_paper_trade(state, decision, current_price, PRODUCT_ID)
    if result.startswith("hold -- invalid decision"):
        decision = {"action": "hold", "amount_usd": 0, "reasoning": result}
    if result.startswith("aborted"):
        print(f"ABORT: {result}; state preserved")
        raise SystemExit(2)

    ending_value = portfolio_value(state, current_price)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(), "product": PRODUCT_ID,
        "price": current_price, "decision": decision, "result": result,
        "portfolio_value_usd": round(ending_value, 2),
        "portfolio_change_this_cycle": round(ending_value - starting_value, 2),
        "cumulative_return_pct": round(((ending_value - STARTING_BALANCE_USD) / STARTING_BALANCE_USD) * 100, 3),
    }
    save_state(state)
    log_decision(entry)

    print(f"Price: ${current_price:.2f}")
    reasoning = decision.get("reasoning", "")
    print(f"Decision: {decision.get('action')} -- {str(reasoning)[:150]}")
    print(f"Result: {result}")
    print(f"Portfolio value: ${ending_value:.2f} ({entry['cumulative_return_pct']:+.3f}% since start)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--validate-state"]:
        validate_state_only()
    elif args == ["--execute"]:
        run(allow_state_mutation=True)
    else:
        print("Usage: coinbase_paper_trader.py --validate-state | --execute")
        raise SystemExit(2)
