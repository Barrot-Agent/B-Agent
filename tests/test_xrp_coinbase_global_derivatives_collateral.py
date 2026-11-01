from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "data/xrp_intelligence/snapshots/20261101T222456Z-coinbase-global-derivatives-xrp-collateral.json"

def load():
    return json.loads(SNAP.read_text(encoding="utf-8"))

def test_xrp_is_non_us_cross_collateral_with_separate_haircuts():
    d = load()["non_us_global_derivatives"]
    assert d["xrp_cross_collateral"] is True
    assert d["xrp_haircut_cross_standard_margin_pct"] == 15
    assert d["xrp_haircut_cross_portfolio_margin"] == "dash/no haircut listed"
    assert "outside" in d["eligibility"]

def test_xrp_collateral_can_support_usdc_settled_derivatives():
    d = load()["non_us_global_derivatives"]
    assert "any cross-margined derivative position" in d["scope"]
    assert d["xrp_options"]["settlement_currency"] == "USDC"
    assert d["xrp_options"]["contract_multiplier_xrp"] == 1000

def test_us_prime_public_collateral_list_does_not_include_xrp():
    d = load()["us_prime_global_derivatives"]
    assert d["publicly_listed_eligible_collateral"] == ["USDC", "BTC", "ETH"]
    assert d["xrp_collateral_in_current_public_list"] is False

def test_cftc_letter_is_pathway_not_actual_xrp_use():
    d = load()["cftc_letter_26_17"]
    assert "XRP" in d["digital_commodity_interpretation"]
    assert d["actual_xrp_use"] == "NOT_VERIFIED; current Coinbase Prime public collateral list remains USDC, BTC and ETH."

def test_rebalancing_is_separate_from_liquidation():
    d = load()["non_us_global_derivatives"]["risk_controls"]
    assert "separate from liquidation" in d["rebalancing"]
    assert d["collateral_fee_default_pct_per_day"] == 0.05
