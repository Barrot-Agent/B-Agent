import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data/xrp_intelligence/sources/binance_recovery_update3_20261031.json").read_text(encoding="utf-8"))
SNAPSHOT = json.loads((ROOT / "data/xrp_intelligence/snapshots/20261031T143132Z-binance-recovery-update3-xrp-reserve-reconciliation.json").read_text(encoding="utf-8"))
GRAPH = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T143132Z-binance-recovery-update3-reserve-and-issuer-graph.json").read_text(encoding="utf-8"))
DECISION = json.loads((ROOT / "data/xrp_intelligence/architecture_decisions/20261031T143132Z-binance-recovery-update3-feature-admission.json").read_text(encoding="utf-8"))


def test_recovery_update3_source_provenance_and_timestamps_are_explicit():
    ids = [item["source_id"] for item in SOURCE["sources"]]
    assert len(ids) == len(set(ids))
    primary = next(item for item in SOURCE["sources"] if item["source_id"] == "SRC-BINANCE-RECOVERY-UPDATE3-20261031")
    assert primary["published_at_utc"] == "2026-10-31T14:24:00Z"
    assert primary["evidence_class"] == "PRIMARY_COMPANY_STATEMENT"
    assert SNAPSHOT["captured_at_utc"] == "2026-10-31T14:31:32Z"
    assert SNAPSHOT["reserve_recovery"]["proof_generation"]["snapshot_time_utc"] == "2026-10-31T00:00:00Z"


def test_xrp_is_in_the_ten_named_assets_but_full_proof_remains_pending():
    recovery = SNAPSHOT["reserve_recovery"]
    assert "XRP" in recovery["top_ten_assets_claimed_at_least_1_to_1"]
    assert recovery["xrp"]["coverage_claim"] == "AT_LEAST_1_TO_1"
    assert recovery["xrp"]["independently_recomputed"] is False
    assert recovery["xrp"]["full_zk_proof_available_at_capture"] is False
    assert recovery["proof_generation"]["estimated_completion_date"] == "2026-11-03"


def test_aggregate_coverage_does_not_become_xrp_actual_capital():
    capital = SNAPSHOT["actual_capital_separation"]
    assert capital["current_aggregate_coverage_percent_from_update_3"] == 90
    assert capital["xrp_specific_spot_purchase_usd"] == "UNKNOWN"
    assert capital["xrp_specific_otc_purchase_usd"] == "UNKNOWN"
    assert capital["xrp_units_purchased"] == "UNKNOWN"
    assert SNAPSHOT["feature_admission"]["actual_capital_feature"] == "BLOCKED_PENDING_XRP_SPECIFIC_EXECUTION_EVIDENCE"


def test_safu_futures_insurance_and_treasury_are_separate_sources():
    funding = SNAPSHOT["funding_sources"]
    assert funding["partial_safu_deployment"]["status"].startswith("ANNOUNCED")
    assert funding["futures_insurance_fund"]["exact_balance"] == "UNKNOWN"
    assert funding["corporate_treasury"]["token_specific_allocation"] == "UNKNOWN"
    assert "BINANCE_SAFU" in {node["id"] for node in GRAPH["nodes"]}
    assert "BINANCE_FUTURES_INSURANCE" in {node["id"] for node in GRAPH["nodes"]}


def test_graph_edges_resolve_and_retain_evidence_class():
    node_ids = {node["id"] for node in GRAPH["nodes"]}
    source_ids = {source["source_id"] for source in SOURCE["sources"]}
    edge_ids = [edge["id"] for edge in GRAPH["edges"]]
    assert len(edge_ids) == len(set(edge_ids))
    for edge in GRAPH["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert set(edge["source_ids"]).issubset(source_ids)
        assert edge["evidence_class"]


def test_coinbase_security_response_is_not_misclassified_as_xrp_demand():
    edge = next(edge for edge in GRAPH["edges"] if edge["id"] == "EDGE-COINBASE-OFFLINE-KEY-HARDENING")
    assert edge["relationship"] == "PRECAUTIONARY_SECURITY_ADJUSTMENT_AFTER_BINANCE_INCIDENT"
    assert "not evidence of a new XRP market position" in edge["claim"]


def test_prediction_remains_not_issued_and_market_feature_admission_is_bounded():
    assert SNAPSHOT["forecast"]["status"] == "NOT_ISSUED"
    assert SNAPSHOT["feature_admission"]["directional_xrp_signal"] == "NOT_ADMITTED"
    assert DECISION["prediction_status"] == "NOT_ISSUED"
    assert DECISION["feature_admission"]["incident_timeline"] == "ADMITTED"
