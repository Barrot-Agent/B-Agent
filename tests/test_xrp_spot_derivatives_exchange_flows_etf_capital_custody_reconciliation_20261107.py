from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T153238Z-xrp-spot-derivatives-exchange-flows-etf-capital-custody-reconciliation.json"
)


@pytest.fixture(scope="module")
def evidence() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _source(evidence: dict, source_id: str) -> dict:
    return next(item for item in evidence["sources"] if item["source_id"] == source_id)


def test_direct_exchange_payload_receipts_match_exact_json_text(evidence: dict) -> None:
    for source_id in ("kraken_xrpusd_ticker", "okx_xrpusdt_ticker"):
        source = _source(evidence, source_id)
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_kraken_timestamp_is_unknown_and_level_one_quote_is_not_depth(evidence: dict) -> None:
    source = _source(evidence, "kraken_xrpusd_ticker")
    assert source["provider_event_time_utc"] is None
    assert source["model_eligible"] is False
    assert "Level-1" in " ".join(source["limitations"])
    quote = json.loads(source["raw_response_text"])["result"]["XXRPZUSD"]
    bid = float(quote["b"][0])
    ask = float(quote["a"][0])
    last = float(quote["c"][0])
    assert bid == pytest.approx(1.15879)
    assert ask == pytest.approx(1.15880)
    assert last == pytest.approx(1.15882)
    assert last > ask


def test_okx_response_is_stale_and_repeated_not_a_new_observation(evidence: dict) -> None:
    source = _source(evidence, "okx_xrpusdt_ticker")
    assert source["provider_age_seconds_at_capture"] == pytest.approx(1347.435)
    assert source["freshness"] == "stale_over_300_seconds"
    assert source["new_provider_event"] is False
    assert source["model_eligible"] is False


def test_cross_venue_price_difference_is_not_an_arbitrage_feature(evidence: dict) -> None:
    source = _source(evidence, "okx_xrpusdt_ticker")
    assert evidence["calculations"]["okx_raw_cross_venue_last_difference_pct"] == pytest.approx(0.2998552423)
    assert source["model_eligible"] is False
    assert "not directly normalized" in source["limitations"][2]


def test_future_dated_liqwall_snapshot_is_excluded(evidence: dict) -> None:
    source = _source(evidence, "liqwall_xrp_futures")
    assert source["provider_age_seconds_at_capture"] == -562
    assert source["freshness"] == "invalid_future_timestamp"
    assert source["model_eligible"] is False


def test_derivatives_open_interest_is_split_by_contract_scope(evidence: dict) -> None:
    trad = _source(evidence, "tradradar_xrp_perpetuals")
    trdesk = _source(evidence, "trdesk_xrp_futures_oi")
    alpha = _source(evidence, "alpha_finance_xrp_liquidation_heatmap")
    assert trad["observations"]["contract_scope"] == "perpetual futures"
    assert trdesk["observations"]["contract_scope"] == "perpetual swaps and quarterly futures"
    assert trdesk["observations"]["cme_open_interest_usd"] == 426_600_000
    assert trdesk["observations"]["coinbase_open_interest_usd"] == 41_500_000
    assert alpha["observations"]["open_interest_usd"] == 2_730_000_000
    assert all(item["model_eligible"] is False for item in (trad, trdesk, alpha))
    assert evidence["source_independence"]["derivatives_caveat"]


def test_alpha_liquidation_clusters_are_modelled_not_resting_orders(evidence: dict) -> None:
    source = _source(evidence, "alpha_finance_xrp_liquidation_heatmap")
    assert "modelled" in source["normalized_excerpt"].lower()
    assert "not real resting orders" in source["normalized_excerpt"]
    assert source["model_eligible"] is False


def test_exchange_wallet_snapshot_is_same_wallet_not_tradable_float(evidence: dict) -> None:
    source = _source(evidence, "xrp_insights_exchange_balances_json")
    obs = source["observations"]
    assert obs["total_xrp"] == 22_330_000_000
    assert obs["wallet_count"] == 701
    assert obs["exchange_count"] == 24
    assert obs["same_wallet_change_7d_xrp"] == -150_700_000
    assert obs["same_wallet_change_30d_xrp"] == -161_200_000
    assert obs["new_wallets_xrp"] == 512_000_000
    assert obs["naive_total_change_xrp"] == 350_800_000
    assert obs["non_customer_reserves_xrp"] == 487_800_000
    assert source["raw_payload_retained"] is False
    assert source["model_eligible"] is False
    assert "not tradable float" in " ".join(source["limitations"])


def test_coinbase_binance_and_sbi_vc_wallets_are_not_company_treasuries(evidence: dict) -> None:
    obs = _source(evidence, "xrp_insights_exchange_balances_json")["observations"]
    assert obs["coinbase_attributed_xrp"] == 5_790_000_000
    assert obs["coinbase_cbXRP_reserve_xrp"] == 150_800_000
    assert obs["binance_peg_reserve_xrp"] == 325_800_000
    assert obs["sbi_vc_trade_attributed_xrp"] == 56_600_000
    assert obs["sbi_vc_trade_change_7d_xrp"] == -2_900_000
    assert obs["sbi_vc_trade_change_30d_xrp"] == -4_200_000


def test_five_fund_etf_daily_flow_and_dashboard_conflict_are_preserved(evidence: dict) -> None:
    alpha = _source(evidence, "alpha_finance_xrp_etf_flows")
    crypto = _source(evidence, "cryptoetf_xrp_etf_dashboard")
    assert alpha["observations"]["net_flow_2026_11_06_usd"] == 0
    assert crypto["observations"]["headline_daily_net_flow_usd"] == 0
    assert crypto["observations"]["dashboard_table_daily_net_flow_usd"] == -500_000
    assert crypto["internal_consistency"].startswith("headline_and_daily_issue_zero")
    assert evidence["calculations"]["etf_30_session_flow_difference_usd"] == 93_800_000
    assert alpha["model_eligible"] is False and crypto["model_eligible"] is False


def test_holdings_derived_etf_flow_is_not_share_creation_redemption_flow(evidence: dict) -> None:
    source = _source(evidence, "xrp_insights_spot_etf_holdings_flow")
    obs = source["observations"]
    assert obs["product_count"] == 7
    assert obs["daily_flow_xrp"] == -663_043
    assert obs["gxrp_included_in_holdings_excluded_from_flow"] is True
    assert "issuer-reported XRP holdings" in source["limitations"][0]
    assert source["model_eligible"] is False


def test_21shares_primary_filing_distinguishes_q2_from_first_half(evidence: dict) -> None:
    source = _source(evidence, "sec_21shares_q2_2026_10q")
    obs = source["observations"]
    assert obs["q2_2026_net_shares"] == 260_000
    assert obs["q2_net_capital_transactions_usd"] == 3_701_981
    assert obs["h1_2026_net_shares"] == -2_780_000
    assert obs["h1_net_capital_transactions_usd"] == -49_500_531
    assert obs["q2_xrp_contributions"] == pytest.approx(4_679_662.7365)
    assert obs["q2_xrp_redemptions"] == pytest.approx(2_144_858.2811)
    assert source["model_eligible"] is False


def test_ripple_seed_and_coinbase_custody_are_indirect_edges_through_toxr(evidence: dict) -> None:
    source = _source(evidence, "sec_21shares_q2_2026_10q")
    obs = source["observations"]
    assert obs["ripple_markets_seed_shares"] == 10_000_000
    assert obs["ripple_markets_seed_proceeds_usd"] == 220_676_000
    assert obs["seed_lockup_end_utc"] == "2026-12-20"
    assert "Coinbase Custody Trust Company, LLC" in obs["custodians"]
    edges = evidence["relationship_edges"]
    assert any(e["from"] == "Ripple Markets Inc." and e["to"] == "21Shares XRP ETF (TOXR)" for e in edges)
    assert any(e["from"] == "21Shares XRP ETF (TOXR)" and e["to"] == "Coinbase Custody Trust Company, LLC" for e in edges)
    assert not any(e["from"] == "Ripple Markets Inc." and e["to"] == "Coinbase" for e in edges)


def test_cash_vs_in_kind_and_beneficial_ownership_are_not_inferred(evidence: dict) -> None:
    source = _source(evidence, "sec_21shares_q2_2026_10q")
    joined = " ".join(source["limitations"])
    assert "does not split Q2/H1 XRP contributions/redemptions between cash and in-kind" in joined
    assert "does not publish a current beneficial-ownership table for Ripple Markets" in joined
    assert source["observations"]["dtc_record_participants"] == 1


def test_13f_aggregation_is_historical_and_secondary(evidence: dict) -> None:
    source = _source(evidence, "cryptoetf_q2_2026_13f_aggregation")
    assert source["data_as_of_date"] == "2026-06-30"
    assert source["observations"]["institutions"] == 127
    assert source["observations"]["reported_long_positions_usd"] == 179_000_000
    assert source["model_eligible"] is False
    assert "not current holdings" in source["limitations"][0]


def test_all_normalized_excerpt_receipts_match(evidence: dict) -> None:
    for source in evidence["sources"]:
        if "normalized_excerpt" in source:
            digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
            assert digest == source["normalized_excerpt_sha256"]


def test_no_directional_forecast_is_issued(evidence: dict) -> None:
    assert evidence["forecast"]["status"] == "NOT_ISSUED"
    assert evidence["forecast"]["directional_probabilities"] is None
    assert evidence["model_admission"]["all_new_observations_eligible"] is False
    assert evidence["forecast"]["real_money_actions"] is False
