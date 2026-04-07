"""
Cycle Manager.

Orchestrates single-shot and scheduled recurring analysis cycles.

Usage:
    from apex_lattice.cycle import CycleManager

    mgr = CycleManager(repo_root=Path("."))
    summary = mgr.run_once()

    # Scheduled (blocking, interval in seconds)
    mgr.run_scheduled(interval=3600)
"""

from __future__ import annotations

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
