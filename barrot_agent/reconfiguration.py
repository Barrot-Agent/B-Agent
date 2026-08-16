"""
Reconfiguration Report – supporting dataclass and MCPIntegration helper.

:class:`ReconfigurationReport` is a structured record produced after Barrot
audits his own infrastructure via the SmartAgent reasoning loop.  It
captures:

- capability gaps (targets with no registered MCP server)
- servers proposed for promotion in the next pipeline run
- an estimated coverage gain if those proposals were accepted
- whether the report was produced in dry-run mode

:func:`build_reconfiguration_report` is a standalone factory that wraps
:class:`~barrot_agent.mcp_integration.MCPIntegration` and can be called
both from the MCP pipeline and from the SmartAgent ``reconfigure_infra``
tool.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ReconfigurationReport
# ---------------------------------------------------------------------------


@dataclass
class CapabilityGap:
    """A single capability target that has no active registered server."""

    target_id: str
    target_name: str
    priority: str
    required_tool_categories: List[str]
    notes: str = ""


@dataclass
class ServerProposal:
    """A server candidate recommended for promotion in the next run."""

    server_id: str
    server_name: str
    tool_categories: List[str]
    covers_target_ids: List[str]
    requires_auth: bool
    estimated_score: float


@dataclass
class ReconfigurationReport:
    """
    Full output of one infrastructure reconfiguration audit.

    Attributes
    ----------
    timestamp:
        ISO-8601 UTC timestamp when the report was produced.
    dry_run:
        Whether the report was produced without touching live state.
    gaps:
        Capability targets that currently have no active MCP server
        covering them.
    proposals:
        Server candidates recommended for promotion.
    estimated_coverage_gain:
        Fraction of capability targets that would be covered after
        accepting all proposals.  Range [0.0, 1.0].
    required_human_approvals:
        Number of human approvals that would be needed to apply all
        proposals (always ≥ 1 per proposal when
        ``require_human_approval_for_writes`` is True).
    pipeline_stats:
        Raw stats dict returned by the most recent pipeline run, if any.
    """

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    dry_run: bool = True
    gaps: List[CapabilityGap] = field(default_factory=list)
    proposals: List[ServerProposal] = field(default_factory=list)
    estimated_coverage_gain: float = 0.0
    required_human_approvals: int = 0
    pipeline_stats: Dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def summary_lines(self) -> List[str]:
        """Return a human-readable list of summary lines."""
        lines = [
            f"**Reconfiguration Report** — {self.timestamp}",
            f"  dry_run: {self.dry_run}",
            "",
            f"**Capability gaps ({len(self.gaps)}):**",
        ]
        if self.gaps:
            for g in self.gaps:
                lines.append(
                    f"  • [{g.priority.upper()}] {g.target_name} ({g.target_id})"
                    f" — needs: {', '.join(g.required_tool_categories)}"
                )
        else:
            lines.append("  None — all capability targets are covered. ✅")

        lines += [
            "",
            f"**Proposed server promotions ({len(self.proposals)}):**",
        ]
        if self.proposals:
            for p in self.proposals:
                auth_note = " [requires auth]" if p.requires_auth else ""
                lines.append(
                    f"  • {p.server_name} ({p.server_id}){auth_note}"
                    f" — score est. {p.estimated_score:.0f}/100"
                    f" — covers: {', '.join(p.covers_target_ids)}"
                )
        else:
            lines.append("  No new servers proposed at this time.")

        lines += [
            "",
            f"**Estimated capability coverage gain:** "
            f"{self.estimated_coverage_gain * 100:.1f}%",
            f"**Human approvals required to apply:** {self.required_human_approvals}"
            + (" *(not yet triggered — dry_run=True)*" if self.dry_run else ""),
        ]

        if self.pipeline_stats:
            lines += [
                "",
                "**Last pipeline stats:**",
            ]
            for k, v in self.pipeline_stats.items():
                lines.append(f"  {k}: {v}")

        return lines

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Factory – build a report from live infrastructure state
# ---------------------------------------------------------------------------


def build_reconfiguration_report(
    dry_run: bool = True,
    registry_path: Optional[object] = None,
) -> ReconfigurationReport:
    """
    Inspect Barrot's live infrastructure state and produce a
    :class:`ReconfigurationReport`.

    This function is *read-only* unless ``dry_run=False`` is explicitly
    requested.  Even then, no state is mutated here — the report only
    describes what *would* change; a separate call to
    :meth:`~barrot_agent.mcp_integration.MCPIntegration.run_pipeline`
    would be required to effect changes.

    Parameters
    ----------
    dry_run:
        When True (default) the function performs no writes.
    registry_path:
        Optional override for the registry JSON path; passed through to
        :class:`~barrot_agent.mcp_registry.MCPRegistry`.

    Returns
    -------
    ReconfigurationReport
    """
    # Import here to avoid circular imports at module load time
    from barrot_agent.mcp_registry import MCPRegistry
    from barrot_agent.mcp_targets import CAPABILITY_TARGETS, SUPPORTED_MCP_SERVERS

    registry = MCPRegistry(registry_path=registry_path)  # type: ignore[arg-type]
    active_entries = registry.list_active()

    # ---- Determine which tool_categories are already covered ----
    covered_categories: set[str] = set()
    for entry in active_entries:
        covered_categories.update(entry.tool_categories)

    # ---- Find capability gaps ----
    gaps: List[CapabilityGap] = []
    for target in CAPABILITY_TARGETS:
        missing = [cat for cat in target.required_tool_categories if cat not in covered_categories]
        if missing:
            gaps.append(
                CapabilityGap(
                    target_id=target.id,
                    target_name=target.name,
                    priority=target.priority,
                    required_tool_categories=target.required_tool_categories,
                    notes=f"Missing categories: {', '.join(missing)}",
                )
            )

    # ---- Build proposals for unregistered servers that fill gaps ----
    gap_categories: set[str] = {cat for gap in gaps for cat in gap.required_tool_categories}
    proposals: List[ServerProposal] = []
    for srv in SUPPORTED_MCP_SERVERS:
        if registry.is_registered(srv.server_id):
            continue  # already active
        overlap = set(srv.tool_categories) & gap_categories
        if not overlap:
            continue

        # Which targets would this server cover?
        covers: List[str] = []
        for gap in gaps:
            if overlap & set(gap.required_tool_categories):
                covers.append(gap.target_id)

        # Rough score heuristic: 60 base + 5 per covered target - 10 if auth needed
        est_score = min(100.0, 60.0 + 5.0 * len(covers) - (10.0 if srv.requires_auth else 0.0))
        proposals.append(
            ServerProposal(
                server_id=srv.server_id,
                server_name=srv.name,
                tool_categories=list(srv.tool_categories),
                covers_target_ids=covers,
                requires_auth=srv.requires_auth,
                estimated_score=est_score,
            )
        )

    # ---- Estimated coverage gain ----
    n_targets = len(CAPABILITY_TARGETS)
    initially_uncovered = len(gaps)
    newly_covered_targets: set[str] = set()
    for prop in proposals:
        newly_covered_targets.update(prop.covers_target_ids)
    still_uncovered = initially_uncovered - len(newly_covered_targets & {g.target_id for g in gaps})
    coverage_gain = (initially_uncovered - max(0, still_uncovered)) / max(1, n_targets)

    # ---- Human approvals: 1 per proposal is always required (safety requirement).
    # Report the full count regardless of dry_run; dry_run only means the
    # approvals haven't been triggered yet, not that they can be skipped.
    required_approvals = len(proposals)

    logger.info(
        "Reconfiguration report: gaps=%d proposals=%d coverage_gain=%.2f",
        len(gaps),
        len(proposals),
        coverage_gain,
    )

    return ReconfigurationReport(
        dry_run=dry_run,
        gaps=gaps,
        proposals=proposals,
        estimated_coverage_gain=coverage_gain,
        required_human_approvals=required_approvals,
    )
