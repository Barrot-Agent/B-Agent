from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261107T020636Z-xrp-binance-outflow-soter-institutional-insurance-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_normalized_source_receipts_are_content_addressed():
    data = load_artifact()
    sources = {item["id"]: item for item in data["sources"]}
    assert len(sources) == 10
    for source in sources.values():
        excerpt = source["normalized_excerpt"]
        encoded = excerpt.encode("utf-8")
        assert len(encoded) == source["receipt_bytes"]
        assert hashlib.sha256(encoded).hexdigest() == source["receipt_sha256"]
        assert source["receipt_hash_scope"].startswith("SHA-256 of the exact UTF-8 normalized excerpt")


def test_binance_outflow_is_not_conflated_with_the_october_29_theft():
    flow = load_artifact()["observations"]["binance_xrp_exchange_outflow"]
    assert flow["event_date_utc"] == "2026-11-04"
    assert flow["reported_xrp_outflow"] == 418_500_000
    assert flow["reported_prior_comparison"]["reported_xrp_outflow"] == 315_000_000
    theft = flow["october_29_security_incident"]
    assert theft["reported_xrp_stolen_from_five_hot_wallets"] == 233_460_000
    assert theft["not_equivalent_to_cryptoquant_exchange_outflow_metric"] is True
    assert theft["difference_from_cryptoquant_october_29_outflow_not_decomposed"] is True
    assert flow["wallet_level_transfer_list_captured"] is False
    assert flow["internal_exchange_transfer_caveat"] is True
    assert flow["exchange_reserve_change_independently_verified"] is False


def test_withdrawal_reopening_and_all_asset_flows_are_context_not_causation():
    flow = load_artifact()["observations"]["binance_xrp_exchange_outflow"]
    reopen = flow["withdrawal_reopening_context"]
    assert reopen["binance_announced_phased_withdrawal_reopening_date"] == "2026-11-01"
    assert reopen["xrp_in_first_phase"] is True
    assert "not a proven cause" in reopen["temporal_relation"]
    aggregate = flow["all_asset_flow_context"]
    assert aggregate["reported_customer_net_withdrawals_usd"] == 3_640_000_000
    assert aggregate["scope"] == "All assets, not XRP-specific."
    assert aggregate["binance_disputed_higher_aggregator_total_due_to_own_hot_wallet_deposits"] is True


def test_soter_relationships_are_group_level_and_not_xrp_demand():
    soter = load_artifact()["observations"]["soter_institutional_insurance_network"]
    assert soter["second_close_strategic_investors"] == ["SC Ventures", "SBI Group"]
    assert soter["first_close_investors"] == ["Coinbase Ventures", "Franklin Templeton", "Brevan Howard Digital"]
    assert soter["exact_legal_sbi_investing_entity_disclosed"] is False
    assert soter["sbi_group_equivalent_to_sbi_holdings_verified"] is False
    assert soter["coinbase_ventures_is_operating_exchange_partnership"] is False
    assert soter["investor_specific_amounts_disclosed"] is False
    assert soter["product_scope"]["xrp_or_xrpl_specific_policy_evidence_found"] is False
    assert soter["xrp_network_relationships"]["ripple_relationship_evidenced"] is False
    assert soter["xrp_network_relationships"]["circle_relationship_evidenced"] is False
    policy = soter["product_scope"]["unnamed_tier1_exchange_btc_policy"]
    assert policy["insured_exchange_identity_disclosed"] is False
    assert policy["do_not_infer_binance_or_coinbase"] is True
    assert policy["announced_before_binance_2026_10_29_incident"] is True


def test_source_independence_and_secondary_claims_are_preserved():
    data = load_artifact()
    independence = data["source_independence"]
    assert "not independent corroboration" in independence["cryptoquant_outflow_claim"]
    assert "aggregate all-asset flow" in independence["binance_withdrawal_context"]
    assert "not the same metric" in independence["october_29_theft"]
    assert "does not establish investor allocations" in independence["soter_investor_network"]
    soter = data["observations"]["soter_institutional_insurance_network"]
    assert soter["secondary_total_funding_report"]["status"] == "SECONDARY_REPORTED_NOT_PRIMARY_CORROBORATED"
    assert soter["insurance_capacity_secondary_report"]["status"].startswith("SECONDARY_REPORT")


def test_snapshot_is_not_model_eligible_and_issues_no_forecast_or_action():
    data = load_artifact()
    assert data["model_eligibility"]["admitted_to_point_in_time_feature_store"] is False
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["directional_forecast_issued"] is False
    assert data["predictions"]["shadow_forecast_issued"] is False
    assert data["actions"]["paper_trade"] is False
    assert data["actions"]["real_money_action"] is False
    assert data["actions"]["deployment"] is False
    assert data["actions"]["secret_rotation"] is False
    assert data["actions"]["space_restart"] is False
    assert data["actions"]["kaggle_submission"] is False
