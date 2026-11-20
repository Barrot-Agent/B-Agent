from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "research" / "xrp_intelligence" / "20261108T000206Z-sec-xrp-digital-commodity-and-rulemaking-status.json"
XRPL = ROOT / "research" / "xrp_intelligence" / "20261108T000206Z-xrpl-lending-amendment-vote-denominator-reconciliation.json"
LETTERS = ROOT / "research" / "xrp_intelligence" / "20261108T002500Z-coinbase-ripple-sec-comment-letter-reconciliation.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_sec_artifact_preserves_only_short_excerpts_and_hashes():
    data = read(SEC)
    assert data["source_registry"]
    for source in data["source_registry"]:
        excerpt = source.get("normalized_excerpt")
        digest = source.get("normalized_excerpt_sha256")
        if excerpt is not None:
            assert digest == hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
            assert len(excerpt.split()) <= 25
    assert data["capture"]["raw_http_bytes_captured"] is False


def test_xrpl_artifact_preserves_only_short_excerpts_and_hashes():
    data = read(XRPL)
    for source in data["source_registry"]:
        excerpt = source.get("normalized_excerpt")
        digest = source.get("normalized_excerpt_sha256")
        if excerpt is not None:
            assert digest == hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
            assert len(excerpt.split()) <= 25
    assert data["capture"]["raw_http_bytes_captured"] is False


def test_coinbase_letter_is_primary_company_submission_with_date_and_signatories():
    data = read(LETTERS)["coinbase"]
    assert data["letter_date"] == "2026-10-20"
    assert data["file_number"] == "S7-2026-27"
    assert {x["name"] for x in data["signatories"]} == {"Molly Abraham", "Scott Bauguess"}
    assert data["position"] == "SUPPORTS_PROPOSED_FRAMEWORK_WITH_REFINEMENTS"


def test_ripple_letter_is_primary_company_submission_with_date_and_signatories():
    data = read(LETTERS)["ripple"]
    assert data["letter_date"] == "2026-05-07"
    assert data["file_number"] == "S7-2026-09"
    assert {x["name"] for x in data["signatories"]} == {"Stuart Alderoty", "Sameer Dhond", "Deborah McCrimmon"}
    assert data["position"] == "SUPPORTS_INTERPRETATION_SEEKS_FURTHER_GUIDANCE"


def test_coinbase_and_ripple_positions_are_not_collapsed():
    data = read(LETTERS)["comparison"]
    assert "Coinbase asks" in data["material_difference"]
    assert "Ripple asks" in data["material_difference"]
    assert "not effective" in data["agency_position"]


def test_comment_letters_are_not_misrepresented_as_law_or_court_holdings():
    data = read(LETTERS)
    assert "not law" in data["executive_findings"][4]
    assert "not a court ruling" in data["source_registry"][4]["summary"]


def test_circle_or_sbi_nonappearance_is_not_claimed_as_absence():
    data = read(LETTERS)
    assert "does not establish that none exists" in data["executive_findings"][6]
    assert "No matching Circle or SBI letter was identified" in data["relationship_to_xrp"]["circle_sbi_status"]


def test_ripple_central_party_question_remains_unresolved():
    data = read(SEC)["staff_faq"]["central_party_test"]
    assert data["ripple_specific_status"] == "UNRESOLVED_NO_PRIMARY_VALIDATOR_CONTROL_EVIDENCE_IN_THIS_RUN"
    assert data["research_requirements"]


def test_comment_letter_artifact_is_not_a_directional_feature():
    data = read(LETTERS)
    assert data["model_eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
    for source in data["source_registry"]:
        excerpt = source.get("normalized_excerpt")
        digest = source.get("normalized_excerpt_sha256")
        if excerpt is not None:
            assert digest == hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
            assert len(excerpt.split()) <= 25
