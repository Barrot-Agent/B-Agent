#!/usr/bin/env python3
"""Retired legacy XRP scorer.

This command is intentionally read-only. The former implementation compared a
signal with a mutable spot quote at invocation time after only a minimum age,
then rewrote history and reported a variable-horizon binary percentage. That
metric is not fixed-horizon out-of-sample predictive accuracy.
"""
import json


STATUS = {
    "status": "NOT_EVALUATED",
    "forecast_issued": False,
    "reason_code": "LEGACY_VARIABLE_HORIZON_SCORER_RETIRED",
    "message": (
        "Legacy signal outcomes are preserved for audit, but the old scorer is "
        "disabled. No current-price comparison, history rewrite, or accuracy "
        "claim is produced."
    ),
}


def main() -> int:
    print(json.dumps(STATUS, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
