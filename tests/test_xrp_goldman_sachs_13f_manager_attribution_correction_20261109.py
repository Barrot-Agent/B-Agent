import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261109T013133Z-goldman-sachs-xrp-etf-13f-manager-attribution-correction.json"
)


def test_goldman_xrp_13f_positions_reconcile_to_primary_sec_rows():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["filing"]["accession"] == "0000886982-26-000519"
    assert artifact["filing"]["report_period_end"] == "2026-06-30"
    assert artifact["included_manager_attribution"]["row_manager_number"] == 1
    assert artifact["included_manager_attribution"]["included_manager_name"] == "GOLDMAN SACHS & CO. LLC"
    assert artifact["included_manager_attribution"]["cik"] == "0000769993"
    positions = artifact["positions"]
    assert len(positions) == 5
    assert {row["other_manager_number"] for row in positions} == {1}
    assert sum(row["value_usd"] for row in positions) == 86_506_129
    assert sum(row["shares"] for row in positions) == 7_390_191


def test_goldman_q1_to_q2_13f_first_reportable_appearance_is_qualified():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    comparison = artifact["prior_quarter_comparison"]
    q1 = comparison["q1"]
    q2 = comparison["q2"]
    assert q1["accession"] == "0000886982-26-000274"
    assert q1["report_period_end"] == "2026-03-31"
    assert q1["xrp_named_information_table_row_count"] == 0
    assert q1["exact_search_result"] == "No matching text found for XRP"
    assert q1["included_manager_no_1"] == "GOLDMAN SACHS & CO. LLC"
    assert q1["q1_no_q2_cusips_present"] is True
    assert {x["cusip"] for x in q1["q1_cusip_search_results"]} == {row["cusip"] for row in artifact["positions"]}
    assert all(x["result"] == "No matching text found" for x in q1["q1_cusip_search_results"])
    assert q2["xrp_named_information_table_row_count"] == 5
    assert q2["aggregate_reported_value_usd"] == 86_506_129
    assert "all five Q2 CUSIPs" in comparison["temporal_interpretation"]
    assert "does not prove purchases" in comparison["temporal_interpretation"]


def test_goldman_13f_does_not_claim_parent_proprietary_xrp_capital():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["model_eligible"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert "does not establish" in artifact["correction"]["unresolved"]
    assert "not XRP tokens" in artifact["reconciliation"]["interpretation"]
    assert artifact["actual_capital_classification"] == "Reported ETF-share securities exposure; not verified XRP-token capital deployment."


def test_goldman_13f_normalized_source_excerpt_hashes_are_sha256():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    hashes = artifact["provenance"]["normalized_excerpt_sha256"]
    expected = {"filing_index", "primary_document_manager_mapping", "information_table_xrp_rows", "q1_manager_mapping", "q1_xrp_absence_search_record"}
    expected.update(f"q1_cusip_{cusip}_absence_search_record" for cusip in ("90137T103", "09174F107", "13723M100", "355233107", "38965L106"))
    assert set(hashes) == expected
    for digest in hashes.values():
        assert len(digest) == 64
        int(digest, 16)
