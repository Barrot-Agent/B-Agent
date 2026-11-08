from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261108T170121Z-coinbase-circle-sbi-robinhood-institutional-rails-correction.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_coinbase_q3_filing_values_and_circle_renewal_are_preserved():
    data = load_artifact()["findings"]["coinbase_q3_2026"]
    assert data["stablecoin_revenue_usd_thousands"] == {
        "q3_2026": 306905,
        "q3_2025": 324534,
        "nine_months_2026": 904487,
        "nine_months_2025": 907485,
    }
    assert "same terms" in data["circle_arrangement"]
    assert "Other revenue" in data["presentation_correction"]
    assert "no impact on total revenue" in data["presentation_correction"]


def test_circle_q3_usdc_and_coinbase_distribution_costs_are_separate_measures():
    data = load_artifact()["findings"]["circle_q3_2026"]
    assert data["usdc_usd_billions"]["average_circulation_q3_2026"] == 73.264
    assert data["usdc_usd_billions"]["end_period_circulation_q3_2026"] == 73.879
    assert data["usdc_usd_billions"]["end_period_usdc_on_platform_q3_2026"] == 13.868
    assert data["reserve_return_rate_percent"]["q3_2026"] == 3.5
    assert data["daily_weighted_average_on_platform_percentage"]["q3_2026"] == 18.1
    assert data["coinbase_related_distribution_costs_usd_millions"]["q3_2026"] == 331.3
    assert data["coinbase_related_distribution_costs_usd_millions"]["nine_months_2026"] == 986.6


def test_coinbase_revenue_and_circle_distribution_costs_are_never_netted():
    data = load_artifact()["findings"]["accounting_boundary"]
    assert "Do not subtract or net" in data["rule"]
    assert "not a verified bilateral profit" in data["prohibited_inference"]


def test_sbi_vc_trade_rlusd_is_currently_ethereum_only_not_live_on_xrpl():
    data = load_artifact()["findings"]["sbi_vc_trade_rlusd"]
    assert data["current_network"] == "SBI VC Trade's current VCTRADE network-support FAQ lists RLUSD on Ethereum only."
    assert "expand supported chains sequentially" in data["future_network"]
    assert "does not establish XRPL support as live" in data["future_network"]
    assert "SBI Holdings" in data["legal_entity"]
    assert "SBI VC Trade" in data["legal_entity"]


def test_coinbase_rlusd_networks_are_live_but_global_exchange_collateral_was_future():
    data = load_artifact()["findings"]["coinbase_ripple_rlusd"]
    assert set(data["supported_networks"]) == {"XRPL", "Base", "Ethereum"}
    assert "Coinbase Global Exchange availability" in data["future_at_announcement"]
    assert "RLUSD collateral use on Coinbase Global Exchange" in data["future_at_announcement"]


def test_bny_custody_is_distinguished_from_future_mint_redeem_and_trade_finance():
    data = load_artifact()["findings"]["bny_ripple"]
    assert "supports XRP and RLUSD" in data["live_or_announced_current_capability"]
    assert "Direct RLUSD mint/redeem through BNY" in data["future_or_exploratory"]
    assert any("Tokenized trade-finance workflows" in item for item in data["future_or_exploratory"])
    assert "not a disclosed balance" in data["interpretation"]


def test_robinhood_rlusd_network_status_and_xrpl_institutional_use_are_not_overstated():
    data = load_artifact()["findings"]["robinhood_ripple"]
    assert any("Robinhood Chain" in item for item in data["live_at_announcement"])
    assert any("Bitstamp by Robinhood" in item for item in data["live_at_announcement"])
    assert "Robinhood app availability" in data["expected_later_2026"]
    assert "will leverage RLUSD on XRPL" in data["announced_xrpl_use"]
    assert "does not disclose completed XRPL settlement volumes" in data["interpretation"]


def test_sources_preserve_independence_receipt_limits_and_no_market_admission():
    data = load_artifact()
    assert len(data["source_inventory"]) == 7
    assert all(len(source["sha256_of_normalized_excerpt"]) == 64 for source in data["source_inventory"])
    assert all(source["raw_wire_bytes_captured"] is False for source in data["source_inventory"])
    assert len(data["source_independence"]["groupings"]) == 3
    assert data["model_admission"]["admitted_to_feature_store"] is False
    assert data["model_admission"]["directional_signal"] is False
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["receipt_limits"]["raw_http_bytes"] is False
