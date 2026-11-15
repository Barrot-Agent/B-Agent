from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T164100Z-sbi-vc-trade-rlusd-chain-and-reserve-snapshot-correction.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_normalized_primary_source_records_have_reproducible_hashes():
    artifact = load_artifact()
    assert artifact["source_capture"]["raw_http_bytes_captured"] is False
    for source in artifact["source_receipts"]:
        canonical = json.dumps(
            source["normalized_observation_record"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == source["normalized_record_sha256"]


def test_sbi_vc_trade_is_ethereum_only_and_xrpl_is_future():
    source = load_artifact()["source_receipts"][0]["normalized_observation_record"]
    assert source["current_supported_networks"] == ["Ethereum"]
    assert source["xrpl_support_status"] == "PLANNED_FUTURE"
    assert source["legal_classification"].startswith("Type 4")
    assert "Do not attribute current SBI VC Trade RLUSD handling to XRPL" in (
        load_artifact()["reconciled_network"]["sbi_vc_trade"]["conclusion"]
    )


def test_sbi_reserve_snapshot_is_historical_and_not_exhaustive():
    snapshot = load_artifact()["supply_and_reserve_reconciliation"]["sbi_snapshot_2026_08_27"]
    assert snapshot["circulation_usd"] == 1_866_500_000
    assert snapshot["reserve_fund_usd"] == 1_981_300_000
    assert snapshot["arithmetic_reserve_excess_usd"] == 114_800_000
    assert snapshot["listed_asset_categories_usd"] == 1_550_000_000
    assert snapshot["listed_categories_not_itemized_in_excerpt_usd"] == 431_300_000
    assert "not evidence of a reserve shortfall" in snapshot["caution"]


def test_coinbase_chain_support_and_collateral_status_are_separate():
    source = load_artifact()["source_receipts"][2]["normalized_observation_record"]
    assert source["rlusd_networks"] == ["XRPL", "Base", "Ethereum"]
    assert source["live_platforms"] == ["Coinbase Retail", "Coinbase Prime", "Coinbase Exchange"]
    assert source["coinbase_global_exchange_availability"] == "FUTURE_AT_LAUNCH"
    assert source["rlusd_collateral_on_coinbase_global_exchange"] == "FUTURE_AT_LAUNCH"


def test_bny_custody_is_live_but_mint_redeem_and_trade_finance_are_future_or_exploratory():
    source = load_artifact()["source_receipts"][3]["normalized_observation_record"]
    assert set(source["custody_support_live_assets"]) == {"XRP", "RLUSD"}
    assert source["bny_direct_rlusd_mint_redeem"] == "INTENDED_FUTURE"
    assert source["tokenized_trade_finance"] == "EXPLORATION"
    assert source["c2fo_supply_chain_finance"] == "EXPLORATION"


def test_standard_chartered_xrpl_custody_is_live_but_lmax_collateral_is_planned():
    source = load_artifact()["source_receipts"][4]["normalized_observation_record"]
    assert source["rlusd_custody_on_xrpl"] == "LIVE"
    assert source["lmax_rlusd_collateral"] == "PLANNED_NOT_LIVE"
    assert len(source["conditions"]) >= 4


def test_ripple_supply_statements_are_approximate_and_not_independent():
    comparison = load_artifact()["supply_and_reserve_reconciliation"]["ripple_market_cap_statements"]
    assert comparison["coinbase_release_2026_10_28_lower_bound_usd"] == 2_400_000_000
    assert comparison["bny_release_2026_10_27_approximate_usd"] == 2_500_000_000
    assert comparison["status"] == "APPROXIMATE_SAME_ISSUER_VINTAGE_DIFFERENCE"
    assert "not independent measurements" in comparison["interpretation"]


def test_no_xrp_demand_feature_or_directional_forecast_is_created():
    artifact = load_artifact()
    assert artifact["model_admission"]["feature_store_admission"] == "PROHIBITED"
    assert any("not XRP supply" in item for item in artifact["model_admission"]["reasons"])
    assert artifact["forecast_status"] == "NOT_ISSUED"
