"""Persist only verified Barrot learning records."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .learning_filter import LearningRecord


class VerifiedLearningStore:
    """Append accepted learning records to a curated JSONL store."""

    def __init__(
        self,
        path: str | Path = "data/evolution/verified_lessons.jsonl",
    ):
        self.path = Path(path)


    def read_all(self) -> list[dict]:
        """Read all persisted verified learning records."""

        if not self.path.exists():
            return []

        records: list[dict] = []

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if isinstance(payload, dict):
                    records.append(payload)

        return records

    def append(self, record: LearningRecord) -> bool:
        """Persist an accepted learning record."""

        if not record.accepted:
            return False

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "lesson": record.lesson,
            "reason": record.reason,
            "recorded_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                json.dumps(
                    payload,
                    sort_keys=True,
                )
                + "\n"
            )

        return True
