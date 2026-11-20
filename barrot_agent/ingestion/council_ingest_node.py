#!/usr/bin/env python3
"""Quarantined legacy council ingestion node.

The former implementation converted a synthetic sentiment score into
MAX_ACCUMULATION_TRIGGERED and wrote a 1.15 orchestrator multiplier. It is
retained as a compatibility placeholder and cannot create or inject actions.
"""
import json

STATUS = {
    "status": "NOT_ISSUED",
    "forecast_issued": False,
    "forecast_eligible": False,
    "council_action": "NOT_ISSUED",
    "orchestrator_weight_multiplier": None,
    "reason_code": "LEGACY_UNVALIDATED_COUNCIL_ACTION_QUARANTINED",
}


class CouncilIngestionEngine:
    def parse_physical_artifact(self):
        return dict(STATUS)

    def calculate_and_inject(self, metrics=None):
        return dict(STATUS)


def main():
    print(json.dumps(STATUS, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
