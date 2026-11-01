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
    assert haircut["standard_margin_x_sm_haircut_pct"] == 15
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


def test_coinbase_q3_filing_is_pre_integration_disconfirmation_not_post_integration_proof():
    source = load(f"data/xrp_intelligence/source_revisions/20261101T215500Z-coinbase-xrp-collateral-q3-disconfirmation.json")
    ledger = load(f"data/xrp_intelligence/research_ledger_addenda/20261101T215500Z-coinbase-xrp-collateral-q3-disconfirmation.json")
    snapshot = load(f"data/xrp_intelligence/snapshots/20261101T215500Z-coinbase-xrp-collateral-q3-disconfirmation.json")
    custody = next(item for item in source["sources"] if item["id"] == f"SRC-DERIBIT-CUSTODY-POLICY-2026-10-14-20261101T215500Z")
    assert snapshot["coinbase_q3_2026"]["recognized_derivatives_collateral_usd"] == 325766000
    assert snapshot["coinbase_q3_2026"]["xrp_in_recognized_derivatives_collateral_table"] is False
    assert snapshot["coinbase_q3_2026"]["unrecognized_customer_lending_crypto_usd"] == 2804112000
    assert "to be added after September 2026" in " ".join(custody["claims"])
    assert any(item["classification"] == "DISCONFIRMING_EVIDENCE" for item in ledger["findings"])
    assert ledger["feature_admission"] == "NONE"
    assert ledger["forecast_status"] == "NOT_ISSUED"


def test_cftc_26_05_post_initial_xrp_eligibility_requires_a_verified_route():
    source = load(f"data/xrp_intelligence/source_revisions/20261101T220100Z-cftc-26-05-xrp-eligibility.json")
    ledger = load(f"data/xrp_intelligence/research_ledger_addenda/20261101T220100Z-cftc-26-05-xrp-eligibility.json")
    snapshot = load(f"data/xrp_intelligence/snapshots/20261101T220100Z-cftc-26-05-xrp-eligibility.json")
    letter = next(item for item in source["sources"] if item["id"] == f"SRC-CFTC-26-05-20261101T220100Z")
    assert any("minimum is 20%" in claim for claim in letter["claims"])
    assert any("revised risk-management policies" in claim for claim in letter["claims"])
    assert snapshot["cftc_26_05"]["initial_allowed_assets"] == ["payment stablecoins", "BTC", "ETH"]
    assert snapshot["cfm_actual_status"]["foreign_clearing_qualification_under_26_05"] == "UNKNOWN"
    assert any(item["classification"] == "UNKNOWN_LEGAL_QUALIFICATION" for item in ledger["findings"])
    assert ledger["feature_admission"] == "NONE"


def test_deribit_xrp_is_cross_collateral_only_not_offset_currency():
    correction = load(f"data/xrp_intelligence/snapshots/20261101T220500Z-deribit-xrp-cross-collateral-column-correction.json")
    ledger = load(f"data/xrp_intelligence/research_ledger_addenda/20261101T220500Z-deribit-xrp-cross-collateral-column-correction.json")
    row = correction["venue_haircut"]
    assert row["cross_collateral_currency"] is True
    assert row["offset_currency"] is False
    assert row["x_pm_haircut"] == "no haircut stated"
    assert row["x_sm_haircut_pct"] == 15
    assert ledger["correction"]["previous_value"] is True
    assert ledger["correction"]["corrected_value"] is False
