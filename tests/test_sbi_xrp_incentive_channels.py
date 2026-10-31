import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXISTING_SOURCES = json.loads((ROOT / "data/xrp_intelligence/sources/sbi_xrp_recurring_distribution_20261031.json").read_text(encoding="utf-8"))
SOURCES = json.loads((ROOT / "data/xrp_intelligence/sources/sbi_xrp_incentive_channels_20261031.json").read_text(encoding="utf-8"))
EXISTING_GRAPH = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T133048Z-sbi-recurring-xrp-distribution.json").read_text(encoding="utf-8"))
GRAPH = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T140328Z-sbi-xrp-incentive-channels.json").read_text(encoding="utf-8"))
SNAPSHOT = json.loads((ROOT / "data/xrp_intelligence/snapshots/20261031T140328Z-sbi-xrp-incentive-channels-and-actual-capital.json").read_text(encoding="utf-8"))


def test_all_new_graph_nodes_edges_and_sources_resolve():
    source_ids = {item["source_id"] for item in EXISTING_SOURCES["sources"] + SOURCES["sources"]}
    node_ids = {item["id"] for item in EXISTING_GRAPH["nodes"] + GRAPH["nodes"]}
    assert len(source_ids) == len(EXISTING_SOURCES["sources"]) + len(SOURCES["sources"])
    assert len(node_ids) == len(EXISTING_GRAPH["nodes"]) + len(GRAPH["nodes"])
    edge_ids = {item["id"] for item in EXISTING_GRAPH["edges"] + GRAPH["edges"]}
    assert len(edge_ids) == len(EXISTING_GRAPH["edges"]) + len(GRAPH["edges"])
    for edge in GRAPH["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert edge["source_ids"]
        assert set(edge["source_ids"]).issubset(source_ids)
    for finding in SNAPSHOT["confirmed_findings"]:
        assert set(finding["source_ids"]).issubset(source_ids)


def test_start_bond_reward_upper_bound_is_two_tenths_percent_of_issue():
    capital = SNAPSHOT["actual_capital_separation"]
    assert capital["bond_principal_jpy"] == 10_000_000_000
    assert capital["bond_xrp_reward_rate"] == 0.002
    assert capital["bond_max_theoretical_reward_jpy"] == 20_000_000
    assert capital["bond_max_reward_status"] == "INFERRED_UPPER_BOUND_NOT_ACTUAL_REDEMPTION"


def test_start_bond_reward_is_separate_from_ibet_security_token_rail():
    edges = {item["id"]: item for item in GRAPH["edges"]}
    assert edges["EDGE-SBI-START-BOND-IBET-FIN"]["target"] == "IBET_FOR_FIN"
    assert edges["EDGE-SBI-START-BOND-XRP-INCENTIVE"]["target"] == "XRP"


def test_shinsei_campaign_timeline_inconsistency_is_preserved():
    source = next(item for item in SOURCES["sources"] if item["source_id"] == "SRC-SBI-SHINSEI-DEPOSIT-XRP-COUPON-20260202")
    assert any("July 2" in item for item in source["limitations"])
    assert "date_inconsistency" in SNAPSHOT["actual_capital_separation"]["bank_deposit_campaign"]


def test_registered_account_count_is_not_xrp_holder_count():
    metric = SNAPSHOT["actual_capital_separation"]
    assert metric["registered_vc_trade_accounts"] == 2_000_000
    assert metric["account_count_is_xrp_holders"] is False


def test_rewards_and_market_impact_are_not_admitted_as_prediction_features():
    assert SNAPSHOT["feature_admission"]["status"] == "NOT_ADMITTED"
    assert SNAPSHOT["forecast"]["status"] == "NOT_ISSUED"
    assert SNAPSHOT["actual_capital_separation"]["open_market_xrp_purchase_value"] == "UNKNOWN"
    assert SNAPSHOT["actual_capital_separation"]["net_external_xrp_capital"] == "UNKNOWN"
