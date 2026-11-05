import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T143601Z-xrp-spot-depth-derivatives-snapshot.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_ticker_spread_and_daily_open_are_labeled_correctly():
    data = load()
    spot = data["market_snapshot"]["kraken_spot"]
    expected = (spot["best_ask_usd"] - spot["best_bid_usd"]) / spot["midpoint_usd"] * 10000
    assert abs(spot["spread_bps"] - expected) < 1e-12
    assert spot["daily_open_label"] == "current UTC-day open; not a rolling 24-hour open"
    assert spot["last_vs_vwap_pct"] if "last_vs_vwap_pct" in spot else spot["derived"]["last_vs_vwap_pct"] < 0
    assert spot["derived"]["last_vs_daily_open_pct"] < 0


def test_fuelmaps_depth_preserves_venue_coverage_and_cancellation_limits():
    data = load()
    depth = data["market_snapshot"]["fuelmaps_spot_depth"]
    assert depth["snapshot_at_utc"] == "2026-11-05T14:00:00Z"
    assert depth["depth_usd"]["within_0_5_pct"]["bid_share_pct"] == 64.1
    assert depth["depth_usd"]["within_10_pct"]["venues"] == "5 of 6"
    assert set(depth["full_depth_venues"]) == {"Coinbase", "Bitstamp", "Bitfinex", "Gemini"}
    assert "Resting orders can cancel at any time" in depth["limitations"][0]


def test_perpetual_open_interest_disagreement_is_not_averaged():
    data = load()["market_snapshot"]["derivatives"]
    k = data["kodexius"]["open_interest_usd"]
    t = data["tradradar"]["open_interest_usd"]
    disagreement = data["disagreement"]
    assert k == 884_080_000
    assert t == 2_060_000_000
    assert disagreement["absolute_oi_difference_usd"] == t - k
    assert abs(disagreement["trad_radar_to_kodexius_ratio"] - t / k) < 1e-12
    assert disagreement["aggregation"] == "not_averaged"
    assert data["tradradar"]["long_short_account_ratio"] == 3.23
    assert data["tradradar"]["long_account_pct"] == 76.4


def test_market_snapshot_remains_model_ineligible_and_no_forecast_is_issued():
    data = load()
    assert data["source_capture_policy"]["raw_bytes_preserved"] is False
    assert data["source_capture_policy"]["sha256_receipts"] is None
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["forecast_status"] == "NOT_ISSUED"
    assert len(data["source_registry"]) == 4
    assert len({source["source_independence_group"] for source in data["source_registry"]}) == 4
