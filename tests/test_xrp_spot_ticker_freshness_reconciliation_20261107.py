import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T181119Z-xrp-spot-ticker-freshness-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_exchange_response_hashes_match_exact_returned_json_text():
    artifact = load_artifact()
    for source in artifact["sources"]:
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_kraken_without_provider_event_timestamp_is_not_model_eligible():
    source = load_artifact()["sources"][0]
    assert source["venue"] == "Kraken"
    assert source["provider_event_timestamp_utc"] is None
    assert source["timestamp_status"] == "not_supplied"
    assert source["model_eligible"] is False


def test_okx_quote_exceeds_freshness_limit_and_is_not_model_eligible():
    source = load_artifact()["sources"][1]
    assert source["provider_event_timestamp_utc"] == "2026-11-07T17:44:50.054Z"
    assert source["age_seconds_at_capture"] == 1588.946
    assert source["age_seconds_at_capture"] > source["freshness_limit_seconds"]
    assert source["model_eligible"] is False


def test_level_one_spreads_and_rolling_volumes_are_reproducible():
    observations = load_artifact()["observations"]
    assert round(observations["kraken"]["level1_spread_bps"], 6) == 0.172212
    assert round(observations["okx"]["level1_spread_bps"], 6) == 0.860844
    assert observations["kraken"]["volume_24h_xrp"] == 21680370.5787476
    assert observations["okx"]["volume_24h_xrp"] == 37002499.470069


def test_cross_venue_gap_is_not_mislabeled_as_arbitrage():
    calculations = load_artifact()["calculations"]
    assert round(calculations["raw_cross_venue_last_price_gap_pct"], 6) == 0.018941
    assert calculations["cross_venue_gap_is_arbitrage_signal"] is False


def test_unavailable_depth_and_other_venues_are_not_invented():
    coverage = load_artifact()["depth_and_venue_coverage"]
    assert coverage["kraken_depth_20"].startswith("not retrievable")
    assert coverage["okx_books_20"].startswith("not retrievable")
    assert coverage["coinbase_xrp_usd_ticker_and_level2"].startswith("not retrievable")
    assert coverage["binance_perpetual_premium_index"].startswith("HTTP 451")
    assert coverage["executable_depth_admitted"] is False


def test_no_directional_forecast_or_financial_action_is_issued():
    artifact = load_artifact()
    assert artifact["model_admission"]["admitted"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["paper_or_real_money_actions"] == "NONE"
