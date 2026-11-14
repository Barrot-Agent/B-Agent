#!/usr/bin/env python3
"""
EXPERIMENTAL SANDBOX — does NOT touch web/latest_signal.json.
Runs the real hrm_resolve() against the already-generated live score,
using it as the only real input (sentiment channel). orderbook/onchain
have no real data source yet, so they are passed as 0.0 (neutral) and
explicitly labeled as unavailable in the output — never fabricated.
Writes web/hrm_sandbox_signal.json for comparison only.

--engine hrm2 runs the SHRM 2.0 refinement (barrot_agent.reasoning.hrm)
instead of v1; add --refined for the full 2.0 dynamics (H-hierarchy +
slope convergence). The output records which engine produced the call.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "core"))
sys.path.insert(0, str(REPO_ROOT / "utils"))
sys.path.insert(0, str(REPO_ROOT))

from hrm_ternary import hrm_resolve  # noqa: E402
from score_to_signal import score_to_unit  # noqa: E402

LIVE_PATH = REPO_ROOT / "web" / "latest_signal.json"
OUT_PATH = REPO_ROOT / "web" / "hrm_sandbox_signal.json"


def main():
    parser = argparse.ArgumentParser(description="HRM sandbox signal emitter")
    parser.add_argument("--engine", choices=("v1", "hrm2"), default="v1",
                        help="v1 = core/hrm_ternary.py, hrm2 = SHRM 2.0 refinement")
    parser.add_argument("--refined", action="store_true",
                        help="with --engine hrm2: enable refined 2.0 dynamics")
    args = parser.parse_args()

    if not LIVE_PATH.exists():
        print(f"SKIP: {LIVE_PATH} not found — run emit_signal.py first.")
        return

    live = json.loads(LIVE_PATH.read_text())
    sent_sig = score_to_unit(live.get("score", 50))

    signals = {
        "orderbook": 0.0,   # real data source not yet built — neutral, not guessed
        "onchain": 0.0,     # real data source not yet built — neutral, not guessed
        "sentiment": sent_sig,
    }

    if args.engine == "hrm2":
        from barrot_agent.reasoning.hrm import hrm2_resolve, resolve_with_trace

        if args.refined:
            result, trace = resolve_with_trace(signals, refined=True)
        else:
            result, trace = resolve_with_trace(signals)
    else:
        result = hrm_resolve(signals)
        trace = None

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sandbox": True,
        "note": "orderbook/onchain inputs are neutral placeholders (no real data source yet)",
        "engine": args.engine,
        "refined": bool(args.refined and args.engine == "hrm2"),
        "source_score": live.get("score"),
        "source_confidence": live.get("confidence"),
        "hrm_state": result.state,
        "hrm_raw_state": result.raw_state,
        "hrm_confidence": result.confidence,
        "hrm_absolution_fired": result.absolution_fired,
        "hrm_basis": result.basis,
    }
    if trace is not None:
        out["trace"] = trace
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
