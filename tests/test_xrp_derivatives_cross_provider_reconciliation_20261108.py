from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261108T114400Z-xrp-derivatives-open-interest-funding-cross-provider-reconciliation.json"

def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))

def test_open_interest_provider_universes_remain_separate():
    a = load_artifact()["observations"]["cross_provider_reconciliation"]
    assert a["open_interest_values_usd"] == {"kodexius": 785_310_000, "tradradar": 1_900_000_000, "coingecko": 3_995_000_000}
    assert a["do_not_average_open_interest"] is True
    assert a["open_interest_status"] == "UNRESOLVED_UNIVERSE_AND_CONTRACT_SCOPE_DIFFERENCE"

def test_funding_intervals_and_venue_outliers_are_preserved():
    a = load_artifact()["observations"]
    assert a["tradradar"]["venue_funding_pct_per_8h"]["Bitget"] < 0
    assert a["bentley_markets"]["exchanges_positive"] == 16
    assert a["fensory_hyperliquid"]["funding_pct_per_hour"] == 0.00027
    assert a["cross_provider_reconciliation"]["do_not_average_funding"] is True

def test_long_liquidation_skew_is_risk_context_not_directional_forecast():
    a = load_artifact()["observations"]["tradradar"]
    assert a["long_account_share_pct"] == 79.1
    assert a["long_liquidations_usd"] > a["short_liquidations_usd"]
    assert load_artifact()["forecast_status"] == "NOT_ISSUED"

def test_derivatives_sources_are_not_model_eligible_without_raw_receipts():
    a = load_artifact()
    assert a["data_quality"]["raw_exchange_payloads"] is False
    assert all(s["model_eligible"] is False for s in a["sources"])
    assert a["admission"]["feature_store_admission"] == "PROHIBITED"
