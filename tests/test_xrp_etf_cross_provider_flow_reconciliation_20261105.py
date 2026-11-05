from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T102000Z-xrp-etf-cross-provider-flow-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_xrp_insights_universe_and_holdings_delta_are_not_cash_redemptions():
    item = load()["provider_observations"]["xrp_insights"]
    assert item["spot_etf_funds"] == 6
    assert item["index_sleeves"] == 1
    assert item["net_flow_xrp_nov2_nov3"] == -194875
    assert item["holdings_xrp_nov3"] == 1196405311
    assert "holdings" in item["flow_method"]
    assert item["model_eligible"] is False


def test_cryptokeyhole_four_fund_partial_day_includes_fee_and_payout_changes():
    item = load()["provider_observations"]["cryptokeyhole"]
    assert item["daily_flow_universe"] == ["XRP", "XRPZ", "XRPC", "TOXR"]
    assert item["net_flow_xrp_nov3"] == -3339
    assert item["net_flow_xrp_nov4_partial"] == -3339
    assert item["nov4_reporting_funds"] == 3
    assert item["nov4_total_daily_funds"] == 4
    assert "fee sales" in item["method"]
    assert item["model_eligible"] is False


def test_cryptoetf_today_zero_is_partial_not_a_complete_daily_total():
    item = load()["provider_observations"]["cryptoetf_today"]
    assert item["tracked_spot_funds"] == 5
    assert item["net_flow_xrp_nov4_partial"] == 0
    assert item["status"] == "PARTIAL_NOT_ALL_FUNDS_REPORTED"
    assert "missing funds are not treated as zero" in item["definition"]


def test_cross_provider_holdings_difference_is_reconciled_by_unlike_universes():
    item = load()["cross_provider_reconciliation"]
    assert item["holdings_difference_xrp_xrp_insights_minus_cryptokeyhole"] == 119592749
    assert "not the same universe" in item["explanation"]
    assert "Do not average" in item["comparison_rule"]
    assert "not three independent measurements" in item["source_independence"]


def test_counter_hypotheses_distinguish_fees_from_investor_redemptions():
    items = {x["id"]: x for x in load()["counter_hypotheses"]}
    assert "reported_holdings_delta_not_investor_redemption" in items
    assert "partial_zero_not_complete_neutrality" in items
    assert any("Authorized-participant cash records" in x for x in items["reported_holdings_delta_not_investor_redemption"]["disconfirming_evidence_to_seek"])


def test_etf_flow_sources_remain_ineligible_without_raw_issuer_receipts():
    data = load()
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["source_capture_policy"]["raw_issuer_bytes_captured"] is False
    assert data["source_capture_policy"]["raw_content_sha256"] is None
    assert all(x["raw_content_sha256"] is None for x in data["source_registry"])
    assert all(x["model_eligible"] is False for x in data["source_registry"])
    assert data["predictive_admission"]["forecast_status"] == "NOT_ISSUED"
