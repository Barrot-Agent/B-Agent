import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "xrp_intelligence"
STAMP = "20261101T181734Z"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_new_source_revision_uses_canonical_ids_and_contains_project_trinity():
    source = load(f"source_revisions/{STAMP}-xrpl-exchange-etf-stablecoin-x402-sources.json")
    ids = {item["id"] for item in source["sources"]}
    assert "sbi-project-trinity-2026-10-06" in ids
    assert "sbiholdings-sbi-ripple-asia-ownership-60pct" in ids
    assert "sbi-remit-xrp-corridor-2023-09-06" in ids
    assert "sbi-remit-cumulative-remittances-2026-05-29" in ids
    assert "sbic-tokyo-profile" in ids
    assert "sbic-ai-training-2025-06-12" in ids
    assert all(item.get("url") and item.get("classification") is not None for item in source["sources"])


def test_graph_does_not_attribute_direct_xrp_use_to_sbi_ripple_asia():
    graph = load(f"relationship_graph_addenda/{STAMP}-sbi-circle-arc-coinbase-xrpl-agentic-graph.json")
    edges = graph["edges"]
    assert not any(e["from"] == "SBI_Ripple_Asia" and e["to"] in {"XRP", "XRPL"} for e in edges)
    assert any(e["from"] == "SBI_Group" and e["to"] == "SBI_Ripple_Asia" and "60_percent" in e["relation"] for e in edges)
    assert not any(e["from"] == "SBI_Remit" and e["to"] == "XRP" for e in edges)
    assert any(e["from"] == "SBI_Remit" and e["to"] == "SBI_VC_Trade" for e in edges)
    assert any(e["from"] == "SBI_VC_Trade" and e["to"] == "XRP" for e in edges)
    assert any(e["from"] == "Tranglo" and e["to"] == "Beneficiary_Bank" for e in edges)
    assert any(e["from"] == "Project_Trinity" and e["to"] == "SMBC" for e in edges)
    assert any(e["from"] == "SBI_Ripple_Asia" and "does_not_handle_XRP" in e["relation"] for e in edges)
    assert any(e["from"] == "SBI_VC_Trade" and e["to"] == "RLUSD" for e in edges)
    assert any(e["from"] == "SBI_VC_Trade" and e["to"] == "USDC" for e in edges)


def test_graph_and_ledger_source_references_resolve():
    source = load(f"source_revisions/{STAMP}-xrpl-exchange-etf-stablecoin-x402-sources.json")
    graph = load(f"relationship_graph_addenda/{STAMP}-sbi-circle-arc-coinbase-xrpl-agentic-graph.json")
    ledger = load(f"research_ledger_addenda/{STAMP}-xrp-stablecoin-supply-and-agentic-payment-addendum.json")
    ids = {item["id"] for item in source["sources"]}
    graph_ids = {edge["source_id"] for edge in graph["edges"] if edge.get("source_id")}
    ledger_ids = {item["source_id"] for item in ledger["findings"] if item.get("source_id")}
    assert graph_ids <= ids
    assert ledger_ids <= ids
