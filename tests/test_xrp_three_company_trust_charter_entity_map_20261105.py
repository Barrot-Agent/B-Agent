import json
from pathlib import Path


ARTIFACT = Path(
    "research/xrp_intelligence/"
    "20261105-circle-usdc-rlusd-custody-charter-entity-map-correction.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_circle_federal_and_new_york_trust_entities_are_separate():
    data = _load()
    circle = data["entities"]["circle"]
    assert circle["state_entity"]["legal_name"] == "Circle Internet Trust Company LLC"
    assert circle["state_entity"]["dba"] == "Circle New York Trust"
    assert circle["federal_entity"]["legal_name"] == "First National Digital Currency Bank, N.A."
    assert circle["federal_entity"]["dba"] == "Circle National Trust"
    assert circle["federal_entity"]["proposed_charter_number"] == "25361"
    assert circle["federal_entity"]["occ_status_actions"][-1]["date"] == "2026-07-24"


def test_ripple_state_issuer_and_federal_trust_bank_are_separate():
    data = _load()
    ripple = data["entities"]["ripple"]
    assert ripple["state_entity"]["legal_name"] == "Standard Custody & Trust Company, LLC"
    assert ripple["state_entity"]["role"] == "RLUSD issuer, according to Ripple's October 26, 2026 announcement."
    assert ripple["federal_entity"]["legal_name"] == "Ripple National Trust Bank"
    assert ripple["federal_entity"]["proposed_charter_number"] == "25364"
    assert ripple["federal_entity"]["occ_status_actions"][-1]["date"] == "2026-10-26"
    assert ripple["federal_entity"]["rlusd_issuer"] is False


def test_coinbase_existing_state_custodian_is_not_the_proposed_federal_bank():
    data = _load()
    coinbase = data["entities"]["coinbase"]
    assert coinbase["state_entity"]["legal_name"] == "Coinbase Custody Trust Company, LLC"
    assert coinbase["federal_entity"]["legal_name"] == "Coinbase National Trust Company"
    assert coinbase["federal_entity"]["proposed_charter_number"] == "25390"
    assert coinbase["federal_entity"]["effective_action_visible_in_retrieved_cas_record"] is False
    assert coinbase["federal_entity"]["distinct_from_state_custody_entity"] is True


def test_three_company_regulatory_matrix_does_not_overstate_federal_status():
    data = _load()
    matrix = data["comparison"]
    assert matrix["circle_state_lp_trust"] is True
    assert matrix["circle_federal_national_trust_effective"] is True
    assert matrix["ripple_state_lp_trust"] is True
    assert matrix["ripple_federal_national_trust_effective"] is True
    assert matrix["coinbase_state_lp_trust"] is True
    assert matrix["coinbase_federal_national_trust_effective"] is False
    assert "no Consummated/Effective row" in matrix["coinbase_federal_status"]


def test_circle_and_ripple_operational_and_issuer_scope_remain_qualified():
    data = _load()
    circle = data["entities"]["circle"]["federal_entity"]
    ripple = data["entities"]["ripple"]["federal_entity"]
    assert circle["operational_opening_verified"] is False
    assert circle["current_usdc_issuer"] is False
    assert "future capability" in circle["future_scope"]
    assert ripple["operational_opening_verified"] is False
    assert ripple["rlusd_issuer"] is False


def test_state_limited_purpose_trust_constraints_are_not_applied_to_occ_entities():
    data = _load()
    text = data["comparison"]["nydfs_lp_trust_limitations"]
    assert "not receiving deposits" in text
    assert "not automatically to the OCC national trust-bank entities" in text


def test_charter_events_do_not_create_xrp_market_or_collateral_features():
    data = _load()
    assert data["xrp_relevance"]["xrp_purchases_disclosed"] is False
    assert data["xrp_relevance"]["xrp_assets_under_custody_disclosed"] is False
    assert data["xrp_relevance"]["xrp_collateral_balances_disclosed"] is False
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["directional_forecast_issued"] is False
    assert data["preservation"]["no_xrp_flow_or_collateral_inferred"] is True
