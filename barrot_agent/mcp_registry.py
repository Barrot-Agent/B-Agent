"""
MCP Framework Registry – Step 9
=================================
Promotes only validated MCP components into Barrot's framework registry.

A component may only be registered after:
    1. Passing ping-pong acceptance (:mod:`barrot_agent.mcp_pingpong`)
    2. Passing sandbox validation (:mod:`barrot_agent.mcp_sandbox`)
    3. Receiving human approval (:mod:`barrot_agent.mcp_approval`)
    4. Having a provenance record (:mod:`barrot_agent.mcp_provenance`)

The registry is backed by a JSON file and is the single source of truth
for which MCP servers are active in Barrot's framework.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_REGISTRY_PATH = Path("barrot_agent") / "mcp_registry.json"


# ---------------------------------------------------------------------------
# Registry entry
# ---------------------------------------------------------------------------


@dataclass
class RegistryEntry:
    """A validated and approved MCP server entry in the framework registry."""

    server_id: str
    name: str
    version: str
    license: str
    adapter_class: str
    tool_categories: List[str]
    score: float
    approved_by: str
    provenance_event_id: Optional[str] = None
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    active: bool = True
    notes: str = ""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class MCPRegistry:
    """
    Barrot's framework registry for validated MCP components.

    Only components that have passed all validation gates can be promoted
    here.  Deregistration is supported for rollback scenarios.
    """

    def __init__(self, registry_path: Optional[Path] = None) -> None:
        self._path = registry_path or _DEFAULT_REGISTRY_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: Dict[str, RegistryEntry] = {}
        self._load()

    # ------------------------------------------------------------------
    # Promotion (write)
    # ------------------------------------------------------------------

    def promote(self, entry: RegistryEntry) -> None:
        """
        Add or update a validated component in the registry.

        Raises :class:`ValueError` if the entry fails basic integrity checks.
        """
        self._validate_entry(entry)
        self._entries[entry.server_id] = entry
        self._save()
        logger.info(
            "Registry: promoted server_id=%s version=%s score=%.1f",
            entry.server_id,
            entry.version,
            entry.score,
        )

    def deregister(self, server_id: str, reason: str = "") -> bool:
        """
        Mark a component as inactive (soft-delete for rollback support).

        Returns True if the entry existed, False otherwise.
        """
        entry = self._entries.get(server_id)
        if entry is None:
            logger.warning("Registry: deregister failed – unknown server_id=%s", server_id)
            return False
        entry.active = False
        entry.notes = f"Deregistered: {reason}"
        self._save()
        logger.info("Registry: deregistered server_id=%s reason=%s", server_id, reason)
        return True

    # ------------------------------------------------------------------
    # Query (read-only)
    # ------------------------------------------------------------------

    def get(self, server_id: str) -> Optional[RegistryEntry]:
        """Return the registry entry for *server_id*, or None."""
        return self._entries.get(server_id)

    def list_active(self) -> List[RegistryEntry]:
        """Return all active (non-deregistered) entries."""
        return [e for e in self._entries.values() if e.active]

    def list_all(self) -> List[RegistryEntry]:
        """Return all entries including inactive ones."""
        return list(self._entries.values())

    def is_registered(self, server_id: str) -> bool:
        """Return True if *server_id* is actively registered."""
        entry = self._entries.get(server_id)
        return entry is not None and entry.active

    def to_json(self) -> str:
        """Serialise the full registry to a JSON string."""
        return json.dumps(
            {sid: asdict(e) for sid, e in self._entries.items()},
            indent=2,
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with self._path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            for sid, raw in data.items():
                self._entries[sid] = RegistryEntry(**raw)
            logger.debug("Registry loaded: %d entries", len(self._entries))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load registry from %s: %s", self._path, exc)

    def _save(self) -> None:
        with self._path.open("w", encoding="utf-8") as fh:
            json.dump(
                {sid: asdict(e) for sid, e in self._entries.items()},
                fh,
                indent=2,
            )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_entry(entry: RegistryEntry) -> None:
        if not entry.server_id:
            raise ValueError("server_id must not be empty.")
        if entry.score < 0 or entry.score > 100:
            raise ValueError(f"score must be in [0, 100], got {entry.score}.")
        if not entry.approved_by:
            raise ValueError("approved_by must not be empty.")
