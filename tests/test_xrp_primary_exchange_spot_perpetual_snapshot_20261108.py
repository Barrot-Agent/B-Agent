from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T080438Z-xrp-primary-exchange-spot-perpetual-snapshot.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_primary_exchange_receipts_match_exact_returned_json_text():
    data = load_artifact()
    for receipt in data["source_receipts"]:
        digest = hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest()
        assert digest == receipt["excerpt_sha256"]


def test_kraken_ticker_preserves_missing_provider_timestamp_and_usd_scope():
    data = load_artifact()
    kraken = data["market_observations"]["kraken_xrp_usd"]
    assert kraken["last_usd"] == 1.16337
    assert kraken["provider_event_timestamp_utc"] is None
    assert kraken["timestamp_status"] == "MISSING_FROM_ENDPOINT_RESPONSE"
    assert kraken["volume_24h_xrp"] == 12864859.95770978


def test_okx_snapshot_timestamp_and_staleness_are_explicit():
    data = load_artifact()
    okx = data["market_observations"]["okx_xrp_usdt"]
    assert okx["provider_snapshot_timestamp_utc"] == "2026-11-08T07:48:17.772Z"
    assert okx["provider_snapshot_age_seconds_at_reference"] == 980.228
    assert okx["timestamp_semantics"].startswith("OKX ticker response ts")
    assert okx["volume_24h_xrp"] == 19244995.456667


def test_binance_perpetual_funding_and_basis_are_not_misread_as_fresh():
    data = load_artifact()
    perp = data["market_observations"]["binance_xrp_usdt_perpetual"]
    assert perp["provider_response_timestamp_utc"] == "2026-11-08T07:27:58.002Z"
    assert perp["provider_response_age_seconds_at_reference"] == 2199.998
    assert perp["last_funding_rate_pct_per_8h"] == 0.009747
    assert data["derived_metrics"]["binance_perpetual_mark_vs_index_basis_bps"] < 0


def test_cross_venue_last_price_gap_is_not_called_arbitrage():
    data = load_artifact()
    assert data["derived_metrics"]["raw_kraken_usd_vs_okx_usdt_last_difference_pct"] > 0
    assert "not an executable spread or arbitrage" in data["derived_metrics"]["comparison_limit"]
    assert data["model_admission"]["eligible"] is False


def test_missing_depth_oi_and_wire_bytes_fail_closed():
    data = load_artifact()
    quality = data["quality_controls"]
    assert quality["full_depth_captured"] is False
    assert quality["raw_http_bytes_captured"] is False
    assert any("open-interest endpoint was inaccessible" in item for item in quality["unavailable_endpoints"])
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["external_actions"]["paper_trade"] is False
    assert data["external_actions"]["real_money"] is False
