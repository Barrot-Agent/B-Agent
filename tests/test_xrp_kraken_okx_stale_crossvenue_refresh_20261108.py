from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T040927Z-xrp-kraken-okx-stale-crossvenue-refresh.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_latest_exchange_receipts_match_surfaced_response_strings():
    artifact = load_artifact()
    for source in artifact["sources"]:
        raw = source["raw_response"]
        assert hashlib.sha256(raw.encode("utf-8")).hexdigest() == source["raw_response_sha256"]
        assert len(raw.encode("utf-8")) == source["raw_response_utf8_bytes"]


def test_fresh_okx_does_not_make_timestampless_kraken_comparable():
    artifact = load_artifact()
    sources = {item["source_id"]: item for item in artifact["sources"]}
    assert sources["kraken_xrp_usd_ticker"]["provider_event_time_utc"] is None
    assert sources["okx_xrp_usdt_ticker"]["age_at_capture_seconds"] < 300
    assert artifact["cross_venue_comparison"]["comparable"] is False
    assert artifact["data_quality"]["model_eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"


def test_identical_kraken_response_is_not_assumed_to_be_fresh():
    artifact = load_artifact()
    kraken = next(item for item in artifact["sources"] if item["source_id"] == "kraken_xrp_usd_ticker")
    assert kraken["raw_response_sha256"] == "f05b27b7f5773e18819fc238c2bf3a068e8c4e2a280098725e5c8f9bb3c2a223"
    assert "cannot distinguish" in kraken["limitations"][1]


def test_conflicting_venue_quotes_are_not_admitted_as_a_signal():
    artifact = load_artifact()
    market = artifact["market_snapshot"]
    assert market["kraken"]["level1_bid_share"] < 0.30
    assert market["okx"]["level1_bid_share"] > 0.84
    assert artifact["cross_venue_comparison"]["raw_last_price_gap_pct"] < -0.20
    assert artifact["forecast"]["model_feature_admission"] is False
