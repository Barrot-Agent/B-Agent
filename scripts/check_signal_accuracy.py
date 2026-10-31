#!/usr/bin/env python3
import json
import time
from pathlib import Path

import requests

HISTORY_PATH = Path("web/signal_history.jsonl")
SUMMARY_PATH = Path("web/signal_accuracy.json")
MIN_AGE_SECONDS = 24 * 3600


def _get_xrp_price():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ripple", "vs_currencies": "usd"},
            timeout=6,
        )
        return float(r.json().get("ripple", {}).get("usd", 0))
    except Exception:
        return 0.0


def _load_entries():
    if not HISTORY_PATH.exists():
        return []
    out = []
    for line in HISTORY_PATH.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def main():
    entries = _load_entries()
    now = time.time()
    current_price = _get_xrp_price()

    checked = 0
    correct = 0
    for e in entries:
        if e.get("checked"):
            if e.get("correct"):
                correct += 1
            checked += 1
            continue
        emitted_at = e.get("generated_at_unix", 0)
        if not emitted_at or (now - emitted_at) < MIN_AGE_SECONDS:
            continue
        price_then = e.get("price_at_emission", 0)
        score = e.get("score", 50)
        if not price_then or not current_price:
            continue
        moved_up = current_price > price_then
        called_bullish = score > 60
        called_bearish = score < 40
        if called_bullish:
            was_correct = moved_up
        elif called_bearish:
            was_correct = not moved_up
        else:
            was_correct = abs(current_price - price_then) / price_then < 0.02
        e["checked"] = True
        e["correct"] = was_correct
        e["price_at_check"] = current_price
        checked += 1
        if was_correct:
            correct += 1

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            print(json.dumps(e), file=f)

    accuracy = round(100 * correct / checked, 1) if checked else None
    summary = {
        "checked_count": checked,
        "correct_count": correct,
        "accuracy_pct": accuracy,
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
