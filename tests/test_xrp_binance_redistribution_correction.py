"""Tests for the append-only Binance XRP redistribution correction."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261104T192000Z-binance-xrp-redistribution-correction.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_initial_xrp_drain_is_primary_and_independently_corroborated():
    data = load()
    claim = next(x for x in data["claims"] if x["id"] == "INITIAL-XRP-DRAIN")
    assert claim["amount_xrp"] == 233_461_943.1
    assert claim["source_wallet_count"] == 5
    assert len(claim["transfers"]) == 5
    assert round(sum(x["amount_xrp"] for x in claim["transfers"]), 1) == 233_461_943.1
    assert {"BINANCE-INITIAL-FINDINGS", "TRM-LABS-REPORT", "XRPLWIN-ONLEDGER"}.issubset(set(claim["source_ids"]))


def test_full_nov2_redistribution_is_not_only_the_two_40m_transfers():
    data = load()
    claim = next(x for x in data["claims"] if x["id"] == "NOV2-FULL-REDISTRIBUTION")
    assert claim["bulk_transfer_count"] == 9
    assert claim["bulk_recipient_count"] == 6
    assert claim["test_transfer_count"] == 7
    assert claim["total_source_outgoing_transactions_24h"] == 16
    assert claim["bulk_amount_xrp"] == 233_454_920
    assert claim["test_amount_xrp"] == 7_000
    assert claim["recipient_total_xrp"] == 233_461_920
    assert claim["recipient_outgoing_transactions_as_of_snapshot"] == 0
    assert claim["recipient_destination_tags"] == 0
    assert claim["recipient_account_names_registered"] == 0
    assert claim["on_ledger_dex_offers_as_of_snapshot"] == 0
    assert claim["reconciliation_gap_xrp"] == 0.59905
    assert len(claim["recipients"]) == 6


def test_whale_alert_80m_pair_is_subset_and_hash_timestamp_conflict_is_preserved():
    data = load()
    claim = next(x for x in data["claims"] if x["id"] == "WHALE-ALERT-40M-PAIR")
    assert claim["amount_xrp"] == 80_000_000
    assert claim["transfer_count"] == 2
    assert claim["subset_of"] == "NOV2-FULL-REDISTRIBUTION"
    assert claim["verified_timestamp_for_first_hash_utc"] == "2026-11-02T03:56:21Z"
    assert claim["second_hash_timestamp_utc"] is None
    assert "timestamp" in claim["timestamp_mapping_conflict"].lower()


def test_competing_recipient_ownership_hypotheses_remain_unresolved():
    data = load()
    claim = next(x for x in data["claims"] if x["id"] == "OWNERSHIP-INTERPRETATIONS")
    assert claim["status"] == "unresolved_competing_interpretations"
    ids = {x["id"] for x in claim["hypotheses"]}
    assert {"attacker_distribution", "binance_internal_custody_sweep", "third_party_intermediary"}.issubset(ids)
    assert "No first-party Binance statement" in claim["hypotheses"][1]["limitation"]


def test_rlusd_freeze_and_native_xrp_freeze_controls_are_distinguished():
    data = load()
    claims = {x["id"]: x for x in data["claims"]}
    eth = claims["RLUSD-ETH-FREEZE"]
    assert eth["total_rlusd_stolen"] == 88_500_000
    assert eth["swapped_on_dex_rlusd"] == 48_000_000
    assert eth["frozen_by_ripple_rlusd"] == 40_500_000
    assert eth["network"] == "Ethereum"
    xrpl = claims["RLUSD-XRPL-MOVEMENT"]
    assert xrpl["network"] == "XRP Ledger"
    assert xrpl["amount_rlusd"] == 51_172_508
    native = claims["NATIVE-XRP-FREEZE-CONTROL"]
    assert "cannot be frozen" in native["claim"]


def test_binance_por_is_not_mistaken_for_recovery_of_stolen_xrp():
    data = load()
    claims = {x["id"]: x for x in data["claims"]}
    ten = claims["BINANCE-10-ASSET-POR"]
    assert "XRP" in ten["assets"] and "RLUSD" in ten["assets"]
    assert ten["user_verifiable_1_to_1_balance_inclusion"] is True
    forty_four = claims["BINANCE-44-ASSET-POR-PENDING"]
    assert forty_four["token_count"] == 44
    assert forty_four["replenishment_pct_reported"] == 98
    assert forty_four["proof_expected_in_hours"] == [50, 60]
    assert "not proof that stolen XRP was recovered" in ten["limitations"][0]


def test_correction_is_research_only_and_raw_capture_gaps_are_explicit():
    data = load()
    assert data["forecast_issued"] is False
    assert data["prediction_status"] == "NOT_ISSUED"
    assert data["model_eligible"] is False
    assert data["source_capture"]["raw_http_bytes_retained"] is False
    assert data["source_capture"]["raw_source_sha256"] is None
    assert data["data_quality"]["recipient_beneficial_ownership_verified"] is False
    assert data["data_quality"]["balance_reconciliation_gap_xrp"] == 0.59905
