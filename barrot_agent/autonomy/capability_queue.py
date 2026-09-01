"""Sequential autonomous capability queue for Barrot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


QUEUE_PATH = Path("data/autonomy/capability_queue.json")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Capability:
    id: str
    name: str
    status: str = "pending"
    priority: int = 0
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        now = utcnow()

        if not self.created_at:
            self.created_at = now

        if not self.updated_at:
            self.updated_at = now

        if self.metadata is None:
            self.metadata = {}


class CapabilityQueue:
    """Persistent sequential capability queue."""

    def __init__(
        self,
        path: Path = QUEUE_PATH,
    ) -> None:
        self.path = path
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load(self) -> list[Capability]:
        if not self.path.exists():
            return []

        raw = json.loads(
            self.path.read_text(
                encoding="utf-8",
            )
        )

        return [
            Capability(**item)
            for item in raw
        ]

    def save(
        self,
        capabilities: list[Capability],
    ) -> None:
        payload = [
            asdict(item)
            for item in capabilities
        ]

        self.path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    def add(
        self,
        capability: Capability,
    ) -> None:
        items = self.load()

        if any(
            item.id == capability.id
            for item in items
        ):
            return

        items.append(capability)

        items.sort(
            key=lambda item: (
                item.priority,
                item.created_at,
            )
        )

        self.save(items)

    def next(self) -> Capability | None:
        for item in self.load():
            if item.status == "pending":
                return item

        return None

    def update_status(
        self,
        capability_id: str,
        status: str,
    ) -> Capability:
        items = self.load()

        for item in items:
            if item.id == capability_id:
                item.status = status
                item.updated_at = utcnow()

                self.save(items)

                return item

        raise KeyError(
            f"Capability not found: {capability_id}"
        )
