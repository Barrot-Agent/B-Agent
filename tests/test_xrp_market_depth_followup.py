import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = "data/xrp_intelligence/snapshots/20261101T164508Z-xrp-market-depth-derivatives.json"


def load():
    return json.loads((ROOT / PATH).read_text(encoding="utf-8"))


def test_market_snapshot_is_retrieval_timestamped_and_quarantined():
    snap = load()
    assert snap["captured_at_utc"] == "2026-11-01T16:45:08Z"
    assert snap["market"]["price_usd"] == 1.25
    assert snap["market"]["perpetual_open_interest_usd"] == 3_501_000_000
    assert snap["market"]["funding_rate_8h_pct"] == 0.0093
    assert snap["market"]["perpetual_to_spot_24h_volume_ratio"] == 16.4
    assert snap["market"]["feature_admission"].startswith("DESCRIPTIVE_ONLY")
    assert snap["forecast_status"] == "NOT_ISSUED"


def test_coinbase_and_binance_depth_remains_pair_specific():
    snap = load()
    pairs = {(x["exchange"], x["pair"]): x for x in snap["spot_pairs"]}
    cb = pairs[("Coinbase Exchange", "XRP/USD")]
    binance_usdc = pairs[("Binance", "XRP/USDC")]
    binance_usdt = pairs[("Binance", "XRP/USDT")]
    assert cb["depth_plus_2pct_usd"] == 4_486_633
    assert cb["depth_minus_2pct_usd"] == 7_711_117
    assert binance_usdc["depth_plus_2pct_usd"] == 363_842
    assert binance_usdt["depth_plus_2pct_usd"] == 2_028_573
    assert "total_exchange_liquidity" not in snap


def test_treasury_field_is_not_attributed_to_evernorth():
    snap = load()
    market = snap["market"]
    assert market["coin_gecko_total_treasury_holding_field_xrp"] == 473_276_430
    assert "Unassigned" in market["treasury_field_attribution"]
    assert "not_admitted" in market["feature_admission"].lower()


def test_derivatives_metrics_are_not_promoted_to_directional_signal():
    snap = load()
    assert len(snap["derivatives_top_pairs"]) == 10
    assert snap["market"]["open_interest_to_market_cap_pct"] == 4.43
    assert snap["market"]["perpetual_to_spot_24h_volume_ratio"] > 1
    assert snap["forecast_status"] == "NOT_ISSUED"
