"""
Event System - Publish/subscribe, signal system, event queuing.

Implements:
- Type-safe event publishing and subscription
- Signal-based communication between systems
- Event queuing and deferred dispatch
- Priority-ordered event handling
- Broadcast and targeted event delivery
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar

T = TypeVar("T")


@dataclass
class Event:
    """Base class for all game events."""
    name: str = ""
    timestamp: float = field(default_factory=time.time)
    source: Any = None
    data: Dict[str, Any] = field(default_factory=dict)
    consumed: bool = False
    priority: int = 0   # Higher = processed first


@dataclass
class Subscription:
    """A subscription handle for event callbacks."""
    event_type: str
    callback: Callable
    priority: int = 0
    once: bool = False
    filter_fn: Optional[Callable[[Event], bool]] = None

    def matches(self, event: Event) -> bool:
        """Check if this subscription matches an event."""
        if self.filter_fn:
            return self.filter_fn(event)
        return True


class Signal(Generic[T]):
    """
    Typed signal for direct system-to-system communication.

    Usage:
        health_changed = Signal[int]()
        health_changed.connect(on_health_changed)
        health_changed.emit(50)
    """

    def __init__(self):
        self._listeners: List[Callable[[T], None]] = []

    def connect(self, callback: Callable[[T], None]) -> None:
        """Connect a callback to this signal."""
        self._listeners.append(callback)

    def disconnect(self, callback: Callable[[T], None]) -> bool:
        """Disconnect a callback from this signal."""
        try:
            self._listeners.remove(callback)
            return True
        except ValueError:
            return False

    def emit(self, value: T) -> None:
        """Emit the signal with a value, calling all listeners."""
        for listener in self._listeners[:]:
            listener(value)

    def clear(self) -> None:
        """Remove all listeners."""
        self._listeners.clear()

    def has_listeners(self) -> bool:
        """Check if there are any connected listeners."""
        return bool(self._listeners)


class EventBus:
    """Central event bus for publish/subscribe messaging."""

    def __init__(self):
        self._subscriptions: Dict[str, List[Subscription]] = {}
        self._queued_events: List[Event] = []
        self._processing = False

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Event], None],
        priority: int = 0,
        once: bool = False,
        filter_fn: Optional[Callable[[Event], bool]] = None,
    ) -> Subscription:
        """Subscribe to an event type."""
        sub = Subscription(
            event_type=event_type,
            callback=callback,
            priority=priority,
            once=once,
            filter_fn=filter_fn,
        )
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
        self._subscriptions[event_type].append(sub)
        # Keep subscriptions sorted by priority (descending)
        self._subscriptions[event_type].sort(key=lambda s: -s.priority)
        return sub

    def unsubscribe(self, subscription: Subscription) -> bool:
        """Remove a subscription."""
        subs = self._subscriptions.get(subscription.event_type, [])
        try:
            subs.remove(subscription)
            return True
        except ValueError:
            return False

    def publish(self, event: Event) -> int:
        """
        Publish an event immediately to all subscribers.
        Returns the number of callbacks invoked.
        """
        subs = self._subscriptions.get(event.name, [])
        called = 0
        to_remove = []

        for sub in subs:
            if event.consumed:
                break
            if sub.matches(event):
                sub.callback(event)
                called += 1
                if sub.once:
                    to_remove.append(sub)

        for sub in to_remove:
            try:
                subs.remove(sub)
            except ValueError:
                pass

        return called

    def queue(self, event: Event) -> None:
        """Queue an event for deferred processing."""
        self._queued_events.append(event)

    def process_queue(self) -> int:
        """Process all queued events. Returns number of events processed."""
        if self._processing:
            return 0  # Prevent re-entrancy

        self._processing = True
        events = sorted(self._queued_events, key=lambda e: -e.priority)
        self._queued_events.clear()
        total = 0

        for event in events:
            total += self.publish(event)

        self._processing = False
        return total

    def clear_subscriptions(self, event_type: str) -> None:
        """Remove all subscriptions for an event type."""
        self._subscriptions.pop(event_type, None)

    def get_subscriber_count(self, event_type: str) -> int:
        """Return number of subscribers for an event type."""
        return len(self._subscriptions.get(event_type, []))


class EventSystem:
    """
    Complete event system with bus, signals, and broadcast support.

    Combines a central event bus with typed signals for flexible
    inter-system communication patterns.
    """

    def __init__(self):
        self.bus = EventBus()
        self._signals: Dict[str, Signal] = {}
        self._broadcast_history: List[Event] = []
        self._max_history = 1000

    def emit(
        self,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
        source: Any = None,
        priority: int = 0,
        deferred: bool = False,
    ) -> None:
        """Emit a named event."""
        event = Event(
            name=event_name,
            data=data or {},
            source=source,
            priority=priority,
        )
        if deferred:
            self.bus.queue(event)
        else:
            self.bus.publish(event)
            if len(self._broadcast_history) < self._max_history:
                self._broadcast_history.append(event)

    def on(
        self,
        event_name: str,
        callback: Callable,
        priority: int = 0,
        once: bool = False,
    ) -> Subscription:
        """Subscribe to an event."""
        return self.bus.subscribe(event_name, callback, priority, once)

    def off(self, subscription: Subscription) -> bool:
        """Unsubscribe from an event."""
        return self.bus.unsubscribe(subscription)

    def signal(self, name: str) -> Signal:
        """Get or create a named signal."""
        if name not in self._signals:
            self._signals[name] = Signal()
        return self._signals[name]

    def update(self) -> int:
        """Process deferred event queue. Call once per frame."""
        return self.bus.process_queue()

    def get_history(self, event_name: Optional[str] = None) -> List[Event]:
        """Return event history, optionally filtered by event name."""
        if event_name:
            return [e for e in self._broadcast_history if e.name == event_name]
        return self._broadcast_history.copy()
