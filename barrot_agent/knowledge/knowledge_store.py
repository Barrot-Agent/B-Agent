"""Persistent deduplicated knowledge storage for Barrot."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class KnowledgeStore:
    """Append-only JSONL knowledge store with deterministic deduplication."""

    def __init__(
        self,
        path: str | Path = "data/knowledge/knowledge.jsonl",
    ):
        self.path = Path(path)

    @staticmethod
    def fingerprint(
        *,
        kind: str,
        subject: str,
        content: str,
        source: str,
    ) -> str:
        payload = {
            "kind": kind.strip(),
            "subject": subject.strip(),
            "content": content.strip(),
            "source": source.strip(),
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(encoded).hexdigest()

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        records: list[dict[str, Any]] = []

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if isinstance(record, dict):
                    records.append(record)

        return records

    def add(
        self,
        *,
        kind: str,
        subject: str,
        content: str,
        source: str,
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                kind,
                subject,
                content,
                source,
            )
        ):
            raise ValueError(
                "kind, subject, content, and source must be non-empty strings"
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        fingerprint = self.fingerprint(
            kind=kind,
            subject=subject,
            content=content,
            source=source,
        )

        existing = {
            record.get("fingerprint")
            for record in self.read_all()
        }

        if fingerprint in existing:
            return False

        record = {
            "kind": kind,
            "subject": subject,
            "content": content,
            "source": source,
            "confidence": confidence,
            "metadata": metadata or {},
            "fingerprint": fingerprint,
            "recorded_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                json.dumps(
                    record,
                    sort_keys=True,
                    ensure_ascii=False,
                )
                + "\n"
            )

        return True
