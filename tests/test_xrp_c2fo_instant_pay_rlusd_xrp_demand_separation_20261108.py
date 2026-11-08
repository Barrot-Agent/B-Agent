from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108-c2fo-instant-pay-rlusd-xrp-demand-separation.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_c2fo_instant_pay_names_rlusd_not_xrp_as_settlement_asset():
    data = load_artifact()
    assert data["product_state"]["announced_financing_and_settlement_ledger"] == "XRPL"
    assert data["product_state"]["settlement_asset"] == "RLUSD"
    assert data["product_state"]["status"] == "ANNOUNCED_INITIATIVE_WAITLIST; PRODUCTION_THROUGHPUT_NOT_DISCLOSED"
    assert data["product_state"]["verified_settlement_volume_usd"] is None
    assert data["product_state"]["verified_xrp_bridge_volume"] is None
    assert data["product_state"]["verified_xrp_purchases"] is None


def test_existing_c2fo_working_capital_is_not_instant_pay_or_xrpl_volume():
    data = load_artifact()
    claims = data["commercial_activity"]["c2fo_existing_early_pay_working_capital_claims"]
    assert {x["reported_value_usd"] for x in claims} == {520_000_000_000, 525_000_000_000}
    assert all(x["is_xrpl_volume"] is False for x in claims)
    assert all(x["is_instant_pay_volume"] is False for x in claims)
    assert data["commercial_activity"]["discrepancy"]["status"] == "UNRESOLVED_SOURCE_WORDING_DIFFERENCE"
    assert data["commercial_activity"]["discrepancy"]["difference_usd"] == 5_000_000_000


def test_xrp_fees_and_reserves_are_separate_from_invoice_notional():
    data = load_artifact()
    utility = data["xrp_protocol_utility"]
    assert utility["transaction_fee_asset"] == "XRP"
    assert utility["standard_transaction_minimum_drops"] == 10
    assert utility["illustrative_xrp_burn_per_100000_standard_transactions_at_minimum"] == 1
    assert utility["mainnet_base_reserve_xrp"] == 1
    assert utility["mainnet_owner_reserve_xrp_per_object"] == 0.2
    assert utility["bridge_asset_use"] == "NOT_DISCLOSED"
    assert "does not determine XRP fees" in utility["inference_limit"]


def test_primary_sources_are_clustered_and_normalized_hashes_are_truthfully_scoped():
    data = load_artifact()
    receipts = data["source_receipts"]
    assert len(receipts) == 5
    by_id = {x["source_id"]: x for x in receipts}
    assert by_id["c2fo_instant_pay_joint_release"]["independence_cluster"] == by_id["ripple_instant_pay_joint_release"]["independence_cluster"]
    assert by_id["c2fo_instant_pay_joint_release"]["independent_confirmation"] is False
    assert by_id["ripple_instant_pay_joint_release"]["independent_confirmation"] is False
    for receipt in receipts:
        assert receipt["raw_source_bytes_captured"] is False
        assert receipt["http_headers_captured"] is False
        assert receipt["hash_scope"] == "SHA-256 of normalized web-rendered excerpt UTF-8, not raw page bytes"
        digest = hashlib.sha256(receipt["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == receipt["normalized_excerpt_sha256"]


def test_bny_custody_and_trade_finance_are_not_conflated_with_instant_pay():
    data = load_artifact()
    separation = data["relationship_separation"]
    assert "RLUSD" in separation["bny_custody"]
    assert "separate" in separation["bny_c2fo_trade_finance"].lower()
    assert "C2FO lifetime Early Pay working capital with Instant Pay volume" in separation["do_not_conflate"]
    assert data["model_admission"]["eligible_for_price_feature_store"] is False
    assert data["model_admission"]["eligible_for_directional_forecast"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
