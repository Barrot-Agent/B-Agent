import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T054303Z-rlusd-institutional-custody-collateral-network.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def edge(data, edge_id):
    return next(item for item in data["relationships"] if item["id"] == edge_id)


def test_standard_chartered_rlusd_custody_is_separate_from_planned_lmax_collateral():
    data = load()
    custody = edge(data, "standard_chartered_custody_xrpl_rlusd")
    collateral = edge(data, "standard_chartered_ripple_lmax_collateral")
    assert custody["status"] == "LIVE_REPORTED"
    assert custody["instrument"] == "RLUSD"
    assert "DIFC Branch" in custody["scope"]
    assert collateral["status"] == "PLANNED_NOT_LIVE"
    assert "successful testing" in collateral["conditions"]
    assert "XRP collateral" in collateral["not_established"]


def test_coinbase_rlusd_distribution_is_live_but_global_exchange_collateral_is_future():
    data = load()
    distribution = edge(data, "ripple_coinbase_rlusd_distribution")
    collateral = edge(data, "coinbase_rlusd_global_exchange_collateral")
    assert distribution["status"] == "LIVE_REPORTED"
    assert set(distribution["networks"]) == {"XRPL", "Base", "Ethereum"}
    assert "Coinbase is RLUSD issuer" in distribution["not_established"]
    assert collateral["status"] == "FUTURE_NOT_LIVE_IN_LAUNCH_ANNOUNCEMENT"


def test_sbi_vc_trade_chain_support_is_service_specific_and_ethereum_only_at_launch():
    data = load()
    sbi = edge(data, "sbi_vc_trade_rlusd_distribution")
    assert sbi["status"] == "LIVE_REPORTED"
    assert sbi["service_network_at_launch"] == ["Ethereum"]
    assert sbi["network_expansion_status"] == "NO_LATER_OFFICIAL_XRPL_SUPPORT_CONFIRMATION_FOUND_BY_2026-11-05"
    assert "any involvement by SBIC East/Central/West" in sbi["not_established"]


def test_lmax_financing_commitment_is_not_counted_as_disbursed_capital():
    data = load()
    financing = edge(data, "ripple_lmax_financing")
    assert financing["amount_usd"] == 150000000
    assert financing["status"] == "COMMITMENT_ANNOUNCED_DISBURSEMENT_UNVERIFIED"
    assert "cash disbursement" in financing["not_established"]
    assert data["capital_reconciliation"]["status"] == "ANNOUNCED_NOT_VERIFIED_AS_DISBURSED"


def test_rlusd_reserve_dashboard_arithmetic_and_attestation_vintage_are_distinct():
    data = load()
    reserves = edge(data, "rlusd_reserve_dashboard_20261029")
    assert reserves["circulation_usd"] == 2627000000
    assert reserves["reserve_funds_usd"] == 2758600000
    assert reserves["excess_reserves_usd"] == 131600000
    expected = reserves["reserve_funds_usd"] / reserves["circulation_usd"] * 100
    assert math.isclose(reserves["reserve_coverage_pct"], expected, rel_tol=0, abs_tol=1e-12)
    assert "October 29 CPA attestation" in reserves["not_established"]


def test_rlusd_issuer_is_not_coinbase_or_ripple_national_trust_bank():
    data = load()
    separation = data["instrument_separation"]
    assert "Standard Custody & Trust Company" in separation["rlusd"]
    assert "not the RLUSD issuer" in separation["ripple_national_trust_bank"]
    assert "not the issuer" in separation["coinbase"]


def test_rlusd_institutional_adoption_does_not_issue_an_xrp_forecast():
    data = load()
    assert data["model_eligible"] is False
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"
    assert data["data_quality"]["raw_source_bytes_captured"] is False
    assert all(source["model_eligible"] is False for source in data["source_registry"])
