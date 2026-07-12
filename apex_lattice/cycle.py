"""
CycleManager -- orchestrates a single analysis cycle or scheduled recurring
analysis cycles.

A cycle is the full pipeline:
    SandboxPipeline -> FindingGenerator -> RecommendationEngine -> PRFramework
    + AuditTrail logging at every step.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

from .audit import AuditTrail
from .pipeline import SandboxPipeline
from .findings import FindingGenerator
from .recommendations import RecommendationEngine
from .pr_framework import PRFramework


class CycleResult:
    """Collects the outputs of a completed analysis cycle."""

    def __init__(
        self,
        *,
        cycle_id: str,
        artefacts: list[dict[str, Any]],
        findings_count: int,
        recommendations_count: int,
        pr_document: Path | None,
        duration_seconds: float,
        error: str | None = None,
    ) -> None:
        self.cycle_id = cycle_id
        self.artefacts = artefacts
        self.findings_count = findings_count
        self.recommendations_count = recommendations_count
        self.pr_document = pr_document
        self.duration_seconds = duration_seconds
        self.error = error

    def summary(self) -> str:
        status = "ERROR" if self.error else "OK"
        lines = [
            f"Cycle {self.cycle_id}  [{status}]",
            f"  Artefacts processed : {len(self.artefacts)}",
            f"  Findings            : {self.findings_count}",
            f"  Recommendations     : {self.recommendations_count}",
            f"  Duration            : {self.duration_seconds:.2f}s",
        ]
        if self.pr_document:
            lines.append(f"  PR document         : {self.pr_document}")
        if self.error:
            lines.append(f"  Error               : {self.error}")
        return "\n".join(lines)


class CycleManager:
    """
    Runs single or scheduled recurring analysis cycles.

    Parameters
    ----------
    apex_dir:
        Root of the ``.apex_lattice`` workspace.
    generate_pr_document:
        Whether to write a PR Markdown document after each cycle.
    """

    def __init__(
        self,
        apex_dir: Path | str | None = None,
        *,
        generate_pr_document: bool = True,
        base_branch: str = "Main",
    ) -> None:
        self._apex = Path(apex_dir) if apex_dir else Path(".apex_lattice")
        self._pr_docs = generate_pr_document
        self._base_branch = base_branch

        self._audit = AuditTrail(self._apex / "audit_logs")
        self._pipeline = SandboxPipeline(self._apex)
        self._findings = FindingGenerator(self._apex / "findings")
        self._recs = RecommendationEngine(self._apex / "recommendations")
        self._pr = PRFramework(self._apex / "recommendations")

        # Scheduler state
        self._scheduler_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    @property
    def apex_dir(self) -> Path:
        """The root of the .apex_lattice workspace."""
        return self._apex

    # ------------------------------------------------------------------
    # Single cycle
    # ------------------------------------------------------------------

    def run_cycle(self, cycle_id: str | None = None) -> CycleResult:
        """Execute one full analysis cycle and return the result."""
        import uuid

        cid = cycle_id or str(uuid.uuid4())[:8]
        t0 = time.time()

        self._audit.log("cycle_start", {"cycle_id": cid})

        pr_doc: Path | None = None
        try:
            # 1. Process sandbox data
            artefacts = self._pipeline.run()
            self._audit.log("pipeline_complete", {"cycle_id": cid, "artefacts": len(artefacts)})

            # 2. Generate findings
            findings = self._findings.generate(artefacts)
            self._audit.log("findings_complete", {"cycle_id": cid, "findings": len(findings)})

            # 3. Build recommendations
            recs = self._recs.generate(findings)
            self._audit.log("recommendations_complete", {"cycle_id": cid, "recs": len(recs)})

            # 4. Optionally write a PR document
            if self._pr_docs and recs:
                pr_doc = self._pr.create_pr_document(
                    recs,
                    title=f"Apex Lattice Cycle {cid} Improvements",
                    branch=f"apex-lattice/cycle-{cid}",
                )
                self._audit.log("pr_document_created", {"cycle_id": cid, "path": str(pr_doc)})

            duration = time.time() - t0
            self._audit.log("cycle_complete", {"cycle_id": cid, "duration": duration})

            return CycleResult(
                cycle_id=cid,
                artefacts=artefacts,
                findings_count=len(findings),
                recommendations_count=len(recs),
                pr_document=pr_doc,
                duration_seconds=duration,
            )

        except Exception as exc:  # noqa: BLE001
            duration = time.time() - t0
            self._audit.log("cycle_error", {"cycle_id": cid, "error": str(exc)})
            return CycleResult(
                cycle_id=cid,
                artefacts=[],
                findings_count=0,
                recommendations_count=0,
                pr_document=None,
                duration_seconds=duration,
                error=str(exc),
            )

    # ------------------------------------------------------------------
    # Scheduled recurring analysis
    # ------------------------------------------------------------------

    def start_scheduler(self, interval_seconds: float = 3600.0) -> None:
        """
        Start a background thread that runs a cycle every
        *interval_seconds*.  Does nothing if already running.
        """
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            args=(interval_seconds,),
            daemon=True,
            name="apex-lattice-scheduler",
        )
        self._scheduler_thread.start()
        self._audit.log("scheduler_started", {"interval_seconds": interval_seconds})

    def stop_scheduler(self) -> None:
        """Signal the background scheduler thread to stop."""
        self._stop_event.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        self._audit.log("scheduler_stopped", {})

    def is_scheduler_running(self) -> bool:
        return bool(self._scheduler_thread and self._scheduler_thread.is_alive())

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _scheduler_loop(self, interval: float) -> None:
        while not self._stop_event.is_set():
            self.run_cycle()
            self._stop_event.wait(interval)
