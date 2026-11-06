from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T094856Z-sbic-regional-company-primary-profile-vs-sbi-holdings-addendum.json"


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_three_regional_sbic_entities_have_distinct_legal_names_dates_and_capital() -> None:
    entities = {x["label"]: x for x in load()["entity_resolution"]["entities"]}
    assert entities["SBIC East Japan"]["legal_name_ja"] == "東京中小企業投資育成株式会社"
    assert entities["SBIC East Japan"]["corporate_number"] == "9011001030621"
    assert entities["SBIC East Japan"]["established"] == "1963-11-15"
    assert entities["SBIC East Japan"]["capital_jpy"] == 6673400000
    assert entities["SBIC Central Japan"]["legal_name_ja"] == "名古屋中小企業投資育成株式会社"
    assert entities["SBIC Central Japan"]["established"] == "1963-11-18"
    assert entities["SBIC Central Japan"]["capital_jpy"] == 4380800000
    assert entities["SBIC West Japan"]["legal_name_ja"] == "大阪中小企業投資育成株式会社"
    assert entities["SBIC West Japan"]["established"] == "1963-11-20"
    assert entities["SBIC West Japan"]["capital_jpy"] == 6822000000


def test_regional_profiles_call_one_another_sister_companies() -> None:
    data = load()
    profiles = {x["source_id"]: x for x in data["source_registry"]}
    east = profiles["SBIC_EAST_OFFICIAL_PROFILE_20261106"]["content"]["official_sister_companies"]
    central = profiles["SBIC_CENTRAL_OFFICIAL_PROFILE_20261106"]["content"]["official_sister_companies"]
    west = profiles["SBIC_WEST_OFFICIAL_PROFILE_20261106"]["content"]["official_sister_companies"]
    assert "Nagoya Small and Medium Business Investment & Consultation Co., Ltd." in east
    assert "Osaka Small and Medium Business Investment & Consultation Co., Ltd." in east
    assert "Tokyo Small and Medium Business Investment & Consultation Co., Ltd." in central
    assert "Osaka Small and Medium Business Investment & Consultation Co., Ltd." in central
    assert "Tokyo Small and Medium Business Investment & Consultation Co., Ltd." in west
    assert "Nagoya Small and Medium Business Investment & Consultation Co., Ltd." in west


def test_sbi_holdings_is_a_separate_corporate_identity() -> None:
    data = load()
    sbi = next(x for x in data["source_registry"] if x["source_id"] == "SBI_HOLDINGS_OFFICIAL_CORPORATE_PROFILE_20260626")
    assert sbi["content"]["legal_name"] == "SBI Holdings, Inc."
    assert sbi["content"]["established"] == "1999-07-08"
    assert sbi["content"]["principal_business"] == "Control and management of the SBI Group through share ownership."
    assert sbi["content"]["paid_in_capital_jpy_as_of_2026_03_31"] == 238019000000
    assert data["entity_resolution"]["sbi_holdings_separate_entity"]["corporate_identity_distinct"] is True


def test_ownership_conclusion_is_bounded_to_the_evidence() -> None:
    boundary = load()["entity_resolution"]["ownership_claim_boundary"]
    assert "complete named shareholder-register" in boundary
    assert "does not claim that no SBI-affiliated entity" in boundary


def test_chatgpt_sbic_events_are_not_misrepresented_as_openai_partnerships() -> None:
    phrase = load()["chatgpt_phrase_reconciliation"]
    assert "course page marks the course ended" in phrase["sbic_east"]
    assert "actual occurrence is not independently verified" in phrase["sbic_west"]
    assert "non-discovery is not proof of absence" in phrase["sbic_central"]
    assert "OpenAI partnership" in phrase["not_established"]
    assert "SBI Holdings sponsorship or control" in phrase["not_established"]


def test_sbic_identity_artifact_is_context_only_not_a_market_feature() -> None:
    data = load()
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["forecast_status"]["model_admission"] is False
    assert data["source_registry"][0]["raw_html_bytes_captured"] is False
