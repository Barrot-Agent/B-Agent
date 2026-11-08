from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T063207Z-xrp-etf-flow-coverage-and-institutional-demand-reconciliation.json"
)


def test_etf_flow_reconciliation_preserves_universe_and_cutoff_differences():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    obs = data["observations"]
    assert data["captured_at_utc"] == "2026-11-08T06:32:07Z"
    assert obs["xrp_insights"]["universe"] == "Six US spot XRP ETFs plus the XRP sleeve of BITW"
    assert obs["xrp_insights"]["net_flow_xrp_2026_11_02_through_2026_11_06"] == -812529
    assert obs["xrp_insights"]["total_xrp_holdings"] == 1195787657
    assert obs["alpha_finance"]["universe"] == "Five US spot XRP funds"
    assert obs["alpha_finance"]["net_flow_usd_30_sessions"] == 45900000
    assert obs["alpha_finance"]["net_flow_usd_2026_11_06"] == 0
    assert obs["crypto_keyhole"]["latest_complete_day"]["net_flow_xrp"] == -3338.61
    assert obs["crypto_keyhole"]["partial_day"]["reporting_coverage"].startswith("Three of four")
    assert obs["crypto_keyhole"]["institutional_13f_snapshot"]["managers_reporting"] == 117
    assert obs["crypto_keyhole"]["institutional_13f_snapshot"]["reported_spot_xrp_etf_share_value_usd"] == 154300000
    assert data["reconciliation"]["resolution_status"] == "NOT_COMPARABLE_PENDING_UNIVERSE_AND_VINTAGE_NORMALIZATION"
    assert data["source_independence"]["independent_corroboration_count_for_etf_flow_claim"] == 0
    assert data["model_admission"]["feature_store_admission"] is False
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"


def test_derivatives_and_bny_edges_do_not_overstate_live_capital_or_custody():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    deriv = data["observations"]["tradradar_derivatives"]
    assert deriv["open_interest_7_exchanges_usd"] == 1900000000
    assert deriv["long_account_share_pct"] == 79.1
    assert deriv["liquidations_24h_minimum_usd"] == 1500000
    bny = data["observations"]["bny_ripple_c2fo"]
    assert "now supports XRP and RLUSD" in bny["verified_live_capability"]
    assert len(bny["planned_or_exploratory"]) == 2
    assert len(bny["not_established"]) >= 4
    assert bny["model_eligible"] is False
