from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "data/xrp_intelligence/snapshots").glob("*-xrp-market-structure-multi-provider-reconciliation.json"))


def load():
    assert FILES, "XRP market structure reconciliation snapshot missing"
    return json.loads(FILES[-1].read_text(encoding="utf-8"))


def test_open_interest_providers_are_not_averaged_or_misrepresented_as_same_universe():
    d = load()
    assert d["provider_disagreement"]["classification"] == "UNRESOLVED_COVERAGE_AND_METHODOLOGY_DIFFERENCE"
    assert d["provider_disagreement"]["tradradar_oi_usd"] != d["provider_disagreement"]["kodexius_oi_usd"]
    assert "Do not average" in d["provider_disagreement"]["rule"]


def test_long_short_accounts_and_liquidation_lower_bounds_keep_their_units():
    d = load()
    tr = next(x for x in d["observations"] if x["provider"] == "TradRadar")
    assert tr["long_account_share_pct"] == 77.9
    assert "not notional exposure" in tr["notes"][1]
    assert tr["liquidations_24h_usd_lower_bound"] == 1010000


def test_exchange_wallet_balances_are_not_tradable_float():
    d = load()
    ex = next(x for x in d["observations"] if x["provider"] == "XRP Insights exchange-wallet tracker")
    assert ex["coinbase_cold_labeled_xrp"] == 5800000000
    assert any("not tradable float" in note for note in ex["notes"])


def test_etf_flow_gap_and_inclusion_scope_are_explicit():
    d = load()
    etf = next(x for x in d["observations"] if x["provider"] == "XRP Insights ETF tracker")
    assert etf["weekly_net_flow_xrp"] == 3390000
    assert any("GXRP is excluded" in note for note in etf["notes"])
    assert d["prediction_status"] == "NOT_ISSUED"
