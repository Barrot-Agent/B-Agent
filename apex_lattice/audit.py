"""
Audit trail – records every step of the analysis pipeline to
.apex_lattice/audit_logs/<timestamp>_audit.log
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_AUDIT_DIR = Path(".apex_lattice") / "audit_logs"


class AuditTrail:
    """Thread-safe audit logger that writes structured NDJSON entries."""

    def __init__(self, cycle_id: str, base_dir: Path | None = None) -> None:
        self.cycle_id = cycle_id
        audit_dir = (base_dir or Path(".")) / _AUDIT_DIR
        audit_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self._log_path = audit_dir / f"{ts}_{cycle_id}_audit.log"
        # also mirror to Python logging
        self._logger = logging.getLogger(f"apex_lattice.audit.{cycle_id}")

    # ------------------------------------------------------------------
    def log(self, event: str, details: dict[str, Any] | None = None) -> None:
        """Append a structured log entry."""
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "cycle_id": self.cycle_id,
            "event": event,
            "details": details or {},
        }
        line = json.dumps(entry, default=str)
        with self._log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        self._logger.debug(line)

    # ------------------------------------------------------------------
    def path(self) -> Path:
        return self._log_path

    def read_entries(self) -> list[dict[str, Any]]:
        """Return all audit entries for this cycle."""
        if not self._log_path.exists():
            return []
        entries: list[dict[str, Any]] = []
        with self._log_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries
