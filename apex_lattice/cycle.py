"""
Cycle Manager.

Orchestrates single-shot, query-scoped, and iteratively-refined analysis
cycles.

A cycle is the full pipeline:
    SandboxPipeline -> FindingGenerator -> RecommendationEngine -> PRFramework
    + AuditTrail logging at every step.

Usage:
    from apex_lattice.cycle import CycleManager

    mgr = CycleManager(repo_root=Path("."))
    summary = mgr.run_once()
    summary = mgr.run_once(query="security audit")
    summary = mgr.run_until_stable()

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
from apex_lattice.sandbox import SandboxPipeline, select_analyzers


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

    def run_once(self, query: str | None = None) -> dict[str, Any]:
        """Execute a single analysis cycle and return a summary dict."""
        cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
        audit = AuditTrail(cycle_id, base_dir=self._base_dir)
        audit.log(
            "cycle_start",
            {"cycle_id": cycle_id, "repo_root": str(self.repo_root), "query": query},
        )

        analyzer_modules = select_analyzers(query)

        pipeline = SandboxPipeline(
            cycle_id=cycle_id,
            repo_root=self.repo_root,
            base_dir=self._base_dir,
            analyzer_modules=analyzer_modules,
        )
        raw_results = pipeline.run()

        finder = FindingGenerator(cycle_id, base_dir=self._base_dir)
        findings = finder.generate(raw_results)

        engine = RecommendationEngine(cycle_id, base_dir=self._base_dir)
        recommendations = engine.generate(findings)

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
            "query": query,
            "analyzers_run": analyzer_modules,
            "findings_count": len(findings),
            "recommendations_count": len(recommendations),
            "prs_count": len(prs),
            "audit_log": str(audit.path()),
            "prs": prs,
        }
        audit.log("cycle_complete", summary)
        return summary

    def run_until_stable(
        self,
        query: str | None = None,
        max_iterations: int = 5,
    ) -> dict[str, Any]:
        """Run cycles repeatedly until an iteration produces zero findings,
        or findings stop decreasing, or max_iterations is reached."""
        iterations: list[dict[str, Any]] = []
        previous_count: int | None = None
        stop_reason = "max_iterations_reached"

        for i in range(1, max_iterations + 1):
            summary = self.run_once(query=query)
            summary["iteration"] = i
            iterations.append(summary)

            current_count = summary["findings_count"]
            if current_count == 0:
                stop_reason = "no_findings"
                break
            if previous_count is not None and current_count >= previous_count:
                stop_reason = "no_improvement"
                break
            previous_count = current_count

        return {
            "iterations_run": len(iterations),
            "stop_reason": stop_reason,
            "iterations": iterations,
            "final_findings_count": iterations[-1]["findings_count"] if iterations else 0,
        }

    def run_scheduled(self, interval: float = 3600, max_cycles: int | None = None) -> None:
        """Run analysis cycles on a fixed interval."""
        cycles_run = 0
        print(
            f"[Apex Lattice] Starting scheduled analysis "
            f"(interval={interval}s, max_cycles={max_cycles or 'unlimited'})"
        )
        while True:
            summary = self.run_once()
            cycles_run += 1
            print(
                f"[Apex Lattice] Cycle {cycles_run} complete - "
                f"{summary['findings_count']} findings, "
                f"{summary['recommendations_count']} recommendations, "
                f"{summary['prs_count']} PRs"
            )
            if max_cycles and cycles_run >= max_cycles:
                break
            time.sleep(interval)
