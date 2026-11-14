from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "data/xrp_intelligence/research_ledger_addenda").glob("*-coinbase-xrp-collateral-pathways-cftc-26-17.json"))


def load():
    assert FILES, "Coinbase XRP collateral-pathway evidence artifact missing"
    return json.loads(FILES[-1].read_text(encoding="utf-8"))


def test_non_us_xrp_collateral_is_separated_from_us_prime_scope():
    d = load()
    by_id = {item["id"]: item for item in d["confirmed_facts"]}
    assert "15%" in by_id["CB_NONUS_XRP_COLLATERAL"]["finding"]
    assert "UNSPECIFIED" in by_id["CB_NONUS_XRP_COLLATERAL"]["finding"]
    assert "XRP is not on the public U.S. Prime collateral list" in by_id["CB_US_PRIME_SCOPE"]["finding"]


def test_cftc_26_05_initial_period_and_xrp_dcm_limb_are_not_conflated():
    d = load()
    by_id = {item["id"]: item for item in d["confirmed_facts"]}
    assert "first three months" in by_id["CFTC_26_05_FIRST_THREE_MONTHS"]["finding"]
    assert "underlying commodity" in by_id["XRP_CFTC_DCM_FUTURES"]["finding"]
    assert "notice of intent" in " ".join(d["unknowns"]).lower()


def test_rebalancing_is_a_conditional_flow_not_an_observed_sale():
    d = load()
    assert any(item["id"] == "POTENTIAL_STRESS_SELL_FLOW" for item in d["inferences"])
    assert "No posted XRP balances or rebalancing volumes are disclosed." in d["inferences"][0]["disconfirming_or_limiting_evidence"]


def test_cftc_custody_representation_and_120_percent_cap_are_scoped_correctly():
    d = load()
    item = next(x for x in d["confirmed_facts"] if x["id"] == "CFTC_26_17_CUSTODY_REPRESENTATION")
    assert "not an independent custody audit" in item["finding"]
    assert "Regulation 30.7(c)" in item["finding"]


def test_no_xrp_forecast_is_issued_from_product_eligibility_alone():
    d = load()
    assert d["prediction_status"] == "NOT_ISSUED"
