"""Regression tests for the legacy XRP telemetry report's safety boundary."""

import asyncio

import pytest

from barrot_agent.analysis.xrp_telemetry_matrix import CouncilReportNode


def test_legacy_report_does_not_fabricate_market_data_or_directional_advice(tmp_path):
    report_path = tmp_path / "COUNCIL_REVIEW.md"
    node = CouncilReportNode(report_path=report_path)

    asyncio.run(node.process_telemetry())

    report = report_path.read_text(encoding="utf-8")
    assert "NO_VERIFIED_TELEMETRY" in report
    assert "NOT_ISSUED" in report
    assert "No price, order-book depth" in report
    assert "No accumulation recommendation" in report
    assert "1.185" not in report
    assert "0.94" not in report
    assert "MAX_LIQUIDITY" not in report
    assert "optimal accumulation" not in report.lower()


def test_legacy_anchor_is_metadata_not_a_market_feature(tmp_path):
    report_path = tmp_path / "report.md"
    node = CouncilReportNode(stability_anchor=0.8, report_path=report_path)

    asyncio.run(node.generate_report())

    report = report_path.read_text(encoding="utf-8")
    assert "0.8 (not a market observation)" in report
    assert "NOT_ISSUED" in report


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), float("-inf"), "0.7"])
def test_legacy_anchor_rejects_invalid_configuration(value):
    with pytest.raises(ValueError, match="finite number"):
        CouncilReportNode(stability_anchor=value)
