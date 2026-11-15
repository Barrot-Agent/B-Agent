import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T081543Z-coinbase-xrp-collateral-derivatives-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_coinbase_first_party_excerpt_hashes_are_preserved():
    artifact = load_artifact()
    for source in artifact["evidence"]["primary_coinbase_sources"]:
        excerpts = source.get("excerpts") or [source.get("excerpt")]
        for excerpt in excerpts:
            assert hashlib.sha256(excerpt["text"].encode()).hexdigest() == excerpt["sha256"]


def test_xrp_is_accepted_global_exchange_collateral_but_usage_is_unknown():
    artifact = load_artifact()
    collateral = artifact["product_separation"]["coinbase_global_exchange"]
    interpretation = artifact["collateral_interpretation"]
    assert collateral["xrp_accepted_as_collateral"] is True
    assert "not evidence that customers have posted XRP" in interpretation["demand_conclusion"]
    assert artifact["model_admission"]["eligible"] is False


def test_global_xrp_perp_and_us_xpp_are_not_conflated():
    products = load_artifact()["product_separation"]
    assert products["coinbase_global_exchange"]["contract_code"] == "XRP-PERP"
    assert products["coinbase_global_exchange"]["settlement"] == "USDC every 5 minutes"
    assert products["coinbase_us"]["contract_code"] == "XPP"
    assert products["coinbase_us"]["contract_size_xrp"] == 500
    assert products["coinbase_global_exchange"]["contract_code"] != products["coinbase_us"]["contract_code"]


def test_official_us_expiry_conflict_is_preserved():
    conflict = load_artifact()["product_separation"]["coinbase_us"]["official_document_conflict"]
    assert conflict["status"] == "UNRESOLVED_PRIMARY_SOURCE_CONFLICT"
    assert "no expiration" in conflict["contract_spec_page"]
    assert "five years" in conflict["us_overview_page"]


def test_collateral_limits_haircuts_and_liquidation_are_recorded():
    artifact = load_artifact()
    constraints = artifact["collateral_interpretation"]["constraints"]
    assert any("average daily quantity" in x for x in constraints)
    assert any("haircuts" in x for x in constraints)
    assert any("liquidated" in x for x in constraints)


def test_loris_coinbase_row_is_stale_and_not_primary():
    artifact = load_artifact()
    market = artifact["market_data_interpretation"]
    cb = next(x for x in artifact["evidence"]["secondary_market_sources"] if x["id"] == "loris_coinbase_us_market")
    assert cb["source_class"] == "secondary_aggregator"
    assert cb["mapping_status"] == "UNVERIFIED_PRODUCT_MAPPING"
    assert market["coinbase_us_xrp_data_age_seconds"] > 3600
    assert market["coinbase_us_xrp_oi_vintage_discrepancy_usd"] == 1050000


def test_source_groups_are_not_counted_as_independent_per_page():
    groups = load_artifact()["source_independence"]
    assert groups["coinbase_product_documentation_group"] == "coinbase_first_party"
    assert groups["loris_market_data_group"] == "loris_tools"
    assert "not two independent sources" in groups["independence_note"]


def test_no_market_forecast_or_external_action_was_taken():
    artifact = load_artifact()
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert artifact["external_actions"]["accounts_accessed"] is False
    assert artifact["external_actions"]["orders_sent"] is False
    assert artifact["external_actions"]["collateral_posted"] is False
    assert artifact["external_actions"]["real_money_used"] is False
