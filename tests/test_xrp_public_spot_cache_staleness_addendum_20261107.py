import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261107T134050Z-xrp-public-spot-cache-staleness-addendum.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_public_api_text_hashes_and_byte_counts_are_reproducible():
    data = load()
    for source in data["sources"]:
        raw = source["raw_response_text"].encode("utf-8")
        assert len(raw) == source["raw_response_utf8_bytes"]
        assert hashlib.sha256(raw).hexdigest() == source["raw_response_sha256"]
    assert data["receipt_contract"]["raw_http_wire_bytes_preserved"] is False
    assert data["receipt_contract"]["response_headers_or_cache_headers_exposed"] is False


def test_repeated_kraken_and_okx_payloads_are_quarantined_as_cache_or_staleness_suspicions():
    data = load()
    by_id = {source["source_id"]: source for source in data["sources"]}
    for source_id in (
        "kraken_xrpusd_ticker_repeat_20261107T134050Z",
        "okx_xrpusdt_ticker_repeat_20261107T134050Z",
    ):
        repeat = by_id[source_id]["repeat_observation"]
        assert repeat["elapsed_seconds"] == 487
        assert repeat["prior_and_current_payload_sha256_equal"] is True
    assessment = data["cross_source_reconciliation"]["cache_assessment"]
    assert assessment["status"] == "CACHE_OR_STALE_SOURCE_SUSPECTED_NOT_PROVEN"
    assert "may reflect" in assessment["unknowns"][1]


def test_provider_timestamps_fail_the_300_second_freshness_threshold():
    data = load()
    by_id = {source["source_id"]: source for source in data["sources"]}
    okx = by_id["okx_xrpusdt_ticker_repeat_20261107T134050Z"]
    bybit = by_id["bybit_xrpusdt_spot_ticker_20261107T134050Z"]
    coinpaprika = by_id["coinpaprika_xrp_aggregate_ticker_20261107T134050Z"]
    assert okx["provider_age_seconds_at_observation_upper_bound"] == 978.733
    assert bybit["provider_age_seconds_at_observation_upper_bound"] == 6369.019
    assert coinpaprika["provider_age_seconds_at_observation_upper_bound"] == 456
    for source in (okx, bybit, coinpaprika):
        assert source["freshness_limit_seconds"] == 300
        assert source["model_eligible"] is False


def test_ages_recompute_from_the_stored_provider_timestamps():
    data = load()
    upper = datetime.fromisoformat(data["observation_upper_bound_utc"].replace("Z", "+00:00"))
    by_id = {source["source_id"]: source for source in data["sources"]}
    for source_id, field in (
        ("okx_xrpusdt_ticker_repeat_20261107T134050Z", "provider_snapshot_timestamp_utc"),
        ("bybit_xrpusdt_spot_ticker_20261107T134050Z", "provider_snapshot_timestamp_utc"),
        ("coinpaprika_xrp_aggregate_ticker_20261107T134050Z", "provider_last_updated_utc"),
    ):
        source = by_id[source_id]
        event_time = datetime.fromisoformat(source[field].replace("Z", "+00:00"))
        assert (upper - event_time).total_seconds() == source["provider_age_seconds_at_observation_upper_bound"]


def test_usd_and_usdt_are_not_normalized_using_an_untimestamped_quote():
    data = load()
    by_id = {source["source_id"]: source for source in data["sources"]}
    conversion = by_id["kraken_usdtusd_ticker_context_20261107T134050Z"]
    assert conversion["provider_event_timestamp_utc"] is None
    assert conversion["normalized"]["midpoint_usdt_usd"] == 0.998755
    reconciliation = data["cross_source_reconciliation"]
    assert reconciliation["usd_usdt_normalization_performed"] is False
    assert reconciliation["usdt_usd_timestamp_available"] is False


def test_kraken_last_trade_below_best_bid_is_not_mislabeled_as_a_crossed_book():
    data = load()
    kraken = next(x for x in data["sources"] if x["source_id"] == "kraken_xrpusd_ticker_repeat_20261107T134050Z")
    quote = kraken["normalized"]
    assert quote["last_usd"] < quote["best_bid_usd"]
    assert quote["last_below_best_bid_usd"] == 0.00048
    assert kraken["provider_event_timestamp_utc"] is None
    assert kraken["model_eligible"] is False


def test_no_synchronized_depth_feature_or_forecast_is_admitted():
    data = load()
    reconciliation = data["cross_source_reconciliation"]
    assert reconciliation["synchronized_direct_venue_count_within_300_seconds"] == 0
    assert reconciliation["multi_level_depth_captured"] is False
    assert data["model_admission"]["eligible_for_live_price_features"] is False
    assert data["model_admission"]["eligible_for_historical_point_in_time_features"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast"] is None
    assert data["forecast"]["shadow_forecast"] is None
    assert data["forecast"]["paper_trade_executed"] is False
    assert data["forecast"]["real_money_action"] is False
    assert data["external_actions"]["orders_sent"] is False
