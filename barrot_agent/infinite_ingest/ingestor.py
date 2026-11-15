"""Continuous source ingestion with hard per-run caps.

Safety properties:

* a URL is fetched at most once (persistent ledger);
* identical content is stored at most once (sha256 dedupe);
* every media record passes the hype filter before it is accepted;
* at most ``max_ingests`` documents per run;
* a rate-limit signal stops the run and returns unprocessed queue items;
* ``data/raw`` is pruned to the configured cap after every write.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..hype_filter import enforce_gate
from .models import (
    AdapterUnavailable,
    Document,
    FetchError,
    IngestItem,
    RateLimitStop,
    RawRecord,
    utc_now,
)
from .sources import SourceFetcher
from .storage import Store

DEFAULT_MAX_INGESTS = 10
DEFAULT_MAX_DOCUMENT_CHARS = 1_000_000


@dataclass
class IngestReport:
    """Outcome of one ingestion run."""

    accepted: list[RawRecord] = field(default_factory=list)
    skipped: list[dict] = field(default_factory=list)
    failed: list[dict] = field(default_factory=list)
    stopped_on_rate_limit: bool = False
    remaining_queue: int = 0

    @property
    def ingested(self) -> int:
        """Number of accepted documents."""
        return len(self.accepted)

    @property
    def hype_blocked(self) -> int:
        """Number of accepted documents tagged HYPE."""
        return sum(1 for record in self.accepted if record.is_hype)

    def summary(self) -> str:
        """One-line summary for logs and CLI output."""
        return (
            f"ingested={self.ingested} hype={self.hype_blocked} "
            f"skipped={len(self.skipped)} failed={len(self.failed)} "
            f"rate_limited={self.stopped_on_rate_limit}"
        )


class Ingestor:
    """Fetch, audit, dedupe and store sources.

    Args:
        store: Persistent state.
        fetcher: Transport; injectable for tests.
        max_ingests: Hard cap per run.
        raw_cap_bytes: Disk cap for ``data/raw``.
        hype_runner: Callable matching :func:`barrot_agent.hype_filter.enforce_gate`.
    """

    def __init__(
        self,
        store: Store,
        fetcher: SourceFetcher | None = None,
        max_ingests: int = DEFAULT_MAX_INGESTS,
        raw_cap_bytes: int | None = None,
        max_document_chars: int = DEFAULT_MAX_DOCUMENT_CHARS,
        hype_runner=enforce_gate,
    ):
        self.store = store
        self.fetcher = fetcher or SourceFetcher()
        self.max_ingests = max(1, max_ingests)
        if raw_cap_bytes is not None:
            self.store.raw_cap_bytes = raw_cap_bytes
        self.max_document_chars = max_document_chars
        self.hype_runner = hype_runner
        self._used = 0

    def reset_run(self) -> None:
        """Reset the per-run ingest counter."""
        self._used = 0

    # -- single item ------------------------------------------------------

    def _store_document(self, item: IngestItem, document: Document) -> RawRecord:
        if len(document.text) > self.max_document_chars:
            raise FetchError(
                f"document too large ({len(document.text)} chars > "
                f"{self.max_document_chars}): {item.url}"
            )
        gate = self.hype_runner(
            kind=document.kind,
            text=document.text,
            title=document.title or item.title,
            source=document.url,
        )
        record = RawRecord(
            url=document.url,
            kind=document.kind,
            title=document.title or item.title,
            sha256=document.sha256,
            text=document.text,
            fetched_at=utc_now(),
            tag=gate.tag if gate is not None else "OK",
            hype=gate.to_dict() if gate is not None else {},
            published=document.published,
            fetch_mode=document.fetch_mode,
        )
        self.store.write_raw(record)
        self.store.register(record)
        return record

    def _ingest_one(self, item: IngestItem) -> tuple[RawRecord | None, str]:
        if self.store.is_known_url(item.url):
            return None, "already ingested"
        try:
            document = self.fetcher.fetch(item)
            if not document.text.strip():
                return None, "empty document"
            if self.store.is_known_hash(document.sha256):
                return None, "duplicate content"
            return self._store_document(item, document), ""
        except RateLimitStop:
            raise
        except AdapterUnavailable as exc:
            return None, f"adapter unavailable: {exc}"
        except FetchError as exc:
            return None, str(exc)

    # -- runs -------------------------------------------------------------

    def ingest_item(self, item: IngestItem, report: IngestReport | None = None) -> RawRecord | None:
        """Ingest one item as its own run (still respects the max cap)."""
        report = report or IngestReport()
        self.ingest_items([item], report=report)
        return report.accepted[0] if report.accepted else None

    def ingest_items(
        self, items: list[IngestItem], report: IngestReport | None = None
    ) -> IngestReport:
        """Ingest up to the remaining per-run budget."""
        report = report or IngestReport()
        budget = max(0, self.max_ingests - self._used)
        batch = items[:budget]
        deferred = items[budget:]
        for position, item in enumerate(batch):
            try:
                record, reason = self._ingest_one(item)
            except RateLimitStop as exc:
                report.stopped_on_rate_limit = True
                report.failed.append({"url": item.url, "reason": str(exc)})
                deferred = batch[position + 1 :] + deferred
                self.store.log_event("rate_limit_stop", url=item.url, reason=str(exc))
                break
            self._used += 1
            if record is None:
                report.skipped.append({"url": item.url, "reason": reason})
                self.store.log_event("skipped", url=item.url, reason=reason)
                continue
            report.accepted.append(record)
            self.store.log_event(
                "ingested",
                url=record.url,
                kind=record.kind,
                tag=record.tag,
                sha256=record.sha256,
                chars=len(record.text),
            )
        report.remaining_queue = len(deferred)
        if deferred:
            self.store.push_queue(deferred)
        return report

    def ingest_queue(self, capability: str = "", limit: int | None = None) -> IngestReport:
        """Drain queued sources for a capability, within the run cap."""
        remaining_budget = max(0, self.max_ingests - self._used)
        count = min(limit or remaining_budget, remaining_budget)
        items = self.store.take_queue(count, capability=capability) if count else []
        return self.ingest_items(items)
