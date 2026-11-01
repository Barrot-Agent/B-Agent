import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_ripple_institutional_and_macro_addendum_separates_company_claims_from_xrp_flows():
    ripple = load("data/xrp_intelligence/source_revisions/20261101T143000Z-ripple-institutional-treasury-prime-and-xrpl-adoption.json")
    macro = load("data/xrp_intelligence/source_revisions/20261101T143000Z-fed-treasury-sofr-macro.json")
    snapshot = load("data/xrp_intelligence/snapshots/20261101T143000Z-ripple-institutional-adoption-and-macro-snapshot.json")
    graph = load("data/xrp_intelligence/relationship_graph_addenda/20261101T143000Z-ripple-prime-treasury-bny-privy-and-collateral-graph.json")
    decision = load("data/xrp_intelligence/architecture_decisions/20261101T143000Z-ripple-prime-collateral-vs-cbxrp-and-macro.json")
    handoff = load("data/xrp_intelligence/hand_offs/20261101T143000Z-ripple-institutional-and-macro-handoff.json")
    ledger = load("data/xrp_intelligence/research_ledger_addenda/20261101T143000Z-ripple-institutional-and-macro-ledger-addendum.json")

    assert any("not XRP-specific volume" in item for item in ripple["sources"][1]["limitations"])
    assert "both dissenters preferred a 25bp rate increase" in macro["sources"][0]["claims"][1]
    assert snapshot["macro"]["target_range_pct"] == [3.75, 4.0]
    assert snapshot["ripple_institutional_products"]["ripple_prime"].startswith("provides cross-margining")
    assert any(edge["from"] == "BNY" and edge["to"] == "Ripple" for edge in graph["edges"])
    assert decision["forecast_status"] == "NOT_ISSUED"
    assert handoff["forecast_status"] == "NOT_ISSUED"
    assert ledger["feature_admission"] == "none"
