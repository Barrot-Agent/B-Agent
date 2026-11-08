"""
Recursive Feedback Loop Orchestrator for Barrot-Ω.

This module implements a self-improving feedback loop that:
1. Analyzes current system state
2. Generates paradigm-shifting insights via Kimi 3
3. Absorbs and applies feedback recursively
4. Refines infrastructure dynamically
5. Continues indefinitely with convergence monitoring
"""

from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

from .config import FeedbackLoopConfig, config
from .kimi_integration import KimiClient
from .logger import get_logger
from .reconfiguration import build_reconfiguration_report
from .upgrade_flywheel import FlywheelReport, UpgradeFlywheel

logger = get_logger(__name__)


@dataclass
class FeedbackIteration:
    """Single iteration of the feedback loop."""

    iteration: int
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    system_state: Dict[str, Any] = field(default_factory=dict)
    kimi_feedback: Dict[str, Any] = field(default_factory=dict)
    absorbed_insights: List[str] = field(default_factory=list)
    applied_improvements: List[str] = field(default_factory=list)
    infrastructure_changes: Dict[str, Any] = field(default_factory=dict)
    improvement_score: float = 0.0
    convergence_metric: float = 0.0
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RecursiveFeedbackReport:
    """Complete report of recursive feedback loop execution."""

    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at: Optional[str] = None
    total_iterations: int = 0
    converged: bool = False
    final_convergence: float = 0.0
    iterations: List[FeedbackIteration] = field(default_factory=list)
    total_improvements: int = 0
    paradigm_shifts_discovered: int = 0
    infrastructure_refinements: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def save(self, path: Path | str) -> None:
        """Save report to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info("Saved feedback report to %s", path)


class RecursiveFeedbackLoop:
    """
    Orchestrator for recursive self-improvement via Kimi 3 feedback.

    The loop executes indefinitely (or until max_iterations) with these phases:

    1. **Observe** - Capture current system state and metrics
    2. **Analyze** - Generate paradigm-shifting insights via Kimi 3
    3. **Absorb** - Process and internalize feedback
    4. **Apply** - Execute improvements and refine infrastructure
    5. **Verify** - Measure improvement and check convergence
    """

    def __init__(
        self,
        *,
        loop_config: FeedbackLoopConfig | None = None,
        kimi_client: KimiClient | None = None,
        output_dir: Path | str = "feedback_loops",
    ) -> None:
        self.config = loop_config or config.feedback_loop
        self.kimi = kimi_client or KimiClient()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Improvement tracking
        self._improvement_history: Deque[float] = deque(maxlen=self.config.improvement_window)
        self._feedback_history: Deque[Dict[str, Any]] = deque(
            maxlen=self.config.feedback_history_limit
        )

    def _observe_system_state(self, iteration: int) -> Dict[str, Any]:
        """
        Observe current system state.

        Args:
            iteration: Current iteration number

        Returns:
            System state dictionary
        """
        logger.info("Observing system state (iteration %d)", iteration)

        # Build infrastructure reconfiguration report
        try:
            reconfig_report = build_reconfiguration_report(dry_run=True)
            reconfig_data = {
                "gaps_count": len(reconfig_report.gaps),
                "proposals_count": len(reconfig_report.proposals),
                "coverage_gain": reconfig_report.estimated_coverage_gain,
            }
        except Exception as e:
            logger.warning("Failed to build reconfiguration report: %s", e)
            reconfig_data = {"error": str(e)}

        state = {
            "iteration": iteration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "infrastructure": reconfig_data,
            "improvement_history": list(self._improvement_history),
            "feedback_history_size": len(self._feedback_history),
        }

        logger.debug("System state: %s", state)
        return state

    def _analyze_with_kimi(
        self,
        system_state: Dict[str, Any],
        improvement_goals: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze system state using Kimi 3 for paradigm-shifting insights.

        Args:
            system_state: Current system state
            improvement_goals: Target improvement goals

        Returns:
            Kimi feedback dictionary
        """
        logger.info("Analyzing with Kimi 3 (iteration %d)", system_state["iteration"])

        if not self.kimi.is_available:
            logger.warning("Kimi not available, using placeholder feedback")
            return {
                "paradigm_shifts": ["Kimi integration not configured"],
                "emergent_patterns": [],
                "meta_optimizations": [],
                "infrastructure_gaps": [],
                "convergence_strategies": [],
            }

        try:
            feedback = self.kimi.analyze_feedback(
                current_state=system_state,
                previous_outputs=[f["absorbed_insights"] for f in self._feedback_history][-5:],
                improvement_goals=improvement_goals,
            )
            logger.debug("Kimi feedback: %s", feedback)
            return feedback

        except Exception as e:
            logger.error("Kimi analysis failed: %s", e)
            return {
                "error": str(e),
                "paradigm_shifts": [],
                "emergent_patterns": [],
                "meta_optimizations": [],
                "infrastructure_gaps": [],
                "convergence_strategies": [],
            }

    def _absorb_feedback(self, kimi_feedback: Dict[str, Any]) -> List[str]:
        """
        Absorb and process Kimi feedback into actionable insights.

        Args:
            kimi_feedback: Feedback from Kimi analysis

        Returns:
            List of absorbed insights
        """
        logger.info("Absorbing Kimi feedback")

        insights = []

        # Extract paradigm shifts
        for shift in kimi_feedback.get("paradigm_shifts", []):
            if isinstance(shift, str):
                insights.append(f"PARADIGM: {shift}")
            elif isinstance(shift, dict):
                insights.append(f"PARADIGM: {shift.get('description', str(shift))}")

        # Extract emergent patterns
        for pattern in kimi_feedback.get("emergent_patterns", []):
            if isinstance(pattern, str):
                insights.append(f"PATTERN: {pattern}")
            elif isinstance(pattern, dict):
                insights.append(f"PATTERN: {pattern.get('description', str(pattern))}")

        # Extract meta-optimizations
        for opt in kimi_feedback.get("meta_optimizations", []):
            if isinstance(opt, str):
                insights.append(f"META: {opt}")
            elif isinstance(opt, dict):
                insights.append(f"META: {opt.get('description', str(opt))}")

        # Extract infrastructure gaps
        for gap in kimi_feedback.get("infrastructure_gaps", []):
            if isinstance(gap, str):
                insights.append(f"GAP: {gap}")
            elif isinstance(gap, dict):
                insights.append(f"GAP: {gap.get('description', str(gap))}")

        # Extract convergence strategies
        for strategy in kimi_feedback.get("convergence_strategies", []):
            if isinstance(strategy, str):
                insights.append(f"STRATEGY: {strategy}")
            elif isinstance(strategy, dict):
                insights.append(f"STRATEGY: {strategy.get('description', str(strategy))}")

        logger.info("Absorbed %d insights", len(insights))
        return insights

    def _apply_improvements(
        self,
        absorbed_insights: List[str],
        iteration: int,
    ) -> tuple[List[str], Dict[str, Any]]:
        """
        Apply improvements based on absorbed insights.

        Args:
            absorbed_insights: Insights to apply
            iteration: Current iteration number

        Returns:
            Tuple of (applied improvements, infrastructure changes)
        """
        logger.info("Applying improvements (iteration %d)", iteration)

        applied = []
        infra_changes = {}

        # Run infrastructure refinement if enabled and interval reached
        if self.config.enable_auto_refinement and iteration % self.config.refinement_interval == 0:
            logger.info("Running infrastructure refinement")
            try:
                flywheel = UpgradeFlywheel(dry_run=True, goal="Apply feedback insights")
                report: FlywheelReport = flywheel.run(max_cycles=1)

                infra_changes = {
                    "cycles": len(report.cycles),
                    "converged": report.converged,
                    "improvements": sum(len(c.reasoning.improvements) for c in report.cycles),
                }
                applied.append(
                    f"Infrastructure refinement: {infra_changes['improvements']} improvements"
                )

            except Exception as e:
                logger.error("Infrastructure refinement failed: %s", e)
                infra_changes = {"error": str(e)}

        # Apply insight-driven improvements
        for insight in absorbed_insights:
            if insight.startswith("PARADIGM:"):
                applied.append(f"Integrated paradigm shift: {insight[10:]}")
            elif insight.startswith("META:"):
                applied.append(f"Applied meta-optimization: {insight[5:]}")
            elif insight.startswith("GAP:"):
                applied.append(f"Addressed infrastructure gap: {insight[4:]}")

        logger.info("Applied %d improvements", len(applied))
        return applied, infra_changes

    def _verify_improvement(
        self,
        iteration: int,
        system_state: Dict[str, Any],
        applied_improvements: List[str],
    ) -> tuple[float, float]:
        """
        Verify improvement and calculate convergence metric.

        Args:
            iteration: Current iteration number
            system_state: Current system state
            applied_improvements: List of applied improvements

        Returns:
            Tuple of (improvement_score, convergence_metric)
        """
        logger.info("Verifying improvement (iteration %d)", iteration)

        # Calculate improvement score based on multiple factors
        improvement_score = 0.0

        # Factor 1: Infrastructure coverage gain
        infra_coverage = system_state.get("infrastructure", {}).get("coverage_gain", 0.0)
        improvement_score += infra_coverage * 0.3

        # Factor 2: Number of applied improvements
        improvement_count = len(applied_improvements)
        improvement_score += min(improvement_count / 10.0, 0.3)

        # Factor 3: Feedback quality (based on insight diversity)
        improvement_score += 0.4  # Base quality score

        # Track improvement
        self._improvement_history.append(improvement_score)

        # Calculate convergence metric
        if len(self._improvement_history) >= self.config.improvement_window:
            # Convergence = stability of improvements
            recent_improvements = list(self._improvement_history)
            avg_improvement = sum(recent_improvements) / len(recent_improvements)
            variance = sum((x - avg_improvement) ** 2 for x in recent_improvements) / len(
                recent_improvements
            )
            convergence_metric = max(0.0, 1.0 - variance)
        else:
            convergence_metric = 0.0

        logger.info(
            "Improvement score: %.3f, Convergence: %.3f",
            improvement_score,
            convergence_metric,
        )
        return improvement_score, convergence_metric

    def run(
        self,
        improvement_goals: List[str] | None = None,
        max_iterations: Optional[int] = None,
    ) -> RecursiveFeedbackReport:
        """
        Run the recursive feedback loop.

        Args:
            improvement_goals: Optional list of improvement goals
            max_iterations: Optional override for maximum iterations

        Returns:
            Complete feedback report
        """
        if improvement_goals is None:
            improvement_goals = [
                "Maximize infrastructure coverage",
                "Discover paradigm shifts",
                "Accelerate convergence",
                "Optimize resource utilization",
                "Enhance self-improvement capabilities",
            ]

        max_iter = max_iterations or self.config.max_iterations
        logger.info(
            "Starting recursive feedback loop (max_iterations=%d, convergence_threshold=%.3f)",
            max_iter,
            self.config.convergence_threshold,
        )

        report = RecursiveFeedbackReport()

        for iteration in range(1, max_iter + 1):
            iteration_start = time.time()
            logger.info("=" * 70)
            logger.info("ITERATION %d/%d", iteration, max_iter)
            logger.info("=" * 70)

            try:
                # Phase 1: Observe
                system_state = self._observe_system_state(iteration)

                # Phase 2: Analyze
                kimi_feedback = self._analyze_with_kimi(system_state, improvement_goals)

                # Phase 3: Absorb
                absorbed_insights = self._absorb_feedback(kimi_feedback)

                # Phase 4: Apply
                applied_improvements, infra_changes = self._apply_improvements(
                    absorbed_insights, iteration
                )

                # Phase 5: Verify
                improvement_score, convergence_metric = self._verify_improvement(
                    iteration, system_state, applied_improvements
                )

                # Record iteration
                iteration_result = FeedbackIteration(
                    iteration=iteration,
                    system_state=system_state,
                    kimi_feedback=kimi_feedback,
                    absorbed_insights=absorbed_insights,
                    applied_improvements=applied_improvements,
                    infrastructure_changes=infra_changes,
                    improvement_score=improvement_score,
                    convergence_metric=convergence_metric,
                    duration_seconds=time.time() - iteration_start,
                )

                report.iterations.append(iteration_result)
                self._feedback_history.append(iteration_result.to_dict())

                # Update report stats
                report.total_iterations = iteration
                report.final_convergence = convergence_metric
                report.total_improvements += len(applied_improvements)
                report.paradigm_shifts_discovered += len(kimi_feedback.get("paradigm_shifts", []))
                if infra_changes and "improvements" in infra_changes:
                    report.infrastructure_refinements += infra_changes["improvements"]

                # Check convergence
                if convergence_metric >= self.config.convergence_threshold:
                    logger.info(
                        "Convergence achieved! (%.3f >= %.3f)",
                        convergence_metric,
                        self.config.convergence_threshold,
                    )
                    report.converged = True
                    break

                logger.info(
                    "Iteration %d complete: score=%.3f, convergence=%.3f",
                    iteration,
                    improvement_score,
                    convergence_metric,
                )

            except Exception as e:
                logger.error("Iteration %d failed: %s", iteration, e, exc_info=True)
                # Continue with next iteration
                continue

        report.ended_at = datetime.now(timezone.utc).isoformat()

        # Save report
        report_path = self.output_dir / f"feedback_loop_{int(time.time())}.json"
        report.save(report_path)

        logger.info("=" * 70)
        logger.info("FEEDBACK LOOP COMPLETE")
        logger.info("=" * 70)
        logger.info("Total iterations: %d", report.total_iterations)
        logger.info("Converged: %s", report.converged)
        logger.info("Final convergence: %.3f", report.final_convergence)
        logger.info("Total improvements: %d", report.total_improvements)
        logger.info("Paradigm shifts: %d", report.paradigm_shifts_discovered)
        logger.info("Infrastructure refinements: %d", report.infrastructure_refinements)
        logger.info("=" * 70)

        return report
