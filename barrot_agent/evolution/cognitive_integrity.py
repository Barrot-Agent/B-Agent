"""
Barrot Cognitive Integrity Loop.

Records processing outcomes, preserves provenance, detects contradictions,
and connects Barrot's reasoning with its evolution and research systems.

This layer observes and evaluates. It does not silently modify production code.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "evolution"
LEDGER_FILE = DATA_DIR / "outcome_ledger.json"


class CognitiveIntegrityLoop:
    """Persistent evidence and outcome integrity layer for Barrot."""

    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load_ledger(self) -> list[dict[str, Any]]:
        if not LEDGER_FILE.exists():
            return []
        try:
            return json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def record_outcome(
        self,
        operation: str,
        outcome: Any,
        sources: list[str] | None = None,
        confidence: float = 0.5,
    ) -> dict[str, Any]:
        """Record a processing outcome with provenance."""

        ledger = self.load_ledger()
        serialized = json.dumps(outcome, sort_keys=True, default=str)
        record_id = hashlib.sha256(f"{operation}:{serialized}".encode()).hexdigest()

        record = {
            "id": record_id,
            "operation": operation,
            "outcome": outcome,
            "sources": sources or [],
            "confidence": max(0.0, min(1.0, confidence)),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }

        if not any(item.get("id") == record_id for item in ledger):
            ledger.append(record)
            LEDGER_FILE.write_text(
                json.dumps(ledger, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )

        return record

    def evaluate_integrity(self) -> dict[str, Any]:
        """Measure provenance coverage and confidence across outcomes."""

        ledger = self.load_ledger()
        if not ledger:
            return {
                "records": 0,
                "integrity_score": 0.0,
                "status": "no_data",
            }

        sourced = sum(bool(item.get("sources")) for item in ledger)
        average_confidence = sum(item.get("confidence", 0.0) for item in ledger) / len(ledger)

        provenance_ratio = sourced / len(ledger)
        integrity_score = (provenance_ratio + average_confidence) / 2

        return {
            "records": len(ledger),
            "provenance_ratio": round(provenance_ratio, 3),
            "average_confidence": round(average_confidence, 3),
            "integrity_score": round(integrity_score, 3),
            "status": (
                "strong"
                if integrity_score >= 0.8
                else "developing" if integrity_score >= 0.5 else "requires_corroboration"
            ),
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }


if __name__ == "__main__":
    loop = CognitiveIntegrityLoop()
    print(json.dumps(loop.evaluate_integrity(), indent=2))
