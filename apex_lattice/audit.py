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
        log_dir = _DEFAULT_LOG_DIR
        log_filename = "apex_lattice.jsonl"
        now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        if base_dir is not None:
            self.cycle_id = str(cycle_id_or_log_dir or f"cycle_{now_stamp}")
            log_dir = base_dir / _DEFAULT_LOG_DIR
            log_filename = f"{now_stamp}_{self.cycle_id}_audit.log"
        elif isinstance(cycle_id_or_log_dir, Path):
            log_dir = cycle_id_or_log_dir
        elif isinstance(cycle_id_or_log_dir, str) and (
            os.sep in cycle_id_or_log_dir or "/" in cycle_id_or_log_dir
        ):
            log_dir = Path(cycle_id_or_log_dir)
        elif isinstance(cycle_id_or_log_dir, str) and cycle_id_or_log_dir:
            self.cycle_id = cycle_id_or_log_dir
            log_filename = f"{now_stamp}_{self.cycle_id}_audit.log"

        log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = log_dir / log_filename

    def log(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Append a structured event to the audit log.

        Logged payloads use ``data``; ``read_all()`` exposes a compatibility
        alias for legacy ``details`` consumers.
        """
        entry: dict[str, Any] = {"ts": time.time(), "event": event}
        if self.cycle_id:
            entry["cycle_id"] = self.cycle_id
        if data:
            entry["data"] = data
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
        entries: list[dict[str, Any]] = []
        for event in self.read_all():
            e = dict(event)
            if "data" in e and "details" not in e:
                e["details"] = e["data"]
            if "details" in e and "data" not in e:
                e["data"] = e["details"]
            entries.append(e)
        return entries

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
