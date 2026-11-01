import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_binance_update4_supersedes_aggregate_recovery_without_inventing_xrp_purchases():
    snapshot = load("data/xrp_intelligence/snapshots/20261101T151200Z-binance-update4-xrp-phase1-and-market-observation.json")
    recovery = snapshot["binance_recovery"]
    assert recovery["update4_aggregate_replenishment_pct"] == 95
    assert recovery["update3_aggregate_replenishment_pct"] == 90
    assert "XRP" in recovery["top_ten_assets"]
    assert recovery["xrp_customer_asset_backing_pct"] if "xrp_customer_asset_backing_pct" in recovery else recovery["top_ten_customer_asset_backing_pct"] == 100
    assert recovery["xrp_specific_acquisition_quantity"] is None
    assert recovery["xrp_withdrawal_status"] == "ANNOUNCED_IN_PHASE1_EXECUTION_NOT_INDEPENDENTLY_VERIFIED"


def test_xrp_phase1_is_announced_but_not_misclassified_as_verified():
    source = load("data/xrp_intelligence/source_revisions/20261101T151200Z-binance-recovery-update4-and-xrp-withdrawal-phase1.json")
    binance = next(s for s in source["sources"] if s["id"] == "binance-recovery-update4-20261101")
    assert any("XRP network" in claim for claim in binance["claims"])
    assert any("does not independently prove" in limitation for limitation in binance["limitations"])


def test_coin_gecko_market_observation_is_timestamped_as_access_not_provider_time():
    snapshot = load("data/xrp_intelligence/snapshots/20261101T151200Z-binance-update4-xrp-phase1-and-market-observation.json")
    market = snapshot["xrp_market_observation"]
    assert market["provider_data_timestamp"] is None
    assert market["feature_admission"] == "NONE"
    assert market["perpetual_open_interest_usd"] == 3529000000


def test_escrow_tracker_freshness_conflict_is_preserved():
    snapshot = load("data/xrp_intelligence/snapshots/20261101T151200Z-binance-update4-xrp-phase1-and-market-observation.json")
    escrow = snapshot["escrow_source_freshness"]
    assert escrow["current_page_pinned_ledger"] == 108034152
    assert escrow["earlier_handoff_ledger_claim"] == 108036051
    assert escrow["reconciliation_status"] == "CONFLICT_UNRESOLVED"


def test_cross_chain_attribution_is_not_promoted_to_direct_address_identity():
    graph = load("data/xrp_intelligence/relationship_graph_addenda/20261101T151200Z-binance-update4-xrp-phase1-and-native-asset-custody-graph.json")
    edge = next(e for e in graph["edges"] if e["from"] == "TraderTraitor" and e["to"] == "XRPL_attacker_account")
    assert edge["status"].startswith("INFERENCE_ONLY")
    assert graph["competing_hypotheses"][2]["status"] == "CONDITIONAL_RISK_NOT_CURRENT_SELLING_EVIDENCE"


def test_current_main_audit_records_writers_and_dependency_scan_gap():
    audit = load("data/repository_audits/20261101T151200Z-current-main-workflow-prediction-and-dependency-audit.json")
    assert audit["main_sha"] == "46e9f9d276a862157906dce63a0910e20eb8f7b5"
    assert audit["workflow_inventory"]["active_workflow_files"] == 77
    assert audit["security_and_dependencies"]["dependabot"]["frequency"] == "weekly"
    assert audit["security_and_dependencies"]["status"].startswith("DEPENDENCY_AUDIT_GAP_OR_DOCUMENTATION_DRIFT")
    assert audit["pr_inventory"]["prediction_pr_1466"]["status"] == "OPEN_DRAFT_NEW_FRESH_MAIN_SUCCESSOR_CI_PENDING"


def test_handoff_keeps_forecast_unissued():
    handoff = load("data/xrp_intelligence/hand_offs/20261101T151200Z-binance-update4-and-current-main-safety-handoff.json")
    assert handoff["forecast_status"] == "NOT_ISSUED"
    assert handoff["feature_admission"] == "NONE"

def test_november_escrow_same_account_release_is_not_market_float():
    snapshot = load("data/xrp_intelligence/snapshots/20261101T154204Z-xrp-escrow-destination-binance-phase1-and-prediction-audit.json")
    escrow = snapshot["escrow"]
    assert escrow["gross_released_xrp"] == 1_000_000_000
    assert escrow["tracker_reported_net_out_of_escrow_xrp"] == 1_000_000_000
    assert escrow["market_float_increase_xrp"] is None
    same_account = next(tx for tx in escrow["transactions"] if tx["hash"].startswith("33F693"))
    assert same_account["sender_account"] == same_account["receiver_account"]
    assert same_account["classification"] == "ESCROW_RELEASE_TO_SAME_RIPPLE_ACCOUNT"
    unknown = next(tx for tx in escrow["transactions"] if tx["hash"].startswith("3CB037"))
    assert unknown["destination_account"] is None
    assert snapshot["forecast_status"] == "NOT_ISSUED"


def test_binance_xrp_phase1_status_is_media_reported_not_directly_verified():
    snapshot = load("data/xrp_intelligence/snapshots/20261101T154204Z-xrp-escrow-destination-binance-phase1-and-prediction-audit.json")
    binance = snapshot["binance"]
    assert binance["aggregate_replenishment_pct"] == 95
    assert "XRP" in binance["top_ten_assets"]
    assert binance["xrp_network_listed_in_phase1"] is True
    assert binance["withdrawal_status"] == "MEDIA_REPORTED_AVAILABLE; DIRECT_NETWORK_STATUS_NOT_VERIFIED"
    assert binance["successful_xrp_withdrawal_independently_observed"] is None
    assert binance["xrp_specific_replenishment_quantity"] is None


def test_future_dated_snapshot_is_quarantined_from_point_in_time_use():
    snapshot = load("data/xrp_intelligence/snapshots/20261101T154204Z-xrp-escrow-destination-binance-phase1-and-prediction-audit.json")
    future = snapshot["point_in_time_integrity"]["future_dated_existing_artifact"]
    assert future["recorded_captured_at_utc"] > snapshot["captured_at_utc"]
    assert future["status"] == "FUTURE_DATED_AT_THIS_CUTOFF"
    assert "QUARANTINE" in future["treatment"]


def test_prediction_cohort_guard_and_dependency_audit_are_recorded_without_overclaim():
    audit = load("data/repository_audits/20261101T154204Z-prediction-cohort-guard-and-python-dependency-audit.json")
    assert audit["main_sha"] == "46e9f9d276a862157906dce63a0910e20eb8f7b5"
    assert audit["dependency_audit"]["conclusion"] == "SUCCESS"
    assert all(item["result"] == "NO_KNOWN_VULNERABILITIES_FOUND" for item in audit["dependency_audit"]["scanned_requirement_sets"])
    assert audit["prediction_integrity_review"]["exact_head_tests_passed"] == 389
    assert audit["prediction_integrity_review"]["exact_head_subtests_passed"] == 8
    assert audit["prediction_integrity_review"]["status"] == "OPEN_DRAFT_UNMERGED"
