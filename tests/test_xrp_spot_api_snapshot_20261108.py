from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T061808Z-xrp-kraken-okx-binance-spot-freshness-snapshot.json"


def _artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exact_exchange_response_receipts_and_hashes():
    data = _artifact()
    assert data["capture_policy"]["raw_http_wire_bytes_preserved"] is False
    for source in data["sources"][:2]:
        raw = source["raw_response"].encode("utf-8")
        assert len(raw) == source["raw_response_utf8_bytes"]
        assert hashlib.sha256(raw).hexdigest() == source["raw_response_sha256"]


def test_provider_timestamp_freshness_fails_closed():
    data = _artifact()
    kraken, okx, binance = data["sources"]
    assert kraken["provider_event_time_utc"] is None
    assert kraken["freshness"]["eligible"] is False
    assert okx["age_at_retrieval_seconds"] > 300
    assert okx["freshness"]["eligible"] is False
    assert binance["http_status"] == 451
    assert data["model_admission"]["model_eligible"] is False


def test_venue_level_imbalances_and_quote_currencies_are_not_combined():
    data = _artifact()
    kraken, okx, _ = data["sources"]
    assert kraken["normalized"]["bid_size_share_pct"] < 50
    assert okx["normalized"]["bid_size_share_pct"] > 50
    assert kraken["normalized"]["last_usd"] != okx["normalized"]["last_usdt"]
    assert data["cross_venue_comparison"]["comparison_status"] == "NOT_COMPARABLE_AS_ARBITRAGE"
    assert data["disagreement"]["top_of_book"].find("conflicts") >= 0
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"
