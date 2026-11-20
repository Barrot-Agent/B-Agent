from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T190906Z-xrp-spot-depth-derivatives-etf-institutional-capital-update.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_source_receipts_reproduce_and_capture_limits_are_explicit():
    data = load_artifact()
    assert len(data["sources"]) == 10
    for source in data["sources"]:
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == source["sha256"]
        assert source["independence_group"]
        assert source["url"].startswith("https://")
    assert data["capture_contract"]["common_cutoff_utc"] is None
    assert data["capture_contract"]["original_wire_bytes_captured"] is False
    assert data["capture_contract"]["headers_captured"] is False


def test_direct_exchange_timestamps_do_not_form_a_synchronized_return():
    spot = load_artifact()["observations"]["spot"]
    assert spot["kraken"]["last"] == 1.18304
    assert spot["kraken"]["provider_timestamp"] is None
    assert spot["okx"]["event_time_utc"] == "2026-11-06T19:02:21.864Z"
    assert spot["okx"]["last_usdt"] == 1.1847
    assert spot["cross_venue_comparison_eligible"] is False


def test_spot_only_and_mixed_spot_perpetual_depth_are_not_combined():
    depth = load_artifact()["observations"]["depth"]
    fuelmaps = depth["fuelmaps"]
    edge = depth["edgeornot"]
    assert fuelmaps["bands_usd"]["0.5"] == [9_000_000, 5_100_000]
    assert fuelmaps["bands_usd"]["1"] == [14_000_000, 9_300_000]
    assert fuelmaps["venues_by_band"]["10"] == 5
    assert "spot venues" in fuelmaps["scope"]
    assert "Binance spot plus OKX perpetual" in edge["scope"]
    assert edge["within_1pct_usd"] == {"bids": 9_500_000, "asks": 8_600_000}


def test_derivatives_coverage_units_and_liquidation_lower_bound_are_explicit():
    row = load_artifact()["observations"]["derivatives"]
    assert row["oi_usd"] == 1_900_000_000
    assert row["oi_venues"] == 7
    assert row["oi_change_pct"] == -2.47
    assert row["funding_pct_per_8h"] == 0.001
    assert row["liquidations_lower_bound_usd"] == 11_960_000
    assert row["long_liquidations_usd"] == 11_360_000
    assert row["short_liquidations_usd"] == 600_340
    assert row["liquidation_venues"] == 5
    assert row["long_short_account_ratio"] == 3.9


def test_etf_holdings_delta_is_not_ap_cash_flow_and_vintages_are_preserved():
    row = load_artifact()["observations"]["etf"]
    assert row["holdings_delta_xrp"] == -149_487
    assert row["holdings_xrp"] == 1_196_450_700
    assert row["settled_days"] == 4
    assert row["not_ap_cash_flow"] is True
    assert row["flow_excluded_funds_count_as_zero"] is True
    assert row["prior_vintage_nov2_4_xrp"] == -259_701


def test_evernorth_actual_proceeds_debt_and_sbi_entity_classes_are_separate():
    row = load_artifact()["observations"]["capital"]
    evernorth = row["evernorth_pik_notes"]
    facility = row["ripple_company_facility"]
    assert evernorth["net_proceeds_before_expenses_usd"] == 30_000_000
    assert evernorth["issued_paid"] == "2026-10-12"
    assert evernorth["purchaser"] == "NH Investment & Securities Co., as trustee of Kyobo AIM Corporate Finance General Private Investment Trust No. 3"
    assert evernorth["net_cash_after_advisor_fee_usd"] == 29_000_000
    assert evernorth["advisor_fee_usd"] == 1_000_000
    assert evernorth["conversion_earliest_date"] == "2027-10-12"
    assert evernorth["holder_controls_settlement_form"] is True
    assert evernorth["settlement_forms"] == ["cash", "shares", "cash_and_shares"]
    assert evernorth["conversion_applies_to_all_notes_only"] is True
    assert evernorth["cash_settlement_exposure_up_to_usd"] == 120_000_000
    assert evernorth["default_or_fundamental_transaction_yield_to_put_pct"] == 8.0
    assert evernorth["potential_xrp_sale_to_fund_cash_settlement"] is True
    assert evernorth["permitted_use_includes_xrp"] is True
    assert evernorth["actual_xrp_spend_verified"] is False
    assert facility["limit_usd"] == 10_000_000
    assert facility["drawn_as_of_2026_10_07_usd"] == 9_700_000
    assert facility["xrp_purchase_disclosed"] is False
    assert row["separate_evernorth_facility_limit_usd"] == 1_000_000
    assert len(row["sbi_stockholders"]) == 4
    assert row["sbi_parent"] == "SBI Holdings, Inc."
    assert row["regional_sbic_is_distinct"] is True


def test_custody_is_distinguished_from_planned_collateral_and_transaction_volume():
    institutional = load_artifact()["observations"]["institutional"]
    sc = institutional["standard_chartered_lmax_ripple"]
    bny = institutional["bny"]
    assert sc["rlusd_xrpl_custody"].startswith("live")
    assert sc["rlusd_collateral_mirroring"].startswith("planned")
    assert sc["live_balance_disclosed"] is False
    assert bny["primary_rlusd_reserve_custodian"] is True
    assert bny["xrp_rlusd_custody_support"].startswith("announced")
    assert bny["auc_disclosed"] is False


def test_xrpl_lending_votes_do_not_imply_live_collateralized_lending():
    row = load_artifact()["observations"]["governance"]
    assert row["single_asset_vault_yes"] == 23
    assert row["lending_protocol_yes"] == 21
    assert row["lending_v1_1_yes"] == 21
    assert row["trusted_validators"] == 35
    assert row["required_yes"] == 29
    assert row["continuous_days"] == 14
    assert row["production_lending_verified"] is False
    assert row["lending_uncollateralized"] is True
    assert row["vault_deposits_are_pool_funding_not_borrower_collateral"] is True


def test_hypotheses_retain_counterevidence_and_no_forecast_is_issued():
    data = load_artifact()
    hypotheses = data["hypotheses"]
    assert len(hypotheses) == 6
    assert all(item["support"] and item["counter"] for item in hypotheses)
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast"] == {"status": "NOT_ISSUED", "directional_forecast": False}


def test_no_external_or_financial_actions_occurred():
    safety = load_artifact()["safety"]
    assert all(value is False for value in safety.values())
