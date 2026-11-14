from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T000206Z-sec-xrp-digital-commodity-and-rulemaking-status.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sec_commission_interpretation_explicitly_lists_xrp():
    data = load_artifact()
    scope = data["commission_interpretation"]
    assert scope["classification"] == "DIGITAL_COMMODITY"
    assert scope["xrp_explicitly_listed"] is True
    assert scope["effective_date"] == "2026-03-23"
    assert scope["not_established"]


def test_asset_classification_does_not_immunize_transactions():
    data = load_artifact()
    scope = data["commission_interpretation"]
    assert "investment contract" in scope["legal_scope"]
    assert "every XRP sale" in scope["not_established"][0]


def test_november_staff_faq_is_explicitly_nonbinding():
    faq = load_artifact()["staff_faq"]
    assert faq["updated"] == "2026-11-02"
    assert faq["status"] == "NONBINDING_STAFF_VIEWS"
    assert "no legal force or effect" in faq["explicit_disclaimer"]
    assert "functional" in faq["clarification"].lower()
    assert "decentralized" in faq["clarification"].lower()


def test_proposed_rule_is_not_treated_as_effective():
    proposal = load_artifact()["proposed_rule"]
    assert proposal["current_sec_page_status"] == "PROPOSED"
    assert proposal["public_comment_due"] == "2026-10-20"
    assert proposal["not_effective"] is True
    assert proposal["docket_activity_through"] == "2026-11-05"


def test_commenter_advocacy_is_not_misrepresented_as_sec_or_court_finding():
    position = load_artifact()["counter_positions"]
    assert position["letter_date"] == "2026-10-16"
    assert position["evidentiary_status"] == "ADVOCACY_COMMENT_NOT_COMMISSION_FINDING_NOT_COURT_HOLDING"


def test_senate_vote_is_procedural_and_not_described_as_enactment():
    vote = load_artifact()["legislative_context"]
    assert vote["vote"] == "49-50"
    assert vote["result"] == "NOT_INVOKED"
    assert "did not advance" in vote["implication"]


def test_normalized_excerpt_hashes_match():
    for source in load_artifact()["source_registry"]:
        excerpt = source.get("normalized_excerpt")
        digest = source.get("normalized_excerpt_sha256")
        if excerpt is not None:
            assert digest == hashlib.sha256(excerpt.encode("utf-8")).hexdigest()


def test_no_raw_http_bytes_or_exact_retrieval_times_are_claimed():
    data = load_artifact()
    assert data["capture"]["raw_http_bytes_captured"] is False
    assert data["capture"]["exact_http_retrieval_times_utc"] is None
    assert all(source.get("raw_http_bytes_captured", False) is False for source in data["source_registry"])
    assert all(source.get("exact_retrieval_time_utc") is None for source in data["source_registry"])


def test_regulatory_context_is_not_used_as_a_directional_forecast():
    data = load_artifact()
    assert data["model_eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
