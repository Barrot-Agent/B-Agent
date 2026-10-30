"""Tamper-evident append-only MMI execution ledger."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


GENESIS = "0" * 64


class LedgerIntegrityError(RuntimeError):
    """Raised when canonical ledger history is malformed or altered."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class MMIExecutionLedger:
    """Append-only JSONL ledger with sequence numbers and hash chaining.

    A malformed line is fatal. The ledger is never silently reset, repaired,
    compacted, or truncated by this class.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _record_hash(record: dict[str, Any]) -> str:
        body = {key: value for key, value in record.items() if key != "record_hash"}
        return hashlib.sha256(_canonical(body)).hexdigest()

    def verify(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        previous = GENESIS
        with self.path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    raise LedgerIntegrityError(f"blank ledger line at {line_number}")
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise LedgerIntegrityError(f"malformed ledger line {line_number}") from exc
                expected_sequence = len(records) + 1
                if record.get("sequence") != expected_sequence:
                    raise LedgerIntegrityError(f"invalid sequence at line {line_number}")
                if record.get("previous_hash") != previous:
                    raise LedgerIntegrityError(f"broken hash link at line {line_number}")
                if record.get("record_hash") != self._record_hash(record):
                    raise LedgerIntegrityError(f"record hash mismatch at line {line_number}")
                records.append(record)
                previous = record["record_hash"]
        return records

    def append(
        self,
        *,
        execution_id: str,
        event_type: str,
        payload: dict[str, Any],
        evaluator_version: str,
        actor: str,
        authorization_ref: str | None = None,
        parent_execution_id: str | None = None,
    ) -> dict[str, Any]:
        if not execution_id or not event_type or not evaluator_version or not actor:
            raise ValueError("execution_id, event_type, evaluator_version, and actor are required")
        records = self.verify()
        previous = records[-1]["record_hash"] if records else GENESIS
        record: dict[str, Any] = {
            "sequence": len(records) + 1,
            "execution_id": execution_id,
            "parent_execution_id": parent_execution_id,
            "event_type": event_type,
            "payload": payload,
            "evaluator_version": evaluator_version,
            "actor": actor,
            "authorization_ref": authorization_ref,
            "previous_hash": previous,
        }
        record["record_hash"] = self._record_hash(record)
        encoded = _canonical(record).decode("utf-8") + "\n"
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        return record
