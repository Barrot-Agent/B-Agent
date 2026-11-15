"""Data types shared by the infinite-ingestion pipeline.

Every persisted fact carries ``source_url`` and ``retrieved_at``; the
transmuter refuses to emit a :class:`MemoryRecord` without them.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MAX_STATEMENT_CHARS = 400


class FetchError(RuntimeError):
    """A source could not be fetched or parsed."""


class RateLimitStop(RuntimeError):
    """The run must stop: the source signalled a rate limit."""


class AdapterUnavailable(RuntimeError):
    """An optional dependency for a source adapter is missing."""


def utc_now() -> str:
    """Current UTC time, second precision, ISO-8601 with ``Z``."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    """Hex sha256 of UTF-8 text."""
    return hashlib.sha256((text or "").encode("utf-8", "ignore")).hexdigest()


def normalise(text: str) -> str:
    """Collapse all whitespace runs to single spaces."""
    return " ".join((text or "").split())


def clip(text: str, limit: int = MAX_STATEMENT_CHARS) -> tuple[str, bool]:
    """Clip to ``limit`` characters; returns ``(text, was_clipped)``."""
    clean = normalise(text)
    if len(clean) <= limit:
        return clean, False
    return clean[:limit].rstrip() + "...", True


def slugify(text: str, max_length: int = 60) -> str:
    """Filesystem-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return (slug[:max_length].rstrip("-")) or "record"


def read_text(path: str | Path) -> str:
    """Read a text file defensively (UTF-8, replacement on bad bytes)."""
    return Path(path).read_text(encoding="utf-8", errors="replace")


@dataclass(frozen=True)
class IngestItem:
    """One URL queued for ingestion.

    Attributes:
        url: Canonical source URL, recorded on every derived fact.
        kind: Source kind (video, paper, code, web, ...).
        title: Optional title; the adapter may refine it.
        capability: Capability this source is intended to help.
        path: Optional local file used instead of the network (offline replay).
        added_at: Queue insertion time.
    """

    url: str
    kind: str = "web"
    title: str = ""
    capability: str = ""
    path: str = ""
    added_at: str = field(default_factory=utc_now)

    def as_dict(self) -> dict:
        """JSON-safe representation."""
        return {
            "url": self.url,
            "kind": self.kind,
            "title": self.title,
            "capability": self.capability,
            "path": self.path,
            "added_at": self.added_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IngestItem":
        """Rebuild from JSON."""
        return cls(
            url=data["url"],
            kind=data.get("kind", "web"),
            title=data.get("title", ""),
            capability=data.get("capability", ""),
            path=data.get("path", ""),
            added_at=data.get("added_at") or utc_now(),
        )


@dataclass
class Document:
    """Fetched text plus provenance, before storage."""

    url: str
    kind: str
    title: str
    text: str
    published: str = ""
    fetch_mode: str = "http"
    extra: dict = field(default_factory=dict)

    @property
    def sha256(self) -> str:
        """Content hash used for dedupe."""
        return sha256_text(self.text)


@dataclass
class RawRecord:
    """A stored raw document and its hype verdict."""

    url: str
    kind: str
    title: str
    sha256: str
    text: str
    fetched_at: str
    tag: str = "OK"
    hype: dict = field(default_factory=dict)
    published: str = ""
    fetch_mode: str = "http"
    path: str = ""

    @property
    def is_hype(self) -> bool:
        """Whether the hype filter rejected this record."""
        return self.tag == "HYPE"

    def as_dict(self) -> dict:
        """JSON-safe representation without the body (the body is the raw file)."""
        return {
            "url": self.url,
            "kind": self.kind,
            "title": self.title,
            "sha256": self.sha256,
            "fetched_at": self.fetched_at,
            "tag": self.tag,
            "hype": self.hype,
            "published": self.published,
            "fetch_mode": self.fetch_mode,
            "path": self.path,
            "chars": len(self.text),
        }


@dataclass
class MemoryRecord:
    """A single extractive fact in Barrot format.

    ``statement`` is copied from the source; it is never paraphrased.
    """

    id: str
    statement: str
    kind: str
    capability: str
    source_url: str
    retrieved_at: str
    document_sha256: str
    tags: tuple[str, ...] = ()
    derived_from: str = ""

    @classmethod
    def build(
        cls,
        *,
        statement: str,
        kind: str,
        source_url: str,
        retrieved_at: str,
        document_sha256: str,
        capability: str = "",
        tags: tuple[str, ...] = (),
        derived_from: str = "",
    ) -> "MemoryRecord":
        """Create a validated record.

        Raises:
            ValueError: If the statement is empty or provenance is missing.
        """
        clean, clipped = clip(statement)
        if not clean:
            raise ValueError("empty statement")
        if not source_url:
            raise ValueError("memory record requires source_url")
        if not retrieved_at:
            raise ValueError("memory record requires retrieved_at")
        record_id = sha256_text(f"{clean}\x00{source_url}")[:16]
        all_tags = tuple(dict.fromkeys((*tags, "truncated" if clipped else "")))
        return cls(
            id=record_id,
            statement=clean,
            kind=kind,
            capability=capability,
            source_url=source_url,
            retrieved_at=retrieved_at,
            document_sha256=document_sha256,
            tags=tuple(tag for tag in all_tags if tag),
            derived_from=derived_from,
        )

    def as_dict(self) -> dict:
        """JSON-safe representation."""
        return {
            "id": self.id,
            "statement": self.statement,
            "kind": self.kind,
            "capability": self.capability,
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "document_sha256": self.document_sha256,
            "tags": list(self.tags),
            "derived_from": self.derived_from,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryRecord":
        """Rebuild from JSON."""
        return cls(
            id=data["id"],
            statement=data["statement"],
            kind=data.get("kind", "fact"),
            capability=data.get("capability", ""),
            source_url=data["source_url"],
            retrieved_at=data["retrieved_at"],
            document_sha256=data.get("document_sha256", ""),
            tags=tuple(data.get("tags", ())),
            derived_from=data.get("derived_from", ""),
        )
