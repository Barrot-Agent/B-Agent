from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T171619Z-sbi-ripple-xrpl-tokenization-and-remittance-network-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sbi_ripple_asia_xrpl_platform_and_registration_are_distinct_from_usage():
    data = load()
    item = data["reconciled_relationships"]["sbi_ripple_asia_xrpl_platform"]
    assert item["development"] == "COMPLETED"
    assert item["issuer_registration_date"] == "2026-03-26"
    assert item["actual_token_issuance_or_volume"] == "NOT_DISCLOSED"
    assert data["model_admission"]["feature_store"] == "PROHIBITED"


def test_sbi_ripple_asia_joint_venture_ownership_is_primary_sourced():
    data = load()
    item = data["reconciled_relationships"]["sbi_ripple_asia"]
    assert item["ownership_pct"] == {"sbi_group": 60, "ripple": 40}
    receipt = next(x for x in data["source_receipts"] if x["source_id"] == "sbi_ripple_asia_jv_and_sbi_remit_20250509")
    assert "2025-05-09" == receipt["source_date"]


def test_sbi_reported_ripple_stake_is_approximate_and_dated():
    data = load()
    item = data["reconciled_relationships"]["sbi_holdings_to_ripple"]
    assert item["reported_stake_pct_approx"] == 9
    assert item["latest_primary_snapshot_date"] == "2026-05-01"
    assert "not a November 8" in item["caution"]


def test_evernorth_sbi_cash_investment_is_not_aggregate_raise():
    data = load()
    item = data["capital_and_supply_reconciliation"]["evernorth"]
    assert item["sbi_reported_cash_investment_usd_m"] == 200
    assert item["aggregate_raise_usd_bn_over"] == 1.0
    assert item["do_not_conflate"] is True
    assert "multiple parties" in item["contributors"]


def test_sbi_xrp_holdings_snapshot_is_historical_and_not_a_current_flow():
    data = load()
    item = data["capital_and_supply_reconciliation"]["ripple_xrp_holdings"]
    assert item["as_of"] == "2026-04-27"
    assert item["ripple_actual_xrp_bn"] == 5.10
    assert item["ripple_escrow_xrp_bn"] == 33.20
    assert item["model_eligible"] is False


def test_sbi_multi_chain_strategy_prevents_xrpl_exclusivity_assumption():
    data = load()
    item = data["reconciled_relationships"]["sbi_group_digital_strategy"]
    assert item["chains"] == ["XRPL", "Canton", "Solana", "Ethereum"]
    assert item["stablecoins"] == ["USDC", "RLUSD", "JPYSC planned"]
    assert data["competing_hypotheses"][1]["status"] == "PLAUSIBLE_AND_CONSISTENT_WITH_PRIMARY_DISCLOSURES"


def test_sbi_remit_xrp_bridge_use_is_historical_not_a_current_volume_measure():
    data = load()
    item = data["reconciled_relationships"]["sbi_remit"]
    assert item["xrp_bridge_use_announced"] == "2021"
    assert item["corridor_expansion_announced"] == "2023-09-06"
    assert item["current_volume"] == "NOT_DISCLOSED"


def test_sbi_vctrade_rlusd_ethereum_status_is_not_confused_with_sbi_ripple_asia_xrpl():
    data = load()
    item = data["reconciled_relationships"]["sbi_vc_trade_rlusd"]
    assert item["current_supported_networks"] == ["Ethereum"]
    assert item["xrpl_support"] == "PLANNED_NOT_LIVE"
    assert data["reconciled_relationships"]["sbi_ripple_asia_xrpl_platform"]["development"] == "COMPLETED"


def test_normalized_source_record_hashes_are_exact():
    data = load()
    for receipt in data["source_receipts"]:
        canonical = json.dumps(
            receipt["normalized_observation_record"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        assert hashlib.sha256(canonical).hexdigest() == receipt["normalized_record_sha256"]


def test_no_sbi_relationship_observation_is_admitted_as_an_xrp_feature_or_forecast():
    data = load()
    assert data["model_admission"]["feature_store"] == "PROHIBITED"
    assert data["forecast_status"] == "NOT_ISSUED"
