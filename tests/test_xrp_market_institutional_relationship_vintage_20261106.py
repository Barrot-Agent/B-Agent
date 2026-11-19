from decimal import Decimal
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T131500Z-xrp-market-institutional-relationship-vintage.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_spot_receipt_and_top_of_book_arithmetic():
    data = load_artifact()
    spot = data["market"]["spot"]
    bid = Decimal(spot["best_bid_usd"])
    ask = Decimal(spot["best_ask_usd"])
    mid = (bid + ask) / Decimal("2")
    spread = (ask - bid) / mid * Decimal("10000")
    assert abs(spread - Decimal(spot["spread_bps"])) < Decimal("0.000001")
    last = Decimal(spot["last_usd"])
    vwap = Decimal(spot["vwap_24h_usd"])
    open_price = Decimal(spot["utc_day_open_usd"])
    low = Decimal(spot["low_24h_usd"])
    assert abs((last / vwap - 1) * 100 - Decimal(spot["last_vs_vwap_pct"])) < Decimal("0.000001")
    assert abs((last / open_price - 1) * 100 - Decimal(spot["last_vs_open_pct"])) < Decimal("0.000001")
    assert abs((last / low - 1) * 100 - Decimal(spot["last_vs_low_pct"])) < Decimal("0.000001")
    assert spot["provider_event_time_utc"] is None
    assert "Top-of-book only" in spot["depth_scope"]
    receipt = next(x for x in data["source_registry"] if x["id"] == "kraken_xrp_usd_ticker")["receipt"]
    assert len(receipt["digest"]) == 64
    assert "not byte-complete HTTP wire bytes" in receipt["scope"]


def test_binance_perpetual_timestamp_basis_and_funding_units():
    perp = load_artifact()["market"]["derivatives"]["binance_xrpusdt"]
    assert perp["provider_event_time_utc"] == "2026-11-06T12:14:01Z"
    mark = Decimal(perp["mark_price_usdt"])
    index = Decimal(perp["index_price_usdt"])
    basis = (mark / index - 1) * Decimal("10000")
    assert abs(basis - Decimal(perp["mark_index_basis_bps"])) < Decimal("0.000001")
    assert Decimal(perp["last_funding_rate_fraction_per_8h"]) * 100 == Decimal(perp["funding_rate_percent_per_8h"])
    assert perp["next_funding_time_utc"] == "2026-11-06T16:00:00Z"


def test_derivatives_aggregators_keep_venue_universes_and_vintages_separate():
    derivatives = load_artifact()["market"]["derivatives"]
    trad = derivatives["trad_radar"]
    alpha = derivatives["alpha_finance"]
    assert trad["displayed_update_utc"] == "2026-11-06T10:35:00Z"
    assert trad["displayed_delay_minutes"] == 15
    assert trad["oi_exchange_count"] == 7
    assert trad["liquidation_account_sample_exchange_count"] == 5
    assert alpha["displayed_update_utc"] == "2026-11-06T07:48:00Z"
    assert derivatives["reconciliation"]["comparable_oi_total"] is False
    assert "Do not average" in derivatives["reconciliation"]["reason"]
    assert Decimal(trad["long_liquidations_usd"]) > Decimal(trad["short_liquidations_usd"])
    assert Decimal(alpha["long_liquidations_usd"]) > Decimal(alpha["short_liquidations_usd"])


def test_etf_holdings_flows_do_not_masquerade_as_comparable_cash_flows():
    flows = load_artifact()["market"]["etf_holdings_flows"]
    insights = flows["xrp_insights"]
    keyhole = flows["cryptokeyhole"]
    assert insights["window_start"] == "2026-11-02"
    assert insights["window_end"] == "2026-11-04"
    assert insights["holdings_delta_xrp"] == "-259701"
    assert "not direct authorized-participant cash" in insights["method"]
    assert keyhole["latest_complete_day"] == "2026-11-04"
    assert keyhole["complete_day_flow_xrp"] == "-3339"
    assert "Partial" in keyhole["november_5_status"]
    assert flows["reconciliation"]["comparable"] is False
    assert len(flows["reconciliation"]["excluded_sources"]) == 3


def test_coinbase_ripple_rlusd_distribution_is_live_but_collateral_is_planned():
    edge = next(
        x for x in load_artifact()["institutional_relationships"]["edges"]
        if x["from"] == "Ripple" and x["to"] == "Coinbase"
    )
    assert edge["status"] == "live_for_supported_regions_and_products"
    assert set(edge["live_scope"]["networks"]) == {"XRP Ledger", "Base", "Ethereum"}
    assert "RLUSD collateral eligibility for Coinbase Global Exchange customers" in edge["planned_not_live"]
    assert "Coinbase buying XRP" in edge["not_established"]
    assert "measured incremental XRP demand" in edge["not_established"]


def test_sbi_vc_trade_is_a_distribution_channel_not_rlusd_issuer():
    edges = load_artifact()["institutional_relationships"]["edges"]
    sbi = next(x for x in edges if x["from"] == "SBI VC Trade" and x["to"] == "Ripple / Standard Custody & Trust Company")
    assert sbi["status"] == "launched"
    assert sbi["issuer"] == "Standard Custody & Trust Company, LLC, a Ripple subsidiary; SBI VC Trade is distributor, not issuer."
    assert "BITPOINT service was excluded from the announcement" in sbi["exclusions"]
    assert "RLUSD adds another USD stablecoin rather than replacing USDC" in sbi["coexisting_product"]
    identity = load_artifact()["identity_research_status"]["japanese_sbic"]
    assert "distinct from SBI Holdings" in identity


def test_sbi_ripple_asia_and_evernorth_relationships_are_not_open_market_xrp_flow():
    edges = load_artifact()["institutional_relationships"]["edges"]
    poc = next(x for x in edges if x["from"] == "SBI Ripple Asia")
    assert poc["status"] == "existing JV"
    assert "production launch" in poc["not_established"]
    pipe = next(x for x in edges if x["from"] == "SBI Holdings" and x["to"] == "Evernorth Holdings")
    assert pipe["status"] == "investment disclosed"
    assert "open-market XRP purchase by SBI Holdings" in pipe["not_established"]


def test_coinbase_circle_usdc_relationship_continues_alongside_rlusd():
    edges = load_artifact()["institutional_relationships"]["edges"]
    circle = next(x for x in edges if x["from"] == "Coinbase" and x["to"] == "Circle")
    assert circle["status"] == "renewed_on_same_terms_in_Q3_2026"
    assert circle["economics"]["q3_2026_stablecoin_revenue_usd"] == "306905000"
    assert circle["economics"]["year_over_year_increase_from_higher_average_usdc_balances_usd"] == "84600000"
    assert circle["economics"]["year_over_year_decrease_from_lower_average_interest_rates_usd"] == "52800000"
    assert "exclusive distribution" in circle["not_established"]
    assert circle["economics"]["company_level_q3_2026_stablecoin_revenue_usd"] == "306905000"
    assert "not a Circle-only revenue figure" in circle["economics_scope_note"]
    circle_metrics = load_artifact()["institutional_relationships"]["circle_q3_2026"]
    assert circle_metrics["average_usdc_circulation_usd_billions"] == "73.3"
    assert circle_metrics["q3_usdc_onchain_transaction_volume_usd_trillions"] == "13.9"
    assert "not realized quarterly settlement volume" in circle_metrics["qualification"]


def test_occ_circle_ripple_and_coinbase_charter_statuses_are_distinct():
    statuses = {x["entity"]: x for x in load_artifact()["institutional_relationships"]["occ_charter_status"]}
    assert statuses["First National Digital Currency Bank, N.A. (Circle National Trust)"]["consummated_effective"] == "2026-07-24"
    assert statuses["Ripple National Trust Bank"]["consummated_effective"] == "2026-10-26"
    coinbase = statuses["Coinbase National Trust Company"]
    assert coinbase["approved"] == "2026-04-02"
    assert coinbase["consummated_effective"] is None
    assert coinbase["status"] == "approved_no_consummated_effective_date_in_retrieved_cas"


def test_rlusd_reserve_custody_and_collateral_roles_are_not_mislabeled_as_xrp():
    relationships = load_artifact()["institutional_relationships"]
    reserve = relationships["rlusd_transparency"]
    assert Decimal(reserve["reserve_minus_circulation_usd_millions"]) == Decimal("131.6")
    assert Decimal(reserve["reserve_over_circulation_pct"]) > Decimal("5")
    edges = relationships["edges"]
    sc = next(x for x in edges if x["from"] == "Ripple" and x["to"] == "Standard Chartered")
    assert sc["status"] == "custody_support_live"
    assert "RLUSD collateral integration with LMAX Group" in sc["planned_not_live"]
    bny = next(x for x in edges if x["from"] == "Ripple" and x["to"] == "BNY")
    assert "RLUSD reserve assets" in bny["reserve_custody_scope"]
    assert "supports XRP and RLUSD" in bny["digital_asset_custody_scope"]
    assert "XRP assets under custody or AUC balances" in bny["not_established"]


def test_macro_expectations_are_not_release_data_and_no_forecast_is_issued():
    data = load_artifact()
    jobs = data["macro"]["employment_situation"]
    assert jobs["scheduled_release_utc"] == "2026-11-06T13:30:00Z"
    assert jobs["status_at_snapshot"] == "upcoming_not_observed"
    assert jobs["reuters_survey_expectations"]["nonfarm_payroll_change"] == "65000"
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["forecast_status"]["shadow_forecast_issued"] is False
    assert data["forecast_status"]["paper_trade_executed"] is False
    assert data["forecast_status"]["real_money_action"] is False
    assert data["data_quality"]["model_eligibility"] is False

def test_circle_capital_and_payment_rail_strategy_is_not_mislabeled_as_xrp_demand():
    relationships = load_artifact()["institutional_relationships"]
    binance = next(x for x in relationships["edges"] if x["from"] == "Circle" and x["to"] == "Binance")
    assert binance["status"] == "announced"
    assert "$100 million equity investment" in binance["scope"]
    assert "XRP purchases" in binance["not_established"]
    tazapay = next(x for x in relationships["edges"] if x["from"] == "Circle" and x["to"] == "Tazapay")
    assert tazapay["status"] == "pending_close_expected_2027_subject_to_regulatory_approvals"
    assert "completed acquisition" in tazapay["not_established"]
    circle_strategy = relationships["circle_q3_2026"]["corporate_strategy"]
    assert circle_strategy["arc_mainnet_launch"] == "2026-09-16"
    assert circle_strategy["native_usdc_integration"] is True


def test_ripple_corporate_scale_claims_remain_issuer_reported_and_not_xrp_features():
    claims = load_artifact()["institutional_relationships"]["ripple_corporate_claims"]
    assert claims["reported_licenses"] == ">85"
    assert claims["reported_financial_institution_relationships"] == ">1700"
    assert claims["reported_2025_transactions_enabled_usd_trillions"] == ">16"
    assert "not independently audited" in claims["qualification"]
    robinhood = next(x for x in load_artifact()["institutional_relationships"]["edges"] if x["from"] == "Ripple" and x["to"] == "Robinhood")
    assert "RLUSD on XRPL for institutional settlement" in robinhood["announced_not_measured"]
    assert "measured RLUSD institutional settlement volume on XRPL" in robinhood["not_established"]

def test_bny_supports_xrp_and_rlusd_custody_but_discloses_no_xrp_auc():
    bny = next(x for x in load_artifact()["institutional_relationships"]["edges"] if x["from"] == "Ripple" and x["to"] == "BNY")
    assert bny["status"] == "xrp_and_rlusd_custody_support_announced_for_eligible_clients"
    assert "supports XRP and RLUSD" in bny["digital_asset_custody_scope"]
    assert "primary custodian of RLUSD reserve assets" in bny["reserve_custody_scope"]
    assert "XRP assets under custody or AUC balances" in bny["not_established"]
    assert "XRP collateral posted" in bny["not_established"]


def test_c2fo_instant_pay_is_announced_rlusd_settlement_not_production_flow():
    c2fo = next(x for x in load_artifact()["institutional_relationships"]["edges"] if x["from"] == "Ripple" and x["to"] == "C2FO")
    assert c2fo["status"] == "announced_waitlist_limited_rollout_not_production_volume"
    assert c2fo["settlement_asset"] == "RLUSD"
    assert c2fo["ledger"] == "XRP Ledger"
    assert "$525B" in c2fo["capital_context"]
    assert "not Instant Pay" in c2fo["capital_context"]
    assert "incremental XRP demand" in c2fo["not_established"]


def test_privy_xrpl_wallet_integration_is_not_payment_volume():
    privy = next(x for x in load_artifact()["institutional_relationships"]["edges"] if x["from"] == "Ripple" and x["to"] == "Privy (Stripe company)")
    assert privy["status"] == "developer_integration_announced"
    assert "XRP, RLUSD and other assets" in privy["scope"]
    assert "production transaction volume" in privy["not_established"]


def test_ripple_treasury_and_prime_strategy_are_separated_from_xrp_market_flows():
    relationships = load_artifact()["institutional_relationships"]
    treasury = relationships["ripple_treasury_strategy"]
    assert treasury["customer_claim"] == ">1000 customers across 160 countries"
    assert "tokenized money-market funds on XRPL" in treasury["product_24_7_returns"]["scope"]
    assert "XRP purchase volume" in treasury["product_24_7_returns"]["not_established"]
    prime = relationships["ripple_prime_strategy"]
    assert "Kalshi" in prime["named_relationships"]
    assert "not evidence of XRP-specific" in prime["qualification"]


def test_exact_phrase_identity_results_do_not_create_false_partnerships_or_video_inventory():
    identity = load_artifact()["identity_research_status"]
    assert "Permission Coin ASK token" in identity["ask_coin"]
    assert "No primary-source XRP relationship" in identity["ask_coin"]
    assert "public training activity" in identity["japanese_sbic"]
    assert "not an OpenAI partnership" in identity["japanese_sbic"]
    assert "No new YouTube videos added" in identity["camilla_kamilah_stevenson"]
    ids = {x["id"] for x in load_artifact()["source_registry"]}
    assert {"sbic_tokyo_chatgpt_training","ask_coin_exchange_profile","permission_coin_ask_token","ripple_2026_year_in_review","bny_ripple_xrp_rlusd_custody","c2fo_instant_pay","privy_xrpl_wallets"} <= ids
