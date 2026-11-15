from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research/xrp_intelligence/20261108-xrp-cftc-bitnomial-cme-derivatives-inventory.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_primary_excerpt_receipts_match_sha256_and_word_limits():
    data = load_artifact()
    receipts = data["source_receipts"]
    assert len(receipts) >= 9
    for receipt in receipts:
        excerpt = receipt["normalized_excerpt"]
        digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
        assert digest == receipt["normalized_excerpt_sha256"]
        assert digest == receipt["sha256"]
        assert len(excerpt.split()) <= 25


def test_cftc_registry_records_six_certified_btnl_xrp_product_entries():
    rows = load_artifact()["cftc_registry_entries"]
    assert len(rows) == 6
    assert all(row["organization"] == "BTNL" for row in rows)
    assert all(row["type"] == "Future" and row["status"] == "Certified" for row in rows)
    spot_rows = [row for row in rows if row["product"] == "XRP US Dollar Spot Contract"]
    assert [row["registry_date"] for row in spot_rows] == ["2025-12-01", "2026-04-21"]


def test_btnl_identity_and_certified_status_are_not_overstated_as_cftc_approval():
    data = load_artifact()
    entity = data["entity_resolution"]
    status = data["cftc_status_interpretation"]
    assert entity["legal_entity"] == "Bitnomial Exchange, LLC"
    assert entity["clearing_entity"] == "Bitnomial Clearinghouse, LLC (BNCH)"
    assert "CFTC-registered derivatives clearing organization" in entity["clearing_status"]
    assert "not an affirmative CFTC order" in status["not_a_cftc_approval"]
    assert "40.2(a)" in status["self_certification_basis"]


def test_spot_labelled_xrpusd_contract_versions_keep_their_100_million_fold_unit_change():
    data = load_artifact()["bitnomial_products"]
    old = data["XRPUSD_2025_version"]
    new = data["XRPUSD_2026_version"]
    assert old["contract_size_xrp"] == 1
    assert old["settlement_method"] == "Deliverable"
    assert new["contract_size_xrp"] == 0.00000001
    assert new["contract_size_change_factor_vs_2025_version"] == 100000000
    assert new["cftc_registry_type"] == "Future"
    assert "physically settled" in new["contract_description"].lower()
    assert new["long_position_limit_xrp"] == 3200000
    assert new["short_position_limit_xrp"] == 1800000
    assert new["reportable_position_xrp"] == 900000
    assert new["settlement_method"].startswith("Deliverable")


def test_bitnomial_pxrp_us_contract_is_cash_settled_perpetual_not_spot():
    product = load_artifact()["bitnomial_products"]["PXRPUS"]
    assert product["reportable_contract_size_xrp"] == 10000
    assert product["minimum_contract_size_xrp"] == 1
    assert product["settlement_method"] == "Cash settled"
    assert product["market_hours"] == "24/7"
    assert product["position_limit_contracts"] == 35000
    assert product["reportable_position_level_contracts"] == 25
    assert product["intended_trade_date_on_or_after"] == "2026-09-04"


def test_bitnomial_hecto_perpetual_and_hecto_futures_have_distinct_settlement():
    products = load_artifact()["bitnomial_products"]
    perp = products["PXRPUH"]
    future = products["XRUH"]
    assert perp["contract_size_xrp"] == 500
    assert perp["settlement_method"] == "Cash settled"
    assert perp["market_hours"] == "24/7"
    assert future["contract_size_xrp"] == 100
    assert future["settlement_method"] == "Deliverable"
    assert future["market_hours"] == "23/5"


def test_cme_standard_micro_and_spot_quoted_contract_units_are_normalized_separately():
    products = load_artifact()["cme_products"]
    assert products["standard_xrp_futures"]["contract_size_xrp"] == 50000
    assert products["micro_xrp_futures"]["contract_size_xrp"] == 2500
    assert products["spot_quoted_xrp_futures"]["contract_size_xrp"] == 250
    assert products["standard_xrp_futures"]["settlement"].startswith("Financially settled")
    assert products["spot_quoted_xrp_futures"]["product_type"].startswith("Long-dated spot-quoted future")
    assert products["spot_quoted_xrp_futures"]["trading_hours"].startswith("Excluded")


def test_cme_q2_contract_volume_is_not_promoted_to_net_spot_flow():
    stats = load_artifact()["cme_q2_2026_reported_statistics"]
    assert stats["xrp_suite_average_daily_volume_contracts"] == 36600
    assert stats["xrp_suite_total_notional_volume_usd"] == 10800000000
    assert stats["qxrp_record_average_daily_volume_contracts"] == 32100
    assert stats["qxrp_xrp_equivalent_contract_turnover_per_day"] == 8025000
    assert "not net XRP purchases" in stats["interpretation"]


def test_coinbase_ventures_and_ripple_labs_are_a_shared_investee_link_not_a_direct_partnership():
    row = load_artifact()["bitnomial_corporate_relationships"]
    assert "Coinbase Ventures" in row["investors_named_in_2025_press_release"]
    assert "Ripple Labs" in row["investors_named_in_2025_press_release"]
    assert "shared-investee link" in row["relationship_interpretation"]
    assert row["investment_amounts_disclosed"] is False
    assert row["current_ownership_percentages_disclosed"] is False


def test_rlusd_settlement_remains_historical_future_intent_not_verified_live_xrp_product():
    text = load_artifact()["bitnomial_corporate_relationships"]["rlusd_settled_contracts"]
    assert "planned pending" in text
    assert "No current RLUSD-settled XRP contract was identified" in text


def test_no_market_feature_admission_forecast_or_financial_action():
    data = load_artifact()
    assert data["model_admission"]["event_timeline_eligible"] is True
    assert data["model_admission"]["feature_store_admission"] is False
    assert data["model_admission"]["directional_price_signal"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_probability_issued"] is False
    assert data["external_actions"]["feature_store_write"] is False
    assert data["external_actions"]["paper_trade"] is False
    assert data["external_actions"]["real_money"] is False
