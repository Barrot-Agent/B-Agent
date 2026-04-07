"""OpenShell Audit Engine — durable, queryable record of all agent actions."""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from openshell.audit.audit_logger import AuditLogger


class AuditEngine:
    """Central component for recording and querying agent audit trails.

    All events are persisted as newline-delimited JSON (NDJSON) in
    *audit_directory*.  An in-memory index is kept so that query methods
    do not need to re-read every file on each call.

    Example::

        engine = AuditEngine("/audit")
        engine.record_action("inference", {"model": "llama3"}, "inference_agent", "success")
        trail = engine.get_audit_trail(agent_id="inference_agent")
    """

    def __init__(self, audit_directory: str = "/audit") -> None:
        self._audit_dir = Path(audit_directory)
        self._audit_dir.mkdir(parents=True, exist_ok=True)
        self._records: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._logger = AuditLogger(str(self._audit_dir))
        self._load_existing_records()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_action(
        self,
        action_type: str,
        details: Dict[str, Any],
        agent_id: str,
        outcome: str = "success",
    ) -> str:
        """Persist an action record and return its unique event ID.

        Args:
            action_type: High-level category (e.g. ``"inference"``, ``"network_request"``).
            details:     Free-form dict with action-specific data.
            agent_id:    Identifier of the agent that performed the action.
            outcome:     ``"success"``, ``"failure"``, or ``"blocked"``.

        Returns:
            A UUID string identifying the new record.
        """
        event_id = str(uuid.uuid4())
        record: Dict[str, Any] = {
            "event_id": event_id,
            "event_kind": "action",
            "action_type": action_type,
            "agent_id": agent_id,
            "outcome": outcome,
            "details": details,
            "timestamp": _now_iso(),
        }
        self._append_record(record)
        self._logger.log_action(action_type, record)
        return event_id

    def record_violation(
        self,
        violation_type: str,
        details: Dict[str, Any],
        agent_id: str,
    ) -> str:
        """Persist a policy violation record.

        Args:
            violation_type: Category of violation (e.g. ``"unauthorized_network"``).
            details:        Contextual information about the violation.
            agent_id:       Identifier of the offending agent.

        Returns:
            A UUID string identifying the new record.
        """
        event_id = str(uuid.uuid4())
        record: Dict[str, Any] = {
            "event_id": event_id,
            "event_kind": "violation",
            "violation_type": violation_type,
            "agent_id": agent_id,
            "details": details,
            "timestamp": _now_iso(),
        }
        self._append_record(record)
        self._logger.log_violation(violation_type, record)
        return event_id

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def get_audit_trail(
        self,
        agent_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Return matching records from the in-memory index.

        Args:
            agent_id:   Filter to a specific agent (``None`` = all agents).
            start_time: Inclusive lower bound on record timestamp.
            end_time:   Inclusive upper bound on record timestamp.

        Returns:
            A list of matching record dicts sorted by timestamp ascending.
        """
        with self._lock:
            records = list(self._records)

        result: List[Dict[str, Any]] = []
        for rec in records:
            if agent_id is not None and rec.get("agent_id") != agent_id:
                continue
            ts = _parse_ts(rec.get("timestamp", ""))
            if start_time is not None and ts < start_time:
                continue
            if end_time is not None and ts > end_time:
                continue
            result.append(rec)
        return sorted(result, key=lambda r: r.get("timestamp", ""))

    def export_audit_log(self, format: str = "json") -> str:
        """Serialise the entire in-memory audit trail.

        Args:
            format: ``"json"`` (pretty-printed) or ``"ndjson"`` (one record per line).

        Returns:
            A string representation of all records.
        """
        with self._lock:
            records = list(self._records)

        if format == "ndjson":
            return "\n".join(json.dumps(r) for r in records)
        return json.dumps(records, indent=2, default=str)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _append_record(self, record: Dict[str, Any]) -> None:
        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        log_file = self._audit_dir / f"audit-{date_str}.ndjson"
        with self._lock:
            self._records.append(record)
            with open(log_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, default=str) + "\n")

    def _load_existing_records(self) -> None:
        """Populate in-memory index from any existing NDJSON files."""
        for path in sorted(self._audit_dir.glob("audit-*.ndjson")):
            try:
                with open(path, encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if line:
                            self._records.append(json.loads(line))
            except Exception:  # noqa: BLE001
                pass  # Corrupt file — skip silently


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _parse_ts(ts_str: str) -> datetime:
    try:
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)
