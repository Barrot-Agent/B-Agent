from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T000206Z-xrpl-lending-amendment-vote-denominator-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_current_xrplwin_vote_counts_remain_below_threshold():
    data = load_artifact()
    rows = data["amendment_snapshots"]["xrplwin"]["observations"]
    assert {row["amendment"] for row in rows} == {
        "LendingProtocol", "SingleAssetVault", "LendingProtocolV1_1"
    }
    assert all(row["yes_votes"] < 29 for row in rows)
    assert all(row["status"] == "VOTING_NO_MAJORITY" for row in rows)
    assert data["amendment_snapshots"]["xrplwin"]["required_support"] == "More than 80% for 14 uninterrupted days"


def test_denominator_disagreement_is_preserved_not_averaged():
    data = load_artifact()["amendment_snapshots"]
    assert data["xrplwin"]["trusted_validator_count_reported"] == 35
    alternative = data["xrpl_to_alternative_snapshot"]
    assert alternative["trusted_validator_count_reported"] == 36
    assert alternative["observations"][0]["yes_votes"] == 21
    assert alternative["observations"][0]["total_reported"] == 36
    assert alternative["status"] == "SECONDARY_DENOMINATOR_DISAGREEMENT_NOT_CANONICAL"


def test_xrplwin_counts_do_not_show_increased_yes_votes_from_nov6():
    data = load_artifact()["amendment_snapshots"]
    prior = {row["amendment"]: row for row in data["prior_xrplwin_snapshot"]["observations"]}
    current = {row["amendment"]: row for row in data["xrplwin"]["observations"]}
    assert prior["LendingProtocol"]["yes_votes"] == current["LendingProtocol"]["yes_votes"] == 21
    assert prior["SingleAssetVault"]["yes_votes"] == current["SingleAssetVault"]["yes_votes"] == 23
    assert prior["LendingProtocolV1_1"]["yes_votes"] == current["LendingProtocolV1_1"]["yes_votes"] == 21


def test_fixcleanup_activation_does_not_mean_lending_is_active():
    data = load_artifact()
    fix = data["protocol_design"]["fix_cleanup_3_4_0"]
    assert fix["status"] == "ENABLED"
    assert fix["enabled_at_utc"] == "2026-11-04T14:52:00Z"
    assert fix["enabled_ledger"] == 108112129
    assert all(row["status"] == "VOTING_NO_MAJORITY" for row in data["amendment_snapshots"]["xrplwin"]["observations"])


def test_xls66_is_uncollateralized_and_vault_deposits_are_not_borrower_collateral():
    data = load_artifact()
    assert data["protocol_design"]["lending_protocol"]["loan_type"] == "UNCOLLATERALIZED_FIXED_TERM"
    assert data["capital_collateral_reconciliation"]["borrower_collateral_required_by_xls66"] is False
    assert data["capital_collateral_reconciliation"]["vault_deposits_are_borrower_collateral"] is False
    assert data["capital_collateral_reconciliation"]["actual_vault_capital_verified"] is False
    assert data["capital_collateral_reconciliation"]["actual_xrp_collateral_balance_verified"] is False


def test_all_normalized_excerpt_hashes_match_exact_text():
    for source in load_artifact()["source_registry"]:
        excerpt = source.get("normalized_excerpt")
        digest = source.get("normalized_excerpt_sha256")
        if excerpt is not None:
            assert digest == hashlib.sha256(excerpt.encode("utf-8")).hexdigest()


def test_sources_do_not_claim_raw_bytes_or_exact_retrieval_times():
    data = load_artifact()
    assert data["capture"]["raw_http_bytes_captured"] is False
    assert data["capture"]["exact_http_retrieval_times_utc"] is None
    assert all(source.get("raw_http_bytes_captured", False) is False for source in data["source_registry"])
    assert all(source.get("exact_retrieval_time_utc") is None for source in data["source_registry"])


def test_no_actual_capital_or_forecast_is_claimed():
    data = load_artifact()
    assert data["capital_collateral_reconciliation"]["actual_loan_origination_volume_verified"] is False
    assert data["capital_collateral_reconciliation"]["actual_xrp_settlement_volume_verified"] is False
    assert data["model_eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
