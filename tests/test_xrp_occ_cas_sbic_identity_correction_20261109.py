from __future__ import annotations

import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261109T131821Z-occ-cas-trust-charter-sbic-identity-correction.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_occ_cas_records_show_three_distinct_effective_trust_charters() -> None:
    data = load_artifact()
    records = {item["entity"]: item for item in data["occ_cas"]["records"]}

    assert set(records) == {
        "Coinbase National Trust Company",
        "Ripple National Trust Bank",
        "First National Digital Currency Bank, N.A.",
    }
    assert records["Coinbase National Trust Company"]["consummated_effective_date"] == "2026-11-06"
    assert records["Ripple National Trust Bank"]["consummated_effective_date"] == "2026-10-26"
    assert records["First National Digital Currency Bank, N.A."]["consummated_effective_date"] == "2026-07-24"
    assert all(item["status"] == "OCC_CAS_CONSUMMATED_EFFECTIVE" for item in records.values())
    assert all(item["transaction_form"] == "Charter National Bank Under Holding Company (Trust Bank)" for item in records.values())
    assert len({item["occ_control_number"] for item in records.values()}) == 3


def test_coinbase_trust_scope_and_regulatory_capital_are_not_xrp_flows() -> None:
    data = load_artifact()
    coinbase = next(
        item for item in data["occ_cas"]["records"]
        if item["entity"] == "Coinbase National Trust Company"
    )
    scope = coinbase["scope_from_corporate_decision_1370"]
    capital = scope["capital_conditions"]

    assert scope["fiduciary_digital_asset_custody"] is True
    assert "Finder access only" in scope["affiliate_access"]
    assert scope["insured_depository_institution"] is False
    assert scope["stablecoin_issuance_proposed_by_bank"] is False
    assert capital["minimum_tier_1_capital_usd"] == 60_000_000
    assert "180 days" in capital["operating_expense_liquidity"]
    assert data["actual_capital_taxonomy"]["current_verified_xrp_purchase_or_collateral_amount_status"] == "NOT_ESTABLISHED"
    assert data["model_eligible_features"] == []


def test_ripple_and_circle_trust_charters_do_not_imply_xrp_collateral() -> None:
    data = load_artifact()
    records = {item["entity"]: item for item in data["occ_cas"]["records"]}
    ripple = records["Ripple National Trust Bank"]
    circle = records["First National Digital Currency Bank, N.A."]

    assert "RLUSD" in ripple["scope_company_reported"]
    assert "USDC" in " ".join(circle["evidence_limitations"])
    assert any("XRP collateralization" in item for item in ripple["evidence_limitations"])
    assert any("XRP collateral use" in item for item in circle["evidence_limitations"])
    assert data["forecast_status"] == "NOT_ISSUED"


def test_sbic_east_central_west_are_distinct_regional_entities() -> None:
    data = load_artifact()
    entities = {item["regional_label"]: item for item in data["sbic_entity_resolution"]["entities"]}

    assert set(entities) == {"SBIC East Japan", "SBIC Central Japan", "SBIC West Japan"}
    assert entities["SBIC East Japan"]["corporate_number"] == "9011001030621"
    assert entities["SBIC East Japan"]["legal_name_en"].startswith("Tokyo ")
    assert entities["SBIC Central Japan"]["legal_name_en"].startswith("Nagoya ")
    assert entities["SBIC West Japan"]["legal_name_en"].startswith("Osaka ")
    assert "sister companies" in data["sbic_entity_resolution"]["relationship_classification"]
    assert "SBI Holdings" in data["sbic_entity_resolution"]["relationship_classification"]


def test_sbic_chatgpt_reference_is_an_investee_training_course_not_a_partnership() -> None:
    data = load_artifact()
    event = data["sbic_entity_resolution"]["chatgpt_reference"]

    assert event["host"] == "Tokyo Small and Medium Business Investment & Consultation Co., Ltd. (SBIC East Japan)"
    assert event["event_dates"] == ["2025-06-12", "2025-06-13"]
    assert event["audience"] == "Investee companies only; the official page says general companies could not register."
    assert "ChatGPT" in event["curriculum_day_1"]
    assert "Copilot" in event["curriculum_day_2"]
    assert event["classification"] == "EDUCATIONAL_TRAINING_EVENT"
    assert any("commercial partnership" in item for item in event["does_not_establish"])
