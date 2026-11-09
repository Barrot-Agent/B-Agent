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
    assert set(hashes) == {"filing_index", "primary_document_manager_mapping", "information_table_xrp_rows"}
    for digest in hashes.values():
        assert len(digest) == 64
        int(digest, 16)
