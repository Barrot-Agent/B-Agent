"""
Barrot Reactive Cognitive Event Bus.

Provides lightweight in-process communication between engines. Events are
recorded for auditability and dispatched synchronously to registered handlers.
Handlers observe events and may produce new documented outcomes, but the bus
does not permit uncontrolled recursive dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from barrot_agent.evolution.cognitive_integrity import CognitiveIntegrityLoop

EventHandler = Callable[["CognitiveEvent"], Any]


@dataclass
class CognitiveEvent:
    """A structured event produced by a Barrot engine."""

    event_type: str
    payload: dict[str, Any]
    source: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CognitiveEventBus:
    """Route cognitive events through registered observers."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}
        self.integrity = CognitiveIntegrityLoop()
        self._dispatching = False

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for an event type."""
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: CognitiveEvent) -> list[Any]:
        """
        Record and dispatch an event.

        Nested publishing is blocked to prevent accidental recursive loops.
        A future queue-based orchestrator can deliberately support controlled
        multi-step workflows.
        """
        self.integrity.record_outcome(
            operation=f"event:{event.event_type}",
            outcome={
                "payload": event.payload,
                "source": event.source,
                "created_at": event.created_at,
            },
            sources=[event.source],
            confidence=0.7,
        )

        if self._dispatching:
            return []

        self._dispatching = True
        try:
            results = []
            for handler in self._handlers.get(event.event_type, []):
                try:
                    results.append(handler(event))
                except Exception as error:
                    results.append(
                        {
                            "status": "handler_error",
                            "handler": getattr(handler, "__name__", "anonymous"),
                            "error": str(error),
                        }
                    )
            return results
        finally:
            self._dispatching = False
