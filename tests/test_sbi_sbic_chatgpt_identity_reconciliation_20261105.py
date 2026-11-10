import json
from pathlib import Path


ARTIFACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261105T123634Z-sbi-sbic-chatgpt-and-identity-reconciliation.json"
)


def _artifact():
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def test_sbi_holdings_chatgpt_adoption_is_not_regional_sbic_adoption():
    data = _artifact()["identity_resolution"]
    sbi = data["sbi_holdings"]
    assert sbi["publication_date"] == "2025-05-01"
    assert "SBI Holdings, Inc." in sbi["entities"]
    assert "SBI Securities Co., Ltd." in sbi["entities"]
    assert "OpenAI, Inc." in sbi["entities"]
    assert "SBIC East Japan" in sbi["not_equivalent_to"]
    assert "SBIC Central Japan" in sbi["not_equivalent_to"]
    assert "SBIC West Japan" in sbi["not_equivalent_to"]


def test_three_regional_sbic_entities_remain_distinct():
    companies = _artifact()["identity_resolution"]["regional_sbic"]["companies"]
    assert [company["region"] for company in companies] == ["East", "Central", "West"]
    assert len({company["official_url"] for company in companies}) == 3
    assert "none is SBI Holdings" in _artifact()["identity_resolution"]["regional_sbic"]["distinction"]


def test_sbic_east_chatgpt_course_is_investee_training_not_openai_partnership():
    data = _artifact()["identity_resolution"]["sbic_east_chatgpt_training"]
    assert data["dates"] == ["2025-06-12", "2025-06-13"]
    assert "investee companies only" in data["audience"].lower()
    assert "ChatGPT" in data["curriculum_includes"]
    assert "OpenAI partnership with SBIC East" in data["not_established"]


def test_exact_phrase_candidates_do_not_create_an_xrp_relationship():
    data = _artifact()["exact_phrase_research"]
    assert "No new primary-source match" in data["ask_coin"]["result"]
    assert "No new exact-phrase primary-source match" in data["actual_capital"]["result"]
    assert "no exact regional-SBIC/OpenAI partnership" in data["sbic_chatgpt_sbi"]["result"]


def test_youtube_inventory_is_blocked_until_first_party_identity_proof():
    data = _artifact()["youtube_identity_gate"]
    assert data["identity_verified"] is False
    assert data["video_inventory_performed"] is False
    assert len(data["candidate_channels"]) >= 2
    assert all("first-party" in item["status"] or "first-party" in data["reason"] for item in data["candidate_channels"])


def test_stale_coinbase_prediction_market_page_is_not_used_as_a_benchmark():
    data = _artifact()["prediction_market_freshness_check"]
    assert data["status"] == "stale_or_inconsistent_page_vintage"
    assert data["model_eligible"] is False
    assert "Excluded" in data["use"]


def test_identity_research_does_not_issue_a_directional_forecast():
    data = _artifact()
    assert data["raw_capture"]["model_eligible"] is False
    assert data["model_eligibility"]["eligible_sources"] == 0
    assert data["model_eligibility"]["directional_forecast_issued"] is False
