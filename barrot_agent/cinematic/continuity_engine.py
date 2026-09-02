from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
import hashlib
import json


@dataclass
class ContinuityEvent:
    event_id: str
    scene_id: str
    subject: str
    attribute: str
    value: Any
    timestamp: str
    previous_hash: str
    event_hash: str


@dataclass
class ContinuityConflict:
    subject: str
    attribute: str
    established_value: Any
    proposed_value: Any
    established_scene: str
    proposed_scene: str
    severity: str = "warning"


class ContinuityEngine:
    """
    Chronological continuity system.

    History is append-only. Corrections create new events instead of rewriting
    the record, preserving reproducibility of the production timeline.
    """

    def __init__(self) -> None:
        self.events: list[ContinuityEvent] = []

    def _latest(self, subject: str, attribute: str) -> ContinuityEvent | None:
        for event in reversed(self.events):
            if event.subject == subject and event.attribute == attribute:
                return event
        return None

    def record(
        self,
        scene_id: str,
        subject: str,
        attribute: str,
        value: Any,
    ) -> ContinuityEvent:
        previous_hash = self.events[-1].event_hash if self.events else ""
        payload = {
            "scene_id": scene_id,
            "subject": subject,
            "attribute": attribute,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_hash": previous_hash,
        }
        raw = json.dumps(payload, sort_keys=True, default=str)
        event_hash = hashlib.sha256(raw.encode()).hexdigest()
        event = ContinuityEvent(
            event_id=event_hash[:16],
            event_hash=event_hash,
            **payload,
        )
        self.events.append(event)
        return event

    def check(
        self,
        scene_id: str,
        subject: str,
        attribute: str,
        proposed_value: Any,
        allow_change: bool = False,
    ) -> ContinuityConflict | None:
        latest = self._latest(subject, attribute)
        if not latest or latest.value == proposed_value or allow_change:
            return None

        return ContinuityConflict(
            subject=subject,
            attribute=attribute,
            established_value=latest.value,
            proposed_value=proposed_value,
            established_scene=latest.scene_id,
            proposed_scene=scene_id,
            severity="error",
        )

    def validate_scene(
        self,
        scene_id: str,
        assertions: list[dict[str, Any]],
    ) -> list[ContinuityConflict]:
        conflicts = []
        for assertion in assertions:
            conflict = self.check(
                scene_id=scene_id,
                subject=assertion["subject"],
                attribute=assertion["attribute"],
                proposed_value=assertion["value"],
                allow_change=assertion.get("allow_change", False),
            )
            if conflict:
                conflicts.append(conflict)
        return conflicts

    def ledger(self) -> list[dict[str, Any]]:
        return [asdict(event) for event in self.events]

    def verify_integrity(self) -> bool:
        previous_hash = ""
        for event in self.events:
            payload = {
                "scene_id": event.scene_id,
                "subject": event.subject,
                "attribute": event.attribute,
                "value": event.value,
                "timestamp": event.timestamp,
                "previous_hash": event.previous_hash,
            }
            expected = hashlib.sha256(
                json.dumps(payload, sort_keys=True, default=str).encode()
            ).hexdigest()

            if event.previous_hash != previous_hash or event.event_hash != expected:
                return False
            previous_hash = event.event_hash
        return True
