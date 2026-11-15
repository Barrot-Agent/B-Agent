"""Disk layout and persistence for the infinite-ingestion pipeline.

Layout (all under ``data/`` unless a different root is injected)::

    raw/                    raw sources, capped and pruned oldest-first
    memory/records.jsonl    extractive memory records
    capabilities/           capability definitions + their tests
    ingest_ledger.json      url -> {sha256, fetched_at}; prevents re-fetching
    ingest_queue.json       pending sources
    ingest_events.jsonl     append-only run log
    connections.json        cross-source graph
    refinement_log.jsonl    refinement history

Writes that matter for consistency use a temp file plus ``os.replace``.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Iterable

from .models import (
    IngestItem,
    MemoryRecord,
    RawRecord,
    slugify,
    utc_now,
)

DEFAULT_RAW_CAP_BYTES = 500 * 1024 * 1024
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data"
MEMORY_MD = PROJECT_ROOT / "MEMORY.md"


def _atomic_write(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


class Store:
    """Filesystem-backed state for ingestion, memory and connections."""

    def __init__(
        self,
        root: str | Path = DEFAULT_DATA_ROOT,
        raw_cap_bytes: int = DEFAULT_RAW_CAP_BYTES,
    ):
        self.root = Path(root)
        self.raw_dir = self.root / "raw"
        self.memory_dir = self.root / "memory"
        self.capability_dir = self.root / "capabilities"
        self.ledger_path = self.root / "ingest_ledger.json"
        self.queue_path = self.root / "ingest_queue.json"
        self.events_path = self.root / "ingest_events.jsonl"
        self.connections_path = self.root / "connections.json"
        self.memory_path = self.memory_dir / "records.jsonl"
        self.refinement_log_path = self.root / "refinement_log.jsonl"
        self.raw_cap_bytes = raw_cap_bytes
        self.ensure()

    def ensure(self) -> None:
        """Create the directory skeleton."""
        for directory in (self.raw_dir, self.memory_dir, self.capability_dir):
            directory.mkdir(parents=True, exist_ok=True)

    # -- json helpers -----------------------------------------------------

    def _read_json(self, path: Path, default):
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return default

    def _write_json(self, path: Path, payload) -> None:
        _atomic_write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    # -- ledger -----------------------------------------------------------

    def ledger(self) -> dict:
        """URL -> metadata for everything already ingested."""
        return self._read_json(self.ledger_path, {})

    def is_known_url(self, url: str) -> bool:
        """Whether the URL was successfully ingested before."""
        return url in self.ledger()

    def is_known_hash(self, sha256: str) -> bool:
        """Whether identical content was already ingested under any URL."""
        return any(entry.get("sha256") == sha256 for entry in self.ledger().values())

    def register(self, record: RawRecord) -> None:
        """Record a successful ingest so the URL is never fetched again."""
        ledger = self.ledger()
        ledger[record.url] = {
            "sha256": record.sha256,
            "fetched_at": record.fetched_at,
            "kind": record.kind,
            "tag": record.tag,
            "path": record.path,
        }
        self._write_json(self.ledger_path, ledger)

    # -- raw storage ------------------------------------------------------

    def write_raw(self, record: RawRecord) -> str:
        """Write the raw text, prune to the cap, return the stored path."""
        stamp = record.fetched_at.replace("-", "").replace(":", "").replace("Z", "")
        name = f"{stamp}-{record.sha256[:12]}-{slugify(record.title or record.kind)}.txt"
        path = self.raw_dir / name
        _atomic_write(path, record.text)
        record.path = str(path.relative_to(self.root))
        self.prune_raw()
        return str(path)

    def raw_bytes(self) -> int:
        """Total size of ``data/raw`` in bytes."""
        if not self.raw_dir.exists():
            return 0
        return sum(path.stat().st_size for path in self.raw_dir.glob("*") if path.is_file())

    def prune_raw(self, cap_bytes: int | None = None) -> list[str]:
        """Delete oldest raw files until the directory fits ``cap_bytes``."""
        cap = self.raw_cap_bytes if cap_bytes is None else cap_bytes
        files = sorted(
            (path for path in self.raw_dir.glob("*") if path.is_file()),
            key=lambda path: (path.stat().st_mtime, path.name),
        )
        total = sum(path.stat().st_size for path in files)
        removed: list[str] = []
        for path in files:
            if total <= cap:
                break
            size = path.stat().st_size
            path.unlink(missing_ok=True)
            total -= size
            removed.append(path.name)
        return removed

    # -- memory -----------------------------------------------------------

    def load_memory(self) -> list[MemoryRecord]:
        """All stored memory records."""
        if not self.memory_path.exists():
            return []
        records: list[MemoryRecord] = []
        for line in self.memory_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(MemoryRecord.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError):
                continue
        return records

    def append_memory(self, records: Iterable[MemoryRecord]) -> list[MemoryRecord]:
        """Append records, skipping ids already stored. Returns the added ones."""
        existing = {record.id for record in self.load_memory()}
        added: list[MemoryRecord] = []
        for record in records:
            if record.id in existing:
                continue
            existing.add(record.id)
            added.append(record)
        if added:
            with self.memory_path.open("a", encoding="utf-8") as handle:
                for record in added:
                    handle.write(json.dumps(record.as_dict(), ensure_ascii=False) + "\n")
        return added

    # -- capabilities -----------------------------------------------------

    def capability_path(self, name: str) -> Path:
        """Path of a capability definition (underscores preserved)."""
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", name).strip("-") or "capability"
        return self.capability_dir / f"{safe}.json"

    def load_capability(self, name: str) -> dict:
        """Load a capability definition, or an empty dict."""
        return self._read_json(self.capability_path(name), {})

    def save_capability(self, name: str, payload: dict) -> Path:
        """Persist a capability definition."""
        path = self.capability_path(name)
        self._write_json(path, payload)
        return path

    # -- connections ------------------------------------------------------

    def save_connections(self, graph: dict) -> None:
        """Persist the cross-source graph."""
        self._write_json(self.connections_path, graph)

    def load_connections(self) -> dict:
        """Load the cross-source graph."""
        return self._read_json(self.connections_path, {})

    # -- queue ------------------------------------------------------------

    def queue(self) -> list[dict]:
        """Raw queue payload."""
        return self._read_json(self.queue_path, [])

    def queue_size(self) -> int:
        """Number of queued sources."""
        return len(self.queue())

    def push_queue(self, items: Iterable[IngestItem]) -> int:
        """Add items, skipping URLs already ingested or already queued."""
        queue = self.queue()
        known = set(self.ledger())
        queued = {entry.get("url") for entry in queue}
        added = 0
        for item in items:
            if item.url in known or item.url in queued:
                continue
            queue.append(item.as_dict())
            queued.add(item.url)
            added += 1
        if added:
            self._write_json(self.queue_path, queue)
        return added

    def take_queue(self, limit: int, capability: str = "") -> list[IngestItem]:
        """Remove and return up to ``limit`` items, optionally for one capability."""
        queue = self.queue()
        taken: list[IngestItem] = []
        remaining: list[dict] = []
        for entry in queue:
            item = IngestItem.from_dict(entry)
            if len(taken) < limit and (not capability or item.capability in ("", capability)):
                taken.append(item)
            else:
                remaining.append(entry)
        if taken:
            self._write_json(self.queue_path, remaining)
        return taken

    # -- logs -------------------------------------------------------------

    def log_event(self, event: str, **fields) -> None:
        """Append one event to ``ingest_events.jsonl``."""
        payload = {"event": event, "at": utc_now(), **fields}
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def log_refinement(self, payload: dict) -> None:
        """Append one refinement result to ``refinement_log.jsonl``."""
        with self.refinement_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def touch(self, path: Path) -> None:
        """Update mtime, used by tests to simulate old raw files."""
        os.utime(path, (time.time() - 3600, time.time() - 3600))
