import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261111T140912Z-run26c-sbi-vc-trade-stablecoin-custody-lending-and-network-limits.json"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sbi_vc_trade_stablecoin_networks_are_not_conflated_with_issuer_networks() -> None:
    data = _load()
    networks = data["network_support_and_operational_limits"]
    assert networks["usdc"]["native_network_scope"] == "Multiple networks including XRPL"
    assert networks["usdc"]["sbivc_current_deposit_withdrawal_networks"] == ["Ethereum"]
    assert networks["usdc"]["xrpl_supported_by_sbivc"] is False
    assert networks["rlusd"]["native_network_scope"] == "XRPL and Ethereum"
    assert networks["rlusd"]["sbivc_current_deposit_withdrawal_networks"] == ["Ethereum"]
    assert networks["rlusd"]["xrpl_supported_by_sbivc"] is False
    assert networks["usdc"]["customer_balance_limit_jpy_equivalent"] == 1_000_000
    assert networks["rlusd"]["customer_balance_limit_jpy_equivalent"] == 1_000_000


def test_sbi_usdc_lending_is_not_a_deposit_and_preserves_counterparty_risk() -> None:
    data = _load()
    lending = data["usdc_lending_product"]
    assert lending["legal_form"].startswith("Consumption-loan")
    assert lending["stated_term_weeks"] == 12
    assert lending["advertised_annual_rate_percent"] == 5
    assert "not guaranteed" in lending["rate_status"].lower()
    assert lending["maximum_per_subscription_usdc"] == 5_000
    assert lending["segregation_under_japanese_funds_settlement_act"] is False
    assert lending["reuse_or_re_lending"].startswith("SBI VC Trade states it may re-lend")
    assert "insolvent" in lending["counterparty_risk"].lower()
    assert lending["actual_outstanding_usdc"] is None
    assert lending["status"] == "PRODUCT_OFFERED_AGGREGATE_VOLUME_NOT_DISCLOSED"


def test_stablecoin_supply_snapshots_keep_their_dates_and_issuers_separate() -> None:
    data = _load()
    usdc = data["issuer_supply_and_reserve_snapshots"]["usdc"]
    assert usdc[0]["data_as_of"] == "2026-07-31"
    assert usdc[1]["data_as_of"] == "2026-11-09"
    assert usdc[0]["source_id"] != usdc[1]["source_id"]
    rlusd = data["issuer_supply_and_reserve_snapshots"]["rlusd"]
    assert rlusd["data_as_of"] == "2026-08-27"
    assert rlusd["circulation_usd"] == 1_866_500_000
    assert "BNY Mellon" in rlusd["reserve_policy"]


def test_collateral_rules_are_generic_and_do_not_assert_token_balances() -> None:
    data = _load()
    collateral = data["collateral_and_xrp_market_access"]
    assert collateral["generic_crypto_asset_valuation_factor_pct"] == 50
    assert collateral["generic_electronic_payment_instrument_valuation_factor_pct"] == 100
    assert "not enumerated" in collateral["token_specific_collateral_eligibility"].lower()
    assert collateral["actual_collateral_balances"] == "Not disclosed in the reviewed sources."


def test_actual_capital_and_forecast_gates_remain_separate() -> None:
    data = _load()
    assert "not actual subscribed USDC" in data["actual_capital_interpretation"]
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"
    assert data["model_eligibility"]["status"] == "EXCLUDED"
    assert data["model_eligibility"]["raw_receipts_created"] is False
    assert data["safety"]["no_real_money"] is True
