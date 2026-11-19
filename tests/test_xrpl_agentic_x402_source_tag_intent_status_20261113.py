import hashlib
import json
import math
from pathlib import Path

ARTIFACT = Path(
    "research/xrp_intelligence/20261113T152200Z-run97-xrpl-x402-agentic-payment-source-tag-intent-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_t54_operator_counters_are_not_capital_flow_or_xrp_demand():
    data = load_artifact()
    t54 = data["source_observations"]["t54_hub"]["operator_reported"]
    average = t54["all_time_value_settled_usd"] / t54["all_time_transactions"]
    assert t54["all_time_transactions"] == 15_694_282
    assert t54["all_time_value_settled_usd"] == 78_306.59
    assert math.isclose(average, 0.004989498085990808, abs_tol=1e-12)
    assert data["model_admission"]["eligible_as_xrp_price_feature"] is False
    assert data["model_admission"]["eligible_as_xrp_capital_flow"] is False


def test_source_tag_is_merchant_endpoint_attribution_not_agent_identity():
    data = load_artifact()
    source_tag = data["source_observations"]["source_tag"]
    assert source_tag["default_value"] == 804681468
    assert source_tag["semantics"] == "merchant_endpoint_attribution"
    assert source_tag["agent_attribution"] is False
    assert "not agent attribution" in source_tag["direct_excerpt"].lower()
    assert "which endpoint was paid" in source_tag["direct_excerpt"].lower()


def test_intent_unverified_is_not_a_ledger_failure_status():
    data = load_artifact()
    t54 = data["source_observations"]["t54_hub"]["transaction_list"]
    vi = data["source_observations"]["t54_verifiable_intent"]
    assert t54["field_name"] == "Intent"
    assert t54["sampled_intent_status_unverified_rows"] == 25
    assert t54["sample_transaction"]["intent_status"] == "Unverified"
    assert t54["sample_transaction"]["ledger_transaction_independently_verified_by_this_run"] is False
    assert vi["optional"] is True
    assert "plain x402 payment still works" in data["source_observations"]["intent_status"]["direct_excerpt"].lower()
    assert data["evidence_integrity"]["intent_status_semantics_verified_against_t54_docs"] is True


def test_xrp_insights_is_not_an_independent_confirmation_of_t54():
    data = load_artifact()
    rec = data["reconciliation"]
    assert rec["t54_hub_transactions"] == 15_694_282
    assert rec["xrp_insights_transactions"] == 15_679_858
    assert rec["difference"] == 14_424
    assert "do not average" in rec["treatment"].lower()
    assert data["source_observations"]["xrp_insights"]["source_group"] == "t54_downstream_aggregator"
    assert data["source_observations"]["t54_hub"]["source_group"] == "facilitator_operator_primary"


def test_xrp_and_rlusd_agentic_payment_units_remain_separate():
    data = load_artifact()
    assets = data["source_observations"]["xrp_insights"]["operator_attributed_metrics"]
    assert assets["settled_xrp"] == 7031
    assert assets["settled_rlusd"] == 69061
    assert data["reconciliation"]["asset_interpretation"].startswith("XRP and RLUSD must remain separate")
    assert data["model_admission"]["eligible_as_xrp_price_feature"] is False


def test_live_services_and_endpoints_are_not_treated_as_same_metric():
    data = load_artifact()
    t54 = data["source_observations"]["t54_hub"]["operator_reported"]
    radar = data["source_observations"]["xrp_insights"]["operator_attributed_metrics"]
    assert t54["live_services"] == 5410
    assert radar["endpoints"] == 5882
    assert data["reconciliation"]["treatment_services_vs_endpoints"].startswith("Different labels/definitions")


def test_mastercard_participation_does_not_imply_bilateral_xrp_settlement():
    data = load_artifact()
    mc = data["source_observations"]["mastercard"]
    assert {"T54 Labs", "RippleX", "Coinbase"}.issubset(set(mc["initial_participants"]))
    assert "does not establish a bilateral" in mc["interpretation"]
    assert "XRP-denominated Mastercard settlement" in mc["interpretation"]


def test_verifiable_intent_chain_roles_are_separate():
    data = load_artifact()
    vi = data["source_observations"]["t54_verifiable_intent"]
    assert vi["layers"]["L1"].startswith("Trustline")
    assert vi["layers"]["L2"].startswith("Owner")
    assert vi["layers"]["L3"].startswith("Agent")
    assert vi["risk_decision"] == ["allow", "deny", "review"]
    assert vi["optional"] is True


def test_stale_cached_transaction_page_is_not_used_as_current_count():
    data = load_artifact()
    stale = data["source_observations"]["t54_hub"]["stale_page_cache"]
    assert stale["status"] == "stale_cached_snapshot"
    assert stale["model_eligible"] is False
    assert stale["reported_total_transactions"] == 2_444_839
    assert data["evidence_integrity"]["stale_page2_excluded"] is True


def test_authored_excerpt_hashes_are_reproducible_and_not_raw_receipts():
    data = load_artifact()
    for source in data["source_observations"].values():
        excerpt = source.get("direct_excerpt")
        digest = source.get("excerpt_sha256")
        if excerpt and digest:
            assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == digest
    assert data["evidence_integrity"]["authored_excerpt_hashes"] is True
    assert data["evidence_integrity"]["raw_source_bytes_archived"] is False
    assert data["evidence_integrity"]["raw_source_hash_receipts"] is False


def test_agentic_payments_remain_event_timeline_only_and_no_forecast():
    data = load_artifact()
    admission = data["model_admission"]
    assert admission["eligible_for_event_timeline"] is True
    assert admission["eligible_as_xrp_price_feature"] is False
    assert admission["eligible_as_xrp_capital_flow"] is False
    assert admission["eligible_as_verified_agent_identity"] is False
    assert admission["forecast_status"] == "NOT_ISSUED"
