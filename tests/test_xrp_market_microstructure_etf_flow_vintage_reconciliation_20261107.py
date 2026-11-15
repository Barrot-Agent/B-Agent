from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T135830Z-xrp-market-microstructure-etf-flow-vintage-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_market_snapshot_keeps_provider_times_and_spot_context_separate():
    data = load_artifact()
    assert data["captured_at_utc"] == "2026-11-07T13:58:30Z"
    sources = {x["source_id"]: x for x in data["market_microstructure"]["spot_context"]}
    trad = sources["trad_radar_xrp_perpetual_summary"]
    alpha = sources["alpha_finance_xrp_liquidation_heatmap_spot_context"]
    assert trad["reported_mark_price_usd"] == 1.1612
    assert trad["reported_24h_change_pct"] == -2.19
    assert trad["publisher_updated_at_utc"] == "2026-11-07T13:20:00Z"
    assert alpha["reported_spot_usd"] == 1.1593
    assert alpha["publisher_updated_at_utc"] == "2026-11-07T12:46:00Z"
    assert trad["model_eligible"] is False
    assert alpha["model_eligible"] is False


def test_depth_is_mixed_spot_perpetual_and_not_a_consolidated_spot_book():
    depth = load_artifact()["market_microstructure"]["order_book_depth"]
    assert depth["bids_within_1pct_usd"] == 10_400_000
    assert depth["asks_within_1pct_usd"] == 9_200_000
    assert depth["methodology"]["venues"] == ["Binance spot", "OKX perpetual"]
    assert depth["methodology"]["combined_market_types"] is True
    assert depth["model_eligible"] is False
    assert any("mixed spot/perpetual" in x for x in depth["limitations"])


def test_derivatives_open_interest_disagreement_is_preserved_not_averaged():
    derivatives = load_artifact()["market_microstructure"]["derivatives"]
    trad = derivatives["trad_radar"]
    alpha = derivatives["alpha_finance"]
    reconciliation = derivatives["reconciliation"]
    assert trad["open_interest_usd"] == 1_890_000_000
    assert trad["open_interest_venue_count"] == 7
    assert trad["weighted_funding_pct_per_8h"] == 0.009
    assert trad["liquidations_24h_usd_minimum"] == 8_630_000
    assert alpha["open_interest_usd"] == 2_740_000_000
    assert alpha["modelled_short_liquidation_liquidity_usd"] == 55_000_000
    assert alpha["modelled_long_liquidation_liquidity_usd"] == 31_800_000
    assert reconciliation["open_interest_absolute_difference_usd"] == 850_000_000
    assert reconciliation["status"] == "UNRECONCILED_DIFFERENT_PROVIDER_SCOPE_AND_CUTOFF"
    assert "do not average" in reconciliation["explanation"]


def test_xrp_insights_flow_method_and_universe_are_explicit():
    insights = load_artifact()["etf_flow_reconciliation"]["xrp_insights"]
    assert insights["data_as_of"] == "2026-11-06"
    assert insights["dataset_generated_at_utc"] == "2026-11-07T13:37:52.484Z"
    assert insights["nov6_net_flow_xrp"] == -663_043
    assert insights["nov2_to_nov6_net_flow_xrp"] == -812_529
    assert insights["nov6_total_holdings_xrp"] == 1_195_787_657
    assert insights["universe"] == ["XRPC", "XRP", "XRPR", "XRPZ", "GXRP", "TOXR", "BITW"]
    assert any("GXRP flow is excluded" in x for x in insights["important_scope_notes"])
    assert any("BITW is a multi-asset index fund" in x for x in insights["important_scope_notes"])


def test_cryptokeyhole_nov6_flow_is_explicitly_partial_and_date_anomaly_is_quarantined():
    keyhole = load_artifact()["etf_flow_reconciliation"]["cryptokeyhole"]
    assert keyhole["nov6_flow_xrp"] == -752_048
    assert keyhole["nov6_reporting_funds"] == 3
    assert keyhole["nov6_expected_funds"] == 4
    assert keyhole["nov6_by_fund_xrp"] == {"XRP": 0, "XRPZ": None, "XRPC": -752_048, "TOXR": 0}
    assert keyhole["nov6_missing_fund"] == "XRPZ / Franklin Templeton"
    assert keyhole["date_anomaly"]["status"] == "HEADER_CONFLICT_WITH_PER_FUND_TABLE"
    assert "future-dated" in keyhole["date_anomaly"]["treatment"]
    assert "not included in daily flow" in keyhole["excluded_funds"]["GXRP"].lower()


def test_alpha_finance_zero_flow_is_not_promoted_to_verified_zero():
    alpha = load_artifact()["etf_flow_reconciliation"]["alpha_finance"]
    assert alpha["reported_nov6_flow_usd"] == 0
    assert alpha["funds_reporting"] == 5
    assert alpha["published_holdings_or_aum"] is False
    assert alpha["source_lineage_disclosed_on_page"] is False
    assert "not as independently verified zero" in alpha["limitations"][-1]


def test_etf_provider_disagreement_is_not_averaged_or_called_independent():
    reconciliation = load_artifact()["etf_flow_reconciliation"]["reconciliation"]
    independence = load_artifact()["etf_flow_reconciliation"]["source_independence"]
    assert reconciliation["status"] == "UNRESOLVED_DIFFERENT_UNIVERSES_METHODS_AND_COMPLETENESS"
    assert "cannot be averaged" in reconciliation["conclusions"][-1]
    assert "not independent economic flow confirmation" in independence["xrp_insights_vs_cryptokeyhole"]
    assert independence["primary_issuer_confirmation"].startswith("No complete issuer-primary")


def test_no_market_or_etf_observation_is_admitted_as_a_price_or_flow_feature():
    data = load_artifact()
    assert data["model_admission"]["admitted_to_live_price_features"] is False
    assert data["model_admission"]["admitted_to_historical_price_features"] is False
    assert data["model_admission"]["admitted_to_exchange_flow_features"] is False
    assert data["model_admission"]["admitted_to_etf_flow_features"] is False
    assert data["model_admission"]["eligible_for_event_timeline"] is True
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["paper_trade_executed"] is False
    assert data["forecast"]["real_money_action"] is False
    assert data["source_capture_contract"]["raw_http_sha256_claimed"] is False
