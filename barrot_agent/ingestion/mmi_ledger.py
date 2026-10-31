from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


GENESIS_HASH = "0" * 64


class MMILedger:
    """
    Append-only, hash-linked execution ledger.

    A broken chain is never silently repaired. Verification fails closed.
    """

    def __init__(self, path: str | Path = ".barrot/mmi/execution_ledger.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return records

    def verify(self) -> bool:
        previous = GENESIS_HASH

        for record in self._records():
            stored_hash = record.get("record_hash")
            if not stored_hash:
                return False

            body = dict(record)
            body.pop("record_hash", None)

            expected = sha256(
                json.dumps(
                    body,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()

            if record.get("previous_hash") != previous:
                return False

            if stored_hash != expected:
                return False

            previous = stored_hash

        return True

    def append(
        self,
        event: str,
        payload: dict[str, Any],
        *,
        source_id: str | None = None,
        result_hash: str | None = None,
    ) -> dict[str, Any]:
        if not self.verify():
            raise RuntimeError("MMI ledger chain verification failed; append denied")

        records = self._records()
        previous_hash = records[-1]["record_hash"] if records else GENESIS_HASH

        body = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "source_id": source_id,
            "result_hash": result_hash,
            "payload": payload,
            "previous_hash": previous_hash,
        }

        record_hash = sha256(
            json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()

        record = {**body, "record_hash": record_hash}

        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")

        return record
