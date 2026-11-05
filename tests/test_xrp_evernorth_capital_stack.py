from __future__ import annotations

import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261105T041445Z-evernorth-capital-stack-primary-source-reconciliation.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_evernorth_capital_stack_separates_actual_proceeds_from_capacity() -> None:
    data = _artifact()
    events = {item["id"]: item for item in data["capital_events"]}
    capacities = {item["id"]: item for item in data["optional_financing_capacity"]}

    assert events["advance_funding_subscriptions"]["cash_usd"] == 214_049_995
    assert events["advance_funding_subscriptions"]["cash_usd_rounded_in_prospectus"] == 214_050_000
    assert events["advance_funding_subscriptions"]["cash_used_for_xrp_purchase_usd"] == 214_000_000
    assert events["advance_funding_subscriptions"]["cash_difference_usd"] == 49_995
    assert events["delayed_funding_subscriptions"]["cash_usd"] == 10_500_000
    assert events["convertible_pik_note"]["principal_usd"] == 30_000_000
    assert events["convertible_pik_note"]["net_cash_proceeds_usd"] == 29_000_000
    assert capacities["cantor_committed_equity_facility"]["maximum_gross_proceeds_usd"] == 76_800_000
    assert capacities["cantor_committed_equity_facility"]["actual_draw_amount_usd"] is None
    assert capacities["public_warrant_cash_exercise"]["maximum_gross_cash_if_all_exercised_usd"] == 132_249_908
    assert capacities["public_warrant_cash_exercise"]["actual_exercises_usd"] is None


def test_evernorth_xrp_contributions_are_not_mislabeled_as_spot_purchases() -> None:
    data = _artifact()
    events = {item["id"]: item for item in data["capital_events"]}

    assert events["cash_funded_xrp_purchase"]["classification"] == "issuer_reported_xrp_purchase_using_subscription_cash"
    assert events["series_c_rippleworks_arrington"]["classification"] == "in_kind_xrp_subscription_not_spot_purchase"
    assert events["ripple_direct_contribution"]["classification"] == "in_kind_xrp_contribution_not_spot_purchase"
    assert events["ripple_affiliated_trust_contribution"]["classification"] == "related_party_in_kind_xrp_subscription_not_spot_purchase"
    assert events["cash_funded_xrp_purchase"]["xrp_purchased"] == 84_365_876.3625
    assert events["cash_funded_xrp_purchase"]["cash_used_for_purchase_usd"] == 214_000_000
    assert events["cash_funded_xrp_purchase"]["average_price_usd"] == 2.53657058
    assert events["cash_funded_xrp_purchase"]["execution_venue_status"] == "not disclosed"
    assert data["reported_xrp_position_context"]["includes_cash_funded_purchase_xrp"] == 84_365_876.3625


def test_sbi_economic_ownership_is_distinct_from_voting_power() -> None:
    sbi = _artifact()["ownership_and_relationships"]["sbi_holdings"]

    assert sbi["percent_of_total_pubco_common_stock_at_close"] == 21.4
    assert sbi["voting_power_percent_at_close"] == 39.9
    assert sbi["class_c_shares"] == 2_359_038


def test_coinbase_and_circle_relationships_are_not_overstated() -> None:
    relationships = _artifact()["ownership_and_relationships"]

    assert relationships["coinbase"]["relationship"] == "named as the principal market for XRP financial-reporting purposes based on trading activity, price consistency and compliance assessment"
    assert relationships["coinbase"]["direct_execution_or_custody_contract_established_by_this_filing"] is False
    assert relationships["coinbase"]["custodian_identified_by_filing"] == "BitGo Trust"
    assert relationships["circle"]["direct_role_in_reviewed_evernorth_capital_filings"] == "not established"


def test_research_artifact_is_not_model_eligible_or_a_forecast() -> None:
    data = _artifact()

    assert data["source_capture"]["model_eligible"] is False
    assert data["source_capture"]["raw_http_bytes_captured"] is False
    assert data["forecast"]["issued"] is False
    assert data["forecast"]["directional"] is False


def test_ripple_one_million_facility_is_separate_from_nh_kyobo_pik_note() -> None:
    events = {item["id"]: item for item in _artifact()["capital_events"]}

    assert events["evernorth_related_party_facility"]["lender"] == "Ripple Labs Inc."
    assert events["evernorth_related_party_facility"]["facility_limit_usd"] == 1_000_000
    assert events["convertible_pik_note"]["purchaser"].startswith("NH Investment & Securities")
    assert events["convertible_pik_note"]["principal_usd"] == 30_000_000


def test_append_only_corrections_preserve_prior_evernorth_artifact() -> None:
    data = _artifact()
    corrections = data["corrections"]

    assert len(corrections) == 2
    assert all(
        item["prior_artifact_id"]
        == "20261104T134706Z-evernorth-close-actual-capital-sbi-ownership-reconciliation"
        for item in corrections
    )
    assert all(item["disposition"].startswith("Append-only correction") for item in corrections)
    assert data["reported_xrp_position_context"]["calculated_component_sum_xrp"] == 473_276_430.423935
