import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "xrp_intelligence"


def load(path):
    return json.loads((DATA / path).read_text(encoding="utf-8"))


def test_candidate_morpho_market_is_not_mislabeled_as_coinbase_book():
    snap = load("snapshots/20261101T133000Z-cbxrp-circle-sbi-sbic-snapshot.json")
    assert snap["observations"]["morpho_candidate_market"]["lltv_pct"] == 62.5
    assert snap["observations"]["coinbase_product"]["generic_documented_liquidation_ltv_pct"] == 86
    assert snap["observations"]["coinbase_product"]["exact_xrp_market_id_published_by_coinbase"] is False
    assert snap["interpretation"]["inference"].startswith("Morpho Watch")
    assert "86%" in snap["interpretation"]["disconfirming_evidence"][0]
    assert "62.5%" in snap["interpretation"]["disconfirming_evidence"][0]


def test_cbxrp_reserve_and_collateral_math_are_consistent():
    snap = load("snapshots/20261101T133000Z-cbxrp-circle-sbi-sbic-snapshot.json")
    obs = snap["observations"]
    assert obs["cbxrp"]["total_reserve_xrp"] > obs["cbxrp"]["total_supply_cbxrp"]
    assert abs(obs["cbxrp"]["reserve_surplus_xrp"] - 2247.53) < 0.01
    assert 78.0 < snap["derived_metrics"]["cbxrp_supply_in_candidate_market_share_pct"] < 79.0
    assert 39.0 < snap["derived_metrics"]["candidate_market_aggregate_debt_to_collateral_pct"] < 41.0


def test_market_liquidation_metrics_remain_secondary_and_quarantined():
    snap = load("snapshots/20261101T133000Z-cbxrp-circle-sbi-sbic-snapshot.json")
    market = snap["observations"]["morpho_candidate_market"]
    assert market["liquidations_30d_reported"] == 1122
    assert market["debt_repaid_by_liquidations_30d_usdc"] == 3940000
    assert snap["feature_admission"] == "none; all Morpho Watch aggregates remain quarantined pending raw block-level reconstruction"


def test_coinbase_circle_economics_are_separate_from_xrp_capital_flows():
    snap = load("snapshots/20261101T133000Z-cbxrp-circle-sbi-sbic-snapshot.json")
    cb = snap["observations"]["coinbase_financials_q3_2026"]
    circle = snap["observations"]["circle_financials_q2_2026"]
    assert cb["stablecoin_revenue_q3_usd"] == 306905000
    assert cb["usdc_average_on_platform"] == "all-time high"
    assert circle["distribution_costs_to_coinbase_q2_usd"] == 324600000
    assert "not evidence" in snap["interpretation"]["actual_capital"].lower()


def test_sbi_group_and_tokyo_sbic_are_distinct_entities():
    sources = load("sources/20261101T133000Z-cbxrp-circle-sbi-sbic-source-bundle.json")
    entities = sources["entity_disambiguation"]
    assert entities["SBIC"]["distinct_from"] == "SBI Holdings / SBI Group"
    assert entities["SBIC"]["xrp_relationship"] == "none publicly established"
    assert entities["SBI_Group"]["ripple_relationship"].startswith("SBI Holdings reports")


def test_relationship_graph_keeps_unconfirmed_edges_explicit():
    graph = load("relationship_graph_addenda/20261101T133000Z-cbxrp-circle-sbi-sbic-graph.json")
    edges = graph["edges"]
    candidate = next(e for e in edges if e["from"] == "cbXRP" and e["to"] == "Morpho")
    assert "unconfirmed" in candidate["status"]
    unknowns = graph["disconfirming_or_unknown_edges"]
    assert any(e["from"] == "Tokyo_SBIC" and e["to"] == "XRP" for e in unknowns)


def test_no_directional_forecast_was_issued():
    snap = load("snapshots/20261101T133000Z-cbxrp-circle-sbi-sbic-snapshot.json")
    assert snap["forecast_status"] == "NOT_ISSUED"
    assert snap["forecasts"] == []
