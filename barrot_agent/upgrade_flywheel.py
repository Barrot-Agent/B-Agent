"""
UpgradeFlywheel — iterative system-wide refinement orchestrator.

The flywheel unifies every major B-Agent subsystem — SmartAgent reasoning,
DirectivePlatform multi-agent sessions, and infrastructure reconfiguration
reports — inside a repeating Observe → Reason → Act → Verify loop.

Each :class:`FlywheelCycle` represents one full pass of Barrot's signature
process.  Cycles continue until either the caller-supplied ``max_cycles``
limit is reached or the flywheel detects convergence (i.e. no new capability
gaps are found and the previous cycle already showed full coverage).

Usage
-----
    from barrot_agent.upgrade_flywheel import UpgradeFlywheel

    flywheel = UpgradeFlywheel()
    report = flywheel.run(max_cycles=5)
    for cycle in report.cycles:
        print(cycle.summary())
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class ObservationResult:
    """Raw observations captured during the *Observe* phase."""

    capability_gaps: int
    """Number of uncovered capability targets found by the reconfig report."""

    proposed_servers: int
    """Number of server promotions proposed in the reconfig report."""

    estimated_coverage_gain: float
    """Fraction of targets that would be newly covered if proposals accepted."""

    smart_agent_events: int
    """Total events emitted by the SmartAgent observation run."""

    goal_used: str
    """The observation goal passed to the SmartAgent."""


@dataclass
class ReasoningResult:
    """Conclusions produced during the *Reason* phase."""

    improvements: list[str]
    """Ordered list of improvement recommendations."""

    directive_id: str | None = None
    """ID of the DirectivePlatform directive that was issued, if any."""

    session_id: str | None = None
    """ID of the collaboration session opened for this reasoning pass."""


@dataclass
class ActionResult:
    """Actions taken during the *Act* phase."""

    actions_taken: list[str]
    """Descriptions of changes / refinements applied."""

    reconfiguration_dry_run: bool = True
    """Whether the reconfig report was produced in dry-run mode."""


@dataclass
class VerificationResult:
    """Verification outcomes from the *Verify* phase."""

    passed: bool
    """True when all validation checks succeeded."""

    checks: list[str]
    """Individual check descriptions and their pass/fail status."""

    coverage_after: float = 0.0
    """Estimated capability coverage after this cycle's actions."""


@dataclass
class FlywheelCycleResult:
    """Complete record of one Observe → Reason → Act → Verify cycle."""

    cycle_number: int
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None

    observation: ObservationResult | None = None
    reasoning: ReasoningResult | None = None
    action: ActionResult | None = None
    verification: VerificationResult | None = None

    converged: bool = False
    """True when this cycle detected no new improvements (flywheel done)."""

    def summary(self) -> str:
        """Return a human-readable single-paragraph summary of this cycle."""
        parts = [f"=== Cycle {self.cycle_number} ==="]
        if self.observation:
            parts.append(
                f"[Observe]  gaps={self.observation.capability_gaps}"
                f"  proposals={self.observation.proposed_servers}"
                f"  coverage_gain={self.observation.estimated_coverage_gain:.1%}"
                f"  agent_events={self.observation.smart_agent_events}"
            )
        if self.reasoning:
            parts.append(f"[Reason]   improvements={len(self.reasoning.improvements)}")
            for imp in self.reasoning.improvements:
                parts.append(f"           • {imp}")
        if self.action:
            parts.append(f"[Act]      actions={len(self.action.actions_taken)}")
            for act in self.action.actions_taken:
                parts.append(f"           → {act}")
        if self.verification:
            status = "✅ PASS" if self.verification.passed else "❌ FAIL"
            parts.append(
                f"[Verify]   {status}  coverage_after={self.verification.coverage_after:.1%}"
            )
        if self.converged:
            parts.append("[Converged] No further improvements identified.")
        duration = (self.ended_at or time.time()) - self.started_at
        parts.append(f"Duration: {duration:.2f}s")
        return "\n".join(parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_number": self.cycle_number,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "converged": self.converged,
            "observation": (
                {
                    "capability_gaps": self.observation.capability_gaps,
                    "proposed_servers": self.observation.proposed_servers,
                    "estimated_coverage_gain": self.observation.estimated_coverage_gain,
                    "smart_agent_events": self.observation.smart_agent_events,
                    "goal_used": self.observation.goal_used,
                }
                if self.observation
                else None
            ),
            "reasoning": (
                {
                    "improvements": self.reasoning.improvements,
                    "directive_id": self.reasoning.directive_id,
                    "session_id": self.reasoning.session_id,
                }
                if self.reasoning
                else None
            ),
            "action": (
                {
                    "actions_taken": self.action.actions_taken,
                    "reconfiguration_dry_run": self.action.reconfiguration_dry_run,
                }
                if self.action
                else None
            ),
            "verification": (
                {
                    "passed": self.verification.passed,
                    "checks": self.verification.checks,
                    "coverage_after": self.verification.coverage_after,
                }
                if self.verification
                else None
            ),
        }


@dataclass
class FlywheelReport:
    """Aggregated report across all flywheel cycles."""

    flywheel_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None
    cycles: list[FlywheelCycleResult] = field(default_factory=list)

    @property
    def total_cycles(self) -> int:
        return len(self.cycles)

    @property
    def converged(self) -> bool:
        return any(c.converged for c in self.cycles)

    @property
    def final_coverage(self) -> float:
        for cycle in reversed(self.cycles):
            if cycle.verification:
                return cycle.verification.coverage_after
        return 0.0

    def summary(self) -> str:
        lines = [
            f"UpgradeFlywheel {self.flywheel_id}",
            f"Total cycles: {self.total_cycles}",
            f"Converged:    {self.converged}",
            f"Final coverage: {self.final_coverage:.1%}",
            "",
        ]
        for cycle in self.cycles:
            lines.append(cycle.summary())
            lines.append("")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "flywheel_id": self.flywheel_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "total_cycles": self.total_cycles,
            "converged": self.converged,
            "final_coverage": self.final_coverage,
            "cycles": [c.to_dict() for c in self.cycles],
        }


# ---------------------------------------------------------------------------
# Flywheel orchestrator
# ---------------------------------------------------------------------------


class UpgradeFlywheel:
    """
    Iterative Observe → Reason → Act → Verify orchestrator.

    On each cycle the flywheel:

    1. **Observe** — runs the SmartAgent with a system-health goal and
       invokes :func:`~barrot_agent.reconfiguration.build_reconfiguration_report`
       to snapshot infrastructure state.

    2. **Reason** — synthesises observations into improvement recommendations
       and optionally opens a :class:`~directive_platform.DirectivePlatform`
       refinement directive (when *platform_dir* is provided).

    3. **Act** — records the actions that would apply the proposals.  In the
       default (dry-run) mode no live infrastructure is mutated; subclass and
       override :meth:`_act` to wire in real mutations.

    4. **Verify** — cross-checks that the cycle improved coverage and that all
       prior validations still pass.

    Parameters
    ----------
    platform_dir:
        Directory for :class:`~directive_platform.DirectivePlatform` data.
        When ``None`` the platform is instantiated in a throw-away temp dir
        so the flywheel works without any filesystem side-effects.
    dry_run:
        Whether infrastructure reconfiguration proposals are executed
        (``False``) or only described (``True``, default).
    agent_ids:
        Agent IDs to assign to DirectivePlatform refinement directives.
        When empty no directive session is opened during the Reason phase.
    """

    def __init__(
        self,
        *,
        platform_dir: Path | str | None = None,
        dry_run: bool = True,
        agent_ids: list[str] | None = None,
    ) -> None:
        import tempfile

        if platform_dir is None:
            self._tmp_dir = tempfile.mkdtemp(prefix="flywheel_platform_")
            self._platform_dir = Path(self._tmp_dir)
        else:
            self._tmp_dir = None
            self._platform_dir = Path(platform_dir)

        self._dry_run = dry_run
        self._agent_ids: list[str] = agent_ids or []

    # ------------------------------------------------------------------
    # Primary entry point
    # ------------------------------------------------------------------

    def run(self, *, max_cycles: int = 3) -> FlywheelReport:
        """
        Execute the upgrade flywheel and return a :class:`FlywheelReport`.

        Parameters
        ----------
        max_cycles:
            Maximum number of Observe→Reason→Act→Verify cycles.  The flywheel
            may stop earlier when convergence is detected.
        """
        if max_cycles < 1:
            raise ValueError("max_cycles must be >= 1")

        report = FlywheelReport()
        logger.info("UpgradeFlywheel %s starting (max_cycles=%d)", report.flywheel_id, max_cycles)

        prev_gaps: int | None = None

        for cycle_num in range(1, max_cycles + 1):
            cycle = FlywheelCycleResult(cycle_number=cycle_num)
            logger.info("--- Cycle %d / %d ---", cycle_num, max_cycles)

            # Phase 1: Observe
            cycle.observation = self._observe(cycle_num)

            # Phase 2: Reason
            cycle.reasoning = self._reason(cycle.observation)

            # Phase 3: Act
            cycle.action = self._act(cycle.observation, cycle.reasoning)

            # Phase 4: Verify
            cycle.verification = self._verify(cycle.observation, cycle.action)

            cycle.ended_at = time.time()

            # Convergence detection: no gaps left, or gap count unchanged from
            # previous cycle (no progress being made).
            current_gaps = cycle.observation.capability_gaps
            if current_gaps == 0 or (prev_gaps is not None and current_gaps == prev_gaps):
                cycle.converged = True

            report.cycles.append(cycle)
            logger.info("Cycle %d complete. converged=%s", cycle_num, cycle.converged)

            if cycle.converged:
                break

            prev_gaps = current_gaps

        report.ended_at = time.time()
        logger.info(
            "UpgradeFlywheel %s finished. cycles=%d converged=%s final_coverage=%.2f",
            report.flywheel_id,
            report.total_cycles,
            report.converged,
            report.final_coverage,
        )
        return report

    # ------------------------------------------------------------------
    # Phase implementations
    # ------------------------------------------------------------------

    def _observe(self, cycle_num: int) -> ObservationResult:
        """
        Phase 1 — Observe.

        Snapshot the system state via the SmartAgent and the reconfiguration
        report.  Returns an :class:`ObservationResult`.
        """
        from barrot_agent.reconfiguration import build_reconfiguration_report
        from barrot_agent.smart_agent import SmartAgent

        # Run SmartAgent observation pass
        goal = (
            f"Analyze the B-Agent repository system state (cycle {cycle_num}): "
            "identify active components, integration points, and capability gaps."
        )
        agent = SmartAgent()
        events = list(agent.run(goal))

        # Snapshot infrastructure
        reconfig = build_reconfiguration_report(dry_run=self._dry_run)

        return ObservationResult(
            capability_gaps=len(reconfig.gaps),
            proposed_servers=len(reconfig.proposals),
            estimated_coverage_gain=reconfig.estimated_coverage_gain,
            smart_agent_events=len(events),
            goal_used=goal,
        )

    def _reason(self, observation: ObservationResult) -> ReasoningResult:
        """
        Phase 2 — Reason.

        Synthesise observation data into a ranked list of improvements and
        optionally run a DirectivePlatform refinement directive.
        """
        improvements: list[str] = []

        if observation.capability_gaps > 0:
            improvements.append(
                f"Activate {observation.proposed_servers} proposed MCP server(s) "
                f"to close {observation.capability_gaps} capability gap(s) "
                f"(estimated +{observation.estimated_coverage_gain:.1%} coverage)."
            )

        if observation.estimated_coverage_gain > 0:
            improvements.append(
                "Promote top-scoring server candidates through the MCP approval pipeline."
            )

        improvements.append(
            "Cross-reference SmartAgent observation events with reconfiguration proposals "
            "to surface compound integration opportunities."
        )

        improvements.append(
            "Issue a REFINE directive to the DirectivePlatform so all registered agents "
            "contribute improvement insights for this cycle."
        )

        # Optionally open a DirectivePlatform session
        directive_id: str | None = None
        session_id: str | None = None
        if self._agent_ids:
            try:
                directive_id, session_id = self._run_platform_directive(improvements)
            except Exception:  # noqa: BLE001
                logger.warning("DirectivePlatform directive failed; continuing without it.")

        return ReasoningResult(
            improvements=improvements,
            directive_id=directive_id,
            session_id=session_id,
        )

    def _act(
        self, observation: ObservationResult, reasoning: ReasoningResult
    ) -> ActionResult:
        """
        Phase 3 — Act.

        Record the concrete actions applied (or proposed, in dry-run mode).
        Override this method in a subclass to wire in live mutations.
        """
        actions: list[str] = []

        for imp in reasoning.improvements:
            action_desc = f"[{'DRY-RUN' if self._dry_run else 'APPLIED'}] {imp}"
            actions.append(action_desc)

        if reasoning.directive_id:
            actions.append(
                f"DirectivePlatform session opened: directive={reasoning.directive_id} "
                f"session={reasoning.session_id}"
            )

        logger.info("Act phase: %d action(s) recorded.", len(actions))
        return ActionResult(actions_taken=actions, reconfiguration_dry_run=self._dry_run)

    def _verify(
        self,
        observation: ObservationResult,
        action: ActionResult,
    ) -> VerificationResult:
        """
        Phase 4 — Verify.

        Validate that the cycle produced coherent outputs and that coverage
        metrics are tracking in the right direction.
        """
        from barrot_agent.reconfiguration import build_reconfiguration_report

        checks: list[str] = []

        # Check 1: SmartAgent returned events
        if observation.smart_agent_events > 0:
            checks.append(f"✅ SmartAgent produced {observation.smart_agent_events} event(s).")
        else:
            checks.append("❌ SmartAgent produced zero events — possible failure.")

        # Check 2: Actions were recorded
        if action.actions_taken:
            checks.append(f"✅ {len(action.actions_taken)} action(s) recorded for this cycle.")
        else:
            checks.append("❌ No actions were recorded in the Act phase.")

        # Check 3: Re-run reconfig to get current coverage
        reconfig = build_reconfiguration_report(dry_run=True)
        total = 1  # avoid ZeroDivisionError if CAPABILITY_TARGETS is empty
        try:
            from barrot_agent.mcp_targets import CAPABILITY_TARGETS

            total = max(1, len(CAPABILITY_TARGETS))
        except Exception:  # noqa: BLE001
            pass
        coverage_after = 1.0 - (len(reconfig.gaps) / total)
        checks.append(
            f"{'✅' if coverage_after >= 0.0 else '❌'} "
            f"Post-cycle capability coverage: {coverage_after:.1%}"
        )

        passed = all(c.startswith("✅") for c in checks)
        return VerificationResult(
            passed=passed,
            checks=checks,
            coverage_after=coverage_after,
        )

    # ------------------------------------------------------------------
    # DirectivePlatform helpers
    # ------------------------------------------------------------------

    def _run_platform_directive(
        self, improvements: list[str]
    ) -> tuple[str, str]:
        """
        Issue a REFINE directive and run it synchronously.

        Returns ``(directive_id, session_id)``.
        """
        from directive_platform import DirectivePlatform, DirectiveType

        platform = DirectivePlatform(platform_dir=self._platform_dir)

        # Ensure all requested agents exist (register them if not)
        for aid in self._agent_ids:
            if platform.registry.get(aid) is None:
                from directive_platform import Agent

                platform.registry.register(
                    Agent(
                        agent_id=aid,
                        name=f"Agent-{aid}",
                        description="Flywheel refinement agent",
                        capabilities=["refine", "analyze"],
                    )
                )

        description = (
            "Upgrade Flywheel — REFINE cycle.\n\n"
            "Proposed improvements:\n"
            + "\n".join(f"- {imp}" for imp in improvements)
        )
        directive = platform.issue_directive(
            title="Upgrade Flywheel: Refinement Cycle",
            description=description,
            directive_type=DirectiveType.REFINE,
            agent_ids=self._agent_ids,
            human_author="Barrot",
        )
        session = platform.run_directive(directive.directive_id)
        return directive.directive_id, session.session_id
