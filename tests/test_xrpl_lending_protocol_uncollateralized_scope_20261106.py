from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T022802Z-xrpl-lending-protocol-uncollateralized-scope.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_official_xls66_design_is_uncollateralized_and_off_chain_underwritten():
    item = load_artifact()["protocol_design"]["lending_protocol"]
    assert item["standard"] == "XLS-66"
    assert item["loan_type"] == "UNCOLLATERALIZED"
    assert item["funding_source"] == "Pooled funds from a Single Asset Vault"
    assert "Off-chain underwriting" in item["underwriting"]


def test_vault_deposits_are_funding_capital_not_borrower_collateral():
    item = load_artifact()
    assert item["protocol_design"]["single_asset_vault"]["purpose"].startswith("Aggregates assets")
    assert item["capital_and_collateral_reconciliation"]["borrower_collateral_required_by_xls66"] is False
    assert item["capital_and_collateral_reconciliation"]["vault_deposits_are_borrower_collateral"] is False
    assert item["capital_and_collateral_reconciliation"]["actual_vault_capital_verified"] is False


def test_lending_v11_additions_are_not_misrepresented_as_active():
    item = load_artifact()["protocol_design"]["lending_protocol_v1_1"]
    assert any("closed-ended vault" in x for x in item["changes"])
    assert any("cash basis" in x for x in item["changes"])
    assert "does not mean those features are active" in item["dependency_note"]


def test_fixcleanup_is_a_safety_amendment_not_lending_activation():
    item = load_artifact()["protocol_design"]["fix_cleanup_3_4_0"]
    assert item["status"] == "ENABLED"
    assert item["enabled_ledger"] == 108112129
    assert "does not activate LendingProtocol" in item["distinction"]


def test_all_three_lending_and_vault_amendments_are_below_threshold():
    rows = load_artifact()["amendment_state_snapshots"]["observations"]
    assert {x["amendment"] for x in rows} == {"LendingProtocol", "SingleAssetVault", "LendingProtocolV1_1"}
    assert all(x["yes_votes"] < 29 for x in rows)
    assert all(x["status"] == "VOTING_NO_MAJORITY" for x in rows)


def test_no_actual_xrp_collateral_or_loan_capital_is_claimed():
    item = load_artifact()["capital_and_collateral_reconciliation"]
    assert item["actual_vault_capital_verified"] is False
    assert item["actual_loan_origination_volume_verified"] is False
    assert item["actual_xrp_collateral_balance_verified"] is False
    assert item["actual_xrp_settlement_volume_verified"] is False


def test_research_is_not_a_price_forecast_or_model_feature():
    item = load_artifact()
    assert item["model_eligible"] is False
    assert item["forecast_status"] == "NOT_ISSUED"
    assert item["data_cutoff_utc"] is None
