from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T151624Z-xrp-collateral-and-xrpl-lending-vote-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_coinbase_lists_xrp_as_perpetual_futures_collateral_but_not_actual_utilization():
    data = load_artifact()
    assert data["collateral_reconciliation"]["coinbase_global_exchange_xrp_eligible"] is True
    assert data["collateral_reconciliation"]["coinbase_xrp_actual_pledged_quantity"] is None
    assert data["collateral_reconciliation"]["coinbase_xrp_base_haircut"] is None
    assert data["collateral_reconciliation"]["coinbase_xrp_adq_cap"] is None


def test_coinbase_cross_collateral_limits_and_liquidation_are_preserved():
    row = next(x for x in load_artifact()["source_registry"] if x["source_id"] == "coinbase_cross_collateral_help")
    assert "ADQ limits" in row["normalized_excerpt"]
    assert "automatic liquidation" in row["normalized_excerpt"]
    assert row["raw_http_bytes_captured"] is False


def test_morpho_wrapped_xrp_route_is_secondary_and_not_coinbase_balance_sheet_credit():
    data = load_artifact()
    row = next(x for x in data["source_registry"] if x["source_id"] == "coindesk_coinbase_morpho_xrp_usdc_20260219")
    assert row["source_type"] == "secondary_reporting"
    assert data["collateral_reconciliation"]["morpho_wrapped_xrp_loan_route_reported"] is True
    assert data["collateral_reconciliation"]["morpho_current_utilization"] is None
    assert data["key_distinctions"][2].startswith("Coinbase's Morpho-mediated retail loan route")


def test_xls66_is_uncollateralized_and_xls65_deposits_are_funding_capital():
    data = load_artifact()
    assert data["collateral_reconciliation"]["xrpl_xls66_borrower_collateral_required"] is False
    assert data["collateral_reconciliation"]["xrpl_xls65_vault_deposits_are_borrower_collateral"] is False
    assert "uncollateralized loans" in data["key_distinctions"][3]
    assert data["collateral_reconciliation"]["actual_xrpl_vault_capital_verified"] is False


def test_live_amendment_votes_remain_below_activation_threshold():
    data = load_artifact()
    rows = data["current_amendment_snapshots"]["observations"]
    assert {x["amendment"] for x in rows} == {"LendingProtocol", "SingleAssetVault", "LendingProtocolV1_1"}
    assert all(x["yes_votes"] < data["current_amendment_snapshots"]["threshold_yes_votes"] for x in rows)
    assert all(x["status"] == "VOTING_BELOW_SUPERMAJORITY" for x in rows)
    assert data["current_amendment_snapshots"]["required_support_duration_days"] == 14


def test_vote_snapshots_keep_distinct_ledger_indices():
    rows = {x["amendment"]: x for x in load_artifact()["current_amendment_snapshots"]["observations"]}
    assert rows["LendingProtocol"]["state_ledger"] == 108155386
    assert rows["SingleAssetVault"]["state_ledger"] == 108154942
    assert rows["LendingProtocolV1_1"]["state_ledger"] == 108155080
    assert rows["LendingProtocol"]["yes_votes"] == 21
    assert rows["SingleAssetVault"]["yes_votes"] == 23


def test_all_normalized_evidence_hashes_match():
    for source in load_artifact()["source_registry"]:
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]


def test_no_actual_xrp_collateral_or_forecast_is_claimed():
    data = load_artifact()
    assert data["collateral_reconciliation"]["actual_xrp_collateral_balance_verified"] is False
    assert data["collateral_reconciliation"]["actual_xrp_settlement_volume_verified"] is False
    assert data["model_use_policy"]["model_eligible"] is False
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["directional_forecast_issued"] is False
