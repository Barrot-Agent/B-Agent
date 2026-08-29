"""
Barrot Shared Evidence Store.

Maintains normalized claims independently from the cognitive outcome ledger.
The store preserves provenance and deduplicates evidence by claim identity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "evolution"
STORE_FILE = DATA_DIR / "evidence_store.json"


class EvidenceStore:
    """Persistent, bounded-access store for normalized evidence."""

    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[dict[str, Any]]:
        if not STORE_FILE.exists():
            return []

        try:
            return json.loads(STORE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, records: list[dict[str, Any]]) -> None:
        STORE_FILE.write_text(
            json.dumps(records, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    def add(self, evidence: dict[str, Any]) -> dict[str, Any]:
        """Store evidence unless an identical claim/source record exists."""
        claim_id = evidence.get("claim_id")
        if not claim_id:
            raise ValueError("Evidence requires a claim_id")

        records = self.load()

        # The same claim can be supported by multiple independent sources.
        duplicate = any(
            record.get("claim_id") == claim_id and record.get("source") == evidence.get("source")
            for record in records
        )

        if duplicate:
            return {"status": "duplicate", "claim_id": claim_id}

        records.append(evidence)
        self.save(records)

        return {"status": "stored", "claim_id": claim_id}

    def get(self, claim_id: str) -> list[dict[str, Any]]:
        """Return all evidence records associated with a claim."""
        return [record for record in self.load() if record.get("claim_id") == claim_id]

    def by_source(self, source: str) -> list[dict[str, Any]]:
        """Return evidence originating from a specific source."""
        return [record for record in self.load() if record.get("source") == source]

    def summary(self) -> dict[str, int]:
        records = self.load()
        return {
            "records": len(records),
            "claims": len({record.get("claim_id") for record in records}),
            "sources": len({record.get("source") for record in records}),
        }
