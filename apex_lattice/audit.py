"""
AuditTrail — append-only event log for Apex Lattice activity.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFAULT_LOG_DIR = Path(".apex_lattice") / "audit_logs"


class AuditTrail:
    """Append-only structured event log."""

    def __init__(
        self,
        cycle_id_or_log_dir: str | Path | None = None,
        base_dir: Path | None = None,
    ) -> None:
        self.cycle_id: str | None = None
        log_dir: Path

        if base_dir is not None:
            self.cycle_id = str(cycle_id_or_log_dir or f"cycle_{int(time.time())}")
            log_dir = (base_dir / _DEFAULT_LOG_DIR)
            log_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self._log_file = log_dir / f"{ts}_{self.cycle_id}_audit.log"
            return

        if isinstance(cycle_id_or_log_dir, Path):
            log_dir = cycle_id_or_log_dir
            log_dir.mkdir(parents=True, exist_ok=True)
            self._log_file = log_dir / "apex_lattice.jsonl"
            return

        if (
            isinstance(cycle_id_or_log_dir, str)
            and (os.sep in cycle_id_or_log_dir or "/" in cycle_id_or_log_dir)
        ):
            log_dir = Path(cycle_id_or_log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            self._log_file = log_dir / "apex_lattice.jsonl"
            return

        log_dir = _DEFAULT_LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        if isinstance(cycle_id_or_log_dir, str) and cycle_id_or_log_dir:
            self.cycle_id = cycle_id_or_log_dir
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self._log_file = log_dir / f"{ts}_{self.cycle_id}_audit.log"
        else:
            self._log_file = log_dir / "apex_lattice.jsonl"

    def log(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Append a structured event to the audit log.

        Keeps both ``data`` and ``details`` keys for compatibility with
        existing callers/readers during merge-reconciliation.
        """
        entry: dict[str, Any] = {"ts": time.time(), "event": event}
        if self.cycle_id:
            entry["cycle_id"] = self.cycle_id
        if data:
            entry["data"] = data
            entry["details"] = data
        with self._log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        """Return all logged events as a list of dicts."""
        if not self._log_file.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in self._log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events

    def read_entries(self) -> list[dict[str, Any]]:
        """Compatibility alias for callers expecting read_entries()."""
        return self.read_all()

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

    def path(self) -> Path:
        """Compatibility helper for callers expecting path()."""
        return self._log_file
