import hashlib
import json
from pathlib import Path


def test_kraken_okx_spot_capture_remains_research_only_and_timestamp_qualified():
    path = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261108T013900Z-xrp-kraken-okx-spot-freshness-reconciliation.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["captured_at_utc"] == "2026-11-08T01:39:00Z"
    assert artifact["capture_method"]["raw_http_bytes_captured"] is False
    assert "not hashes of the underlying HTTP wire bytes" in artifact["capture_method"]["hashes_are"]
    kraken = artifact["observations"]["kraken"]
    okx = artifact["observations"]["okx"]
    assert kraken["last_usd"] == 1.15873
    assert kraken["provider_event_timestamp"] is None
    assert hashlib.sha256(kraken["response_excerpt"].encode()).hexdigest() == kraken["response_excerpt_sha256"]
    assert okx["provider_event_timestamp_utc"] == "2026-11-08T01:31:57.468Z"
    assert okx["age_at_capture_seconds"] > okx["maximum_live_age_seconds"]
    assert okx["freshness_status"] == "STALE"
    assert hashlib.sha256(okx["response_excerpt"].encode()).hexdigest() == okx["response_excerpt_sha256"]
    assert artifact["cross_venue_comparison"]["comparable"] is False
    assert artifact["feature_policy"]["feature_store_admission"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["external_actions"]["paper_trade"] is False
    assert artifact["external_actions"]["real_money"] is False
