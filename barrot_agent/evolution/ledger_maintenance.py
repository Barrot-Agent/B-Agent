"""Maintenance utilities for Barrot's bounded cognitive event ledger."""

from __future__ import annotations

import json

from barrot_agent.evolution.cognitive_integrity import (
    CognitiveIntegrityLoop,
    LEDGER_FILE,
)

MAX_RECORDS = 2000


def compact_ledger(max_records: int = MAX_RECORDS) -> dict[str, int]:
    """Retain the most recent bounded set of integrity records."""
    loop = CognitiveIntegrityLoop()
    ledger = loop.load_ledger()

    original_count = len(ledger)
    if original_count <= max_records:
        return {"before": original_count, "after": original_count, "removed": 0}

    retained = ledger[-max_records:]
    LEDGER_FILE.write_text(
        json.dumps(retained, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    return {
        "before": original_count,
        "after": len(retained),
        "removed": original_count - len(retained),
    }


if __name__ == "__main__":
    print(compact_ledger())
