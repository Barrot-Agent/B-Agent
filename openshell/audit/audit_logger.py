"""Structured JSON audit logger for OpenShell events."""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class _JsonFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        payload: Dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "audit_data"):
            payload["data"] = record.audit_data  # type: ignore[attr-defined]
        return json.dumps(payload, default=str)


def _build_logger(name: str, log_dir: str) -> logging.Logger:
    """Create (or retrieve) a file-backed JSON logger."""
    logger = logging.getLogger(f"openshell.audit.{name}")
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)
    log_path = Path(log_dir) / f"{name}.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(str(log_path), encoding="utf-8")
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    # Also propagate to root so callers see output in tests
    logger.propagate = True
    return logger


class AuditLogger:
    """Write structured audit events to a JSON-lines log file.

    Example::

        al = AuditLogger("/var/log/barrot")
        al.log_action("inference", {"model": "llama3", "agent_id": "inference_agent"})
    """

    def __init__(self, log_dir: str = "/var/log/barrot") -> None:
        self._log_dir = log_dir
        self._logger = _build_logger("events", log_dir)
        self._records: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    def log_action(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record a normal agent action.

        Args:
            event_type: Short string describing the action.
            data:       Arbitrary dict of contextual fields.
        """
        self._emit("ACTION", event_type, data)

    def log_violation(self, violation_type: str, data: Dict[str, Any]) -> None:
        """Record a security policy violation.

        Args:
            violation_type: Category of violation.
            data:           Contextual details.
        """
        self._emit("VIOLATION", violation_type, data, level=logging.WARNING)

    def log_inference_request(
        self, model: str, endpoint: str, anonymized: bool
    ) -> None:
        """Record an outbound inference request.

        Args:
            model:      Name of the model being queried.
            endpoint:   Target endpoint identifier.
            anonymized: Whether PII was stripped before the request.
        """
        self._emit(
            "INFERENCE_REQUEST",
            "inference_request",
            {"model": model, "endpoint": endpoint, "anonymized": anonymized},
        )

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def get_log_entries(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Return in-memory log entries matching *filters*.

        Args:
            filters: Dict of field→value pairs that must all match.
                     ``None`` returns all entries.

        Returns:
            A (possibly empty) list of matching record dicts.
        """
        with self._lock:
            records = list(self._records)

        if not filters:
            return records

        result: List[Dict[str, Any]] = []
        for rec in records:
            if all(rec.get(k) == v for k, v in filters.items()):
                result.append(rec)
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _emit(
        self,
        kind: str,
        event_type: str,
        data: Dict[str, Any],
        level: int = logging.INFO,
    ) -> None:
        record_dict: Dict[str, Any] = {
            "kind": kind,
            "event_type": event_type,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            **data,
        }
        with self._lock:
            self._records.append(record_dict)

        log_record = self._logger.makeRecord(
            self._logger.name,
            level,
            "<audit>",
            0,
            f"{kind}:{event_type}",
            (),
            None,
        )
        log_record.audit_data = record_dict  # type: ignore[attr-defined]
        self._logger.handle(log_record)
