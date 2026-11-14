#!/usr/bin/env python3
"""Quarantined legacy orchestrator bridge.

No legacy council state is applied. Barrot V3's verified authorization and
execution gates are the only supported path for controlled actions.
"""
import json

STATUS = {
    "status": "NOT_APPLIED",
    "forecast_eligible": False,
    "external_action_performed": False,
    "reason_code": "LEGACY_COUNCIL_BRIDGE_QUARANTINED",
}


def apply_council_weights(state_path="council_weights.json"):
    return dict(STATUS)


def main():
    print(json.dumps(STATUS, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
