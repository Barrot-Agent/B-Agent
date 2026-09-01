"""
Barrot Confidence Calibration.

Records predictions and later outcomes so confidence can eventually be compared
against observed accuracy. This module does not fabricate outcomes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "evolution"
CALIBRATION_FILE = DATA_DIR / "confidence_calibration.json"


class ConfidenceCalibrationEngine:
    """Maintain an auditable history of confidence assessments."""

    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[dict[str, Any]]:
        if not CALIBRATION_FILE.exists():
            return []

        try:
            return json.loads(CALIBRATION_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, records: list[dict[str, Any]]) -> None:
        CALIBRATION_FILE.write_text(
            json.dumps(records, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    def record(
        self,
        claim_id: str,
        confidence: float,
        status: str,
        trust: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "claim_id": claim_id,
            "confidence": round(float(confidence), 3),
            "status": status,
            "outcome": None,
            "trust": trust or {},
        }

        records = self.load()
        records.append(record)
        self.save(records)
        return record

    def trust_summary(self) -> dict[str, Any]:
        records = self.load()

        authoritative_records = 0
        confidence_values: list[float] = []

        for record in records:
            trust = record.get("trust") or {}

            # Per-record verification format.
            if trust.get("authoritative") is True:
                authoritative_records += 1

            # Aggregate corroboration format.
            aggregate = trust.get("authoritative_records")
            evaluated = trust.get("records_evaluated")

            if (
                isinstance(aggregate, int)
                and aggregate > 0
                and isinstance(evaluated, int)
                and evaluated > 0
            ):
                authoritative_records += 1

            aggregate_confidence = trust.get(
                "average_trust_confidence"
            )

            if isinstance(
                aggregate_confidence,
                (int, float),
            ):
                confidence_values.append(
                    float(aggregate_confidence)
                )

            nested = trust.get("confidence")

            if isinstance(nested, dict):
                lower_bound = nested.get("lower_bound")

                if isinstance(
                    lower_bound,
                    (int, float),
                ):
                    confidence_values.append(
                        float(lower_bound)
                    )

        return {
            "records": len(records),
            "authoritative_records": authoritative_records,
            "average_trust_confidence": round(
                (
                    sum(confidence_values)
                    / len(confidence_values)
                )
                if confidence_values
                else 0.0,
                3,
            ),
        }


    def resolve(
        self,
        claim_id: str,
        outcome: bool,
    ) -> bool:
        records = self.load()

        for record in reversed(records):
            if record.get("claim_id") == claim_id and record.get("outcome") is None:
                record["outcome"] = bool(outcome)
                self.save(records)
                return True

        return False

    def summary(self) -> dict[str, Any]:
        records = self.load()
        resolved = [record for record in records if record.get("outcome") is not None]

        if not resolved:
            return {
                "records": len(records),
                "resolved": 0,
                "accuracy": None,
            }

        correct = sum(
            (record["confidence"] >= 0.5 and record["outcome"] is True)
            or (record["confidence"] < 0.5 and record["outcome"] is False)
            for record in resolved
        )

        return {
            "records": len(records),
            "resolved": len(resolved),
            "accuracy": round(correct / len(resolved), 3),
        }
