import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_stablecoin_trust_bank_status_and_genius_effective_date_are_distinguished():
    revision = load("data/xrp_intelligence/source_revisions/20261101T142500Z-occ-trust-charter-status-comparison.json")
    graph = load("data/xrp_intelligence/relationship_graph_addenda/20261101T142500Z-occ-trust-charter-ripple-circle-coinbase-graph.json")
    decision = load("data/xrp_intelligence/architecture_decisions/20261101T142500Z-stablecoin-trust-bank-status-and-genius-effective-date.json")
    handoff = load("data/xrp_intelligence/hand_offs/20261101T142500Z-occ-trust-bank-and-genius-act-regulatory-handoff.json")
    ledger = load("data/xrp_intelligence/research_ledger_addenda/20261101T142500Z-occ-trust-charter-genius-act-ledger-addendum.json")

    assert revision["comparison"]["coinbase"].startswith("OCC primary preliminary conditional approval")
    assert revision["comparison"]["circle"].startswith("company-reported final approval")
    assert revision["comparison"]["ripple"].startswith("company-reported final approval")
    assert any("January 18 2027" in item["claims"][0] for item in revision["sources"] if item["id"] == "occ-genius-final-rule-20261021")
    assert "not disconfirmation" in revision["sources"][0]["limitations"][1]
    assert decision["forecast_status"] == "NOT_ISSUED"
    assert handoff["forecast_status"] == "NOT_ISSUED"
    assert ledger["status_classes"] == ["conditional", "final_approved_preopening", "operational", "permitted_payment_stablecoin_issuer"]
    assert any(edge["status"] == "OCC_primary_conditional_approval_1370" for edge in graph["edges"])
