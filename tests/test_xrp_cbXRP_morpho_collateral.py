from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/xrp_intelligence/snapshots/20261101T221537Z-cbxrp-morpho-usdc-collateral.json"

def load():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))

def test_cbXRP_reserve_and_supply_are_separately_recorded():
    d = load()["data"]["coinbase_wrapped_xrp"]
    assert d["reserve_xrp"] == 150_942_337.33
    assert d["supply_cbxrp"] == 150_940_089.8
    assert d["reserve_coverage_pct"] > 100

def test_morpho_utilization_is_not_collateral_ltv():
    d = load()["data"]["morpho_primary_market"]
    assert d["utilization_pct"] == 89.8
    assert d["liquidation_ltv_pct"] == 62.5
    assert d["aggregate_debt_to_collateral_pct"] < 49
    assert d["utilization_pct"] != d["liquidation_ltv_pct"]

def test_permissionless_market_attribution_remains_an_inference():
    d = load()["data"]["morpho_primary_market"]
    assert "STRONG_PUBLIC_DATA_INFERENCE" in d["attribution"]
    assert "permissionless" in d["attribution"]

def test_wrapped_xrp_and_usdc_credit_are_not_classified_as_new_spot_capital():
    d = load()["data"]["capital_classification"]
    assert d["underlying_xrp"] == "EXISTING_XRP_WRAPPED_AND_CUSTODIED; NOT_PROOF_OF_NEW_SPOT_PURCHASE"
    assert d["usdc_borrowed"] == "CREDIT_LIABILITY; NOT_NET_EXTERNAL_CAPITAL_OR_NEW_USDC_ISSUANCE"

def test_circle_link_is_indirect_and_does_not_claim_direct_lending():
    d = load()["data"]["circle_link"]
    assert d["usdc_is_the_debt_asset_in_the_cbXRP_market"] is True
    assert "no evidence Circle directly lends" in d["relationship"]
