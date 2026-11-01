import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "xrp_intelligence"


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_coinbase_circle_sbi_financial_addendum_is_consistent():
    source = load("data/xrp_intelligence/sources/20261101T140000Z-coinbase-circle-sbi-arc-cbxrp-source-bundle.json")
    snapshot = load("data/xrp_intelligence/snapshots/20261101T140000Z-coinbase-circle-sbi-arc-cbxrp-financial-snapshot.json")
    graph = load("data/xrp_intelligence/relationship_graph_addenda/20261101T140000Z-coinbase-circle-sbi-arc-cbxrp-graph.json")
    decision = load("data/xrp_intelligence/architecture_decisions/20261101T140000Z-coinbase-circle-cbxrp-and-actual-capital-decisions.json")
    handoff = load("data/xrp_intelligence/hand_offs/20261101T140000Z-coinbase-circle-sbi-arc-cbxrp-handoff.json")

    source_ids = {item["id"] for item in source["sources"]}
    assert "coinbase-q3-2026-10q" in source_ids
    assert "circle-q2-2026-10q" in source_ids
    assert "circle-binance-strategic-partnership-20260922" in source_ids
    assert "sbi-remit-xrp-corridors-20230906" in source_ids
    assert "sbic-chatgpt-training-20250612" in source_ids

    observations = snapshot["observations"]
    assert observations["coinbase_q3_2026"]["circle_arrangement"] == "renewed on same terms"
    assert observations["coinbase_q3_2026"]["gains_on_crypto_assets_held_for_investment_usd"] == 715022000
    assert observations["circle_q2_2026"]["usdc_on_coinbase_end_usd"] == 12442000000
    assert observations["sbi_xrp_payments"]["confirmed_xrp_bridge_use"] is True
    assert observations["sbic"]["distinct_from"] == "SBI Holdings / SBI Group"
    assert observations["ripple_coinbase_rlusd"]["global_exchange_collateral_status"] == "future_not_live_at_announcement"

    cbxrp = observations["cbxrp"]
    assert cbxrp["reserve_xrp"] > cbxrp["total_supply_cbxrp"]
    assert abs(cbxrp["surplus_xrp"] - (cbxrp["reserve_xrp"] - cbxrp["total_supply_cbxrp"])) < 0.01

    edge_pairs = {(edge["from"], edge["to"]) for edge in graph["edges"]}
    assert ("Coinbase", "Circle") in edge_pairs
    assert ("Coinbase", "Ripple") in edge_pairs
    assert ("SBI_Remit", "XRP") in edge_pairs
    assert ("Circle", "Binance") in edge_pairs
    assert ("SBI_Holdings", "Arc") in edge_pairs

    assert decision["feature_admission"] == "none"
    assert decision["forecast_status"] == "NOT_ISSUED"
    assert handoff["forecast_status"] == "NOT_ISSUED"
    assert handoff["safety"]["main_modified"] is False

    ledger = load("data/xrp_intelligence/research_ledger_addenda/20261101T140000Z-coinbase-circle-sbi-arc-cbxrp-ledger-addendum.json")
    assert ledger["forecast_status"] == "NOT_ISSUED"
    assert ledger["artifacts"]["relationship_graph"].endswith("20261101T140000Z-coinbase-circle-sbi-arc-cbxrp-graph.json")
    assert "sbi-remit-xrp-corridors-20230906" in ledger["source_ids"]

    arc_revision = load("data/xrp_intelligence/source_revisions/20261101T141200Z-circle-arc-mainnet-canonical-url-and-capability-correction.json")
    assert arc_revision["canonical_urls"][0].endswith("circle-launches-arc-mainnet-an-economic-operating-system-for-the-internet")
    assert "Circle_Payments_Network" in {node["id"] for node in load("data/xrp_intelligence/relationship_graph_addenda/20261101T141200Z-circle-arc-cpn-stablefx-and-xrpl-competitive-graph.json")["nodes"]}

    fee_revision = load("data/xrp_intelligence/source_revisions/20261101T141500Z-xrpl-usdc-fee-burn-and-xrp-bridge-correction.json")
    assert "Every validated XRPL transaction destroys a small amount of XRP" in fee_revision["claims"][0]
    sbi_revision = load("data/xrp_intelligence/source_revisions/20261101T141500Z-sbi-vctrade-rlusd-type4-and-chain-scope-correction.json")
    assert "SBI's primary June 24 announcement does not specify" in sbi_revision["corrections_and_limitations"][0]
    sbi_graph = load("data/xrp_intelligence/relationship_graph_addenda/20261101T141500Z-sbi-vctrade-rlusd-type4-chain-scope-graph.json")
    assert any(edge["status"] == "unknown_not_established_by_primary_release" for edge in sbi_graph["edges"])
