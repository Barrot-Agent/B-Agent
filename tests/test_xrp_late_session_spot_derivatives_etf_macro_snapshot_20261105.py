import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T190803Z-xrp-late-session-spot-derivatives-etf-macro-snapshot.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_kraken_observation_uses_daily_open_and_correct_derived_metrics():
    data = load()
    spot = data["market_snapshot"]["spot"]
    assert spot["venue"] == "Kraken"
    assert spot["last_usd"] == 1.23363
    assert spot["daily_open_utc_usd"] == 1.3041
    assert spot["price_vs_daily_open_pct"] == -5.4037267081
    assert spot["price_vs_vwap_24h_pct"] == -3.8563529134
    assert math.isclose(spot["spread_bps"], 0.081061253937, rel_tol=0, abs_tol=1e-12)
    assert spot["position_in_24h_range_fraction"] < 0.07
    assert "not rolling 24-hour open" in spot["source_timestamp_semantics"]


def test_response_text_hashes_are_explicitly_not_claimed_as_raw_http_bytes():
    data = load()
    sources = {item["source_id"]: item for item in data["source_registry"]}
    kraken = sources["kraken_xrpusd_ticker_20261105_1902_window"]
    binance = sources["binance_xrpusdt_premium_index_20261105_190033"]
    assert kraken["raw_response_text_sha256"] == "321c1b45086a484b368e0238bbaa4d67b0c61c500434f42dfe327646022154eb"
    assert binance["raw_response_text_sha256"] == "fa71db5eb2f01aae7ca28e27c11db6b07f3583ff53ef690ecd1de442ba2e2f40"
    assert kraken["raw_http_bytes_captured"] is False
    assert binance["raw_http_bytes_captured"] is False
    assert kraken["model_eligible"] is False
    assert binance["model_eligible"] is False


def test_binance_mark_funding_and_next_settlement_are_point_in_time_labeled():
    perp = load()["market_snapshot"]["perpetual"]
    assert perp["source_event_time_utc"] == "2026-11-05T19:00:33Z"
    assert perp["mark_price_usd"] == 1.2326
    assert perp["index_price_usd"] == 1.23284253
    assert perp["funding_rate_pct_per_8h"] == 0.01
    assert perp["next_funding_time_utc"] == "2026-11-06T00:00:00Z"
    assert perp["mark_discount_to_index_bps"] < 0


def test_open_interest_provider_disagreement_is_preserved_not_averaged():
    items = load()["market_snapshot"]["open_interest_observations"]
    assert [item["total_oi_usd"] for item in items] == [773000000, 2010000000, 1347300000]
    assert items[0]["coverage"] == "Binance and Bybit USDT perpetuals"
    assert items[1]["coverage"] == "Seven exchanges"
    assert items[2]["event_time_utc"] is None
    assert len(load()["source_disagreement"]) >= 3


def test_etf_flow_universe_and_vintage_disagreement_is_preserved():
    items = load()["market_snapshot"]["etf_flows"]
    assert items[0]["daily_flow_2026_11_04_xrp"] == -64826
    assert items[0]["aggregate_flow_2026_11_02_to_2026_11_04_xrp"] == -259700
    assert items[1]["daily_flow_2026_11_03_xrp"] == -3339
    assert "partial" in items[1]["november_4_status"]
    assert items[2]["fund_universe"] == "five funds"


def test_no_directional_forecast_or_model_admission_from_incomplete_snapshot():
    data = load()
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["forecast_eligible"] is False
    assert data["forecast"]["issued"] is False
    assert data["forecast"]["directional"] is False
    assert len(data["competing_hypotheses"]) == 4
    assert all(item["counterevidence"] for item in data["competing_hypotheses"])
