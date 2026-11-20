"""Regression tests for the legacy XRP telemetry status-only safety boundary."""

import asyncio
import json
import runpy
from pathlib import Path

import pytest

from barrot_agent.analysis.xrp_telemetry_matrix import CouncilReportNode


def test_legacy_report_returns_no_data_status_without_directional_advice(tmp_path):
    report_path = tmp_path / "COUNCIL_REVIEW.md"
    node = CouncilReportNode(report_path=report_path)

    result = asyncio.run(node.process_telemetry())

    assert result["status"] == "NOT_ISSUED"
    assert result["data_status"] == "NO_VERIFIED_TELEMETRY"
    assert result["forecast_issued"] is False
    assert result["forecast_eligible"] is False
    assert result["report_written"] is False
    assert result["external_action_performed"] is False
    assert not report_path.exists()


def test_legacy_anchor_is_configuration_metadata_not_a_market_feature(tmp_path):
    report_path = tmp_path / "report.md"
    node = CouncilReportNode(stability_anchor=0.8, report_path=report_path)

    result = asyncio.run(node.generate_report())

    assert node.stability_anchor == 0.8
    assert "stability_anchor" not in result
    assert result["status"] == "NOT_ISSUED"
    assert result["forecast_issued"] is False
    assert not report_path.exists()


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), float("-inf"), "0.7"])
def test_legacy_anchor_rejects_invalid_configuration(value):
    with pytest.raises(ValueError, match="finite number"):
        CouncilReportNode(stability_anchor=value)


def test_cli_entrypoint_emits_status_only_and_writes_no_report(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    script_path = (
        Path(__file__).parents[1]
        / "barrot_agent"
        / "analysis"
        / "xrp_telemetry_matrix.py"
    )

    runpy.run_path(str(script_path), run_name="__main__")

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "NOT_ISSUED"
    assert payload["data_status"] == "NO_VERIFIED_TELEMETRY"
    assert payload["forecast_issued"] is False
    assert payload["report_written"] is False
    assert not (tmp_path / "COUNCIL_REVIEW.md").exists()
