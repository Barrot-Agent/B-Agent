"""
Tests for UpgradeFlywheel — iterative Observe→Reason→Act→Verify orchestrator.
"""

from __future__ import annotations

import pytest

from barrot_agent.upgrade_flywheel import (
    FlywheelCycleResult,
    FlywheelReport,
    UpgradeFlywheel,
    ObservationResult,
    ReasoningResult,
    ActionResult,
    VerificationResult,
)


class TestFlywheelDataModels:
    """Unit tests for the flywheel data model classes."""

    def test_flywheel_cycle_result_summary_contains_cycle_number(self) -> None:
        cycle = FlywheelCycleResult(cycle_number=1)
        summary = cycle.summary()
        assert "Cycle 1" in summary

    def test_flywheel_cycle_result_to_dict_round_trip(self) -> None:
        cycle = FlywheelCycleResult(
            cycle_number=2,
            observation=ObservationResult(
                capability_gaps=3,
                proposed_servers=2,
                estimated_coverage_gain=0.4,
                smart_agent_events=7,
                goal_used="test goal",
            ),
            reasoning=ReasoningResult(
                improvements=["fix gap A", "promote server B"],
                directive_id="d1",
                session_id="s1",
            ),
            action=ActionResult(
                actions_taken=["[DRY-RUN] fix gap A"],
                reconfiguration_dry_run=True,
            ),
            verification=VerificationResult(
                passed=True,
                checks=["✅ SmartAgent produced 7 event(s)."],
                coverage_after=0.6,
            ),
        )
        d = cycle.to_dict()
        assert d["cycle_number"] == 2
        assert d["observation"]["capability_gaps"] == 3
        assert d["reasoning"]["improvements"] == ["fix gap A", "promote server B"]
        assert d["action"]["reconfiguration_dry_run"] is True
        assert d["verification"]["passed"] is True

    def test_flywheel_report_properties(self) -> None:
        report = FlywheelReport()
        assert report.total_cycles == 0
        assert report.converged is False
        assert report.final_coverage == 0.0

        cycle = FlywheelCycleResult(
            cycle_number=1,
            converged=True,
            verification=VerificationResult(passed=True, checks=[], coverage_after=0.8),
        )
        report.cycles.append(cycle)
        assert report.total_cycles == 1
        assert report.converged is True
        assert report.final_coverage == pytest.approx(0.8)


class TestUpgradeFlywheelSmoke:
    """Integration smoke tests for the UpgradeFlywheel orchestrator."""

    def test_run_single_cycle_returns_report(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        assert isinstance(report, FlywheelReport)
        assert report.total_cycles >= 1

    def test_run_returns_at_most_max_cycles(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=2)

        assert report.total_cycles <= 2

    def test_each_cycle_has_all_phases(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        cycle = report.cycles[0]
        assert cycle.observation is not None
        assert cycle.reasoning is not None
        assert cycle.action is not None
        assert cycle.verification is not None

    def test_observation_has_positive_event_count(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        obs = report.cycles[0].observation
        assert obs.smart_agent_events > 0

    def test_reasoning_contains_improvements(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        reasoning = report.cycles[0].reasoning
        assert len(reasoning.improvements) > 0

    def test_action_records_entries_for_each_improvement(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        cycle = report.cycles[0]
        assert len(cycle.action.actions_taken) >= len(cycle.reasoning.improvements)

    def test_verification_passed(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        assert report.cycles[0].verification.passed is True

    def test_max_cycles_zero_raises(self) -> None:
        fw = UpgradeFlywheel()
        with pytest.raises(ValueError, match="max_cycles"):
            fw.run(max_cycles=0)

    def test_dry_run_flag_propagates_to_action(self) -> None:
        fw = UpgradeFlywheel(dry_run=True)
        report = fw.run(max_cycles=1)

        assert report.cycles[0].action.reconfiguration_dry_run is True

    def test_convergence_stops_early(self) -> None:
        """
        When the infrastructure already has zero gaps the flywheel should
        mark the first cycle as converged and not start a second one.
        """
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=5)

        # The flywheel may converge in cycle 1 when gaps==0
        if report.cycles[0].observation.capability_gaps == 0:
            assert report.cycles[0].converged is True
            assert report.total_cycles == 1

    def test_summary_contains_flywheel_id(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        summary = report.summary()
        assert report.flywheel_id in summary

    def test_to_dict_is_json_serialisable(self) -> None:
        import json

        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        # Should not raise
        serialised = json.dumps(report.to_dict())
        assert len(serialised) > 0


class TestUpgradeFlywheelWithPlatform:
    """Test flywheel with DirectivePlatform integration enabled."""

    def test_run_with_agent_ids_opens_session(self, tmp_path) -> None:
        from directive_platform import DirectivePlatform, Agent

        # Pre-register agents so the directive can be assigned
        platform_dir = tmp_path / "dp"
        dp = DirectivePlatform(platform_dir=platform_dir)
        dp.registry.register(
            Agent(
                agent_id="refine-agent",
                name="Refine Agent",
                description="Refinement specialist",
                capabilities=["refine"],
            )
        )

        fw = UpgradeFlywheel(
            platform_dir=platform_dir,
            agent_ids=["refine-agent"],
        )
        report = fw.run(max_cycles=1)

        cycle = report.cycles[0]
        assert cycle.reasoning is not None
        # With a registered agent, a directive and session should be created
        assert cycle.reasoning.directive_id is not None
        assert cycle.reasoning.session_id is not None
