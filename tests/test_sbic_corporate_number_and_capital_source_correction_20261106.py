from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T095354Z-sbic-corporate-number-and-capital-source-correction.json"


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_central_and_west_corporate_numbers_are_registered_to_the_correct_legal_names() -> None:
    data = load()
    sources = {x["source_id"]: x for x in data["source_registry"]}
    central = sources["GBIZINFO_CENTRAL_CORPORATE_NUMBER_20261106"]["content"]
    west = sources["GBIZINFO_WEST_CORPORATE_NUMBER_20261106"]["content"]
    assert central["legal_name_ja"] == "名古屋中小企業投資育成株式会社"
    assert central["corporate_number"] == "7180001031846"
    assert west["legal_name_ja"] == "大阪中小企業投資育成株式会社"
    assert west["corporate_number"] == "2120001059625"
    assert all("National Tax Agency" in x["primary_registry_lineage"] for x in [sources["GBIZINFO_CENTRAL_CORPORATE_NUMBER_20261106"], sources["GBIZINFO_WEST_CORPORATE_NUMBER_20261106"]])


def test_central_capital_disagreement_prefers_the_official_company_profile() -> None:
    item = load()["capital_disagreement"]
    assert item["official_profile_value_jpy"] == 4380800000
    assert item["secondary_directory_value_jpy"] == 4800800000
    assert item["absolute_difference_jpy"] == 420000000
    assert item["selected_value_jpy"] == item["official_profile_value_jpy"]
    assert item["model_eligible"] is False


def test_previous_sbic_ownership_statement_is_narrowed_not_overstated() -> None:
    item = load()["ownership_claim_correction"]
    assert "not aliases of SBI Holdings" in item["corrected_conclusion"]
    assert "complete named shareholder-register" in item["corrected_conclusion"]
    assert "absolute no-subsidiary/no-affiliate-ownership conclusion is not established" in item["corrected_conclusion"]


def test_corrected_entity_index_keeps_regional_sbic_separate_from_sbi_holdings() -> None:
    entities = {x["label"]: x for x in load()["corrected_entity_index"]}
    assert entities["SBIC East Japan"]["corporate_number"] == "9011001030621"
    assert entities["SBIC Central Japan"]["corporate_number"] == "7180001031846"
    assert entities["SBIC West Japan"]["corporate_number"] == "2120001059625"
    assert entities["SBI Holdings"]["legal_name"] == "SBI Holdings, Inc."
    assert entities["SBI Holdings"]["corporate_number"] is None


def test_correction_is_append_only_context_and_not_a_market_feature() -> None:
    data = load()
    assert "20261106T0425Z-sbic-evernorth-actual-capital-identity-reconciliation.json" in data["correction_of"][0]
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["forecast_status"]["model_admission"] is False
