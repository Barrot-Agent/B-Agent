from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T142000Z-alpha-finance-source-lineage-and-fund-scope-correction.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_alpha_finance_linked_methodology_identifies_coinglass_etf_feed():
    data = load_artifact()
    etf = data["etf_dashboard"]
    assert etf["source_lineage_disclosed_in_linked_methodology"] is True
    assert etf["upstream_source"] == "Coinglass"
    assert etf["upstream_methodology"]["commercial_api_under_license"] is True
    assert "few minutes" in etf["upstream_methodology"]["proxy_cache"]


def test_alpha_finance_five_fund_universe_and_zero_print_are_scoped():
    etf = load_artifact()["etf_dashboard"]
    assert [x["ticker"] for x in etf["funds_identified_by_ticker"]] == [
        "XRP", "XRPZ", "XRPC", "GXRP", "TOXR"
    ]
    assert etf["includes_xrpr"] is False
    assert etf["includes_bitw"] is False
    assert etf["page_data_as_of"] == "2026-11-06"
    assert etf["latest_session_status"] == "5 of 5 provider-listed funds reported for Nov 6"
    assert etf["nov6_reported_net_flow_usd"] == 0
    assert etf["issuer_holdings_or_aum_published"] is False
    assert etf["custody_balances_published"] is False


def test_alpha_finance_liquidation_heatmap_feed_list_is_explicit():
    heatmap = load_artifact()["liquidation_heatmap"]
    assert heatmap["upstream_feeds"] == [
        "Coinglass", "Binance", "Bybit", "OKX", "Hyperliquid",
        "Gate", "Bitget", "MEXC", "Kraken", "Deribit"
    ]
    assert heatmap["modelled_liquidation_map"] is True
    assert heatmap["exchange_metrics_self_reported"] is True
    assert "not the entire market" in heatmap["audit_status"]


def test_previous_alpha_finance_lineage_claim_is_explicitly_corrected():
    data = load_artifact()
    correction = data["correction_scope"][0]
    assert correction["artifact"].endswith(
        "20261107T135830Z-xrp-market-microstructure-etf-flow-vintage-reconciliation.json"
    )
    assert "identifies Coinglass" in correction["correction"]
    assert "incorrect" in data["etf_dashboard"]["source_lineage_correction"]


def test_provider_series_are_not_misrepresented_as_independent_primary_flows():
    independence = load_artifact()["source_independence"]
    assert "issuer" in independence["xrp_insights"]
    assert "issuer" in independence["cryptokeyhole"]
    assert "Coinglass" in independence["alpha_finance"]
    assert "not three independent primary measurements" in independence["conclusion"]


def test_alpha_finance_zero_is_a_provider_print_not_issuer_cash_ledger():
    etf = load_artifact()["etf_dashboard"]
    assert etf["nov6_reported_net_flow_usd"] == 0
    assert any("not an issuer-primary cash creation/redemption ledger" in x for x in etf["upstream_methodology"]["limitations"])
    assert load_artifact()["model_admission"]["admitted_to_etf_flow_features"] is False


def test_no_source_is_promoted_to_model_feature_or_forecast():
    data = load_artifact()
    assert data["model_admission"]["admitted_to_live_price_features"] is False
    assert data["model_admission"]["admitted_to_historical_price_features"] is False
    assert data["model_admission"]["admitted_to_etf_flow_features"] is False
    assert data["model_admission"]["admitted_to_derivatives_features"] is False
    assert data["model_admission"]["eligible_for_event_timeline"] is True
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["paper_trade_executed"] is False
    assert data["forecast"]["real_money_action"] is False
    assert data["source_capture_contract"]["raw_http_sha256_claimed"] is False
