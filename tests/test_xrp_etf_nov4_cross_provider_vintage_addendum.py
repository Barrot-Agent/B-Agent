from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T120020Z-xrp-etf-nov4-cross-provider-vintage-addendum.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_xrp_insights_nov4_update_is_three_settled_days_and_holdings_delta():
    item = load()["provider_observations"]["xrp_insights"]
    assert item["reported_window"] == "2026-11-02_to_2026-11-04"
    assert item["settled_trading_days"] == 3
    assert item["net_holdings_delta_xrp"] == -259701
    assert item["total_holdings_xrp_2026_11_04"] == 1196340485
    assert "BITW" in item["fund_universe"]
    assert "XRPR" in item["fund_universe"]
    assert item["model_eligible"] is False


def test_cryptokeyhole_nov4_remains_partial_and_excludes_indirect_products():
    item = load()["provider_observations"]["cryptokeyhole"]
    assert item["net_flow_xrp_2026_11_03_complete"] == -3339
    assert item["net_flow_xrp_2026_11_04_partial"] == -3339
    assert item["nov4_reporting_funds"] == 3
    assert item["nov4_total_daily_funds"] == 4
    assert "XRPR" not in item["daily_flow_universe"]
    assert "GXRP" not in item["daily_flow_universe"]
    assert item["model_eligible"] is False


def test_alpha_and_maketo_zeroes_are_recorded_as_displayed_not_cash_proof():
    data = load()["provider_observations"]
    assert data["alpha_finance"]["net_flow_usd_displayed_2026_11_04"] == 0
    assert data["alpha_finance"]["reporting_funds_2026_11_04"] == 5
    assert data["alpha_finance"]["holdings_or_aum_published"] is False
    assert data["maketo"]["net_flow_usd_displayed_2026_11_04"] == 0
    assert data["maketo"]["net_flow_usd_displayed_2026_11_02"] == -530000


def test_cross_provider_flow_values_are_not_averaged_or_called_independent():
    item = load()["cross_provider_reconciliation"]
    assert item["reconciliation_status"] == "UNRESOLVED_AT_COMMON_FUND_DATE_LEVEL"
    assert "Do not average" in item["comparison_rule"]
    assert "not four independent measurements" in item["source_independence"]


def test_counter_hypotheses_preserve_fees_timing_and_upstream_staleness():
    items = {x["id"]: x for x in load()["counter_hypotheses"]}
    assert "fund_universe_and_product_structure" in items
    assert "publication_lag_and_date_alignment" in items
    assert "holdings_delta_not_cash_redemption" in items
    assert "provider_rounding_or_upstream_staleness" in items
    assert any(
        "Authorized-participant cash" in x
        for x in items["holdings_delta_not_cash_redemption"]["disconfirming_evidence_to_seek"]
    )


def test_artifact_is_model_ineligible_without_raw_issuer_receipts():
    data = load()
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["source_capture_policy"]["raw_source_bytes_captured"] is False
    assert data["source_capture_policy"]["raw_content_sha256"] is None
    assert all(item["raw_content_sha256"] is None for item in data["source_registry"])
    assert data["predictive_admission"]["forecast_status"] == "NOT_ISSUED"
