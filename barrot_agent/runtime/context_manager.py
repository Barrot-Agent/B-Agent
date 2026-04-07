"""Execution context management — track per-session state for agents."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionContext:
    """Immutable snapshot of a single agent execution session.

    Attributes:
        agent_id:     Identifier of the agent owning the session.
        session_id:   Unique UUID string assigned at context creation.
        policy_name:  Name of the active security policy.
        start_time:   UTC timestamp when the context was created.
        metadata:     Free-form dict of additional session data.
    """

    agent_id: str
    session_id: str
    policy_name: str
    start_time: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """Create and manage :class:`ExecutionContext` objects for agent sessions.

    All operations are thread-safe.

    Example::

        cm = ContextManager()
        ctx = cm.create_context("inference_agent", "default_policy")
        cm.update_context(ctx.session_id, {"model": "llama3"})
        cm.close_context(ctx.session_id)
    """

    def __init__(self) -> None:
        self._contexts: Dict[str, ExecutionContext] = {}
        self._lock = threading.RLock()

    def create_context(
        self,
        agent_id: str,
        policy_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionContext:
        """Create a new session context.

        Args:
            agent_id:    Agent identifier.
            policy_name: Name of the policy to associate with this session.
            metadata:    Optional initial metadata dict.

        Returns:
            The newly created :class:`ExecutionContext`.
        """
        session_id = str(uuid.uuid4())
        ctx = ExecutionContext(
            agent_id=agent_id,
            session_id=session_id,
            policy_name=policy_name,
            start_time=datetime.now(tz=timezone.utc),
            metadata=dict(metadata or {}),
        )
        with self._lock:
            self._contexts[session_id] = ctx
        return ctx

    def get_context(self, session_id: str) -> Optional[ExecutionContext]:
        """Retrieve the context for *session_id*, or ``None`` if not found.

        Args:
            session_id: UUID string returned by :meth:`create_context`.
        """
        with self._lock:
            return self._contexts.get(session_id)

    def update_context(
        self, session_id: str, updates: Dict[str, Any]
    ) -> ExecutionContext:
        """Merge *updates* into the metadata of an existing context.

        Args:
            session_id: Target session UUID.
            updates:    Dict of metadata fields to merge.

        Returns:
            The updated :class:`ExecutionContext`.

        Raises:
            KeyError: When *session_id* is not found.
        """
        with self._lock:
            ctx = self._contexts.get(session_id)
            if ctx is None:
                raise KeyError(f"Session '{session_id}' not found")
            # dataclass fields are mutable via direct assignment
            ctx.metadata.update(updates)
            return ctx

    def close_context(self, session_id: str) -> Optional[ExecutionContext]:
        """Remove and return the context for *session_id*.

        Args:
            session_id: Target session UUID.

        Returns:
            The removed :class:`ExecutionContext`, or ``None`` if not found.
        """
        with self._lock:
            return self._contexts.pop(session_id, None)

    def list_active_contexts(self) -> List[ExecutionContext]:
        """Return a list of all currently active contexts."""
        with self._lock:
            return list(self._contexts.values())
