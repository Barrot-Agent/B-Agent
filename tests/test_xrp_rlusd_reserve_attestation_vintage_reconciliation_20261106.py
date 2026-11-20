from __future__ import annotations

import json
import math
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T031500Z-rlusd-reserve-attestation-vintage-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_september_attested_units_reserves_and_coverage_reconcile():
    data = load_artifact()["independently_attested_reserve_snapshots"]["report_dates"]
    for row in data.values():
        assert row["market_value_of_reserve_usd"] - row["outstanding_stablecoin_units"] == row["reserve_surplus_usd"]
        calculated = row["market_value_of_reserve_usd"] / row["outstanding_stablecoin_units"] * 100
        assert math.isclose(calculated, row["reserve_coverage_percent"], abs_tol=1e-10)
        assert row["reserve_surplus_usd"] > 0


def test_reserve_asset_composition_reconciles_to_reported_totals():
    data = load_artifact()["independently_attested_reserve_snapshots"]["report_dates"]
    for row in data.values():
        composition = row["asset_composition_usd"]
        total = sum(composition.values())
        assert total == row["market_value_of_reserve_usd"]


def test_attestation_report_date_is_separate_from_publication_date():
    data = load_artifact()["independently_attested_reserve_snapshots"]
    assert data["report_signed_date"] == "2026-10-26"
    assert data["report_dates"]["2026-09-21"]["outstanding_stablecoin_units"] == 2_425_816_183
    assert data["report_dates"]["2026-09-30"]["outstanding_stablecoin_units"] == 2_399_995_528
    assert "fairly stated" in data["independent_accountant_opinion"]


def test_october_29_live_dashboard_is_not_mislabeled_as_cpa_attested():
    item = load_artifact()["issuer_dashboard_snapshot"]
    assert item["circulating_rlusd_usd"] == 2_627_000_000
    assert item["reserve_funds_usd"] == 2_758_600_000
    assert item["arithmetic_excess_reserves_usd"] == 131_600_000
    assert item["attested_as_of_this_date"] is False
    assert item["latest_independent_attestation_balance_date"] == "2026-09-30"


def test_rlusd_issuer_and_parent_are_distinguished():
    item = load_artifact()["issuer_and_regulatory_scope"]
    assert item["legal_issuer"] == "Standard Custody & Trust Company, LLC"
    assert item["parent"] == "Ripple Labs Inc."
    assert item["charter"] == "New York limited purpose trust company supervised by NYDFS"


def test_reserve_asset_classes_do_not_claim_xrp_as_collateral():
    data = load_artifact()
    text = json.dumps(data["independently_attested_reserve_snapshots"]).lower()
    assert "us treasury bills" in text
    assert "government money-market funds" in text
    assert "deposits" in text
    assert "does not identify xrp as a reserve asset" in data["independently_attested_reserve_snapshots"]["interpretation"].lower()
    assert "not xrp balances or xrp collateral" in data["model_eligibility"]["reasons"][0].lower()


def test_approved_networks_are_not_mislabeled_as_actual_chain_supply():
    item = load_artifact()["issuer_and_regulatory_scope"]
    assert "XRPL" in item["nydfs_approved_blockchain_networks"]
    assert "Ethereum" in item["nydfs_approved_blockchain_networks"]
    assert "Base" in item["nydfs_approved_blockchain_networks"]
    assert "does not establish actual circulating supply" in item["network_approval_limitation"]


def test_reserve_snapshot_is_not_an_xrp_model_feature_or_forecast():
    data = load_artifact()
    assert data["model_eligibility"]["eligible"] is False
    assert data["model_eligibility"]["forecast_issued"] is False
    assert data["model_eligibility"]["feature_admission"] == "INSTITUTIONAL_CONTEXT_ONLY_NOT_XRP_FEATURE"
    assert data["source_capture_policy"]["raw_source_bytes_preserved"] is False
