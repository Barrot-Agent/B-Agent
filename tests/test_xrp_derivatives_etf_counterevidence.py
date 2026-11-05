"""Regression tests for XRP market, derivatives and ETF-flow counterevidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T012000Z-xrp-market-derivatives-etf-counterevidence.json"


def test_spot_ticker_is_not_promoted_to_market_wide_depth():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    spot = data["market_snapshot"]
    assert spot["venue"] == "Kraken"
    assert spot["best_bid_size_xrp"] == 5963
    assert spot["best_ask_size_xrp"] == 11898
    assert spot["quoted_spread_basis_points"] == 0.0768
    assert "not a full depth ladder" in spot["interpretation"]
    assert data["feature_admission"]["model_eligible"] is False


def test_derivatives_provider_scope_and_disagreement_are_not_averaged():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    disagreement = data["provider_disagreement"]
    assert disagreement["binance_open_interest"]["fibonomy_usd"] == 451120000
    assert disagreement["binance_open_interest"]["tradradar_binance_component_usd"] == 538280000
    assert disagreement["binance_open_interest"]["absolute_difference_usd"] == 87160000
    assert "Do not average" in disagreement["binance_open_interest"]["treatment"]
    trad = next(x for x in data["derivatives_snapshots"] if x["provider"] == "TradRadar")
    assert trad["open_interest_7_exchanges_usd"] == 2040000000
    assert trad["long_short_account_ratio_5_exchanges"] == 3.24
    assert trad["model_eligible"] is False


def test_etf_flow_predictiveness_counterevidence_is_preserved_without_forecast():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    study = data["etf_flow_predictiveness_study"]
    assert study["xrp_rank_correlation_next_24h"] == -0.02
    assert study["xrp_rank_correlation_same_day"] == 0.11
    assert study["sample_count_disclosed_in_available_extract"] is False
    assert study["model_eligible"] is False
    assert data["predictions"]["forecast_issued"] is False
    assert data["predictions"]["direction"] is None
