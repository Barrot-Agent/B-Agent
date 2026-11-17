"""Test -> find gap -> ingest -> transmute -> refine -> re-test.

A capability is a JSON definition with a fixed test:

.. code-block:: json

    {
      "name": "long_context_memory",
      "memory_ids": [],
      "questions": [
        {"id": "tokens", "question": "...", "expect": ["16 memory tokens"], "forbid": []}
      ],
      "sources": [
        {"url": "...", "kind": "video", "title": "...", "path": "/tmp/transcript.txt"}
      ],
      "history": []
    }

The test builds the query-conditioned gist from the *bound* memory records and
checks whether expected substrings survive.  It measures retrieval of real
source facts, not LLM answer quality; ``harness`` states that in every result.

One refinement per capability per run is enforced in-process.  A regression
lowers the score, so the patch is rolled back automatically.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..gist_memory import GistMemory
from .cross_analyzer import CrossAnalyzer
from .ingestor import IngestReport, Ingestor
from .models import IngestItem, MemoryRecord, utc_now
from .storage import MEMORY_MD, Store
from .transmuter import Transmuter

HARNESS = (
    "deterministic extractive recall over the gist prompt; "
    "not an LLM answer-accuracy benchmark"
)
DEFAULT_MAX_MEMORY_RECORDS = 128


@dataclass
class QuestionResult:
    """One test question and the terms it found."""

    id: str
    question: str
    matched: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
    prompt_chars: int = 0

    def as_dict(self) -> dict:
        """JSON-safe representation."""
        return {
            "id": self.id,
            "question": self.question,
            "matched": list(self.matched),
            "missing": list(self.missing),
            "forbidden": list(self.forbidden),
            "prompt_chars": self.prompt_chars,
        }


@dataclass
class ScoreResult:
    """Capability score before or after refinement."""

    recall: float
    matched: int
    total: int
    missing: list[str]
    memory_records: int
    prompt_chars: int
    per_question: list[QuestionResult] = field(default_factory=list)
    violations: int = 0
    harness: str = HARNESS

    def summary(self) -> str:
        """One-line score line for logs and CLI output."""
        return (
            f"recall={self.recall:.2f} ({self.matched}/{self.total} facts) "
            f"records={self.memory_records} prompt_chars={self.prompt_chars} "
            f"violations={self.violations}"
        )

    def as_dict(self) -> dict:
        """JSON-safe representation."""
        return {
            "recall": round(self.recall, 4),
            "matched": self.matched,
            "total": self.total,
            "missing": self.missing,
            "memory_records": self.memory_records,
            "prompt_chars": self.prompt_chars,
            "violations": self.violations,
            "harness": self.harness,
            "per_question": [question.as_dict() for question in self.per_question],
        }


@dataclass
class RefinementResult:
    """Outcome of one refinement run."""

    capability: str
    run_id: str
    before: ScoreResult
    after: ScoreResult
    added_records: int = 0
    bound_records: int = 0
    reverted: bool = False
    stopped_on_rate_limit: bool = False
    sources: list[dict] = field(default_factory=list)

    @property
    def improved(self) -> bool:
        """Whether recall increased and the patch survived."""
        return not self.reverted and self.after.recall > self.before.recall

    def summary(self) -> str:
        """One-line result."""
        delta = self.after.recall - self.before.recall
        return (
            f"{self.capability}: {self.before.recall:.2f} -> {self.after.recall:.2f} "
            f"(delta {delta:+.2f}), added={self.added_records}, bound={self.bound_records}, "
            f"reverted={self.reverted}"
        )

    def as_dict(self) -> dict:
        """JSON-safe representation."""
        return {
            "capability": self.capability,
            "run_id": self.run_id,
            "at": utc_now(),
            "before": self.before.as_dict(),
            "after": self.after.as_dict(),
            "added_records": self.added_records,
            "bound_records": self.bound_records,
            "reverted": self.reverted,
            "stopped_on_rate_limit": self.stopped_on_rate_limit,
            "sources": self.sources,
            "harness": HARNESS,
        }


def _terms(question: dict) -> list[str]:
    return [str(term) for term in question.get("expect", [])]


def score_capability(
    capability: dict,
    records: list[MemoryRecord],
    num_memories: int = 16,
    words_per_token: int = 10,
) -> ScoreResult:
    """Run the capability's fixed test against its bound memory records."""
    by_id = {record.id: record for record in records}
    bound = [
        by_id[record_id].statement
        for record_id in capability.get("memory_ids", [])
        if record_id in by_id
    ]
    memory = GistMemory(num_memories=num_memories, words_per_token=words_per_token)
    matched = 0
    total = 0
    violations = 0
    prompt_chars = 0
    missing: list[str] = []
    per_question: list[QuestionResult] = []

    for question in capability.get("questions", []):
        result = memory.compress(bound, question.get("question", "")) if bound else None
        prompt = result.render().lower() if result is not None else ""
        prompt_chars += len(prompt)
        expected = _terms(question)
        total += len(expected)
        found = tuple(term for term in expected if term.lower() in prompt)
        absent = tuple(term for term in expected if term.lower() not in prompt)
        forbidden = tuple(
            term for term in question.get("forbid", []) if term.lower() in prompt
        )
        matched += len(found)
        missing.extend(absent)
        violations += len(forbidden)
        per_question.append(
            QuestionResult(
                id=question.get("id", question.get("question", "")[:24]),
                question=question.get("question", ""),
                matched=found,
                missing=absent,
                forbidden=forbidden,
                prompt_chars=len(prompt),
            )
        )

    recall = 0.0
    if total:
        recall = max(0.0, (matched - violations) / total)
    return ScoreResult(
        recall=recall,
        matched=matched,
        total=total,
        missing=missing,
        memory_records=len(bound),
        prompt_chars=prompt_chars,
        per_question=per_question,
        violations=violations,
    )


class Refiner:
    """Run one measured refinement for one capability."""

    def __init__(
        self,
        store: Store,
        ingestor: Ingestor,
        transmuter: Transmuter | None = None,
        analyzer: CrossAnalyzer | None = None,
        memory_md: str | Path = MEMORY_MD,
        max_memory_records: int = DEFAULT_MAX_MEMORY_RECORDS,
    ):
        self.store = store
        self.ingestor = ingestor
        self.transmuter = transmuter or Transmuter()
        self.analyzer = analyzer or CrossAnalyzer(store)
        self.memory_md = Path(memory_md)
        self.max_memory_records = max_memory_records
        self._refined: set[str] = set()

    def run_once(
        self,
        capability_name: str,
        run_id: str | None = None,
        reset_ingest_budget: bool = True,
    ) -> RefinementResult:
        """Execute the full loop once for ``capability_name``.

        Args:
            capability_name: Capability definition to refine.
            run_id: Optional id used in the log.
            reset_ingest_budget: Reset the ingestor's per-run counter.  Standalone
                refinement is its own run; a continuous run passes ``False`` so
                the outer ingest cap still applies.
        """
        if capability_name in self._refined:
            raise RuntimeError(
                f"capability {capability_name!r} already refined in this run "
                "(limit: 1 per capability per run)"
            )
        capability = self.store.load_capability(capability_name)
        if not capability:
            raise ValueError(f"unknown capability: {capability_name!r}")
        self._refined.add(capability_name)
        if reset_ingest_budget:
            self.ingestor.reset_run()
        run_id = run_id or utc_now()

        memory = self.store.load_memory()
        before = score_capability(capability, memory)

        report = IngestReport()
        added_records = 0
        sources: list[dict] = []
        current_ids = list(capability.get("memory_ids", []))
        after = before
        reverted = False

        if before.missing:
            sources = [source for source in capability.get("sources", []) if source.get("url")]
            self.store.push_queue(
                IngestItem(
                    url=source["url"],
                    kind=source.get("kind", "web"),
                    title=source.get("title", ""),
                    capability=capability_name,
                    path=source.get("path", ""),
                )
                for source in sources
            )
            report = self.ingestor.ingest_queue(capability=capability_name)

            fresh: list[MemoryRecord] = []
            for raw in report.accepted:
                fresh.extend(self.transmuter.transmute(raw, capability=capability_name))
            added = self.store.append_memory(fresh)
            added_records = len(added)

            memory = self.store.load_memory()
            bindable = [record for record in memory if record.capability == capability_name]
            missing_terms = [term.lower() for term in before.missing]
            ranked = sorted(
                bindable,
                key=lambda record: (
                    -sum(term in record.statement.lower() for term in missing_terms),
                    record.retrieved_at,
                ),
            )
            covering = [
                record
                for record in ranked
                if any(term in record.statement.lower() for term in missing_terms)
            ]
            patched = list(dict.fromkeys(current_ids + [record.id for record in covering]))
            patched = patched[-self.max_memory_records :]
            capability["memory_ids"] = patched
            self.store.save_capability(capability_name, capability)

            after = score_capability(capability, memory)
            if after.recall < before.recall:
                capability["memory_ids"] = current_ids
                self.store.save_capability(capability_name, capability)
                after = score_capability(capability, memory)
                reverted = True

        result = RefinementResult(
            capability=capability_name,
            run_id=run_id,
            before=before,
            after=after,
            added_records=added_records,
            bound_records=len(capability.get("memory_ids", [])),
            reverted=reverted,
            stopped_on_rate_limit=report.stopped_on_rate_limit,
            sources=[
                {"url": record.url, "fetched_at": record.fetched_at, "tag": record.tag}
                for record in report.accepted
            ],
        )

        history = capability.setdefault("history", [])
        history.append(
            {
                "run_id": run_id,
                "at": utc_now(),
                "before": round(before.recall, 4),
                "after": round(after.recall, 4),
                "added_records": added_records,
                "bound_records": result.bound_records,
                "reverted": result.reverted,
            }
        )
        self.store.save_capability(capability_name, capability)
        self.analyzer.build()
        self.store.log_refinement(result.as_dict())
        self._append_memory_log(result)
        return result

    # -- logging ---------------------------------------------------------

    def _append_memory_log(self, result: RefinementResult) -> None:
        """Append a short, dated entry to MEMORY.md."""
        source_lines = "\n".join(
            f"  - {source['url']} @ {source['fetched_at']}"
            for source in result.sources
        ) or "  - none"
        entry = (
            f"\n### Refinement {result.run_id} - {result.capability}\n"
            f"- Before: {result.before.summary()}\n"
            f"- After: {result.after.summary()}\n"
            f"- Delta: {result.after.recall - result.before.recall:+.2f} recall; "
            f"added {result.added_records} records, bound {result.bound_records}.\n"
            f"- Reverted: {result.reverted}; rate-limited: {result.stopped_on_rate_limit}.\n"
            f"- Harness: {HARNESS}.\n"
            f"- Sources:\n{source_lines}\n"
        )
        try:
            existing = self.memory_md.read_text(encoding="utf-8") if self.memory_md.exists() else ""
            with self.memory_md.open("a", encoding="utf-8") as handle:
                if "## Refinement log" not in existing:
                    handle.write("\n## Refinement log\n")
                handle.write(entry)
        except OSError:
            # Logging must never break a refinement result.
            pass


def load_json(path: str | Path) -> dict:
    """Small helper used by the CLI and tests."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
