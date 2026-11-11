from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T193218Z-xrp-spot-coinbase-circle-sbi-q3-network-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def test_all_captured_source_hashes_match_the_exact_stored_text() -> None:
    artifact = load_artifact()
    for receipt in artifact["source_receipts"]:
        text = receipt.get("raw_response_text") or receipt.get("captured_excerpt_text")
        digest = receipt.get("raw_response_sha256") or receipt.get("captured_excerpt_sha256")
        assert isinstance(text, str) and text
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == digest


def test_spot_and_perpetual_observations_are_not_admitted_without_arrival_receipts() -> None:
    artifact = load_artifact()
    sources = {item["source_id"]: item for item in artifact["source_receipts"]}
    market = artifact["market_snapshot"]
    assert market["spot"]["kraken"]["provider_event_timestamp_missing"] is True
    assert market["spot"]["okx"]["age_seconds_at_reference_clock"] > 300
    assert market["spot"]["binance_perpetual"]["age_seconds_at_reference_clock"] < 300
    assert sources["binance_xrpusdt_perpetual_premium_index"]["retrieval_arrival_timestamp_utc"] is None
    assert all(item["model_eligible"] is False for item in sources.values())
    assert market["feature_admission"] is False
    assert artifact["model_admission"]["spot_features"] is False
    assert artifact["model_admission"]["derivatives_features"] is False


def test_level_one_imbalance_disagreement_is_not_promoted_to_directional_signal() -> None:
    artifact = load_artifact()
    market = artifact["market_snapshot"]
    assert market["spot"]["kraken"]["top_of_book_bid_imbalance_pct"] > 0
    assert market["spot"]["okx"]["top_of_book_bid_imbalance_pct"] < 0
    assert market["reconciliation"]["top_of_book_imbalance_disagreement"] is True
    assert market["reconciliation"]["multi_level_depth"].startswith("Not retrieved")
    assert artifact["forecast_status"] == "NOT_ISSUED"


def test_coinbase_and_circle_stablecoin_metrics_keep_distinct_accounting_scopes() -> None:
    artifact = load_artifact()["institutional_network"]
    coinbase = artifact["coinbase"]
    circle = artifact["circle"]
    assert coinbase["q3_2026_stablecoin_revenue_usd_m"] == 306.905
    assert circle["q3_2026_distribution_costs_with_coinbase_usd_m"] == 331.3
    assert coinbase["q3_2026_usdc_aop_usd_b"] == 8.616
    assert circle["q3_2026_usdc_on_circle_platform_end_usd_b"] == 13.868
    assert "different accounting line items" in circle["accounting_warning"]
    assert "different time/scoping measures" in coinbase["metric_scope_warning"]


def test_coinbase_collateral_does_not_claim_an_xrp_specific_balance() -> None:
    collateral = load_artifact()["institutional_network"]["coinbase"]["collateral"]
    assert collateral["q3_2026_recognized_lending_collateral_usd_m"] == 1009.297
    assert collateral["q3_2026_unrecognized_customer_collateral_usd_m"] == 3284.562
    assert collateral["q3_2026_derivatives_collateral_usd_m"] == 325.766
    assert collateral["xrp_specific_balance_disclosed"] is False


def test_sbi_jpysc_growth_is_not_mislabeled_as_xrp_demand() -> None:
    jpysc = load_artifact()["institutional_network"]["sbi"]["jpysc"]
    assert jpysc["handling_balance_threshold_jpy"] == 30_000_000_000
    assert jpysc["lending_balance_threshold_jpy"] == 10_000_000_000
    assert jpysc["issuer_report_date"] == "2026-11-02"
    assert jpysc["current_public_chain_migration_status"] == "Not established by the November 2 balance announcement."
    assert "No direct XRP purchase" in jpysc["xrp_linkage"]


def test_smfg_five_percent_participation_is_at_sbi_startale_marketing_not_sbi_holdings() -> None:
    alliance = load_artifact()["institutional_network"]["sbi"]["smfg_alliance"]
    assert alliance["smfg_capital_participation_pct"] == 5
    assert alliance["investee"] == "SBI Startale Marketing"
    assert "5% ownership of SBI Holdings" in alliance["not_established"]


def test_arc_is_kept_distinct_from_xrpl_and_xrp() -> None:
    arc = load_artifact()["institutional_network"]["circle"]["arc"]
    assert arc["initial_supply_arc"] == 10_000_000_000
    assert arc["presale_tokens"] == 807_500_000
    assert arc["aggregate_gross_proceeds_usd_m"] == 242.2
    assert "ARC is not XRP" in arc["relationship_to_xrpl"]


def test_research_only_hypotheses_preserve_counterevidence_and_no_forecast() -> None:
    artifact = load_artifact()
    hypotheses = {item["id"]: item for item in artifact["hypotheses"]}
    assert {"H1", "H2", "H3", "H4"} <= set(hypotheses)
    assert all(item["support"] and item["counterevidence"] for item in hypotheses.values())
    assert hypotheses["H3"]["status"] == "important_counter_hypothesis"
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["safety"]["main_modified"] is False
