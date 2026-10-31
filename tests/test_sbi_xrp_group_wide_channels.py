import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES_A = json.loads((ROOT / "data/xrp_intelligence/sources/sbi_xrp_recurring_distribution_20261031.json").read_text(encoding="utf-8"))
SOURCES_B = json.loads((ROOT / "data/xrp_intelligence/sources/sbi_xrp_incentive_channels_20261031.json").read_text(encoding="utf-8"))
SOURCES_C = json.loads((ROOT / "data/xrp_intelligence/sources/sbi_xrp_group_wide_channels_20261031.json").read_text(encoding="utf-8"))
GRAPH_A = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T133048Z-sbi-recurring-xrp-distribution.json").read_text(encoding="utf-8"))
GRAPH_B = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T140328Z-sbi-xrp-incentive-channels.json").read_text(encoding="utf-8"))
GRAPH_C = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T142000Z-sbi-group-wide-channels.json").read_text(encoding="utf-8"))
CORRECTION = json.loads((ROOT / "data/xrp_intelligence/corrections/20261031T142000Z-sbi-shinsei-voucher-timing-correction.json").read_text(encoding="utf-8"))
SNAPSHOT = json.loads((ROOT / "data/xrp_intelligence/snapshots/20261031T142000Z-sbi-group-wide-xrp-distribution-and-market-access.json").read_text(encoding="utf-8"))


def test_all_group_wide_graph_edges_resolve_to_sources_and_nodes():
    source_ids = {item["source_id"] for bundle in (SOURCES_A, SOURCES_B, SOURCES_C) for item in bundle["sources"]}
    node_ids = {item["id"] for graph in (GRAPH_A, GRAPH_B, GRAPH_C) for item in graph["nodes"]}
    edge_ids = {item["id"] for graph in (GRAPH_A, GRAPH_B, GRAPH_C) for item in graph["edges"]}
    assert len(source_ids) == sum(len(bundle["sources"]) for bundle in (SOURCES_A, SOURCES_B, SOURCES_C))
    assert len(node_ids) == sum(len(graph["nodes"]) for graph in (GRAPH_A, GRAPH_B, GRAPH_C))
    assert len(edge_ids) == sum(len(graph["edges"]) for graph in (GRAPH_A, GRAPH_B, GRAPH_C))
    for edge in GRAPH_C["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert set(edge["source_ids"]).issubset(source_ids)


def test_five_shareholder_programs_remain_separate():
    programs = SNAPSHOT["actual_capital_separation"]
    assert programs["shareholder_reward_programs_count"] == 5
    assert programs["recipient_deduplication"] == "NOT_AVAILABLE"
    assert programs["shareholder_program_total_value_jpy"] == "UNKNOWN"


def test_shinsei_deposit_voucher_timing_is_unresolved_not_misclassified_as_contradiction():
    assert CORRECTION["previous_classification"] == "DISCONFIRMING_EVIDENCE_INTERNAL_DATE_INCONSISTENCY"
    assert CORRECTION["corrected_classification"] == "UNRESOLVED_REDEMPTION_SEQUENCE"
    assert "do not prove an internal contradiction" in CORRECTION["correction_reason"]


def test_xrp_jpy_spread_campaign_is_historical_and_not_depth_evidence():
    source = next(item for item in SOURCES_C["sources"] if item["source_id"] == "SRC-SBI-VC-TRADE-XRPJPY-SPREAD-PROMO-20260622")
    assert "JPY 0.5" in source["claims"][0]
    assert any("not a time-weighted average realized spread" in item for item in source["limitations"])
    assert any("June 22–July 3, 2026" in item for item in SNAPSHOT["program_status_as_of_cutoff"]["historical_or_expired_channels"])


def test_registered_accounts_and_reward_face_value_are_not_spot_capital():
    capital = SNAPSHOT["actual_capital_separation"]
    assert capital["sbi_vc_trade_registered_accounts"] == 2_000_000
    assert capital["xrp_specific_active_account_count"] == "UNKNOWN"
    assert capital["open_market_xrp_purchase_value"] == "UNKNOWN"
    assert capital["net_external_xrp_capital"] == "UNKNOWN"


def test_sbi_incentives_are_not_admitted_as_prediction_features():
    assert SNAPSHOT["feature_admission"]["status"] == "NOT_ADMITTED"
    assert SNAPSHOT["forecast"]["status"] == "NOT_ISSUED"
