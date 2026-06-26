"""
<<<<<<< HEAD
Cycle Manager.

Orchestrates single-shot and scheduled recurring analysis cycles.

Usage:
    from apex_lattice.cycle import CycleManager

    mgr = CycleManager(repo_root=Path("."))
    summary = mgr.run_once()

    # Scheduled (blocking, interval in seconds)
    mgr.run_scheduled(interval=3600)
=======
CycleManager — orchestrates a single analysis cycle or scheduled recurring
analysis cycles.

A cycle is the full pipeline:
    SandboxPipeline → FindingGenerator → RecommendationEngine → PRFramework
    + AuditTrail logging at every step.
>>>>>>> origin/main
"""

from __future__ import annotations

<<<<<<< HEAD
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apex_lattice.audit import AuditTrail
from apex_lattice.findings import FindingGenerator
from apex_lattice.pr_framework import PRFramework
from apex_lattice.recommendations import RecommendationEngine
from apex_lattice.sandbox import SandboxPipeline


class CycleManager:
    """Runs the full end-to-end analysis cycle."""

    def __init__(
        self,
        repo_root: Path | None = None,
        base_dir: Path | None = None,
        github_token: str | None = None,
        github_repo: str | None = None,
        base_branch: str = "Main",
    ) -> None:
        self.repo_root = (repo_root or Path(".")).resolve()
        self._base_dir = base_dir or Path(".")
        self._github_token = github_token
        self._github_repo = github_repo
        self._base_branch = base_branch

    # ------------------------------------------------------------------
    def run_once(self) -> dict[str, Any]:
        """Execute a single analysis cycle and return a summary dict."""
        cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
        audit = AuditTrail(cycle_id, base_dir=self._base_dir)
        audit.log("cycle_start", {"cycle_id": cycle_id, "repo_root": str(self.repo_root)})

        # 1. Sandbox pipeline
        pipeline = SandboxPipeline(
            cycle_id=cycle_id,
            repo_root=self.repo_root,
            base_dir=self._base_dir,
        )
        raw_results = pipeline.run()

        # 2. Finding generation
        finder = FindingGenerator(cycle_id, base_dir=self._base_dir)
        findings = finder.generate(raw_results)

        # 3. Recommendation engine
        engine = RecommendationEngine(cycle_id, base_dir=self._base_dir)
        recommendations = engine.generate(findings)

        # 4. PR framework
        pr_fw = PRFramework(
            cycle_id=cycle_id,
            repo=self._github_repo,
            base_branch=self._base_branch,
            github_token=self._github_token,
            base_dir=self._base_dir,
        )
        prs = pr_fw.create_prs(recommendations)

        summary = {
            "cycle_id": cycle_id,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "findings_count": len(findings),
            "recommendations_count": len(recommendations),
            "prs_count": len(prs),
            "audit_log": str(audit.path()),
            "prs": prs,
        }
        audit.log("cycle_complete", summary)
        return summary

    # ------------------------------------------------------------------
    def run_scheduled(
        self, interval: float = 3600, max_cycles: int | None = None
    ) -> None:
        """Run analysis cycles on a fixed interval.

        Args:
            interval: Seconds between cycles (default: 1 hour).
            max_cycles: Stop after this many cycles (None = run forever).
        """
        cycles_run = 0
        print(
            f"[Apex Lattice] Starting scheduled analysis "
            f"(interval={interval}s, max_cycles={max_cycles or 'unlimited'})"
        )
        while True:
            summary = self.run_once()
            cycles_run += 1
            print(
                f"[Apex Lattice] Cycle {cycles_run} complete – "
                f"{summary['findings_count']} findings, "
                f"{summary['recommendations_count']} recommendations, "
                f"{summary['prs_count']} PRs"
            )
            if max_cycles and cycles_run >= max_cycles:
                break
            time.sleep(interval)
=======
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
>>>>>>> origin/main
