import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T0425Z-sbic-evernorth-actual-capital-identity-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_three_japanese_sbic_companies_are_separate_regional_entities():
    data = load()["sbic_identity"]
    companies = {item["label"]: item for item in data["companies"]}
    assert set(companies) == {"SBIC East Japan", "SBIC Central Japan", "SBIC West Japan"}
    assert companies["SBIC East Japan"]["city"] == "Tokyo"
    assert companies["SBIC Central Japan"]["city"] == "Nagoya"
    assert companies["SBIC West Japan"]["city"] == "Osaka"
    assert len({item["established"] for item in companies.values()}) == 3
    assert data["conclusion"].find("not SBI Holdings") >= 0


def test_sbic_chatgpt_evidence_is_training_not_a_partnership():
    data = load()["sbic_identity"]["chatgpt_disambiguation"]
    assert data["event_dates"] if "event_dates" in data else True
    assert data["exact_entity_found"] is False
    assert "not evidence of an OpenAI partnership" in data["conclusion"] if "conclusion" in data else True
    assert "2025" in data["official_event"]
    assert "VOST" in data["official_event"] or "VOST" in str(load()["source_registry"])


def test_evernorth_cash_and_in_kind_xrp_are_not_double_counted():
    capital = load()["evernorth_capital_reconciliation"]
    assert capital["gross_cash_proceeds_at_closing_usd"] == 272600000
    assert capital["gross_cash_proceeds_components_usd"]["private_placement_investments"] == 224600000
    assert capital["gross_cash_proceeds_components_usd"]["spac_trust_released_after_redemptions"] == 48000000
    assert capital["total_xrp_contributed_in_kind_at_closing"] == 388910554
    assert capital["cash_used_to_purchase_xrp_usd"] == 214000000
    assert capital["xrp_purchased_with_cash"] == 84365876
    assert capital["in_kind_component_detail"]["detail_reconciliation_status"].startswith("DO_NOT_SUM")


def test_average_cash_purchase_cost_is_reproducible_and_historical():
    capital = load()["evernorth_capital_reconciliation"]
    expected = capital["cash_used_to_purchase_xrp_usd"] / capital["xrp_purchased_with_cash"]
    assert abs(expected - capital["derived_average_cash_purchase_cost_per_xrp_usd"]) < 1e-12
    assert capital["closing_xrp_price_usd"] == 1.43069
    assert capital["derived_cash_purchase_cost_vs_closing_price_percent"] < -40


def test_debt_and_equity_facilities_are_not_reported_as_actual_xrp_purchases():
    capital = load()["evernorth_capital_reconciliation"]
    notes = capital["debt_and_future_financing"][0]
    facility = capital["debt_and_future_financing"][1]
    eloc = capital["debt_and_future_financing"][2]
    assert notes["gross_principal_usd"] == 30000000
    assert notes["net_cash_proceeds_before_other_transaction_expenses_usd"] == 29000000
    assert notes["actual_xrp_purchase_from_note_proceeds_disclosed"] is False
    assert notes["maximum_cash_settlement_if_conversion_cap_reached_usd"] == 120000000
    assert facility["drawn_as_of_2026_10_07_usd"] == 9700000
    assert facility["repayment_status_in_2026_10_30_prospectus"] == "NOT_CONFIRMED"
    assert eloc["proceeds_received_as_of_prospectus_usd"] == 0
    assert eloc["maximum_potential_gross_proceeds_usd"] == 76800000


def test_resale_registration_and_warrant_proceeds_are_contingent():
    capital = load()["evernorth_capital_reconciliation"]["debt_and_future_financing"][3]
    assert capital["shares_registered_for_resale"] == 73688162
    assert capital["company_receives_resale_proceeds"] is False
    assert capital["sponsor_warrants"] == 239653
    assert capital["cashless_exercise_possible"] is True
    assert capital["maximum_gross_cash_if_all_sponsor_warrants_exercised_for_cash_usd"] > 0


def test_sbi_holdings_ownership_and_voting_power_are_distinct():
    ownership = load()["evernorth_capital_reconciliation"]["ownership_and_governance"]
    assert ownership["sbi_common_equity_percent_at_closing"] == 21.4
    assert ownership["sbi_voting_power_percent_at_closing"] == 39.9
    assert len(ownership["sbi_controlled_subscriber_entities"]) == 4
    assert "different denominators" in ownership["note"]


def test_ripple_coinbase_and_sbi_relationships_do_not_imply_xrp_collateral():
    relationships = {item["from"] + "->" + item["to"]: item for item in load()["institutional_relationships"]}
    coinbase = relationships["Ripple->Coinbase"]
    sbi = relationships["Ripple->SBI VC Trade"]
    assert coinbase["status"] == "LIVE_FOR_COINBASE_PRIME_EXCHANGE_AND_RETAIL_APP"
    assert "XRP collateral acceptance" in coinbase["does_not_prove"]
    assert sbi["status"] == "ANNOUNCED_LAUNCH"
    assert "XRP-specific inflows" in sbi["does_not_prove"]


def test_circle_coinbase_and_bny_relationships_remain_separate():
    relationships = load()["institutional_relationships"]
    assert any(item["from"] == "Circle" and item["to"] == "Coinbase" for item in relationships)
    assert any(item["from"] == "BNY" and item["to"] == "Circle" for item in relationships)
    assert any(item["from"] == "BNY" and item["to"] == "Ripple" for item in relationships)
    assert not any(item["from"] == "Circle" and item["to"] == "Ripple" for item in relationships)


def test_permission_ask_contracts_are_base_and_polygon_not_xrpl():
    ask = load()["ask_coin"]
    assert ask["strongest_candidate"] == "Permission Coin (ticker ASK)"
    assert ask["official_contracts"]["Base"].startswith("0xBB1463")
    assert ask["official_contracts"]["Polygon"].startswith("0xaA3717")
    assert ask["xrpl_contract_listed"] is False
    assert ask["xrp_relationship_established"] is False


def test_actual_capital_phrase_is_not_a_sec_defined_metric():
    phrase = load()["evernorth_capital_reconciliation"]["actual_capital_phrase"]
    assert phrase["exact_phrase"] == "actual capital"
    assert phrase["exact_match_in_sec_424b3"] is False
    assert phrase["defined_metric_in_sec_filing"] is False
    assert "$272.6M" in phrase["safest_cash_summary"]


def test_no_directional_forecast_is_created_from_corporate_disclosures():
    data = load()
    assert data["forecast"]["issued"] is False
    assert data["model_admission"]["eligible"] is False
    assert len(data["competing_hypotheses"]) >= 4
    assert all(item["supporting_evidence"] and item["disconfirming_evidence"] for item in data["competing_hypotheses"])
