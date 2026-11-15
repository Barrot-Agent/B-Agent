"""Tests for the infinite-ingestion pipeline.

No network: ``FakeFetcher`` returns canned documents.  Every test uses a
temporary data root, so the repository's real ``data/`` is never touched.
"""

from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from barrot_agent.infinite_ingest.cross_analyzer import CrossAnalyzer
from barrot_agent.infinite_ingest.ingestor import Ingestor
from barrot_agent.infinite_ingest.models import (
    Document,
    FetchError,
    IngestItem,
    MemoryRecord,
    RateLimitStop,
    RawRecord,
    sha256_text,
    utc_now,
)
from barrot_agent.infinite_ingest.refiner import (
    Refiner,
    ScoreResult,
    score_capability,
)
from barrot_agent.infinite_ingest.sources import searxng_search
from barrot_agent.infinite_ingest.storage import Store
from barrot_agent.infinite_ingest.transmuter import Transmuter

PAPER_TEXT = (
    "We propose a memory module for a frozen language model. "
    "On FactKG it is more accurate than giving the LLM every document "
    "(84.33% vs. 80.43%) while using 108x fewer tokens. "
    "Training takes about 19 hours on four H100 GPUs."
)
HYPE_TEXT = (
    "AGI is here. This terrifying model scored 99.9% on the benchmark. "
    "It was built to make you afraid after the grant money arrived."
)


class FakeFetcher:
    """Canned transport with call tracking."""

    def __init__(self, documents: dict[str, Document], rate_limit_urls: set[str] | None = None):
        self.documents = documents
        self.rate_limit_urls = rate_limit_urls or set()
        self.calls: list[str] = []

    def fetch(self, item: IngestItem) -> Document:
        self.calls.append(item.url)
        if item.url in self.rate_limit_urls:
            raise RateLimitStop(f"rate limited: {item.url}")
        if item.url not in self.documents:
            raise FetchError(f"no fixture for {item.url}")
        return self.documents[item.url]


def paper_document(url: str, text: str = PAPER_TEXT) -> Document:
    return Document(url=url, kind="paper", title="Paper", text=text)


def video_document(url: str, text: str) -> Document:
    return Document(url=url, kind="video", title="Video", text=text)


def raw_record(text: str = "placeholder", url: str = "https://example.org/a") -> RawRecord:
    return RawRecord(
        url=url,
        kind="paper",
        title="t",
        sha256=sha256_text(text),
        text=text,
        fetched_at=utc_now(),
    )


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = Store(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_ledger_prevents_refetch(self):
        record = raw_record("alpha")
        self.assertFalse(self.store.is_known_url(record.url))
        self.store.register(record)
        self.assertTrue(self.store.is_known_url(record.url))
        self.assertTrue(self.store.is_known_hash(record.sha256))

    def test_queue_dedupes_and_respects_capability(self):
        items = [
            IngestItem(url="https://a.test/1", kind="paper", capability="cap"),
            IngestItem(url="https://a.test/2", kind="video", capability="other"),
        ]
        self.assertEqual(self.store.push_queue(items), 2)
        self.assertEqual(self.store.push_queue(items), 0)
        taken = self.store.take_queue(10, capability="cap")
        self.assertEqual([item.url for item in taken], ["https://a.test/1"])
        self.assertEqual(self.store.queue_size(), 1)

    def test_prune_deletes_oldest_first(self):
        store = Store(self.root, raw_cap_bytes=50)
        for index in range(3):
            path = store.raw_dir / f"f{index}.txt"
            path.write_text("x" * 40)
            os.utime(path, (1000 + index, 1000 + index))
        removed = store.prune_raw()
        self.assertEqual(removed, ["f0.txt", "f1.txt"])
        self.assertEqual([p.name for p in store.raw_dir.glob("*")], ["f2.txt"])

    def test_memory_append_dedupes(self):
        record = MemoryRecord.build(
            statement="A fact.",
            kind="fact",
            source_url="https://a.test",
            retrieved_at=utc_now(),
            document_sha256="x",
        )
        self.assertEqual(len(self.store.append_memory([record])), 1)
        self.assertEqual(len(self.store.append_memory([record])), 0)
        self.assertEqual(len(self.store.load_memory()), 1)


class IngestorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.store = Store(Path(self.tmp.name))
        self.url = "https://example.org/paper"

    def tearDown(self):
        self.tmp.cleanup()

    def _ingestor(self, fetcher, **kwargs) -> Ingestor:
        return Ingestor(self.store, fetcher=fetcher, **kwargs)

    def test_ingest_stores_raw_and_registers(self):
        fetcher = FakeFetcher({self.url: paper_document(self.url)})
        report = self._ingestor(fetcher).ingest_items([IngestItem(url=self.url, kind="paper")])
        self.assertEqual(report.ingested, 1)
        record = report.accepted[0]
        self.assertEqual(record.tag, "OK")
        self.assertTrue((self.store.root / record.path).exists())
        self.assertTrue(self.store.is_known_url(self.url))
        self.assertGreater(self.store.raw_bytes(), 0)

    def test_known_url_is_not_fetched_twice(self):
        fetcher = FakeFetcher({self.url: paper_document(self.url)})
        ingestor = self._ingestor(fetcher)
        ingestor.ingest_items([IngestItem(url=self.url, kind="paper")])
        report = ingestor.ingest_items([IngestItem(url=self.url, kind="paper")])
        self.assertEqual(report.ingested, 0)
        self.assertEqual(report.skipped[0]["reason"], "already ingested")
        self.assertEqual(fetcher.calls, [self.url])

    def test_duplicate_content_is_skipped(self):
        second = "https://example.org/copy"
        fetcher = FakeFetcher(
            {self.url: paper_document(self.url), second: paper_document(second)}
        )
        report = self._ingestor(fetcher).ingest_items(
            [IngestItem(url=self.url, kind="paper"), IngestItem(url=second, kind="paper")]
        )
        self.assertEqual(report.ingested, 1)
        self.assertEqual(report.skipped[0]["reason"], "duplicate content")

    def test_media_is_hype_gated(self):
        url = "https://www.youtube.com/watch?v=abcdefghijk"
        fetcher = FakeFetcher({url: video_document(url, HYPE_TEXT)})
        report = self._ingestor(fetcher).ingest_items([IngestItem(url=url, kind="video")])
        record = report.accepted[0]
        self.assertEqual(record.tag, "HYPE")
        self.assertTrue(record.hype["refinement_blocked"])
        self.assertEqual(Transmuter().transmute(record), [])

    def test_media_passes_when_grounded(self):
        url = "https://example.org/talk"
        text = (
            "I built my own test on custom data after the benchmark. "
            "The model answered in 3.2 seconds instead of 19.3 seconds and failed 4 questions."
        )
        fetcher = FakeFetcher({url: video_document(url, text)})
        report = self._ingestor(fetcher).ingest_items([IngestItem(url=url, kind="video")])
        self.assertEqual(report.accepted[0].tag, "OK")

    def test_max_ingests_per_run(self):
        urls = [f"https://example.org/{index}" for index in range(3)]
        fetcher = FakeFetcher(
            {url: paper_document(url, PAPER_TEXT + f" Item {url}.") for url in urls}
        )
        ingestor = self._ingestor(fetcher, max_ingests=2)
        self.store.push_queue([IngestItem(url=url, kind="paper") for url in urls])
        report = ingestor.ingest_queue()
        self.assertEqual(report.ingested, 2)
        self.assertEqual(self.store.queue_size(), 1)

    def test_rate_limit_stops_and_requeues(self):
        urls = [f"https://example.org/{index}" for index in range(3)]
        fetcher = FakeFetcher(
            {url: paper_document(url, PAPER_TEXT + f" Item {url}.") for url in urls},
            rate_limit_urls={urls[1]},
        )
        ingestor = self._ingestor(fetcher, max_ingests=3)
        self.store.push_queue([IngestItem(url=url, kind="paper") for url in urls])
        report = ingestor.ingest_queue()
        self.assertTrue(report.stopped_on_rate_limit)
        self.assertEqual(report.ingested, 1)
        self.assertEqual(self.store.queue_size(), 1)

    def test_oversized_document_is_rejected(self):
        fetcher = FakeFetcher({self.url: paper_document(self.url, "x" * 500)})
        report = self._ingestor(fetcher, max_document_chars=100).ingest_items(
            [IngestItem(url=self.url, kind="paper")]
        )
        self.assertEqual(report.ingested, 0)
        self.assertIn("too large", report.skipped[0]["reason"])


class TransmuterTests(unittest.TestCase):
    def test_paper_facts_are_extractive_and_provenanced(self):
        record = raw_record(PAPER_TEXT)
        records = Transmuter().transmute(record, capability="cap")
        self.assertTrue(records)
        for memory in records:
            self.assertEqual(memory.source_url, record.url)
            self.assertEqual(memory.retrieved_at, record.fetched_at)
            self.assertTrue(memory.statement)
            self.assertIn(memory.statement.replace("...", ""), PAPER_TEXT)
        self.assertTrue(any("84.33%" in memory.statement for memory in records))

    def test_hype_record_produces_nothing(self):
        record = raw_record(HYPE_TEXT)
        record.tag = "HYPE"
        self.assertEqual(Transmuter().transmute(record), [])

    def test_code_signatures(self):
        text = (
            "import os\n\n"
            "def compress_documents(documents, query):\n"
            '    """Return a gist."""\n'
            "    return documents\n\n"
            "class MemoryModule:\n"
            "    pass\n"
        )
        record = raw_record(text)
        record.kind = "code"
        records = Transmuter().transmute(record)
        statements = [memory.statement for memory in records]
        self.assertIn("def compress_documents(documents, query):", statements)
        self.assertIn("class MemoryModule:", statements)
        self.assertTrue(all(memory.kind == "reusable_function" for memory in records))

    def test_proof_patterns(self):
        text = (
            "Theorem 1. The memory module is bounded. Proof. Assume the budget grows. "
            "Therefore the number of tokens is finite. This contradicts the assumption. QED."
        )
        record = raw_record(text)
        record.kind = "proof"
        records = Transmuter().transmute(record)
        self.assertTrue(records)
        self.assertTrue(all(memory.kind == "reasoning_pattern" for memory in records))

    def test_record_cap(self):
        text = " ".join(
            f"Sentence number {index} has 12 tokens and 34 facts." for index in range(60)
        )
        records = Transmuter(max_records=5).transmute(raw_record(text))
        self.assertLessEqual(len(records), 5)

    def test_transcript_failure_sentence_survives_the_cap(self):
        filler = " ".join(
            f"Model {index} scored 12 tokens on the benchmark test." for index in range(40)
        )
        text = (
            filler
            + " Even though it could only see half the book, RAG got four and "
            "Memorilla got just one."
        )
        records = Transmuter().transmute(raw_record(text))
        self.assertTrue(any("just one" in record.statement for record in records))

    def test_missing_provenance_is_rejected(self):
        with self.assertRaises(ValueError):
            MemoryRecord.build(
                statement="fact",
                kind="fact",
                source_url="",
                retrieved_at=utc_now(),
                document_sha256="x",
            )


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.store = Store(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def _record(self, statement: str, url: str) -> MemoryRecord:
        return MemoryRecord.build(
            statement=statement,
            kind="fact",
            source_url=url,
            retrieved_at=utc_now(),
            document_sha256=sha256_text(statement),
        )

    def test_cross_source_edge(self):
        first = self._record("memory tokens compress long documents efficiently", "https://a.test")
        second = self._record("memory tokens reduce the latency of retrieval", "https://b.test")
        graph = CrossAnalyzer(self.store).build([first, second])
        self.assertEqual(graph["stats"]["nodes"], 2)
        self.assertEqual(len(graph["edges"]), 1)
        self.assertIn("token", graph["edges"][0]["terms"])
        self.assertTrue(self.store.connections_path.exists())

    def test_same_source_has_no_edge(self):
        first = self._record("memory tokens compress long documents efficiently", "https://a.test")
        second = self._record("memory tokens reduce the latency of retrieval", "https://a.test")
        graph = CrossAnalyzer(self.store).build([first, second])
        self.assertEqual(graph["edges"], [])

    def test_suggestions_are_hypotheses(self):
        first = self._record("memory tokens compress long documents efficiently", "https://a.test")
        second = self._record("memory tokens reduce the latency of retrieval", "https://b.test")
        second.kind = "capability_note"
        graph = CrossAnalyzer(self.store).build([first, second])
        self.assertTrue(graph["suggestions"])
        self.assertEqual(graph["suggestions"][0]["status"], "hypothesis")


class RefinerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = Store(self.root)
        self.url = "https://example.org/readme"
        self.memory_md = self.root / "MEMORY.md"
        self.store.save_capability(
            "long_context_memory",
            {
                "name": "long_context_memory",
                "questions": [
                    {
                        "id": "factkg",
                        "question": (
                            "How accurate is Memorilla on FactKG "
                            "compared with full context?"
                        ),
                        "expect": ["84.33%"],
                    }
                ],
                "memory_ids": [],
                "sources": [{"url": self.url, "kind": "paper", "title": "README"}],
                "history": [],
            },
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _refiner(self, fetcher) -> Refiner:
        return Refiner(
            self.store,
            Ingestor(self.store, fetcher=fetcher),
            Transmuter(),
            CrossAnalyzer(self.store),
            memory_md=self.memory_md,
        )

    def test_before_and_after(self):
        fetcher = FakeFetcher({self.url: paper_document(self.url)})
        result = self._refiner(fetcher).run_once("long_context_memory", run_id="run-1")
        self.assertEqual(result.before.recall, 0.0)
        self.assertGreater(result.after.recall, result.before.recall)
        self.assertEqual(result.after.matched, 1)
        self.assertTrue(result.improved)
        self.assertGreaterEqual(result.added_records, 1)
        self.assertTrue(self.memory_md.exists())
        self.assertIn("Refinement run-1", self.memory_md.read_text())
        capability = self.store.load_capability("long_context_memory")
        self.assertTrue(capability["memory_ids"])
        self.assertEqual(capability["history"][-1]["run_id"], "run-1")
        self.assertTrue(self.store.connections_path.exists())

    def test_one_refinement_per_capability_per_run(self):
        refiner = self._refiner(FakeFetcher({self.url: paper_document(self.url)}))
        refiner.run_once("long_context_memory", run_id="run-1")
        with self.assertRaises(RuntimeError):
            refiner.run_once("long_context_memory", run_id="run-2")

    def test_hype_source_cannot_refine(self):
        video_url = "https://www.youtube.com/watch?v=abcdefghijk"
        self.store.save_capability(
            "long_context_memory",
            {
                "name": "long_context_memory",
                "questions": [
                    {
                        "id": "tokens",
                        "question": "How many memory tokens?",
                        "expect": ["16 memory tokens"],
                    }
                ],
                "memory_ids": [],
                "sources": [{"url": video_url, "kind": "video", "title": "Video"}],
                "history": [],
            },
        )
        result = self._refiner(
            FakeFetcher({video_url: video_document(video_url, HYPE_TEXT)})
        ).run_once("long_context_memory")
        self.assertEqual(result.after.recall, 0.0)
        self.assertEqual(result.added_records, 0)
        self.assertEqual(self.store.load_capability("long_context_memory")["memory_ids"], [])

    def test_regression_is_rolled_back(self):
        before = ScoreResult(
            recall=0.5, matched=1, total=2, missing=["84.33%"], memory_records=0, prompt_chars=0
        )
        worse = ScoreResult(
            recall=0.25, matched=1, total=4, missing=["x"], memory_records=1, prompt_chars=10
        )
        refiner = self._refiner(FakeFetcher({self.url: paper_document(self.url)}))
        with patch(
            "barrot_agent.infinite_ingest.refiner.score_capability",
            side_effect=[before, worse, before],
        ):
            result = refiner.run_once("long_context_memory", run_id="run-r")
        self.assertTrue(result.reverted)
        self.assertEqual(self.store.load_capability("long_context_memory")["memory_ids"], [])

    def test_score_reports_missing_terms(self):
        capability = {
            "memory_ids": [],
            "questions": [{"id": "q", "question": "anything", "expect": ["42"]}],
        }
        result = score_capability(capability, [])
        self.assertEqual(result.recall, 0.0)
        self.assertEqual(result.missing, ["42"])


class SearchTests(unittest.TestCase):
    def test_search_parses_and_filters(self):
        payload = json.dumps(
            {
                "results": [
                    {"url": "https://arxiv.org/abs/2610.21375", "title": "Paper"},
                    {"url": "https://www.youtube.com/watch?v=abcdefghijk", "title": "Video"},
                ]
            }
        )
        items = searxng_search("q", http_get=lambda url: payload, kind="paper")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].kind, "paper")
        self.assertEqual(items[0].title, "Paper")


class CliTests(unittest.TestCase):
    def test_status_runs(self):
        from barrot_agent.infinite_ingest.cli import main

        with TemporaryDirectory() as tmp:
            self.assertEqual(main(["--data-root", tmp, "status"]), 0)


if __name__ == "__main__":
    unittest.main()
