import hashlib
import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T121501Z-xrp-kraken-okx-market-quality-snapshot.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_surface_response_hashes_and_timestamp_quality_are_preserved():
    data = _load()
    receipts = {item["source_id"]: item for item in data["source_receipts"]}
    assert len(receipts) == 2
    for item in receipts.values():
        assert item["raw_http_bytes_captured"] is False
        assert hashlib.sha256(item["raw_response_text"].encode("utf-8")).hexdigest() == item["raw_response_sha256"]
        assert item["model_eligible"] is False
    assert receipts["kraken_xrp_usd_ticker_20261108T121501Z"]["provider_event_timestamp"] is None
    assert receipts["okx_xrp_usdt_ticker_20261108T121501Z"]["event_age_seconds_at_capture"] == 656.975


def test_stale_or_missing_event_time_fails_market_feature_admission():
    data = _load()
    market = data["market_snapshot"]
    assert market["kraken_xrp_usd"]["freshness"] == "UNVERIFIABLE"
    assert market["okx_xrp_usdt"]["freshness"] == "STALE_OVER_300_SECONDS"
    assert market["cross_venue_comparison_eligible"] is False
    assert data["market_quality"]["feature_store_admission"] is False


def test_venue_level1_imbalance_conflict_is_not_directional_signal():
    data = _load()
    kraken = data["market_snapshot"]["kraken_xrp_usd"]
    okx = data["market_snapshot"]["okx_xrp_usdt"]
    assert kraken["level1_imbalance"] < 0
    assert okx["level1_imbalance"] > 0
    assert data["level1_disagreement"]["directional_signal_admitted"] is False
    assert data["source_independence"]["cross_venue_confirmation_established"] is False


def test_raw_price_gap_is_not_misrepresented_as_arbitrage():
    data = _load()
    assert math.isclose(
        data["market_snapshot"]["raw_cross_venue_last_price_gap_pct"],
        0.18552875695734272,
        rel_tol=1e-12,
    )
    assert data["market_snapshot"]["cross_venue_comparison_eligible"] is False
    assert "XRP/USD and XRP/USDT are not normalized" in data["market_snapshot"]["cross_venue_comparison_exclusion_reasons"][2]


def test_forecast_and_model_admission_remain_fail_closed():
    data = _load()
    assert data["model_admission"]["eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
