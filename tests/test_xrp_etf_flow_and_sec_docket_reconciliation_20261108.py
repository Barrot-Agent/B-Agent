from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T011925Z-xrp-etf-flow-universe-and-sec-docket-reconciliation.json"


def test_etf_flow_sources_are_kept_separate_and_model_ineligible():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    alpha = data["etf_flow_reconciliation"]["alpha_finance"]
    insights = data["etf_flow_reconciliation"]["xrp_insights"]
    reconciliation = data["etf_flow_reconciliation"]["reconciliation"]
    assert alpha["fund_count"] == 5
    assert alpha["tickers"] == ["XRP", "XRPZ", "XRPC", "GXRP", "TOXR"]
    assert insights["fund_count"] == 7
    assert insights["tickers"] == ["XRPC", "XRP", "XRPR", "XRPZ", "GXRP", "TOXR", "BITW"]
    assert insights["weekly_flow_xrp"] == -813000
    assert alpha["last_7_session_flow_usd"] == 8400000
    assert reconciliation["status"] == "not_comparable_without_universe_and_method_alignment"
    assert reconciliation["model_feature_policy"]["current_model_eligible"] is False
    assert data["classification"] == "research_only_model_ineligible"


def test_flow_provenance_discloses_missing_raw_bytes_and_normalized_hashes():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["provenance_policy"]["raw_http_bytes_captured"] is False
    assert data["provenance_policy"]["normalized_excerpt_hashes_are_not_raw_source_hashes"] is True
    for source in data["source_receipts"]:
        assert source["raw_bytes_captured"] is False
        digest = source.get("normalized_excerpt_sha256")
        assert digest is None or (len(digest) == 64 and all(c in "0123456789abcdef" for c in digest))


def test_coinbase_and_ripple_letters_are_assigned_to_distinct_sec_dockets():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    regulatory = data["sec_docket_reconciliation"]
    assert regulatory["coinbase_letter"]["docket"] == "S7-2026-27"
    assert regulatory["ripple_letter"]["docket"] == "S7-2026-09"
    assert regulatory["coinbase_letter"]["date"] == "2026-10-20"
    assert regulatory["ripple_letter"]["date"] == "2026-05-07"
    assert regulatory["proposed_rule"]["status"] == "PROPOSED"
    assert len(regulatory["later_staff_activity"]) == 2


def test_fund_structure_and_custody_flags_prevent_double_counting():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    notes = data["custody_and_exposure_notes"]
    assert "39.90% CoinShares Physical XRP ETP" in notes["XRPR"]
    assert "monthly rebalancing" in notes["BITW"]
    assert "Coinbase Custody Trust Company" in notes["XRPZ"]
    assert data["etf_flow_reconciliation"]["xrp_insights"]["excluded_or_special_cases"]["GXRP"].startswith("Flow excluded")
