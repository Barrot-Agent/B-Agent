from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T214524Z-coinbase-circle-sbi-ripple-binance-relationship-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_coinbase_circle_relationship_receipts_are_reproducible() -> None:
    artifact = load_artifact()
    receipts = artifact["source_receipts"]
    assert len(receipts) == 29
    assert len({receipt["id"] for receipt in receipts}) == 29
    for receipt in artifact["source_receipts"]:
        assert len(receipt["excerpt"].split()) <= 25
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"]


def test_circle_sbi_japan_is_a_funded_50_50_entity_with_no_significant_results() -> None:
    circle_sbi = load_artifact()["relationship_graph"]["circle_sbi_japan"]
    assert circle_sbi["circle_equity_interest_pct"] == 50
    assert circle_sbi["sbi_holdings_equity_interest_pct"] == 50
    assert circle_sbi["circle_and_sbi_contribution_each_usd_approx"] == 1_500_000
    assert circle_sbi["circle_controls_variable_interest_entity"] is True
    assert circle_sbi["circle_consolidates_entity"] is True
    assert circle_sbi["significant_operating_results_to_date"] is False


def test_circle_binance_equity_and_commercial_agreement_are_separate_from_xrp() -> None:
    relationship = load_artifact()["relationship_graph"]["circle_binance"]
    assert relationship["binance_equity_investment_usd"] == 100_000_000
    assert relationship["shares_issued"] == 1_237_011
    assert relationship["shares_issued_exact"] is True
    assert relationship["monthly_incentive_fee_based_on_usdc_wallet_balances"] is True
    assert relationship["term_years"] == 5
    assert relationship["rounding_difference_usd"] == 30.76
    assert relationship["price_per_share_usd"] == 80.84
    assert relationship["five_year_commercial_agreement_announced"] is True
    assert relationship["xrp_specific_investment_or_flow_proven"] is False


def test_coinbase_circle_arrangement_and_coinbase_usdc_scale_are_distinct_metrics() -> None:
    relationship = load_artifact()["relationship_graph"]["coinbase_circle"]
    assert "same terms" in relationship["current_terms"]
    assert relationship["coinbase_average_usdc_products_usd"] == 22_000_000_000
    assert relationship["coinbase_average_usdc_yoy_growth_pct"] == 49
    assert relationship["coinbase_share_of_average_usdc_market_cap_pct"] == 30
    assert relationship["coinbase_management_claim_share_of_usdc_economics_pct"] == 50
    assert relationship["coinbase_q3_2026_stablecoin_revenue_usd"] == 306_900_000
    assert "not_audited_share_of_total_reserve_income" in next(
        r for r in load_artifact()["source_receipts"] if r["id"] == "coinbase_usdc_economics"
    )["measurement_type"]


def test_circle_q3_usdc_gross_flows_reconcile_to_six_hundred_ten_million_net_issuance() -> None:
    metrics = load_artifact()["q3_circle_metrics"]
    assert metrics["usdc_minted_usd"] == 104_304_000_000
    assert metrics["usdc_redeemed_usd"] == 103_694_000_000
    assert metrics["net_usdc_issuance_usd"] == metrics["usdc_minted_usd"] - metrics["usdc_redeemed_usd"]
    assert metrics["net_usdc_issuance_usd"] == 610_000_000
    assert metrics["average_usdc_circulation_usd"] == 73_264_000_000
    assert metrics["end_usdc_circulation_usd"] == 73_879_000_000
    assert metrics["onchain_transaction_volume_usd"] == 13_900_000_000_000


def test_circle_q3_revenue_and_costs_are_not_all_coinbase_distribution() -> None:
    metrics = load_artifact()["q3_circle_metrics"]
    assert metrics["reserve_income_usd"] == 657_624_000
    assert metrics["total_revenue_and_reserve_income_usd"] == 864_888_000
    assert metrics["other_revenue_usd"] == 207_264_000
    assert metrics["arc_presale_revenue_usd"] == 181_800_000
    assert metrics["distribution_and_transaction_costs_usd"] == 409_169_000
    assert metrics["reserve_income_share_of_total_revenue_pct"] == 76
    assert load_artifact()["relationship_graph"]["coinbase_circle"]["q1_2026_distribution_costs_in_connection_with_coinbase_agreements_usd"] == 330_600_000


def test_coinbase_xrp_and_rlusd_disclosures_are_time_bounded_and_unquantified() -> None:
    graph = load_artifact()["relationship_graph"]
    assert graph["coinbase_xrp"]["disclosure_as_of"] == "2026-03-31"
    assert graph["coinbase_xrp"]["coinbase_holding"] == "Yes"
    assert graph["coinbase_xrp"]["commercial_engagement"] == "Yes"
    assert graph["coinbase_xrp"]["amount_disclosed"] is False
    assert graph["coinbase_xrp"]["customer_custody_balance_disclosed"] is False
    assert graph["coinbase_ripple_rlusd"]["rlusd_corporate_holding_disclosed"] == "No"
    assert graph["coinbase_ripple_rlusd"]["rlusd_commercial_engagement"] == "Yes"
    assert graph["coinbase_xrp"]["wrapped_asset"] == "cbXRP is separately listed and must not be conflated with native XRP."


def test_coinbase_rlusd_distribution_is_live_but_global_exchange_collateral_was_planned() -> None:
    relationship = load_artifact()["relationship_graph"]["coinbase_ripple_rlusd"]
    assert relationship["product_availability"] == ["Coinbase Prime", "Coinbase Exchange", "Coinbase retail"]
    assert relationship["chains"] == ["XRPL", "Base", "Ethereum"]
    assert relationship["global_exchange_collateral_status"] == "planned_later_phase_not_live_at_2026-10-28_launch"
    assert "does not imply XRP settlement" in load_artifact()["source_independence_and_disagreement"]["rlusd_limit"]


def test_sbi_ripple_asia_and_circle_sbi_japan_are_distinct_joint_ventures() -> None:
    graph = load_artifact()["relationship_graph"]
    assert graph["sbi_ripple_asia"]["sbi_group_voting_rights_pct"] == 60
    assert graph["circle_sbi_japan"]["circle_equity_interest_pct"] == 50
    assert graph["circle_sbi_japan"]["sbi_holdings_equity_interest_pct"] == 50
    assert graph["sbi_ripple_asia"]["relationship"] != graph["circle_sbi_japan"]["entity"]


def test_circle_arc_is_an_alternative_usdc_rail_not_xrpl_or_xrp() -> None:
    arc = load_artifact()["relationship_graph"]["circle_arc"]
    assert arc["relationship"].startswith("Circle launched its own Layer-1 Arc")
    assert arc["xrp_or_xrpl_relationship_proven"] is False


def test_related_party_financial_disclosures_do_not_establish_xrp_net_demand() -> None:
    caveats = load_artifact()["source_independence_and_disagreement"]
    assert "do not constitute independent verification of XRP market demand" in caveats["related_party_limit"]
    assert "does not disclose amount" in caveats["coinbase_disclosure_limit"]
    assert "no significant operating results to date" in caveats["circle_sbi_limit"]


def test_relationship_evidence_is_not_a_directional_feature_or_forecast() -> None:
    artifact = load_artifact()
    assert artifact["market_admission"]["admitted_to_feature_store"] is False
    assert artifact["market_admission"]["price_directional_use"] is False
    assert artifact["market_admission"]["event_timeline_only"] is True
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is False
    assert artifact["external_actions"]["financial_action"] is False
    assert artifact["external_actions"]["external_model_transfer"] is False


def test_circle_binance_exact_share_count_and_rounded_proceeds_are_preserved() -> None:
    artifact = load_artifact()
    relationship = artifact["relationship_graph"]["circle_binance"]
    computed = round(relationship["shares_issued"] * relationship["price_per_share_usd"], 2)
    assert relationship["shares_issued"] == 1_237_011
    assert relationship["reported_aggregate_proceeds_usd"] == 100_000_000
    assert computed == 99_999_969.24
    assert round(relationship["reported_aggregate_proceeds_usd"] - computed, 2) == 30.76
    receipt = next(r for r in artifact["source_receipts"] if r["id"] == "circle_binance_equity")
    assert receipt["url"].endswith("/000187604226000276/crcl-20260917.htm")
    assert "1,237,011 shares" in receipt["excerpt"]
    assert relationship["monthly_incentive_fee_based_on_usdc_wallet_balances"] is True


def test_transfer_metadata_preserves_source_branch_and_raw_byte_limit() -> None:
    metadata = load_artifact()["integration_transfer"]
    assert metadata["source_pr"] == 1643
    assert metadata["source_branch_head_sha"] == "238f3ff4a69420882c77d225626a352ba19a412c"
    assert metadata["source_git_blob_sha"] == "e431254c1bed9e3994dae6dc60b7e866699b2ec2"
    assert metadata["destination_pr"] == 1640
    assert metadata["raw_http_bytes_captured"] is False
    assert metadata["model_eligible"] is False
    assert metadata["forecast_status"] == "NOT_ISSUED"
    correction = metadata["source_receipt_hash_corrections"][0]
    assert correction["receipt_id"] == "circle_binance_equity"
    assert correction["original_source_blob_sha256"] == "9682e077cb21e35b3df92947b1929d27285428aa2aeea9301d9d6f907f9cc158"
    assert correction["corrected_excerpt_sha256"] == "79cfa8ca5c3438bd9062b0149b97c75f64102c6ab7349e53e0619cde876af7b0"
