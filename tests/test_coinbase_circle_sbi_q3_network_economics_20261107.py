import hashlib
import json
import re
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T180947Z-coinbase-circle-sbi-q3-network-economics-update.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_coinbase_q3_usdc_revenue_and_balances_are_preserved_separately():
    coinbase = load_artifact()["q3_2026_economics"]["coinbase"]
    assert coinbase["average_usdc_on_coinbase_products_usd"] == 22_000_000_000
    assert coinbase["average_usdc_off_platform_usd"] == 51_000_000_000
    assert coinbase["stablecoin_revenue_on_platform_usd"] == 202_000_000
    assert coinbase["stablecoin_revenue_off_platform_usd"] == 126_000_000
    assert coinbase["total_stablecoin_revenue_usd"] == 328_000_000
    assert coinbase["stablecoin_revenue_on_platform_usd"] + coinbase["stablecoin_revenue_off_platform_usd"] == coinbase["total_stablecoin_revenue_usd"]


def test_circle_q3_distribution_costs_are_not_mislabeled_as_coinbase_profit():
    circle = load_artifact()["q3_2026_economics"]["circle"]
    comparability = load_artifact()["q3_2026_economics"]["comparability"]
    assert circle["coinbase_distribution_costs_q3_usd"] == 331_300_000
    assert circle["coinbase_distribution_costs_nine_months_usd"] == 986_600_000
    assert circle["average_usdc_circulation_q3_usd"] == 73_264_000_000
    assert circle["usdc_circulation_at_2026_09_30_usd"] == 73_879_000_000
    assert circle["usdc_on_circle_platform_at_2026_09_30_usd"] == 13_868_000_000
    assert comparability["status"] == "different_accounting_views_not_a_reconciliation"
    assert comparability["arithmetic_difference_is_not_profit_or_loss"] is True


def test_coinbase_circle_is_direct_and_renewed_but_metrics_are_not_netted():
    artifact = load_artifact()
    edge = next(e for e in artifact["relationship_edges"] if e["from"] == "Coinbase" and e["to"] == "Circle")
    assert edge["status"] == "verified_primary"
    assert artifact["q3_2026_economics"]["coinbase"]["circle_arrangement"] == "renewed in Q3 2026 on the same terms"
    assert artifact["q3_2026_economics"]["comparability"]["coinbase_revenue_usd"] != artifact["q3_2026_economics"]["comparability"]["circle_coinbase_distribution_cost_usd"]


def test_sbi_circle_and_sbi_ripple_are_direct_relationships_with_distinct_rails():
    artifact = load_artifact()
    edges = {(e["from"], e["to"]): e["status"] for e in artifact["relationship_edges"]}
    assert edges[("SBI Holdings", "Circle")] == "verified_primary"
    assert edges[("SBI Holdings", "Ripple")] == "verified_primary"
    rails = artifact["sbi_product_rails"]
    assert rails["circle_equity_investment_usd"] == 50_000_000
    assert rails["circle_equity_investment_breakdown"]["sbi_holdings_usd"] == 25_000_000
    assert rails["circle_equity_investment_breakdown"]["sbi_shinsei_bank_usd"] == 25_000_000
    assert rails["usdc_distribution"]["registration_date"] == "2025-03-04"
    assert rails["rlusd_distribution"]["launch_date"] == "2026-06-24"


def test_sbi_coinbase_open_standard_is_shared_membership_not_bilateral_contract():
    artifact = load_artifact()
    edge = next(e for e in artifact["relationship_edges"] if e["from"] == "SBI Holdings" and e["to"] == "Coinbase")
    open_standard = artifact["sbi_product_rails"]["open_standard"]
    assert edge["status"] == "verified_shared_membership_not_bilateral_partnership"
    assert open_standard["coinbase_role"] == "founding partner"
    assert open_standard["production_service_launched"] is False
    assert open_standard["bilateral_sbi_coinbase_agreement_established"] is False


def test_coinbase_ripple_rlusd_listing_does_not_conflate_xrp_and_rlusd_collateral():
    artifact = load_artifact()
    edge = next(e for e in artifact["relationship_edges"] if e["from"] == "Coinbase" and e["to"] == "Ripple")
    scope = artifact["coinbase_ripple_product_scope"]
    assert edge["status"] == "verified_primary"
    assert scope["rlusd_rails"] == ["XRPL", "Base", "Ethereum"]
    assert scope["ripple_base_liquidity"] is True
    assert scope["coinbase_global_exchange_rlusd_collateral_at_launch"] is False
    assert scope["xrp_collateral_eligibility_is_separate"] is True
    assert scope["actual_xrp_collateral_balances_or_utilization_disclosed"] is False


def test_sbi_xrpl_tokenized_deposit_poc_is_not_mislabeled_as_xrp_bridge_usage():
    poc = load_artifact()["sbi_product_rails"]["xrpl_tokenized_deposit_poc"]
    assert poc["uses_xrpl"] is True
    assert poc["proves_xrp_bridge_usage"] is False


def test_evernorth_market_references_are_not_promoted_to_coinbase_or_circle_partnerships():
    scope = load_artifact()["evernorth_boundary"]
    assert scope["coinbase_reference"] == "principal market used for XRP valuation"
    assert scope["direct_coinbase_contract_disclosed"] is False
    assert scope["direct_circle_contract_disclosed"] is False


def test_all_network_source_receipts_match_their_normalized_excerpt_hashes():
    for receipt in load_artifact()["source_receipts"]:
        assert receipt["receipt_kind"] == "normalized_text_excerpt"
        assert re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"])
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"], receipt["source_id"]


def test_institutional_economics_are_not_admitted_as_xrp_price_features():
    artifact = load_artifact()
    assert artifact["model_admission"]["admitted"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["paper_or_real_money_actions"] == "NONE"
