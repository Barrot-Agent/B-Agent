from __future__ import annotations

import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T003500Z-c2fo-instant-pay-bny-rlusd-and-xrp-market-addendum.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_c2fo_instant_pay_uses_rlusd_on_xrpl_and_does_not_claim_xrp_bridge_volume():
    item = load_artifact()["institutional_rails"]["c2fo_ripple_instant_pay"]
    assert item["network"] == "XRP Ledger"
    assert item["settlement_asset"] == "RLUSD"
    assert item["funding"] == "Participating capital providers"
    assert item["instant_pay_volume_usd"] is None
    assert item["xrp_bridge_asset_usage"] == "Not disclosed; the announced settlement asset is RLUSD."


def test_c2fo_525_billion_is_existing_early_pay_not_instant_pay_volume():
    item = load_artifact()["institutional_rails"]["c2fo_ripple_instant_pay"]
    assert item["historical_early_pay_working_capital_access_usd"] == "more than 525 billion"
    assert item["historical_early_pay_is_not_instant_pay_volume"] is True
    assert "Early Pay" in item["historical_volume_scope"]
    assert "waitlist" in item["status"].lower()


def test_bny_custody_and_future_functions_are_separated():
    item = load_artifact()["institutional_rails"]["bny_ripple_custody_and_trade_finance"]
    assert item["current_platform_support"] == ["XRP", "RLUSD"]
    assert item["primary_rlusd_reserve_custodian"] is True
    assert "subject to final BNY" in item["direct_rlusd_mint_redeem"]
    assert "Exploratory" in item["tokenized_trade_finance_with_c2fo"]
    assert item["xrp_assets_under_custody_usd"] is None
    assert item["xrp_collateral_acceptance_terms"] is None


def test_coinbase_rlusd_distribution_is_not_xrp_purchase_evidence():
    item = load_artifact()["institutional_rails"]["coinbase_rlusd_distribution"]
    assert item["availability"] == "Retail and institutional Coinbase platforms"
    assert item["issuer"] == "Ripple affiliate Standard Custody & Trust Company"
    assert item["xrp_purchase_or_bridge_volume"] is None


def test_evernorth_cash_in_kind_debt_and_sbi_ownership_remain_distinct():
    item = load_artifact()["evernorth_actual_capital_reconciliation"]
    assert item["advance_funding_cash_usd"] == 214_050_000
    assert item["xrp_purchased_with_advance_funding_cash"] == 84_365_876
    assert item["in_kind_xrp_contributions_total"] == 388_910_554.061435
    assert item["gross_cash_proceeds_before_transaction_expenses_usd"] == 272_600_000
    assert item["separate_convertible_notes_usd"] == 30_000_000
    assert item["convertible_notes_deployment_to_xrp_verified"] is False
    assert item["sbi_ownership_at_closing"]["outstanding_pubco_common_stock_percent"] == 21.4
    assert item["sbi_ownership_at_closing"]["voting_power_percent"] == 39.9
    assert item["sbi_ownership_at_closing"]["exact_sbi_cash_subscription_usd"] is None


def test_kraken_spot_snapshot_arithmetic_is_consistent_and_model_ineligible():
    item = load_artifact()["spot_market"]
    assert math.isclose(
        item["displayed_spread_bps"],
        (item["best_ask_usd"] - item["best_bid_usd"])
        / ((item["best_ask_usd"] + item["best_bid_usd"]) / 2)
        * 10_000,
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert item["rolling_24h_volume_xrp"] > 40_000_000
    assert math.isclose(item["last_vs_utc_day_open_percent"], 0.707490440999603, abs_tol=1e-12)
    assert math.isclose(item["last_vs_rolling_24h_vwap_percent"], -3.5745024078618903, abs_tol=1e-12)
    artifact = load_artifact()
    assert artifact["model_eligible"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"


def test_macro_geopolitical_context_is_not_asserted_as_xrp_causality():
    item = load_artifact()["macro_context"]
    assert item["event_date"] == "2026-11-05"
    assert item["brent_daily_change_percent"] == 3.88
    assert "No causal XRP effect is established" in item["interpretation"]


def test_source_provenance_and_independence_groups_are_explicit():
    artifact = load_artifact()
    sources = {item["source_id"]: item for item in artifact["source_records"]}
    assert sources["EVERNORTH_SEC_FILING_20261030"]["publisher"] == "U.S. Securities and Exchange Commission"
    assert sources["BNY_RIPPLE_CUSTODY_TRADE_FINANCE_20261027"]["independence_group"] == "bny_ripple_joint_announcement"
    assert sources["C2FO_RIPPLE_INSTANT_PAY_20261027"]["independence_group"] == "c2fo_ripple_joint_announcement"
    assert "not independent corroboration" in artifact["source_independence_note"]

def test_sbi_controlled_subscribers_and_ripple_in_kind_contribution_are_not_cash_purchases():
    item = load_artifact()["evernorth_actual_capital_reconciliation"]
    assert item["sbi_group_entities"] == [
        "SBI Venture Fund 2023A Investment LPS",
        "SBI Venture Fund 2023B Investment LPS",
        "SBI PE Holdings Co., Ltd.",
        "SBI Holdings USA, Inc.",
    ]
    sbi = item["sbi_subscription_details"]
    assert sbi["controlling_parent"] == "SBI Holdings, Inc."
    assert sbi["entities_controlled_by_sbi_holdings"] is True
    assert sbi["ownership_at_closing"]["percent_outstanding_pubco_common_stock"] == 21.4
    assert sbi["ownership_at_closing"]["percent_voting_power"] == 39.9
    assert sbi["cash_amount_attributable_to_sbi_usd"] is None
    assert "Do not attribute the entire $214.05M" in sbi["interpretation"]

    ripple = item["ripple_in_kind_contribution"]
    assert ripple["xrp_contributed"] == 126_791_458
    assert ripple["cash_purchase"] is False
    assert ripple["consideration"].startswith("30,000,000 Pathfinder Company Units")
