"""
AuditTrail — append-only event log for all Apex Lattice activity.

All events are persisted as newline-delimited JSON under
``.apex_lattice/audit_logs/``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

_DEFAULT_LOG_DIR = Path(".apex_lattice") / "audit_logs"


class AuditTrail:
    """Append-only structured event log."""

    def __init__(self, log_dir: Path | str | None = None) -> None:
        self._dir = Path(log_dir) if log_dir else _DEFAULT_LOG_DIR
        self._dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self._dir / "apex_lattice.jsonl"

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def log(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Append a structured event to the audit log."""
        entry: dict[str, Any] = {
            "ts": time.time(),
            "event": event_type,
        }
        if data:
            entry["data"] = data
        with self._log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        """Return all logged events as a list of dicts."""
        if not self._log_file.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in self._log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return events

    def tail(self, n: int = 20) -> list[dict[str, Any]]:
        """Return the last *n* events."""
        return self.read_all()[-n:]

    def clear(self) -> None:
        """Delete the log file (for testing / reset scenarios)."""
        if self._log_file.exists():
            self._log_file.unlink()

    @property
    def log_path(self) -> Path:
        return self._log_file
