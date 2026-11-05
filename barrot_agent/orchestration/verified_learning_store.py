"""Persist only novel, structurally verified Barrot learning records."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .learning_filter import LearningRecord


VERIFIED_LEARNING_SCHEMA = "barrot.verified-learning.v1"
VERIFIED_LEARNING_REASON = "Deep inspection actions and verification succeeded."
_DEEP_ACTIONS = ("READ_FILE", "SEARCH_TEXT", "RUN_TESTS")


class VerifiedLearningStore:
    """Append accepted learning records and expose only validated records to curriculum."""

    def __init__(
        self,
        path: str | Path = "data/evolution/verified_lessons.jsonl",
    ):
        self.path = Path(path)

    def read_all(self) -> list[dict]:
        """Read every parseable persisted record, including legacy or rejected records."""

        if not self.path.exists():
            return []

        records: list[dict] = []
        with self.path.open("r", encoding="utf-8") as handle:
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
        """Normalize text for duplicate comparison and stable identity."""
        return " ".join(text.lower().split())

    @classmethod
    def _lesson_id(cls, lesson: str) -> str:
        """Create a stable identity for the exact normalized lesson."""
        normalized = cls._normalize(lesson)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _has_deep_verification_findings(lesson: str) -> bool:
        """Require the exact LearningFilter findings shape and a deep action."""
        lines = [line.strip() for line in lesson.splitlines()]
        if "Verified findings:" not in lines:
            return False
        return any(
            line.startswith(f"- {action}:") and bool(line[len(action) + 3 :].strip())
            for line in lines
            for action in _DEEP_ACTIONS
        )

    @staticmethod
    def _has_aware_timestamp(value: object) -> bool:
        if not isinstance(value, str) or not value.strip():
            return False
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return False
        return parsed.tzinfo is not None and parsed.utcoffset() is not None

    @classmethod
    def _is_verified_payload(cls, payload: dict) -> bool:
        lesson = payload.get("lesson")
        if not isinstance(lesson, str) or not lesson.strip():
            return False
        if payload.get("schema_version") != VERIFIED_LEARNING_SCHEMA:
            return False
        if payload.get("lesson_id") != cls._lesson_id(lesson):
            return False
        if payload.get("reason") != VERIFIED_LEARNING_REASON:
            return False
        if not cls._has_aware_timestamp(payload.get("recorded_at")):
            return False
        return cls._has_deep_verification_findings(lesson)

    def read_verified(self) -> list[dict]:
        """Return only records matching the current verified-learning contract.

        Legacy records remain available through read_all(), but cannot advance
        the primary mission because they lack the current evidence structure.
        """
        return [
            record
            for record in self.read_all()
            if self._is_verified_payload(record)
        ]

    def contains(self, lesson: str) -> bool:
        """Return True only when an identical structurally verified lesson exists."""
        lesson_id = self._lesson_id(lesson)
        return any(record.get("lesson_id") == lesson_id for record in self.read_verified())

    def append(self, record: LearningRecord) -> bool:
        """Persist a novel accepted lesson only when its verification structure is valid."""
        if record.accepted is not True:
            return False
        if not isinstance(record.lesson, str) or not record.lesson.strip():
            return False
        if record.reason != VERIFIED_LEARNING_REASON:
            return False
        if not self._has_deep_verification_findings(record.lesson):
            return False

        payload = {
            "schema_version": VERIFIED_LEARNING_SCHEMA,
            "lesson_id": self._lesson_id(record.lesson),
            "lesson": record.lesson,
            "reason": record.reason,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        if not self._is_verified_payload(payload):
            return False
        if self.contains(record.lesson):
            return False

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\\n")
        return True
