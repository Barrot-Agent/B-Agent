import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T181500Z-xrp-late-session-spot-perpetuals-followup.json"


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_late_ticker_arithmetic_and_utc_day_open_label():
    data = _load()
    spot = data["market_snapshot"]["kraken_spot"]
    midpoint = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    spread_bps = (spot["best_ask_usd"] - spot["best_bid_usd"]) / midpoint * 10000
    assert abs(midpoint - spot["midpoint_usd"]) < 1e-12
    assert abs(spread_bps - spot["spread_bps"]) < 1e-12
    assert spot["utc_day_open_label"] == "current UTC-day open, not rolling 24-hour open"
    assert spot["last_at_24h_low"] is True
    assert spot["provider_event_time_utc"] is None
    assert spot["retrieved_at_utc"] is None
    assert spot["model_eligible"] is False


def test_same_venue_capture_difference_is_not_mislabeled_as_a_timed_return():
    comparison = _load()["market_snapshot"]["same_venue_prior_capture_comparison"]
    expected = (comparison["current_last_usd"] / comparison["prior_last_usd"] - 1) * 100
    assert abs(expected - comparison["difference_pct_vs_prior_capture"]) < 1e-12
    assert comparison["elapsed_seconds"] is None
    assert comparison["interval_status"] == "UNKNOWN"


def test_derivatives_open_interest_universes_are_not_averaged():
    market = _load()["market_snapshot"]
    reconciliation = market["reconciliation"]
    assert market["tradradar_perpetuals"]["open_interest_usd"] == 1950000000
    assert market["alpha_finance_perpetuals"]["open_interest_usd"] == 2840000000
    assert reconciliation["oi_difference_usd"] == 890000000
    assert reconciliation["oi_aggregation"] == "NOT_AVERAGED"
    assert market["tradradar_perpetuals"]["liquidation_coverage_exchanges"] == 5
    assert market["tradradar_perpetuals"]["long_short_coverage_exchanges"] == 5


def test_both_latest_dashboards_show_long_dominated_liquidations_but_not_independent_feeds():
    market = _load()["market_snapshot"]
    recon = market["reconciliation"]
    assert market["tradradar_perpetuals"]["long_liquidations_usd"] > market["tradradar_perpetuals"]["short_liquidations_usd"]
    assert market["alpha_finance_perpetuals"]["long_liquidations_24h_usd"] > market["alpha_finance_perpetuals"]["short_liquidations_24h_usd"]
    assert recon["trad_long_share_pct"] > 95
    assert recon["alpha_long_share_pct"] > 95
    assert "overlapping public exchange feeds" in recon["independence_caveat"]


def test_alpha_heatmap_levels_remain_modelled_not_actual_orders_or_forecasts():
    alpha = _load()["market_snapshot"]["alpha_finance_perpetuals"]
    assert alpha["cluster_status"] == "MODELLED_FROM_OPEN_INTEREST_AND_STANDARD_LEVERAGE_TIERS"
    assert alpha["binance_map_status"] == "NOT_AVAILABLE_FOR_THIS_WINDOW"
    assert alpha["model_eligible"] is False
    assert _load()["admission"]["directional_forecast_issued"] is False


def test_prior_alpha_liquidation_vintage_reversal_is_preserved():
    data = _load()
    prior = data["market_snapshot"]["reconciliation"]["prior_alpha_snapshot"]
    assert prior["long_liquidations_usd"] < prior["short_liquidations_usd"]
    assert data["market_snapshot"]["alpha_finance_perpetuals"]["long_liquidations_24h_usd"] > data["market_snapshot"]["alpha_finance_perpetuals"]["short_liquidations_24h_usd"]
    assert "not silently overwritten" in prior["interpretation"]
