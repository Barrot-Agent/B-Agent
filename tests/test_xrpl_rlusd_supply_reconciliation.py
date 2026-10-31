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


def test_sbic_identity_is_not_conflated_with_sbi_holdings_or_xrp():
    snapshot = _load("snapshots/20261031T183000Z-sbic-sbi-rlusd-etf-flow-conflict.json")
    identity = snapshot["sbic_identity"]
    assert identity["legal_name"] == "Tokyo Small and Medium Business Investment & Consultation Co., Ltd."
    assert identity["public_name"] == "SBIC East Japan"
    assert identity["distinction"]["relationship_to_sbi_holdings"].startswith("NO_AFFILIATION")
    assert identity["distinction"]["relationship_to_xrp"] == "NO_DIRECT_XRP_OR_RIPPLE_RELATIONSHIP_ESTABLISHED"
    assert identity["chatgpt_context"]["speaker_affiliation"] == "Microsoft Japan executive evangelist"


def test_sbi_vc_trade_rlusd_listing_is_distribution_not_xrp_capital_flow():
    snapshot = _load("snapshots/20261031T183000Z-sbic-sbi-rlusd-etf-flow-conflict.json")
    sbi = snapshot["sbi_group_xrp_and_rlusd"]
    assert sbi["sbi_vc_trade_relationship"] == "SBI Holdings consolidated subsidiary"
    assert sbi["rlusd_japan_distribution"]["start_date"] == "2026-06-24"
    assert sbi["rlusd_japan_distribution"]["actual_rlusd_volume"] == "NOT_DISCLOSED"
    assert sbi["rlusd_japan_distribution"]["xrp_purchase_or_collateral_flow"] == "NOT_ESTABLISHED"
    assert sbi["visa_rewards_card"]["reward_assets"] == ["BTC", "ETH", "XRP"]
    assert sbi["visa_rewards_card"]["xrp_reward_inventory_source"] == "UNKNOWN"


def test_xrp_etf_provider_conflict_blocks_directional_feature_admission():
    snapshot = _load("snapshots/20261031T183000Z-sbic-sbi-rlusd-etf-flow-conflict.json")
    flows = snapshot["xrp_etf_flow_observations"]
    totals = {item["provider"]: item["reported_total_usd"] for item in flows["observations"]}
    assert totals["CryptoETF.today"] == 200000
    assert totals["Maketo"] == -496500
    assert totals["CryptoKeyhole"] == -1412000
    assert len(flows["material_conflicts"]) >= 4
    assert flows["source_independence"].startswith("All three are secondary aggregators")
    assert flows["admission"] == "NOT_ADMITTED_TO_DIRECTIONAL_MODEL"
    graph = _load("relationship_graph_addenda/20261031T183000Z-sbic-sbi-rlusd-etf-flow-conflict.json")
    ids = {item["id"] for item in graph["hypotheses"]}
    assert {"H-SBIC-NAME-COLLISION", "H-SBI-RLUSD-DISTRIBUTION", "H-ETF-FLOW-SESSION-ALIGNMENT", "H-ETF-FLOW-UNIVERSE"} <= ids
    bundle = _load("sources/20261031T183000Z-sbic-sbi-etf-flow-source-bundle.json")
    source_ids = {item["source_id"] for item in bundle["sources"]}
    assert set(snapshot["source_ids"]) <= source_ids
    assert set(graph["source_ids"]) <= source_ids
    assert snapshot["prediction"]["forecast_status"] == "NOT_ISSUED"
    assert snapshot["prediction"]["directional_features_admitted"] == []


def test_japanese_sbic_candidates_are_distinct_and_chatgpt_event_is_not_sbi_capital():
    snapshot = _load("snapshots/20261031T183925Z-sbic-candidates-and-xrp-derivatives-oi-conflict.json")
    candidates = {item["id"]: item for item in snapshot["sbic_candidates"]}
    assert candidates["TOKYO_SBIC_EAST_JAPAN"]["legal_name"] == "Tokyo Small and Medium Business Investment & Consultation Co., Ltd."
    historical = candidates["SBI_CAPITAL_CO_LTD_HISTORICAL_SBIC"]
    assert "SBIC in SBI Holdings' 2007 release" == historical["abbreviation"]
    assert historical["ownership_timeline"][1]["status"] == "SBI release describes 60% SBI Holdings / 40% Goldman Sachs group ownership"
    assert historical["ownership_timeline"][2]["status"].startswith("SBI's 2012 restructuring release lists SBI Capital Co., Ltd. as 100%")
    assert "exact transaction/date" in historical["unresolved"]
    assert snapshot["sbic_resolution"]["best_supported_context"].startswith("Tokyo SBIC East Japan")
    assert snapshot["sbic_resolution"]["no_openai_partnership_established"] is True
    graph = _load("relationship_graph_addenda/20261031T183925Z-sbic-candidates-and-xrp-derivatives-oi-conflict.json")
    edge_types = {(e["from"], e["to"], e["type"], e["status"]) for e in graph["edges"]}
    assert ("TOKYO_SBIC_EAST_JAPAN", "CHATGPT", "hosted_educational_seminar_and_training", "CONFIRMED") in edge_types
    assert ("SBI_CAPITAL_JP_HISTORICAL", "XRP", "investment_or_commercial_relationship", "NOT_ESTABLISHED") in edge_types


def test_xrp_open_interest_provider_disagreement_is_not_averaged_or_admitted():
    snapshot = _load("snapshots/20261031T183925Z-sbic-candidates-and-xrp-derivatives-oi-conflict.json")
    oi = snapshot["derivatives_open_interest"]
    values = [item["open_interest_usd"] for item in oi["observations"]]
    assert min(values) == 738990000
    assert max(values) == 1860000000
    assert oi["max_to_min_ratio"] > 2.5
    assert oi["same_venue_disagreement"]["bybit"]["tradradar_usd"] > 2 * oi["same_venue_disagreement"]["bybit"]["kodexius_usd"]
    assert oi["source_independence"].startswith("All are secondary aggregators")
    assert oi["admission"] == "NOT_ADMITTED_TO_DIRECTIONAL_MODEL"
    assert snapshot["prediction"]["forecast_status"] == "NOT_ISSUED"
    graph = _load("relationship_graph_addenda/20261031T183925Z-sbic-candidates-and-xrp-derivatives-oi-conflict.json")
    assert "H-XRP-OI-UNIVERSE-MISMATCH" in {h["id"] for h in graph["hypotheses"]}
    bundle = _load("sources/20261031T183925Z-sbic-candidates-and-xrp-derivatives-source-bundle.json")
    assert set(snapshot["source_ids"]) <= {s["source_id"] for s in bundle["sources"]}
