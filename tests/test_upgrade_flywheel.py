"""
Tests for UpgradeFlywheel — iterative Observe→Reason→Act→Verify orchestrator.
"""

from __future__ import annotations

from barrot_agent.upgrade_flywheel import (
    ActionResult,
    FlywheelCycleResult,
    FlywheelReport,
    ObservationResult,
    ReasoningResult,
    UpgradeFlywheel,
    VerificationResult,
)


class TestFlywheelDataModels:
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
                directive_session_id="sess-123",
                directive_message_count=8,
            ),
            action=ActionResult(
                applied_improvements=["fix gap A"],
                dry_run=True,
                notes=["dry-run only"],
            ),
            verification=VerificationResult(
                passed=True,
                checks=["✅ check A", "✅ check B"],
                coverage_after=0.75,
            ),
        )

        data = cycle.to_dict()
        assert data["cycle_number"] == 2
        assert data["observation"]["capability_gaps"] == 3
        assert data["verification"]["passed"] is True


class TestUpgradeFlywheel:
    def test_run_returns_report_with_cycles(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        assert isinstance(report, FlywheelReport)
        assert len(report.cycles) == 1
        assert report.cycles[0].cycle_number == 1
        assert report.cycles[0].observation.goal_used

    def test_verification_passed_shape(self) -> None:
        fw = UpgradeFlywheel()
        report = fw.run(max_cycles=1)

        verification = report.cycles[0].verification
        assert isinstance(verification.passed, bool)
        for check in verification.checks:
            assert check.startswith("✅") or check.startswith("❌")
        assert 0.0 <= verification.coverage_after <= 1.0
