import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "xrp_intelligence"


def _load(relative):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_rlusd_chain_supply_and_coinbase_network_scope_are_explicit():
    snapshot = _load("snapshots/20261031T180340Z-coinbase-rlusd-xrpl-supply-revision.json")
    graph = _load("relationship_graph_addenda/20261031T180340Z-coinbase-rlusd-xrpl-supply-graph.json")
    bundle = _load("sources/20261031T180340Z-coinbase-rlusd-xrpl-supply-source-bundle.json")
    assert snapshot["rlusd_supply"]["current_xrpl_supply_usd"] == 707358109.94
    assert snapshot["rlusd_supply"]["derived_daily_change_usd"] == -274401890.06
    rolling = snapshot["rlusd_supply"]["rolling_24h_observation"]
    assert rolling["xrpl_net_supply_change_usd"] + rolling["ethereum_net_supply_change_usd"] == rolling["combined_ethereum_xrpl_net_change_usd"]
    assert snapshot["coinbase_ripple_distribution"]["supported_deposit_withdrawal_networks"] == ["XRPL", "Base", "Ethereum"]
    assert snapshot["rlusd_supply"]["chain_scope"]["base"].startswith("EXCLUDED")
    source_ids = {source["source_id"] for source in bundle["sources"]}
    assert set(snapshot["source_ids"]) <= source_ids
    assert set(graph["source_ids"]) <= source_ids
    assert snapshot["prediction"]["forecast_status"] == "NOT_ISSUED"
    assert snapshot["prediction"]["directional_features_admitted"] == []


def test_exchange_wallets_are_not_tradable_float_and_revision_is_preserved():
    snapshot = _load("snapshots/20261031T180340Z-coinbase-rlusd-xrpl-supply-revision.json")
    exchange = snapshot["xrp_exchange_balances"]
    assert exchange["total_xrp"] == 22480000000
    assert exchange["same_wallet_change_7d_xrp"] == -133000000
    assert exchange["same_wallet_change_30d_xrp"] == -12300000
    assert exchange["non_customer_reserve_operational_xrp"] == 487200000
    assert exchange["previous_capture_conflict"]["status"] == "MATERIAL_PROVIDER_DISPLAY_REVISION; PRESERVE_BOTH_CAPTURES; CAUSE_UNKNOWN"
    assert exchange["semantics"] == "ATTRIBUTED_CUSTODY_WALLETS_NOT_TRADABLE_FLOAT"


def test_graph_retains_competing_rlusd_causality_hypotheses():
    graph = _load("relationship_graph_addenda/20261031T180340Z-coinbase-rlusd-xrpl-supply-graph.json")
    ids = {item["id"] for item in graph["hypotheses"]}
    assert {"H-RLUSD-CHAIN-MIGRATION", "H-RLUSD-REDEMPTION", "H-RLUSD-PROVIDER-SCOPE", "H-XRP-PRICE-CAUSALITY"} <= ids
    price = next(item for item in graph["hypotheses"] if item["id"] == "H-XRP-PRICE-CAUSALITY")
    assert price["status"] == "UNSUPPORTED_NO_FEATURE_ADMISSION"



def test_occ_charter_effective_status_is_separate_from_operational_launch():
    snapshot = _load("snapshots/20261031T181303Z-xrp-institutional-custody-trade-finance.json")
    regulatory = snapshot["regulatory_status"]
    ripple = regulatory["ripple_national_trust_bank"]
    circle = regulatory["circle_national_trust"]
    assert ripple["occ_cas_status"] == "CONSUMMATED_EFFECTIVE"
    assert ripple["effective_date"] == "2026-10-26"
    assert ripple["rlusd_issuer"] == "Standard Custody & Trust Company (NYDFS-regulated limited-purpose trust company)"
    assert ripple["opening_and_live_operations"] == "NOT_VERIFIED"
    assert circle["occ_cas_status"] == "CONSUMMATED_EFFECTIVE"
    assert circle["effective_date"] == "2026-07-24"
    assert circle["usdc_reserve_management"] == "PLANNED_FUTURE_CAPABILITY_NOT_CONFIRMED_LIVE"


def test_bny_custody_and_c2fo_capital_are_not_misclassified_as_xrp_buying():
    snapshot = _load("snapshots/20261031T181303Z-xrp-institutional-custody-trade-finance.json")
    assert snapshot["bny_custody_and_trade_finance"]["xrp_custody_platform_support"] == "CONFIRMED_BY_BNY_COMPANY_STATEMENT"
    assert snapshot["bny_custody_and_trade_finance"]["direct_bny_rlusd_mint_redeem"].startswith("INTENDED_FUTURE")
    c2fo = snapshot["c2fo_instant_pay"]
    assert c2fo["product_status"] == "WAITLIST_ANNOUNCED"
    assert c2fo["historical_c2fo_early_pay_working_capital_access_usd_lower_bound"] == 520000000000 and c2fo["historical_c2fo_early_pay_working_capital_access_comparison"] == "GREATER_THAN"
    assert c2fo["historical_520b_scope"].startswith("EXISTING_C2FO_EARLY_PAY_PROGRAMS")
    assert c2fo["actual_xrpl_funded_invoice_volume"] == "NOT_DISCLOSED"


def test_launched_tokenized_fund_is_distinguished_from_future_collateral_and_pilot_use():
    snapshot = _load("snapshots/20261031T181303Z-xrp-institutional-custody-trade-finance.json")
    products = snapshot["tokenized_fund_and_euro_stablecoin"]
    assert products["aviva_usd_liquidity_fund_share_class"]["status"] == "LAUNCHED"
    assert products["aviva_usd_liquidity_fund_share_class"]["tokenized_share_class_aum"] == "NOT_DISCLOSED"
    assert products["sg_forge_eur_coinvertible"]["trading_collateral_use"] == "OPPORTUNITY_TO_EXPLORE_NOT_CONFIRMED_LIVE"
    assert snapshot["card_settlement"]["mastercard_webbank_gemini_rlusd"]["status"].startswith("EXPLORATORY")
    assert snapshot["prediction"]["directional_features_admitted"] == []



def test_coinbase_national_trust_is_conditional_and_custody_migration_is_prospective():
    snapshot = _load("snapshots/20261031T181303Z-xrp-institutional-custody-trade-finance.json")
    coinbase = snapshot["regulatory_status"]["coinbase_national_trust"]
    assert coinbase["approval_status"] == "PRELIMINARY_CONDITIONAL_APPROVAL_ONLY"
    assert coinbase["final_approval_and_authorization_to_commence_business"].startswith("NOT_GRANTED")
    assert coinbase["current_custody_provider"] == "Coinbase Custody Trust Company LLC (NYDFS limited-purpose trust company)"
    assert coinbase["operational_opening"] == "NOT_VERIFIED"
    assert "over a three-year" in coinbase["planned_migration"]
    assert coinbase["insured_deposit_taking"] == "NOT_AUTHORIZED"



def test_coinbase_xrp_products_keep_collateral_and_derivatives_risk_models_separate():
    snapshot = _load("snapshots/20261031T181303Z-xrp-institutional-custody-trade-finance.json")
    cb = snapshot["coinbase_tactical_position"]
    assert cb["borrow"]["maximum_borrow_usdc"] == 100000
    assert cb["borrow"]["protocol"] == "Morpho Blue on Base"
    assert cb["borrow"]["xrp_specific_initial_ltv"] == "NOT_PUBLISHED_ON_CURRENT_COINBASE_PRODUCT_PAGE"
    assert cb["global_exchange_cross_collateral"]["xrp_accepted"] is True
    assert cb["global_exchange_cross_collateral"]["xrp_specific_haircut"] == "NOT_DISCLOSED"
    assert cb["xrp_perpetual_futures"]["settlement_asset"] == "USDC"
    assert cb["xrp_perpetual_futures"]["physical_xrp_delivery"] is False
    assert cb["cbxrp_reserve"]["status"].startswith("MATERIAL_RENDER_DATE_CONFLICT")
    assert cb["morpho_cbXRP_usdc_market"]["max_ltv_pct"] == 62.5
