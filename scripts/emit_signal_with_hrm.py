#!/usr/bin/env python3
"""
EXPERIMENTAL SANDBOX — does NOT touch web/latest_signal.json.
Runs the real hrm_resolve() against the already-generated live score,
using it as the only real input (sentiment channel). orderbook/onchain
have no real data source yet, so they are passed as 0.0 (neutral) and
explicitly labeled as unavailable in the output — never fabricated.
Writes web/hrm_sandbox_signal.json for comparison only.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))

from hrm_ternary import hrm_resolve  # noqa: E402
from score_to_signal import score_to_unit  # noqa: E402

LIVE_PATH = Path("web/latest_signal.json")
OUT_PATH = Path("web/hrm_sandbox_signal.json")


def main():
    if not LIVE_PATH.exists():
        print(f"SKIP: {LIVE_PATH} not found — run emit_signal.py first.")
        return

    live = json.loads(LIVE_PATH.read_text())
    sent_sig = score_to_unit(live.get("score", 50))

    result = hrm_resolve({
        "orderbook": 0.0,   # real data source not yet built — neutral, not guessed
        "onchain": 0.0,     # real data source not yet built — neutral, not guessed
        "sentiment": sent_sig,
    })

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sandbox": True,
        "note": "orderbook/onchain inputs are neutral placeholders (no real data source yet)",
        "source_score": live.get("score"),
        "source_confidence": live.get("confidence"),
        "hrm_state": result.state,
        "hrm_raw_state": result.raw_state,
        "hrm_confidence": result.confidence,
        "hrm_absolution_fired": result.absolution_fired,
        "hrm_basis": result.basis,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
