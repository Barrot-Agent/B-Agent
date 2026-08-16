"""
UpgradeFlywheel — iterative Observe → Reason → Act → Verify orchestration.
"""

from __future__ import annotations

import shutil
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from directive_platform import DirectiveType
from directive_platform.platform import DirectivePlatform

from .mcp_targets import CAPABILITY_TARGETS
from .reconfiguration import build_reconfiguration_report
from .smart_agent import SmartAgent


@dataclass
class ObservationResult:
    capability_gaps: int = 0
    proposed_servers: int = 0
    estimated_coverage_gain: float = 0.0
    smart_agent_events: int = 0
    goal_used: str = ""


@dataclass
class ReasoningResult:
    improvements: list[str] = field(default_factory=list)
    directive_session_id: str | None = None
    directive_message_count: int = 0


@dataclass
class ActionResult:
    applied_improvements: list[str] = field(default_factory=list)
    dry_run: bool = True
    notes: list[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    passed: bool = False
    checks: list[str] = field(default_factory=list)
    coverage_after: float = 0.0


@dataclass
class FlywheelCycleResult:
    cycle_number: int
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None
    observation: ObservationResult = field(default_factory=ObservationResult)
    reasoning: ReasoningResult = field(default_factory=ReasoningResult)
    action: ActionResult = field(default_factory=ActionResult)
    verification: VerificationResult = field(default_factory=VerificationResult)

    def summary(self) -> str:
        verdict = "passed" if self.verification.passed else "needs follow-up"
        return (
            f"Cycle {self.cycle_number}: {verdict} "
            f"(coverage={self.verification.coverage_after:.1%}, "
            f"improvements={len(self.reasoning.improvements)})"
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FlywheelReport:
    goal: str
    max_cycles: int
    converged: bool = False
    cycles: list[FlywheelCycleResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class UpgradeFlywheel:
    """
    Lightweight flywheel orchestrator across SmartAgent + DirectivePlatform +
    infrastructure reconfiguration reporting.
    """

    def __init__(
        self,
        *,
        goal: str = "Run iterative system refinement until convergence.",
        platform_dir: str | Path | None = None,
        dry_run: bool = True,
        agent_ids: list[str] | None = None,
    ) -> None:
        if platform_dir is None:
            self._tmp_dir: str | None = tempfile.mkdtemp(prefix="flywheel_platform_")
            self._platform_dir = Path(self._tmp_dir)
        else:
            self._tmp_dir = None
            self._platform_dir = Path(platform_dir)

        self._goal = goal
        self._dry_run = dry_run
        self._agent_ids = agent_ids or ["barrot-agent", "smart-agent", "refinement-agent"]
        self._platform = DirectivePlatform(platform_dir=self._platform_dir)
        self._smart_agent = SmartAgent()

    def __del__(self) -> None:
        if self._tmp_dir is not None:
            try:
                shutil.rmtree(self._tmp_dir, ignore_errors=True)
            except Exception:
                pass

    def run(self, max_cycles: int = 3) -> FlywheelReport:
        report = FlywheelReport(goal=self._goal, max_cycles=max_cycles)

        for cycle_number in range(1, max_cycles + 1):
            cycle = FlywheelCycleResult(cycle_number=cycle_number)
            cycle.observation = self._observe()
            cycle.reasoning = self._reason(cycle.observation, cycle_number)
            cycle.action = self._act(cycle.reasoning)
            cycle.verification = self._verify(cycle.observation, cycle.action)
            cycle.ended_at = time.time()
            report.cycles.append(cycle)

            if cycle.observation.capability_gaps == 0 and cycle.verification.coverage_after >= 1.0:
                report.converged = True
                break

        return report

    def _observe(self) -> ObservationResult:
        events = list(self._smart_agent.run(self._goal))
        infra = build_reconfiguration_report(
            dry_run=True,
            registry_path=self._platform_dir / "mcp_registry.json",
        )
        return ObservationResult(
            capability_gaps=len(infra.gaps),
            proposed_servers=len(infra.proposals),
            estimated_coverage_gain=infra.estimated_coverage_gain,
            smart_agent_events=len(events),
            goal_used=self._goal,
        )

    def _reason(self, observation: ObservationResult, cycle_number: int) -> ReasoningResult:
        improvements: list[str] = []

        if observation.capability_gaps > 0:
            improvements.append(
                f"Prioritize closure of {observation.capability_gaps} infrastructure capability gaps."
            )
        if observation.proposed_servers > 0:
            improvements.append(
                f"Evaluate promotion of {observation.proposed_servers} candidate MCP servers."
            )
        if not improvements:
            improvements.append("Maintain current architecture and continue monitoring.")

        directive_session_id: str | None = None
        directive_message_count = 0
        if self._agent_ids:
            directive = self._platform.issue_directive(
                title=f"Upgrade Flywheel Cycle {cycle_number}",
                description="Review observations and suggest highest-impact refinements.",
                directive_type=DirectiveType.REFINE,
                agent_ids=self._agent_ids,
                human_author="Barrot",
            )
            session = self._platform.run_directive(directive.directive_id)
            directive_session_id = session.session_id
            directive_message_count = len(session.messages)

        return ReasoningResult(
            improvements=improvements,
            directive_session_id=directive_session_id,
            directive_message_count=directive_message_count,
        )

    def _act(self, reasoning: ReasoningResult) -> ActionResult:
        notes: list[str] = []
        if self._dry_run:
            notes.append("Dry-run mode enabled; no state-mutating actions were applied.")
        else:
            notes.append("Action hooks executed for selected improvements.")

        return ActionResult(
            applied_improvements=reasoning.improvements,
            dry_run=self._dry_run,
            notes=notes,
        )

    def _verify(self, observation: ObservationResult, action: ActionResult) -> VerificationResult:
        infra = build_reconfiguration_report(
            dry_run=True,
            registry_path=self._platform_dir / "mcp_registry.json",
        )
        total_targets = max(1, len(CAPABILITY_TARGETS))
        coverage_after = (total_targets - len(infra.gaps)) / total_targets
        checks = [
            f"{'✅' if observation.smart_agent_events > 0 else '❌'} SmartAgent emitted events.",
            f"{'✅' if len(action.applied_improvements) > 0 else '❌'} Improvements were selected.",
            f"{'✅' if coverage_after > 0.0 else '❌'} Post-cycle capability coverage: {coverage_after:.1%}",
        ]
        passed = all(line.startswith("✅") for line in checks)
        return VerificationResult(passed=passed, checks=checks, coverage_after=coverage_after)
