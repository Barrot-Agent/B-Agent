"""Persist only novel verified Barrot learning records."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .learning_filter import LearningRecord


class VerifiedLearningStore:
    """Append accepted and novel learning records to a curated JSONL store."""

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

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for duplicate comparison."""

        return " ".join(
            text.lower().split()
        )

    @classmethod
    def _lesson_id(cls, lesson: str) -> str:
        """Create a stable identity for a lesson."""

        normalized = cls._normalize(lesson)

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    def contains(self, lesson: str) -> bool:
        """Return True if the exact normalized lesson already exists."""

        lesson_id = self._lesson_id(lesson)

        for record in self.read_all():
            existing_id = record.get("lesson_id")

            if existing_id == lesson_id:
                return True

            existing_lesson = record.get("lesson")

            if isinstance(existing_lesson, str):
                if self._normalize(existing_lesson) == self._normalize(lesson):
                    return True

        return False

    def append(self, record: LearningRecord) -> bool:
        """Persist an accepted learning record only if it is novel."""

        if not record.accepted:
            return False

        if not record.lesson.strip():
            return False

        if self.contains(record.lesson):
            return False

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "lesson_id": self._lesson_id(record.lesson),
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
