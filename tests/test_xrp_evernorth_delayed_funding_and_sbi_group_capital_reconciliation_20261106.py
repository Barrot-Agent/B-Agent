from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106-evernorth-delayed-funding-and-sbi-group-capital-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_delayed_funding_share_count_correction_is_not_new_capital():
    data = load_artifact()
    correction = data["delayed_funding_correction"]
    assert correction["prior_reported_class_a_shares"] == 663510
    assert correction["eight_k_reported_class_a_shares"] == 1078613
    assert correction["issuer_press_release_reported_class_a_shares"] == 1078614
    assert correction["one_share_difference"] == 1
    assert "Unresolved one-share discrepancy" in correction["reconciliation_status"]
    assert correction["increase_in_8k_reported_shares"] == 415103
    assert correction["increase_in_press_release_reported_shares"] == 415104
    assert correction["correction_reason"].startswith("Clerical error")
    assert correction["not_new_capital_event"] is True


def test_delayed_subscription_separates_cash_from_xrp_in_kind():
    item = load_artifact()["delayed_subscriber_consideration"]
    assert item["cash_usd"] == 10_500_000
    assert item["in_kind_xrp"] == 200_000
    assert item["implied_in_kind_xrp_value_usd"] == 286_138
    assert item["combined_indicative_consideration_usd"] == 10_786_138
    assert item["eight_k_shares_times_price_usd"] == 10_786_130
    assert item["press_release_shares_times_price_usd"] == 10_786_140
    assert item["eight_k_arithmetic_difference_usd"] == 8
    assert item["press_release_arithmetic_difference_usd"] == -2
    assert item["possible_overlap_with_private_placement_aggregates"] is True
    assert item["additive_to_private_placement_totals"] is False
    assert "not a claim that the subscription was entirely cash" in item["arithmetic_interpretation"]


def test_sbi_group_is_four_sbi_controlled_entities_not_sbic():
    data = load_artifact()["sbi_group"]
    assert data["issuer_definition"] == "The S-1 explicitly defines SBI as SBI Holdings, Inc."
    assert "SBI Venture Fund 2023A Investment LPS" in data["stockholder_group_definition"]
    assert "SBI Venture Fund 2023B Investment LPS" in data["stockholder_group_definition"]
    assert "SBI PE Holdings Co., Ltd." in data["stockholder_group_definition"]
    assert "SBI Holdings USA, Inc." in data["stockholder_group_definition"]
    assert data["class_a_shares"] == 9_431_914
    assert data["class_c_shares"] == 2_359_038
    assert data["common_stock_percentage"] == 21.4
    assert data["voting_power_percentage"] == 39.9
    assert "SBIC East" in data["not_the_same_as"]
    s1 = next(x for x in load_artifact()["source_registry"] if x["id"] == "evernorth_s1_2026_10_30")
    assert "normalized table extraction" in s1["hash_scope"]
    assert "None of these hashes is a raw SEC filing-byte hash" in s1["hash_scope"]


def test_cash_and_in_kind_categories_are_not_double_counted():
    items = {x["category"]: x for x in load_artifact()["separate_capital_categories"]}
    assert items["delayed_subscriber_cash"]["amount_usd"] == 10_500_000
    assert items["delayed_subscriber_cash"]["do_not_add_to_aggregate_totals"] is True
    assert items["delayed_subscriber_in_kind_xrp"]["amount_xrp"] == 200_000
    assert items["delayed_subscriber_in_kind_xrp"]["do_not_add_to_aggregate_totals"] is True
    assert items["prior_cash_xrp_purchase"]["amount_usd"] == 214_100_000
    assert items["prior_cash_xrp_purchase"]["amount_xrp"] == 84_365_876
    assert items["pubco_private_placement_xrp"]["amount_xrp"] == 261_919_096
    assert items["pathfinder_contribution_agreement_xrp"]["amount_xrp"] == 126_791_458
    assert items["delayed_subscriber_in_kind_xrp"]["amount_xrp"] == 200_000
    assert "do not sum independently" in items["delayed_subscriber_in_kind_xrp"]["status"]
    assert items["related_party_company_credit_facility"]["drawn_as_of_2026_10_07_usd"] == 9_700_000
    assert items["related_party_company_credit_facility"]["facility_limit_usd"] == 10_000_000
    liquidity = load_artifact()["preclosing_liquidity_snapshot"]
    assert liquidity["date"] == "2026-06-30"
    assert liquidity["evernorth_unrestricted_cash_usd"] == 100_000
    assert liquidity["evernorth_net_working_capital_deficit_usd"] == 696_100_000
    assert "Not a current post-close" in liquidity["status"]
    holdings = load_artifact()["holdings_reconciliation"]
    assert holdings["arithmetic_sum_xrp"] == 473_076_430
    assert "do not add it again" in holdings["caveat"]
    assert items["convertible_notes"]["amount_usd"] == 30_000_000
    assert items["cantor_affiliate_committed_equity_facility"]["status"].startswith("committed equity facility estimate")
    assert items["cash_exercisable_public_warrants"]["status"].startswith("contingent")
    assert load_artifact()["evidence_quality"]["model_price_feature_eligible"] is False
    assert load_artifact()["forecast_status"]["directional_forecast_issued"] is False


def test_coinbase_personnel_link_is_not_a_corporate_contract():
    data = load_artifact()
    link = data["personnel_links"][0]
    assert link["person"] == "Hugo Jeandesboz"
    assert link["new_role"] == "Chief Investment Officer, Evernorth Holdings Inc."
    assert "Co-Chief Investment Officer, Coinbase Asset Management" in link["prior_coinbase_roles"]
    assert "Previously Coinbase lead derivatives trader" in link["prior_coinbase_roles"]
    assert "trading counterparties and custodians" in " ".join(link["evernorth_responsibilities"])
    assert "does not establish a Coinbase Global custody mandate" in link["corporate_relationship_limit"]
    assert data["evidence_quality"]["coinbase_link_is_personnel_not_corporate_contract"] is True
