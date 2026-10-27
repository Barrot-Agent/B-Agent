#!/usr/bin/env python3
"""
EXPERIMENTAL SENTIMENT SANDBOX — does NOT issue a price forecast.
Uses a validated numeric sentiment score only; unavailable evidence is skipped.
"""
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "core"))
sys.path.insert(0, str(REPO_ROOT / "utils"))

LIVE_PATH = Path("web/latest_signal.json")
OUT_PATH = Path("web/hrm_sandbox_signal.json")


def _write_not_issued(reason: str):
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sandbox": True,
        "status": "NOT_ISSUED",
        "forecast_status": "NOT_ISSUED",
        "reason": reason,
        "note": "No calibrated XRP price forecast is produced by this sentiment sandbox.",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


def main():
    if not LIVE_PATH.exists():
        print(f"SKIP: {LIVE_PATH} not found — run emit_signal.py first.")
        return

    live = json.loads(LIVE_PATH.read_text(encoding="utf-8"))
    score = live.get("score")
    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(float(score))
        or not 0 <= float(score) <= 100
    ):
        _write_not_issued("source sentiment score is unavailable or invalid")
        return

    # Import the heavier numerical dependency only after validating the input.
    # An unavailable score should be handled even in a minimal CI environment.
    from hrm_ternary import hrm_resolve
    from score_to_signal import score_to_unit

    result = hrm_resolve({
        "orderbook": 0.0,
        "onchain": 0.0,
        "sentiment": score_to_unit(score),
    })
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sandbox": True,
        "status": "SENTIMENT_SANDBOX_ONLY",
        "note": "orderbook/onchain inputs are neutral placeholders (no real data source yet)",
        "source_score": score,
        "source_confidence": live.get("confidence"),
        "forecast_status": "NOT_ISSUED",
        "hrm_state": result.state,
        "hrm_raw_state": result.raw_state,
        "hrm_confidence": result.confidence,
        "hrm_absolution_fired": result.absolution_fired,
        "hrm_basis": result.basis,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
