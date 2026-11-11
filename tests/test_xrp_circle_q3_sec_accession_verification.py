"""Regression checks for the append-only Circle Q3 SEC accession correction."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T130700Z-circle-q3-sec-edgar-accession-verification.json"
PRIOR = ROOT / "research" / "xrp_intelligence" / "20261104T200200Z-circle-q3-source-correction.json"


def test_circle_q3_sec_accession_and_exhibit_are_directly_verified():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    filing = data["sec_filing"]
    assert filing["form"] == "8-K"
    assert filing["accession"] == "0001876042-26-000309"
    assert filing["primary_document_url"].endswith("/crcl-20261104.htm")
    assert filing["exhibit_99_1_url"].endswith("/finalq3epr-110326.htm")
    assert filing["item_2_02"] == "Results of Operations and Financial Condition"
    assert filing["exhibit_99_1_description"] == "Press release dated November 4, 2026"
    assert filing["legal_classification"]["item_2_02_and_exhibit_99_1"].startswith("Furnished")
    assert data["correction_scope"]["current_status"] == "VERIFIED"
    assert data["correction_scope"]["append_only"] is True
    assert data["correction_scope"]["original_artifacts_modified"] is False
    assert data["xrp_relevance"]["model_eligible"] is False


def test_prior_circle_q3_source_correction_is_preserved_as_historical():
    data = json.loads(PRIOR.read_text(encoding="utf-8"))
    assert data["captured_at_utc"] == "2026-11-04T20:02:00Z"
    assert data["correction_overlay"]["consumer_application_status"] == "NOT_EXECUTED_RESEARCH_ONLY_OVERLAY"
    assert data["source_registry"][3]["visible_latest_circle_accession"] == "0001876042-26-000291"


def test_circle_and_coinbase_q3_relationship_evidence_remains_separate():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    groups = data["source_independence"]
    assert groups["circle_8k_and_exhibit_group"] == "circle_issuer"
    assert groups["coinbase_10q_group"] == "coinbase_issuer"
    release = next(item for item in data["source_registry"] if item["source_id"] == "coinbase_q3_2026_earnings_release")
    filing = next(item for item in data["source_registry"] if item["source_id"] == "coinbase_q3_2026_sec_10q")
    assert release["published_at"] == "2026-10-29"
    assert any("$22B" in claim for claim in release["claims_supported"])
    assert not any("$22B" in claim for claim in filing["claims_supported"])
    assert data["financial_observations"][-1]["source_id"] == "coinbase_q3_2026_earnings_release"
    assert data["source_correction_log"][-1]["append_only_history_preserved"] is True
    assert groups["sec_hosting_adds_filing_provenance_not_an_independent_financial_audit"] is True
    assert data["xrp_relevance"]["forecast_issued"] is False
