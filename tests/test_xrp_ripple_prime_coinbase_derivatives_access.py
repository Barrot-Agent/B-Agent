from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "data/xrp_intelligence/research_ledger_addenda").glob("*-ripple-prime-coinbase-derivatives-xrp-access-and-cot.json"))


def load():
    assert FILES, "Ripple Prime/Coinbase Derivatives evidence artifact missing"
    return json.loads(FILES[-1].read_text(encoding="utf-8"))


def test_ripple_prime_access_is_a_confirmed_institutional_link_not_spot_demand():
    d = load()
    assert any(x["from"] == "Ripple Prime" and x["to"] == "Coinbase Derivatives" for x in d["confirmed_relationships"])
    assert "not evidence of spot XRP purchases" in d["executive_finding"]


def test_cot_xrp_equivalent_uses_contract_multipliers_and_is_not_custodied_xrp():
    d = load()["cftc_cot_snapshot"]
    assert sum(x["xrp_equivalent"] for x in d["contracts"]) == d["combined_contract_notional_xrp_equivalent"]
    assert d["combined_contract_notional_xrp_equivalent"] == 293853500
    assert "Not XRP held in custody" in d["interpretation"]


def test_cash_settled_futures_are_not_physical_delivery():
    d = load()
    assert any("Cash-settled XRP futures do not require physical XRP delivery." == x for x in d["non_equivalences"])


def test_coinbase_prime_access_does_not_conflate_cftc_26_17_route():
    d = load()
    assert any("26-17" in x and "separate" in x for x in d["non_equivalences"])
    assert d["prediction_status"] == "NOT_ISSUED"
