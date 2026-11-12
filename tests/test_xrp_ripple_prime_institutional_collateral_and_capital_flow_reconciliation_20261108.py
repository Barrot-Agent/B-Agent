from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T173000Z-ripple-prime-institutional-collateral-and-capital-flow-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_hidden_road_acquisition_is_completed_and_consideration_is_unquantified():
    data = load()
    item = data["source_receipts"][1]["normalized_observation_record"]
    assert item["acquisition_status"] == "COMPLETED"
    assert item["new_name"] == "Ripple Prime"
    assert item["xrp_specific_volume"] == "NOT_DISCLOSED"


def test_rlusd_is_explicitly_collateral_but_xrp_collateral_is_not_established():
    data = load()
    item = data["collateral_reconciliation"]
    assert item["rlusd"]["ripple_prime_collateral_use"].startswith("LIVE")
    assert item["xrp"]["xrp_posted_as_collateral"] == "NOT_ESTABLISHED_BY_THE_CITED_ANNOUNCEMENTS"
    assert item["rlusd"]["amount_or_share_of_collateral"] == "NOT_DISCLOSED"


def test_us_spot_prime_brokerage_supports_xrp_without_disclosing_positions():
    data = load()
    item = data["source_receipts"][2]["normalized_observation_record"]
    assert item["service_status"] == "LIVE"
    assert "XRP" in item["supported_assets_include"]
    assert item["xrp_volume_or_positions"] == "NOT_DISCLOSED"


def test_cross_margining_is_not_equivalent_to_proof_of_xrp_collateral():
    data = load()
    item = data["collateral_reconciliation"]["xrp"]
    assert "cross-margined" in item["cross_margining"]
    assert item["xrp_posted_as_collateral"] == "NOT_ESTABLISHED_BY_THE_CITED_ANNOUNCEMENTS"


def test_prime_brokerage_debt_and_notes_are_not_mislabeled_as_xrp_purchases():
    data = load()
    item = data["capital_flow_reconciliation"]
    assert item["ripple_prime_debt_facility_usd"] == "200 million"
    assert item["ripple_prime_senior_notes_usd"] == "275 million"
    assert item["xrp_purchase_use"] == "NOT_STATED"
    assert item["do_not_conflate"] is True


def test_hyperliquid_brevan_howard_and_virtu_relationships_are_not_xrp_volume_claims():
    data = load()
    receipts = {x["source_id"]: x["normalized_observation_record"] for x in data["source_receipts"]}
    assert receipts["ripple_hyperliquid_support_20260204"]["xrp_specific_exposure_or_collateral"] == "NOT_DISCLOSED"
    assert receipts["ripple_prime_brevan_howard_20261006"]["xrp_specific_positions_or_volume"] == "NOT_DISCLOSED"
    assert receipts["ripple_prime_rwa_perpetual_swaps_20261015"]["xrp_specific_volume"] == "NOT_DISCLOSED"


def test_sbi_hidden_road_statement_remains_future_intent_not_a_verified_partnership():
    data = load()
    item = data["source_receipts"][8]["normalized_observation_record"]
    assert item["status"] == "FUTURE_INTENT_NOT_CONFIRMED_PARTNERSHIP"
    assert data["competing_hypotheses"][2]["status"] == "UNCONFIRMED_FUTURE_INTENT_ONLY"


def test_coinbase_bny_standard_chartered_and_sbi_networks_remain_distinct():
    data = load()
    context = data["cross_company_context"]
    assert context["coinbase_rlusd"]["networks"] == ["XRPL", "Base", "Ethereum"]
    assert context["coinbase_rlusd"]["coinbase_global_exchange_collateral"] == "FUTURE_AT_LAUNCH"
    assert context["bny_custody"]["actual_custody_balances"] == "NOT_DISCLOSED"
    assert context["standard_chartered"]["lmax_collateral_integration"] == "PLANNED_NOT_LIVE"
    assert context["sbi_vc_trade"]["current_network_support"] == ["Ethereum"]
    assert context["sbi_vc_trade"]["xrpl_support"] == "PLANNED_NOT_LIVE"


def test_source_receipt_hashes_match_normalized_records():
    data = load()
    for receipt in data["source_receipts"]:
        canonical = json.dumps(
            receipt["normalized_observation_record"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        assert hashlib.sha256(canonical).hexdigest() == receipt["normalized_record_sha256"]


def test_no_institutional_relationship_is_admitted_as_a_directional_feature():
    data = load()
    assert data["model_admission"]["feature_store"] == "PROHIBITED"
    assert data["forecast_status"] == "NOT_ISSUED"
