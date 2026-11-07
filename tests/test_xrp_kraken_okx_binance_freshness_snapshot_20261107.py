import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T190450Z-xrp-kraken-okx-binance-freshness-snapshot.json"
)


def test_direct_exchange_response_hashes_match_exact_rendered_text():
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert artifact["append_only"] is True
    assert artifact["capture_clock_semantics"].startswith("Automation reference clock")
    assert len(artifact["sources"]) == 3
    for source in artifact["sources"]:
        assert source["raw_capture_status"] == "rendered_response_text_only"
        assert source["raw_wire_bytes_and_headers_retained"] is False
        assert source["model_eligible"] is False
        assert hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest() == source["raw_response_sha256"]


def test_kraken_timestamp_missing_and_venue_level1_sizes_disagree():
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    kraken = artifact["observations"]["kraken"]
    okx = artifact["observations"]["okx"]
    assert kraken["provider_event_timestamp_missing"] is True
    assert kraken["last_vs_open_pct"] < 0
    assert kraken["last_vs_vwap_pct"] < 0
    assert kraken["top_of_book_bid_imbalance_pct"] > 0
    assert okx["top_of_book_bid_imbalance_pct"] < 0
    assert artifact["reconciliation"]["top_of_book_imbalance_disagreement"] is True
    assert artifact["reconciliation"]["cross_venue_gap_is_arbitrage_signal"] is False


def test_stale_binance_perpetual_funding_is_context_only():
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    perp = artifact["observations"]["binance_perpetual"]
    source = next(item for item in artifact["sources"] if item["source_id"] == "binance_xrpusdt_perpetual_premium_index")
    assert perp["funding_rate_pct"] == 0.01
    assert perp["mark_minus_index_bps"] < 0
    assert perp["next_funding_time_utc"] == "2026-11-08T00:00:00Z"
    assert source["age_seconds_at_reference_clock_lower_bound"] > source["freshness_limit_seconds"]
    assert perp["model_eligible"] is False


def test_unavailable_depth_and_forecast_gate_remain_fail_closed():
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert artifact["reconciliation"]["order_book_depth"]["executable_multi_level_depth_admitted"] is False
    assert artifact["model_admission"]["admitted"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["paper_or_real_money_actions"] == "NONE"
