import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data/xrp_intelligence/sources/20261031T162903Z-sbi-xrp-dca-card-terms.json").read_text(encoding="utf-8"))
SNAPSHOT = json.loads((ROOT / "data/xrp_intelligence/snapshots/20261031T162903Z-sbi-xrp-dca-card-capital.json").read_text(encoding="utf-8"))
GRAPH = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T162903Z-sbi-xrp-dca-card-graph.json").read_text(encoding="utf-8"))
ADR = json.loads((ROOT / "data/xrp_intelligence/architecture_decisions/20261031T162903Z-sbi-dca-actual-capital.json").read_text(encoding="utf-8"))


def test_sbi_dca_terms_are_primary_and_bounded():
    source = next(x for x in SOURCE["sources"] if "DCA-TERMS" in x["source_id"])
    claims = " ".join(source["claims"])
    assert "JPY 500" in claims and "JPY 2,000,000" in claims
    assert "daily, weekly or monthly" in claims
    assert "does not automatically debit" in claims
    assert "XRP-specific active-plan count" in " ".join(source["limitations"])


def test_card_reward_conversion_is_not_misclassified_as_spot_buy():
    source = next(x for x in SOURCE["sources"] if "VISA-CRYPTO-CARD-TERMS" in x["source_id"])
    claims = " ".join(source["claims"])
    assert "automatically converted" in claims
    assert "campaign as ended" in claims
    assert "not proof of a customer-funded open-market XRP purchase" in " ".join(source["limitations"])


def test_graph_edges_resolve_to_declared_sources_and_nodes():
    source_ids = {x["source_id"] for x in SOURCE["sources"]}
    node_ids = {x["id"] for x in GRAPH["nodes"]}
    edge_ids = [x["id"] for x in GRAPH["edges"]]
    assert len(edge_ids) == len(set(edge_ids))
    for edge in GRAPH["edges"]:
        assert edge["source"] in node_ids and edge["target"] in node_ids
        assert set(edge["source_ids"]).issubset(source_ids)


def test_actual_capital_and_price_feature_remain_unquantified():
    actual = SNAPSHOT["actual_capital_separation"]
    assert actual["active_xrp_dca_plan_count"] == "UNKNOWN"
    assert actual["monthly_xrp_units_filled"] == "UNKNOWN"
    assert actual["external_spot_or_otc_sourcing"] == "UNKNOWN"
    assert actual["net_external_xrp_capital"] == "UNKNOWN"
    assert SNAPSHOT["feature_admission"]["directional_xrp_price_feature"] == "NOT_ADMITTED"
    assert SNAPSHOT["forecast"]["status"] == "NOT_ISSUED"
    assert ADR["forecast_status"] == "NOT_ISSUED"
