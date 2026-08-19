"""
MCP Integration – Main Entry Point
====================================
Wires together all 10 steps of the MCP integration framework:

    Step 1  mcp_targets    – Capability targets, servers, compatibility
    Step 2  mcp_discovery  – Read-only inventory (tools, schemas, security)
    Step 3  mcp_scorer     – Score for usefulness, maturity, risk, etc.
    Step 4  mcp_adapters   – Adapt without modifying upstream code
    Step 5  mcp_pingpong   – Proposal exchange, critique, refinement
    Step 6  mcp_sandbox    – Isolated dependency/secret/regression checks
    Step 7  mcp_approval   – Human approval gate
    Step 8  mcp_provenance – Immutable audit trail
    Step 9  mcp_registry   – Promote only validated components
    Step 10 mcp_scheduler  – Bounded scheduled re-discovery

Usage
-----
    from barrot_agent.mcp_integration import MCPIntegration, IntegrationConfig

    cfg = IntegrationConfig(dry_run=True)
    mi = MCPIntegration(cfg)
    stats = mi.run_pipeline()
    print(stats)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from barrot_agent.mcp_adapters import build_adapter
from barrot_agent.mcp_approval import ActionType, ApprovalRequest, MCPApprovalGate
from barrot_agent.mcp_discovery import MCPDiscovery, ServerInventory
from barrot_agent.mcp_pingpong import MCPPingPong, MCPProposal, Phase
from barrot_agent.mcp_provenance import MCPProvenanceRecorder
from barrot_agent.mcp_registry import MCPRegistry, RegistryEntry
from barrot_agent.mcp_sandbox import MCPSandbox
from barrot_agent.mcp_scheduler import MCPScheduler, SchedulerConfig
from barrot_agent.mcp_scorer import MCPScorer
from barrot_agent.mcp_targets import CAPABILITY_TARGETS, COMPATIBILITY_REQUIREMENTS
from barrot_agent.reconfiguration import ReconfigurationReport, build_reconfiguration_report

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Integration configuration
# ---------------------------------------------------------------------------


@dataclass
class IntegrationConfig:
    """Top-level configuration for the MCP integration pipeline."""

    dry_run: bool = True
    """When True the pipeline discovers and scores but does not write anything."""

    approval_mode: str = "always_deny"
    """Passed to :class:`~barrot_agent.mcp_approval.MCPApprovalGate`."""

    interactive_approval: bool = False
    """Enable interactive stdin/stdout prompts for approval."""

    min_score: float = 50.0
    """Minimum component score to generate a ping-pong proposal."""

    pingpong_max_cycles: int = 3
    """Maximum refinement cycles per proposal."""

    repo_root: Path = field(default_factory=lambda: Path("."))
    """Root of the repository for sandbox and adapter operations."""

    registry_path: Optional[Path] = None
    """Override path for the framework registry JSON file."""

    provenance_path: Optional[Path] = None
    """Override path for the provenance JSONL file."""

    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    """Scheduler settings for repeated discovery runs."""


# ---------------------------------------------------------------------------
# Integration pipeline
# ---------------------------------------------------------------------------


class MCPIntegration:
    """
    Orchestrates the full MCP integration lifecycle for Barrot.

    All 10 steps are executed in sequence.  The pipeline is safe to run
    at any time; no production state is modified unless ``dry_run=False``
    *and* human approval is explicitly granted.
    """

    def __init__(self, config: Optional[IntegrationConfig] = None) -> None:
        self._cfg = config or IntegrationConfig()

        # Instantiate sub-systems
        self._discovery = MCPDiscovery()
        self._scorer = MCPScorer()
        self._pingpong = MCPPingPong(max_cycles=self._cfg.pingpong_max_cycles)
        self._sandbox = MCPSandbox(repo_root=self._cfg.repo_root)
        self._approval = MCPApprovalGate(
            mode=self._cfg.approval_mode,
            interactive=self._cfg.interactive_approval,
        )
        self._provenance = MCPProvenanceRecorder(log_path=self._cfg.provenance_path)
        self._registry = MCPRegistry(registry_path=self._cfg.registry_path)

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

    def run_pipeline(self) -> Dict[str, int]:
        """
        Execute one full discovery → evaluation → integration pass.

        Returns a stats dict with keys:
            ``discovered``, ``proposals``, ``accepted``,
            ``rejected``, ``sandbox_passed``, ``promoted``.
        """
        stats: Dict[str, int] = {
            "discovered": 0,
            "proposals": 0,
            "accepted": 0,
            "rejected": 0,
            "sandbox_passed": 0,
            "promoted": 0,
        }

        # ---- Step 2: Discovery ----
        logger.info("Pipeline: starting discovery")
        inventories = self._discovery.discover_all()
        stats["discovered"] = len(inventories)
        logger.info("Pipeline: discovered %d servers", stats["discovered"])

        # Record discovery events in provenance
        for sid, inv in inventories.items():
            self._provenance.record_discovery(
                server_id=sid,
                schema_hash=inv.schema_hash,
                tool_count=len(inv.tools),
            )

        # ---- Step 3: Scoring ----
        logger.info("Pipeline: scoring components")
        scores = self._scorer.score_all(inventories)
        ranked = self._scorer.rank(scores)

        # ---- Steps 4-9: Per-component integration ----
        for component_score in ranked:
            sid = component_score.server_id
            inv = inventories[sid]
            score_val = component_score.total

            if score_val < self._cfg.min_score:
                logger.info(
                    "Pipeline: skipping %s (score=%.1f < min=%.1f)",
                    sid,
                    score_val,
                    self._cfg.min_score,
                )
                self._provenance.record_rejection(
                    server_id=sid,
                    reason=f"Score {score_val:.1f} below threshold {self._cfg.min_score}.",
                )
                stats["rejected"] += 1
                continue

            # ---- Step 4: Build adapter ----
            adapter = build_adapter(inv)

            # ---- Step 5: Ping-pong proposal exchange ----
            proposal = MCPProposal(
                server_id=sid,
                description=inv.description,
                score=score_val,
                adapter_class=(adapter.__class__.__name__ if adapter else "NoAdapter"),
                rationale=(
                    f"Score={score_val:.1f}/{component_score.grade}; "
                    f"categories={inv.tool_categories}"
                ),
                risks=[
                    f"risk_level={inv.security.risk_level}",
                    f"cves={inv.security.known_cves}",
                ],
                mitigations=(["Adapter layer isolates upstream"] if adapter else []),
            )
            exchange = self._pingpong.run(proposal)
            stats["proposals"] += 1

            if exchange.final_phase != Phase.ACCEPTANCE:
                self._provenance.record_rejection(
                    server_id=sid,
                    reason=f"Ping-pong phase={exchange.final_phase.value}",
                )
                stats["rejected"] += 1
                continue

            stats["accepted"] += 1

            # ---- Step 6: Sandbox ----
            if not self._cfg.dry_run:
                sb_report = self._sandbox.run(
                    server_id=sid,
                    proposed_files={},
                    declared_deps=inv.dependencies,
                )
                if not sb_report.passed:
                    failed = [c.check_name for c in sb_report.failed_checks]
                    self._provenance.record_rejection(
                        server_id=sid,
                        reason=f"Sandbox checks failed: {failed}",
                    )
                    stats["rejected"] += 1
                    continue
                stats["sandbox_passed"] += 1

            # ---- Step 7: Human approval ----
            approval_req = ApprovalRequest(
                action_type=ActionType.REGISTRY_PROMOTE,
                server_id=sid,
                description=(f"Promote {sid} (score={score_val:.1f}) into the framework registry."),
            )
            decision = self._approval.request_approval(approval_req)

            if not decision.approved:
                self._provenance.record_rejection(
                    server_id=sid,
                    reason=f"Approval denied: {decision.reason}",
                )
                stats["rejected"] += 1
                continue

            # ---- Step 8: Record provenance ----
            prov_rec = self._provenance.record_integration(
                server_id=sid,
                license=inv.license,
                test_results={"sandbox": "passed" if not self._cfg.dry_run else "skipped"},
                metadata={
                    "score": score_val,
                    "grade": component_score.grade,
                    "exchange_id": exchange.exchange_id,
                    "approved_by": decision.decided_by,
                },
            )

            # ---- Step 9: Promote into registry ----
            if not self._cfg.dry_run:
                entry = RegistryEntry(
                    server_id=sid,
                    name=inv.name,
                    version=inv.version,
                    license=inv.license,
                    adapter_class=(adapter.__class__.__name__ if adapter else "NoAdapter"),
                    tool_categories=inv.tool_categories,
                    score=score_val,
                    approved_by=decision.decided_by,
                    provenance_event_id=prov_rec.timestamp,
                )
                self._registry.promote(entry)
                stats["promoted"] += 1
                logger.info("Pipeline: promoted %s into registry", sid)
            else:
                logger.info(
                    "Pipeline: dry_run=True – would promote %s (score=%.1f)",
                    sid,
                    score_val,
                )

        logger.info("Pipeline complete: %s", stats)
        return stats

    # ------------------------------------------------------------------
    # Step 10: Scheduler
    # ------------------------------------------------------------------

    def build_scheduler(self, config: Optional[SchedulerConfig] = None) -> MCPScheduler:
        """
        Build a bounded scheduler that calls :meth:`run_pipeline` on each tick.

        The scheduler enforces ``max_runs`` and per-run integration budgets so
        that the agent never autonomously self-modifies beyond the agreed scope.
        """
        sched_cfg = config or self._cfg.scheduler
        return MCPScheduler(
            config=sched_cfg,
            pipeline=self.run_pipeline,
        )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def registry(self) -> MCPRegistry:
        """Direct access to the framework registry (read-only in dry_run mode)."""
        return self._registry

    @property
    def provenance(self) -> MCPProvenanceRecorder:
        """Direct access to the provenance recorder."""
        return self._provenance

    # ------------------------------------------------------------------
    # Reconfiguration report
    # ------------------------------------------------------------------

    def build_reconfiguration_report(self) -> ReconfigurationReport:
        """
        Produce a :class:`~barrot_agent.reconfiguration.ReconfigurationReport`
        that audits the current infrastructure state against declared capability
        targets and proposes servers for promotion.

        The report is always read-only; it describes what *would* change.
        Call :meth:`run_pipeline` to effect changes (subject to the configured
        approval gate).
        """
        report = build_reconfiguration_report(
            dry_run=self._cfg.dry_run,
            registry_path=self._cfg.registry_path,
        )
        # Annotate with the most recent pipeline stats if available via provenance
        return report
