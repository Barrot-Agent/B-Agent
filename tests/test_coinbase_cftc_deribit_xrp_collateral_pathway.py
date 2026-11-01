import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261101T215000Z"


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_cftc_letter_26_17_names_xrp_and_defines_conditional_cfm_path():
    source = load(f"data/xrp_intelligence/source_revisions/{STAMP}-coinbase-cftc-deribit-xrp-collateral-pathway.json")
    letter = next(item for item in source["sources"] if item["id"] == f"SRC-CFTC-26-17-{STAMP}")
    assert any("XRP" in claim and "digital commodities" in claim for claim in letter["claims"])
    assert any("right of re-use" in claim for claim in letter["claims"])
    assert any("not binding" in limitation.lower() for limitation in letter["limitations"])


def test_deribit_current_xrp_cross_collateral_status_supersedes_old_offset_only_state():
    snapshot = load(f"data/xrp_intelligence/snapshots/{STAMP}-coinbase-cftc-deribit-xrp-collateral-pathway.json")
    haircut = snapshot["venue_haircut"]
    assert haircut["cross_collateral_currency"] is True
    assert haircut["offset_currency"] is True
    assert haircut["standard_margin_x_sm_haircut_pct"] == 15
    assert haircut["portfolio_margin_x_pm_haircut_display"] == "dash/no haircut stated"
    assert snapshot["status_matrix"][5]["status"] == "UNKNOWN"
    assert snapshot["status_matrix"][6]["status"] == "UNKNOWN"


def test_coinbase_deribit_collateral_graph_does_not_claim_actual_xrp_usage():
    graph = load(f"data/xrp_intelligence/relationship_graph_addenda/{STAMP}-coinbase-cftc-deribit-xrp-collateral-pathway.json")
    ledger = load(f"data/xrp_intelligence/research_ledger_addenda/{STAMP}-coinbase-cftc-deribit-xrp-collateral-pathway.json")
    assert any(edge["from"] == "COINBASE_FINANCIAL_MARKETS" and edge["to"] == "COINBASE_BERMUDA" for edge in graph["edges"])
    assert any(edge["from"] == "XRP" and edge["to"] == "DERIBIT" for edge in graph["edges"])
    assert graph["conditional_path"]["actual_usage_status"] == "UNKNOWN_NOT_VERIFIED"
    assert ledger["feature_admission"] == "NONE"
    assert ledger["forecast_status"] == "NOT_ISSUED"
    assert any(item["classification"] == "DISCONFIRMING_EVIDENCE" for item in ledger["findings"])
