import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T020621Z-xrp-kraken-okx-current-spot-snapshot.json"
)


def test_current_kraken_okx_snapshot_preserves_exact_bodies_and_hashes():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["captured_at_utc"] == "2026-11-08T02:06:21Z"
    assert artifact["capture_method"]["raw_http_bytes_captured"] is False
    assert "not hashes of HTTP wire bytes" in artifact["capture_method"]["hashes_are"]
    kraken = artifact["observations"]["kraken"]
    okx = artifact["observations"]["okx"]
    assert hashlib.sha256(kraken["response_body"].encode()).hexdigest() == kraken["response_body_sha256"]
    assert hashlib.sha256(okx["response_body"].encode()).hexdigest() == okx["response_body_sha256"]


def test_current_snapshot_qualifies_provider_time_and_window_semantics():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    kraken = artifact["observations"]["kraken"]
    okx = artifact["observations"]["okx"]
    assert kraken["provider_event_timestamp"] is None
    assert kraken["freshness_status"] == "PROVIDER_TIMESTAMP_ABSENT"
    assert kraken["daily_open_utc_usd"] == 1.16234
    assert okx["provider_event_timestamp_utc"] == "2026-11-08T02:01:59.867Z"
    assert okx["age_at_capture_seconds"] == 261.133
    assert okx["age_at_capture_seconds"] <= okx["maximum_live_age_seconds"]
    assert okx["freshness_status"] == "WITHIN_300S_AT_CAPTURE"
    assert okx["open_24h_usdt"] == 1.1782 if "open_24h_usdt" in okx else okx["open24h_usdt"] == 1.1782


def test_current_snapshot_does_not_overstate_depth_or_cross_venue_comparability():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["observations"]["kraken"]["displayed_level_1_depth_levels"] == 1
    assert artifact["observations"]["okx"]["displayed_level_1_depth_levels"] == 1
    comparison = artifact["cross_venue_comparison"]
    assert comparison["comparable"] is False
    assert "not an arbitrage signal" in comparison["interpretation"]
    assert artifact["feature_policy"]["feature_store_admission"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["external_actions"]["paper_trade"] is False
    assert artifact["external_actions"]["real_money"] is False
