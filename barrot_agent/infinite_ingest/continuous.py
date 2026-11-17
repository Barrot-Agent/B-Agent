"""Bounded continuous mode for the ingestion pipeline.

A continuous run is a fixed number of cycles with a wall-clock ceiling.  It is
not an unbounded daemon: every cycle has the normal ingest cap, the refinement
limit stays one per capability, and the run stops on a rate limit, an idle
queue, the cycle budget or the time budget.

The point is to leave something running for a short, auditable stretch without
letting it write tracked files forever.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .cross_analyzer import CrossAnalyzer
from .ingestor import Ingestor
from .refiner import Refiner, score_capability
from .storage import Store
from .transmuter import Transmuter


@dataclass
class CycleReport:
    """Outcome of one continuous cycle."""

    cycle: int
    queue_before: int
    queue_after: int
    ingested: int = 0
    hype: int = 0
    skipped: int = 0
    failed: int = 0
    retrying: int = 0
    memory_added: int = 0
    rate_limited: bool = False
    connections: dict = field(default_factory=dict)
    refinement: dict | None = None
    elapsed_s: float = 0.0

    def as_dict(self) -> dict:
        """JSON-safe representation."""
        return {
            "cycle": self.cycle,
            "queue_before": self.queue_before,
            "queue_after": self.queue_after,
            "ingested": self.ingested,
            "hype": self.hype,
            "skipped": self.skipped,
            "failed": self.failed,
            "retrying": self.retrying,
            "memory_added": self.memory_added,
            "rate_limited": self.rate_limited,
            "connections": self.connections,
            "refinement": self.refinement,
            "elapsed_s": round(self.elapsed_s, 3),
        }


@dataclass
class ContinuousReport:
    """Outcome of a bounded continuous run."""

    cycles: list[CycleReport] = field(default_factory=list)
    stop_reason: str = "cycle_budget"
    elapsed_s: float = 0.0

    @property
    def ingested(self) -> int:
        return sum(cycle.ingested for cycle in self.cycles)

    @property
    def memory_added(self) -> int:
        return sum(cycle.memory_added for cycle in self.cycles)

    def summary(self) -> str:
        """One-line summary for logs and CLI output."""
        return (
            f"cycles={len(self.cycles)} ingested={self.ingested} "
            f"memory_added={self.memory_added} stopped={self.stop_reason} "
            f"elapsed={self.elapsed_s:.1f}s"
        )

    def as_dict(self) -> dict:
        """JSON-safe representation."""
        return {
            "cycles": [cycle.as_dict() for cycle in self.cycles],
            "stop_reason": self.stop_reason,
            "elapsed_s": round(self.elapsed_s, 3),
            "ingested": self.ingested,
            "memory_added": self.memory_added,
        }


class ContinuousRunner:
    """Run a bounded ingest -> transmute -> connect -> refine loop.

    Args:
        store: Persistent state.
        ingestor: Configured ingestor (its ``max_ingests`` is the per-run cap).
        analyzer: Cross-source graph builder.
        refiner: Optional refiner; created from ``store``/``ingestor`` if omitted.
        transmute: Convert accepted raw documents into memory records.
        refine: Run at most one refinement per capability when the test has gaps.
    """

    def __init__(
        self,
        store: Store,
        ingestor: Ingestor,
        analyzer: CrossAnalyzer | None = None,
        refiner: Refiner | None = None,
        transmute: bool = True,
        refine: bool = True,
    ):
        self.store = store
        self.ingestor = ingestor
        self.analyzer = analyzer or CrossAnalyzer(store)
        self.transmuter = Transmuter()
        self.refiner = refiner or Refiner(store, ingestor, self.transmuter, self.analyzer)
        self.transmute = transmute
        self.refine = refine

    def run(
        self,
        *,
        cycles: int = 2,
        max_minutes: float = 10.0,
        capability: str = "",
        idle_cycles: int = 2,
    ) -> ContinuousReport:
        """Run at most ``cycles`` cycles and ``max_minutes`` minutes."""
        cycles = max(1, cycles)
        max_seconds = max(0.0, max_minutes * 60.0)
        idle_cycles = max(1, idle_cycles)
        started = time.monotonic()
        report = ContinuousReport()
        idle = 0

        for index in range(1, cycles + 1):
            if time.monotonic() - started >= max_seconds:
                report.stop_reason = "time_budget"
                break
            cycle_started = time.monotonic()
            queue_before = self.store.queue_size()
            ingest_report = self.ingestor.ingest_queue(capability=capability)
            memory_added = 0
            if self.transmute and ingest_report.accepted:
                memory_added = len(
                    self.store.append_memory(
                        record
                        for raw in ingest_report.accepted
                        for record in self.transmuter.transmute(
                            raw, capability=capability
                        )
                    )
                )
            graph = self.analyzer.build()
            refinement = None
            if self.refine and capability:
                refinement = self._maybe_refine(capability)

            cycle = CycleReport(
                cycle=index,
                queue_before=queue_before,
                queue_after=self.store.queue_size(),
                ingested=ingest_report.ingested,
                hype=ingest_report.hype_blocked,
                skipped=len(ingest_report.skipped),
                failed=len(ingest_report.failed),
                retrying=len(ingest_report.retrying),
                memory_added=memory_added,
                rate_limited=ingest_report.stopped_on_rate_limit,
                connections=graph.get("stats", {}),
                refinement=refinement,
                elapsed_s=time.monotonic() - cycle_started,
            )
            report.cycles.append(cycle)

            if ingest_report.stopped_on_rate_limit:
                report.stop_reason = "rate_limit"
                break
            worked = (
                ingest_report.ingested
                or ingest_report.retrying
                or memory_added
                or refinement is not None
            )
            idle = 0 if worked else idle + 1
            if idle >= idle_cycles:
                report.stop_reason = "idle"
                break
        else:
            report.stop_reason = "cycle_budget"

        report.elapsed_s = time.monotonic() - started
        return report

    def _maybe_refine(self, capability: str) -> dict | None:
        """Refine only when the fixed test still has missing facts."""
        definition = self.store.load_capability(capability)
        if not definition:
            return None
        score = score_capability(definition, self.store.load_memory())
        if not score.missing:
            return None
        try:
            result = self.refiner.run_once(capability, reset_ingest_budget=False)
        except RuntimeError:
            return {"skipped": "already refined in this run"}
        return result.as_dict()
