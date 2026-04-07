"""Agent-side security audit logger — records security-relevant events."""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class SecurityAuditLogger:
    """Record and query security events from the agent side.

    Events are kept in an in-memory list (for test-friendliness) and also
    emitted through the Python ``logging`` system so they appear in application
    logs.

    Example::

        sal = SecurityAuditLogger(agent_id="inference_agent")
        sal.log_execution(["python3", "run.py"], {"returncode": 0}, "inference_agent")
        events = sal.get_security_events()
    """

    def __init__(self, agent_id: str = "default") -> None:
        self._default_agent_id = agent_id
        self._events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._logger = logging.getLogger(f"barrot.security.audit.{agent_id}")

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def log_execution(
        self,
        command: Any,
        result: Dict[str, Any],
        agent_id: Optional[str] = None,
    ) -> None:
        """Record a command execution event.

        Args:
            command:  The command that was executed (list or string).
            result:   Result dict (at minimum ``returncode``).
            agent_id: Overrides the default agent_id.
        """
        self._record(
            event_type="execution",
            data={
                "command": command if isinstance(command, str) else list(command),
                "returncode": result.get("returncode"),
                "stdout_len": len(result.get("stdout", "")),
                "stderr_len": len(result.get("stderr", "")),
            },
            agent_id=agent_id,
        )

    def log_network_attempt(
        self,
        domain: str,
        allowed: bool,
        agent_id: Optional[str] = None,
    ) -> None:
        """Record a network access attempt.

        Args:
            domain:   Target domain name.
            allowed:  Whether the attempt was permitted.
            agent_id: Overrides the default agent_id.
        """
        self._record(
            event_type="network_attempt",
            data={"domain": domain, "allowed": allowed},
            agent_id=agent_id,
            level=logging.INFO if allowed else logging.WARNING,
        )

    def log_filesystem_access(
        self,
        path: str,
        access_type: str,
        allowed: bool,
        agent_id: Optional[str] = None,
    ) -> None:
        """Record a filesystem access event.

        Args:
            path:        The file-system path that was accessed.
            access_type: One of ``"read"``, ``"write"``, ``"append"``.
            allowed:     Whether the access was permitted.
            agent_id:    Overrides the default agent_id.
        """
        self._record(
            event_type="filesystem_access",
            data={"path": path, "access_type": access_type, "allowed": allowed},
            agent_id=agent_id,
            level=logging.INFO if allowed else logging.WARNING,
        )

    def log_policy_violation(
        self,
        violation: Dict[str, Any],
        agent_id: Optional[str] = None,
    ) -> None:
        """Record a policy violation.

        Args:
            violation: Dict describing the violation (e.g. ``reason``, ``action``).
            agent_id:  Overrides the default agent_id.
        """
        self._record(
            event_type="policy_violation",
            data=violation,
            agent_id=agent_id,
            level=logging.ERROR,
        )

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def get_security_events(
        self, agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return stored security events, optionally filtered by *agent_id*.

        Args:
            agent_id: If provided, only events for this agent are returned.

        Returns:
            List of event dicts sorted by timestamp ascending.
        """
        with self._lock:
            events = list(self._events)
        if agent_id is not None:
            events = [e for e in events if e.get("agent_id") == agent_id]
        return sorted(events, key=lambda e: e.get("timestamp", ""))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _record(
        self,
        event_type: str,
        data: Dict[str, Any],
        agent_id: Optional[str],
        level: int = logging.INFO,
    ) -> None:
        agent = agent_id or self._default_agent_id
        event: Dict[str, Any] = {
            "event_type": event_type,
            "agent_id": agent,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            **data,
        }
        with self._lock:
            self._events.append(event)
        self._logger.log(level, json.dumps(event, default=str))
