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
    assert audit["security_and_dependencies"]["status"] == "DEPENDENCY_AUDIT_GAP_OR_DOCUMENTATION_DRIFT"
    assert audit["pr_inventory"]["prediction_pr_1466"]["status"] == "OPEN_DRAFT_NEW_FRESH_MAIN_SUCCESSOR_CI_PENDING"


def test_handoff_keeps_forecast_unissued():
    handoff = load("data/xrp_intelligence/hand_offs/20261101T151200Z-binance-update4-and-current-main-safety-handoff.json")
    assert handoff["forecast_status"] == "NOT_ISSUED"
    assert handoff["feature_admission"] == "NONE"
