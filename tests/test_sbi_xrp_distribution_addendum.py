import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data/xrp_intelligence/sources/sbi_xrp_recurring_distribution_20261031.json"
GRAPH_PATH = ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T133048Z-sbi-recurring-xrp-distribution.json"
SNAPSHOT_PATH = ROOT / "data/xrp_intelligence/snapshots/20261031T133048Z-sbi-recurring-xrp-distribution-and-multirail.json"

SOURCES = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
GRAPH = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
SNAPSHOT = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_graph_edges_resolve_declared_nodes_and_primary_sources():
    source_ids = {item["source_id"] for item in SOURCES["sources"]}
    node_ids = {item["id"] for item in GRAPH["nodes"]}

    assert len(source_ids) == len(SOURCES["sources"])
    assert len(node_ids) == len(GRAPH["nodes"])
    for edge in GRAPH["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert edge["source_ids"]
        assert set(edge["source_ids"]).issubset(source_ids)


def test_snapshot_source_and_hypothesis_references_resolve():
    source_ids = {item["source_id"] for item in SOURCES["sources"]}
    hypothesis_ids = {item["id"] for item in GRAPH["hypotheses"]}

    for finding in SNAPSHOT["confirmed_findings"]:
        assert set(finding["source_ids"]).issubset(source_ids)
    for observation in SNAPSHOT["market_observations"]:
        assert set(observation["source_ids"]).issubset(source_ids)
    assert set(SNAPSHOT["hypotheses"]).issubset(hypothesis_ids)


def test_market_impact_and_forecast_remain_unadmitted():
    assert SNAPSHOT["feature_admission"]["status"] == "NOT_ADMITTED"
    assert SNAPSHOT["forecast"]["status"] == "NOT_ISSUED"
    assert SNAPSHOT["safety"].startswith("Research and shadow evaluation only.")


def test_sbi_wallet_observation_is_not_misclassified_as_official_flow():
    wallet_source = next(
        item for item in SOURCES["sources"]
        if item["source_id"] == "SRC-SBI-VC-TRADE-XRP-WALLET-BALANCES-20261031"
    )
    assert wallet_source["evidence_class"] == "SECONDARY_UNVERIFIED"
    assert any("pooled customer custody" in item for item in wallet_source["limitations"])


def test_sbi_shareholder_xrp_coupon_is_historical_and_not_open_market_flow():
    source = next(
        item for item in SOURCES["sources"]
        if item["source_id"] == "SRC-SBI-HOLDINGS-XRP-SHAREHOLDER-BENEFIT-20260204"
    )
    edge = next(
        item for item in GRAPH["edges"]
        if item["id"] == "EDGE-SBI-HOLDINGS-XRP-SHAREHOLDER-BENEFIT"
    )
    finding = next(item for item in SNAPSHOT["confirmed_findings"] if item["id"] == "F8")

    assert source["evidence_class"] == "CONFIRMED_PRIMARY_SOURCE"
    assert any("deadline has passed" in item for item in source["limitations"])
    assert any("procurement source" in item for item in source["limitations"])
    assert edge["source_ids"] == [source["source_id"]]
    assert finding["source_ids"] == [source["source_id"]]
