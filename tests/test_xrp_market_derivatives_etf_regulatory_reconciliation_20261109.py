from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261109T010332Z-xrp-market-derivatives-etf-regulatory-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_surfaced_payload_and_excerpt_hashes_reproduce() -> None:
    data = load_artifact()
    receipts = {item["id"]: item for item in data["source_receipts"]}
    for source_id, body in data["raw_surface_payloads"].items():
        assert hashlib.sha256(body.encode("utf-8")).hexdigest() == receipts[source_id]["sha256"]
        assert receipts[source_id]["hash_scope"].startswith("exact JSON text surfaced")
    for source_id, excerpt in data["normalized_excerpts"].items():
        assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == receipts[source_id]["sha256"]
        assert receipts[source_id]["hash_scope"].startswith("normalized excerpt text")
    assert set(receipts) == set(data["raw_surface_payloads"]) | set(data["normalized_excerpts"])


def test_direct_market_snapshots_fail_closed_on_freshness() -> None:
    data = load_artifact()
    market = data["market"]
    assert market["direct_spot"]["kraken"]["provider_event_time_utc"] is None
    assert market["direct_spot"]["okx"]["age_seconds_at_reference"] > 300
    assert market["direct_spot"]["coinpaprika"]["age_seconds_at_reference"] > 300
    assert market["perpetual"]["age_seconds_at_reference"] > 300
    assert market["admission"]["model_eligible"] is False
    assert market["cross_venue"]["comparison_validity"] == "INVALID_FOR_ARBITRAGE_OR_DIRECTIONAL_FEATURE"


def test_derivatives_preserve_funding_and_open_interest_disagreement() -> None:
    derivatives = load_artifact()["derivatives"]
    liqwall = derivatives["liqwall"]
    tradradar = derivatives["tradradar"]
    reconciliation = derivatives["reconciliation"]
    assert liqwall["liquidations_24h_usd"] == 30_100_000
    assert tradradar["liquidations_24h_min_usd"] == 30_440_000
    assert liqwall["long_liquidation_share_pct"] > 97
    assert tradradar["long_liquidation_share_pct"] > 98
    assert liqwall["open_interest_usd"] != tradradar["open_interest_usd"]
    assert liqwall["average_funding_percent_per_8h"] > 0
    assert tradradar["oi_weighted_funding_percent_per_8h"] < 0
    assert reconciliation["do_not_average"] is True
    assert reconciliation["independence"].find("overlap") >= 0


def test_cftc_positions_keep_contract_units_and_publication_dates() -> None:
    cftc = load_artifact()["cftc_futures_only"]
    assert cftc["data_as_of"] == "2026-11-03"
    assert cftc["updated_date"] == "2026-11-06"
    products = {item["cftc_code"]: item for item in cftc["products"]}
    assert products["176740"]["contract_multiplier_xrp"] == 50_000
    assert products["176740"]["open_interest_contracts"] == 7_216
    assert products["176740"]["weekly_change_contracts"] == -845
    assert products["176LM1"]["contract_multiplier_xrp"] == 500
    assert products["176LM1"]["open_interest_contracts"] == 32_505
    assert products["176LM1"]["weekly_change_contracts"] == -32_864
    assert products["176LM3"]["open_interest_contracts"] == 38_392
    assert products["176LM3"]["weekly_change_contracts"] == -465
    assert cftc["combined_coinbase_nano_products"]["decline_pct"] == 31.97
    assert "not XRP custody" in cftc["limitations"][2]


def test_etf_holdings_delta_is_not_primary_market_flow() -> None:
    etf = load_artifact()["etf_flow_reconciliation"]
    insights = etf["xrp_insights"]
    alpha = etf["alpha_finance"]
    cryptoetf = etf["cryptoetf_today"]
    assert insights["nov6_holdings_delta_xrp"] == -663_043
    assert "not issuer flow reports" in insights["method"]
    assert "BITW index rebalancing" in insights["known_non_creation_changes"]
    assert alpha["nov6_net_flow_usd"] == 0
    assert cryptoetf["nov6_net_flow_usd"] == 0
    assert alpha["cumulative_net_inflow_usd"] != cryptoetf["cumulative_net_inflow_usd"]
    assert alpha["last_30_sessions_usd"] != cryptoetf["last_30_trading_days_usd"]
    assert etf["disagreement"]["do_not_average"] is True


def test_regulatory_status_distinguishes_interpretation_anprm_and_proposal() -> None:
    regulatory = load_artifact()["regulatory"]
    sec = regulatory["sec_interpretation"]
    cftc = regulatory["cftc_anprm"]
    proposed = regulatory["sec_regulation_crypto_assets"]
    assert sec["xrp_named_as_digital_commodity"] is True
    assert "Howey remains" in sec["caveat"]
    assert cftc["status"].startswith("ADVANCED NOTICE")
    assert cftc["comment_deadline"] == "2026-12-14"
    assert "NOT FINAL" in cftc["status"]
    assert proposed["status"] == "PROPOSED RULE"
    assert proposed["final_rule_verified"] is False


def test_sbi_circle_arc_and_ripple_relationships_are_not_collapsed_into_xrp_demand() -> None:
    relationships = load_artifact()["institutional_relationships"]
    sbi = relationships["sbi_multi_rail"]
    arc = relationships["circle_arc"]
    assert sbi["circle"]["arc_validator"].find("founding validator") >= 0
    assert sbi["circle"]["arc_presale"].find("allocation undisclosed") >= 0
    assert sbi["arc_presale_disagreement"]["sbi_release_total_usd"] == 222_000_000
    assert sbi["arc_presale_disagreement"]["circle_q3_10q_gross_proceeds_usd"] == 242_200_000
    assert sbi["arc_presale_disagreement"]["difference_usd"] == 20_200_000
    assert arc["gas_asset"] == "USDC"
    assert "not XRPL validation or XRP ownership" in load_artifact()["normalized_excerpts"]["arc_validators"]
    assert relationships["ripple_partners"]["ripple_prime"].find("not XRP collateral") >= 0
    assert relationships["ripple_partners"]["bny"].find("No custody balances") >= 0


def test_circle_coinbase_financials_and_reserve_definitions_remain_separate() -> None:
    relationships = load_artifact()["institutional_relationships"]
    circle = relationships["circle_coinbase"]
    reserves = relationships["circle_reserves"]
    assert circle["coinbase_q3_2026_stablecoin_revenue_usd"] == 306_905_000
    assert circle["circle_q3_2026_distribution_cost_to_coinbase_usd"] == 331_300_000
    assert "not a simple profit split" in circle["relationship"]
    assert reserves["reserve_fund_share_pct"] == 84
    assert "Do not infer an overcollateralization ratio" in reserves["measurement_note"]
    assert "cannot be predicted" in reserves["rate_sensitivity"]


def test_goldman_13f_lead_is_secondary_long_etf_share_evidence() -> None:
    lead = load_artifact()["etf_flow_reconciliation"]["institutional_13f_lead"]
    assert lead["reported_xrp_etf_value_usd"] == 86_500_000
    assert lead["positions_usd"]["XRP"] == 25_800_000
    assert lead["positions_usd"]["XRPZ"] == 25_400_000
    assert lead["positions_usd"]["XRPC"] == 19_500_000
    assert lead["positions_usd"]["TOXR"] == 8_200_000
    assert lead["positions_usd"]["GXRP"] == 7_600_000
    assert "not parsed" in lead["limitation"]
    assert load_artifact()["model_admission"]["all_new_observations_model_eligible"] is False


def test_no_directional_forecast_is_issued() -> None:
    data = load_artifact()
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_probability"] is None
    assert data["model_admission"]["admitted_sources"] == []


def test_existing_evernorth_actual_capital_reconciliation_is_reused_not_duplicated() -> None:
    related = load_artifact()["related_existing_research"]
    assert related["owner_pr"] == 1643
    assert related["do_not_duplicate"] is True
    assert len(related["latest_artifacts"]) >= 8
    ledger = related["primary_filing_reconciliation"]
    assert ledger["cash_used_to_purchase_xrp_usd"] == 214_000_000
    assert ledger["xrp_purchased_with_advance_cash"] == 84_365_876
    assert ledger["in_kind_xrp_contributions_total"] == 388_910_554
    assert ledger["xrp_holdings_as_of_2026_10_09_approx"] == 473_000_000
    assert ledger["cantor_eloc"]["status"].startswith("optional")
    assert ledger["public_warrants"]["status"].startswith("potential only")
    assert ledger["sbi_ownership"]["class_c_voting_status"] == "non-voting"
    assert "not an issuer or SEC accounting term" in related["exact_phrase_resolution"]["actual_capital"]
