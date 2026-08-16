"""
MCP Provenance Recorder – Step 8
==================================
Records provenance, licenses, test results, rejected alternatives, and
rollback information for every integration.

All records are append-only and written to a JSON-Lines file so that the
audit trail is tamper-evident (new records are appended, never overwritten).
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_LOG_PATH = Path("barrot_agent") / "mcp_provenance.jsonl"


# ---------------------------------------------------------------------------
# Record types
# ---------------------------------------------------------------------------


@dataclass
class ProvenanceRecord:
    """Immutable audit record for one MCP integration event."""

    event_type: str  # "integration" | "rejection" | "rollback" | "discovery"
    server_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    license: str = "unknown"
    test_results: Dict[str, Any] = field(default_factory=dict)
    rejected_alternatives: List[str] = field(default_factory=list)
    rollback_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        """Serialise to a single JSON-Lines line."""
        return json.dumps(asdict(self), ensure_ascii=False)


# ---------------------------------------------------------------------------
# Recorder
# ---------------------------------------------------------------------------


class MCPProvenanceRecorder:
    """
    Append-only provenance log for MCP integration events.

    The backing store is a JSON-Lines file (one record per line).
    Records are never updated or deleted – new events are appended.
    """

    def __init__(self, log_path: Optional[Path] = None) -> None:
        self._log_path = log_path or _DEFAULT_LOG_PATH
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------

    def record_integration(
        self,
        server_id: str,
        license: str,
        test_results: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProvenanceRecord:
        """Record a successful integration event."""
        rec = ProvenanceRecord(
            event_type="integration",
            server_id=server_id,
            license=license,
            test_results=test_results,
            metadata=metadata or {},
        )
        self._append(rec)
        return rec

    def record_rejection(
        self,
        server_id: str,
        reason: str,
        alternatives: Optional[List[str]] = None,
    ) -> ProvenanceRecord:
        """Record a rejected integration proposal."""
        rec = ProvenanceRecord(
            event_type="rejection",
            server_id=server_id,
            rejected_alternatives=alternatives or [],
            metadata={"reason": reason},
        )
        self._append(rec)
        return rec

    def record_rollback(
        self,
        server_id: str,
        rollback_ref: str,
        reason: str,
    ) -> ProvenanceRecord:
        """Record a rollback event with enough context to restore state."""
        rec = ProvenanceRecord(
            event_type="rollback",
            server_id=server_id,
            rollback_info={"ref": rollback_ref, "reason": reason},
            metadata={"reason": reason},
        )
        self._append(rec)
        return rec

    def record_discovery(
        self,
        server_id: str,
        schema_hash: str,
        tool_count: int,
    ) -> ProvenanceRecord:
        """Record a discovery scan event."""
        rec = ProvenanceRecord(
            event_type="discovery",
            server_id=server_id,
            metadata={
                "schema_hash": schema_hash,
                "tool_count": tool_count,
            },
        )
        self._append(rec)
        return rec

    # ------------------------------------------------------------------
    # Query helpers (read-only)
    # ------------------------------------------------------------------

    def read_all(self) -> List[ProvenanceRecord]:
        """Read all records from the provenance log."""
        records: List[ProvenanceRecord] = []
        if not self._log_path.exists():
            return records
        with self._log_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        records.append(ProvenanceRecord(**data))
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Skipping malformed record: %s", exc)
        return records

    def read_for_server(self, server_id: str) -> List[ProvenanceRecord]:
        """Return all records related to *server_id*."""
        return [r for r in self.read_all() if r.server_id == server_id]

    def get_last_rollback_ref(self, server_id: str) -> Optional[str]:
        """Return the most recent rollback reference for *server_id*, or None."""
        recs = [r for r in self.read_for_server(server_id) if r.event_type == "rollback"]
        if not recs:
            return None
        return recs[-1].rollback_info.get("ref")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _append(self, record: ProvenanceRecord) -> None:
        """Atomically append *record* to the log file."""
        with self._log_path.open("a", encoding="utf-8") as fh:
            fh.write(record.to_jsonl() + "\n")
        logger.debug(
            "Provenance recorded: event=%s server=%s",
            record.event_type,
            record.server_id,
        )
