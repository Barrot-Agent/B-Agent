from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T213528Z-xrp-stablecoin-freeze-native-asset-control-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_receipt_hashes_and_quote_limits_are_reproducible() -> None:
    artifact = load_artifact()
    for receipt in artifact["source_receipts"]:
        assert len(receipt["excerpt"].split()) <= 25
        if receipt["sha256"] is None:
            assert receipt["source_class"] == "secondary_republication_of_trm"
            assert receipt["independent_confirmation"] is False
            continue
        digest = hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest()
        assert digest == receipt["sha256"]


def test_trm_and_xrpl_documentation_are_distinct_source_groups() -> None:
    artifact = load_artifact()
    groups = {receipt["independence_group"] for receipt in artifact["source_receipts"]}
    assert "trm_onchain_analysis" in groups
    assert "xrpl_official_documentation" in groups
    assert artifact["source_independence_and_disagreement"]["tokenpost_is_independent_confirmation"] is False


def test_rlusd_received_amount_reconciles_to_sold_plus_frozen() -> None:
    artifact = load_artifact()
    rlusd = artifact["event_facts"]["rlusd"]
    assert rlusd["total_received_by_attacker"] == 88_500_000
    assert rlusd["sold_before_freeze"] == 48_000_000
    assert rlusd["remaining_at_issuer_freeze"] == 40_500_000
    assert rlusd["sold_before_freeze"] + rlusd["remaining_at_issuer_freeze"] == rlusd["total_received_by_attacker"]
    assert rlusd["returned_to_binance"] is False


def test_yihe_two_hundred_million_claim_is_not_mislabeled_as_verified_freeze() -> None:
    artifact = load_artifact()
    claim = artifact["event_facts"]["yi_he_statement"]
    derived = artifact["derived_reconciliation"]
    assert claim["reported_amount_usd"] == 200_000_000
    assert claim["direct_primary_record"] is False
    assert claim["reconciled_to_onchain_rlusd"] is False
    assert derived["trm_confirmed_rlusd_freeze_usd_approx"] == 40_500_000
    assert derived["difference_is_not_proven_missing_or_recovered"] is True


def test_native_xrp_and_issued_rlusd_have_different_freeze_controls() -> None:
    artifact = load_artifact()
    control = artifact["custody_and_control"]
    assert control["native_xrp"]["protocol_freeze_capability"] is False
    assert control["issued_rlusd"]["issuer_freeze_capability"].startswith("supported")
    assert control["custodial_xrp"]["exchange_account_freeze_capability"] is True
    assert control["custodial_xrp"]["scope"].find("not an XRPL protocol freeze") >= 0


def test_issuer_freeze_amounts_are_not_completed_recoveries() -> None:
    artifact = load_artifact()
    assert len(artifact["event_facts"]["issuer_and_network_actions"]) == 5
    assert artifact["derived_reconciliation"]["stablecoin_and_network_freezes_are_not_completed_recoveries"] is True
    assert artifact["derived_reconciliation"]["binance_replenishment_is_not_stolen_xrp_recovery"] is True


def test_unreconciled_claim_retains_competing_hypotheses() -> None:
    artifact = load_artifact()
    disagreement = artifact["source_independence_and_disagreement"]
    assert "not reconciled" in disagreement["disagreement"]
    assert len(disagreement["competing_hypotheses"]) >= 2
    assert "no calculation or asset breakdown was provided" in disagreement["competing_hypotheses"][1]


def test_freeze_event_is_not_admitted_as_a_directional_price_feature() -> None:
    artifact = load_artifact()
    admission = artifact["market_admission"]
    assert admission["admitted_to_feature_store"] is False
    assert admission["price_directional_use"] is False
    assert admission["event_timeline_only"] is True
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is False


def test_no_external_or_financial_action_was_performed() -> None:
    artifact = load_artifact()
    actions = artifact["external_actions"]
    assert actions["issuer_freeze_performed_by_researcher"] is False
    assert actions["exchange_action_performed"] is False
    assert actions["financial_action"] is False
    assert actions["external_model_transfer"] is False
