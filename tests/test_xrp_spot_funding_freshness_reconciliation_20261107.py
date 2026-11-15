from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261107T011136Z-xrp-spot-funding-freshness-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exchange_receipts_are_exact_and_content_addressed():
    data = load_artifact()
    sources = {item["publisher"]: item for item in data["sources"]}
    expected = {
        "Kraken": ("b066b8bcc2bf26a585bcfd14d234a306de5637d49b3227bf50b707d2107ee3a3", 316),
        "OKX": ("e61a5273fc507546ce3c0b0175d4978ab3f878079a209836cdd5195ae8abbdaa", 356),
        "Binance": ("d96534aca26089e4dbaaad9fa9567a8653fc5d812d2ddbe93fdcf81b6a79ef21", 219),
    }
    for publisher, (digest, size) in expected.items():
        raw = sources[publisher]["raw_response_text"]
        encoded = raw.encode("utf-8")
        assert len(encoded) == size == sources[publisher]["raw_response_bytes"]
        assert hashlib.sha256(encoded).hexdigest() == digest == sources[publisher]["raw_response_sha256"]
        assert json.loads(raw)


def test_spot_quotes_keep_units_timestamps_and_depth_scope_separate():
    data = load_artifact()
    venues = {item["venue"]: item for item in data["observations"]["spot"]["venues"]}
    kraken = venues["Kraken"]
    okx = venues["OKX"]

    assert kraken["instrument"] == "XRP/USD"
    assert kraken["last"] == 1.17818
    assert math.isclose(kraken["spread_bps"], 0.0848770344, abs_tol=1e-10)
    assert kraken["provider_timestamp_utc"] is None
    assert kraken["live_feature_admission"] is False
    assert kraken["multi_level_depth_captured"] is False

    assert okx["instrument"] == "XRP-USDT"
    assert okx["last"] == 1.1802
    assert math.isclose(okx["spread_bps"], 0.8473499131, abs_tol=1e-10)
    assert okx["provider_timestamp_age_seconds_at_capture"] == 36.136
    assert okx["fresh_for_300_second_live_feature_admission"] is True
    assert okx["multi_level_depth_captured"] is False

    cross = data["observations"]["spot"]["cross_venue"]
    assert math.isclose(cross["raw_last_price_difference_percent"], 0.1714508819, abs_tol=1e-10)
    assert cross["normalized_usd_usdt_basis"] is False
    assert cross["provider_timestamps_synchronized"] is False
    assert cross["executable_arbitrage_claim"] is False


def test_binance_funding_is_stale_and_not_misrepresented_as_market_wide_oi():
    perps = load_artifact()["observations"]["derivatives"]["binance_usdt_perpetual"]
    assert perps["last_funding_rate_decimal"] == 0.00004314
    assert perps["last_funding_rate_percent_per_8h"] == 0.004314
    assert perps["provider_timestamp_age_seconds_at_capture"] == 888.998
    assert perps["fresh_for_300_second_live_feature_admission"] is False
    assert perps["open_interest_available"] is False
    assert perps["liquidation_data_available"] is False


def test_quality_gate_excludes_snapshot_from_point_in_time_features():
    data = load_artifact()
    quality = data["quality_assessment"]
    assert quality["okx_ticker_timestamp_fresh"] is True
    assert quality["kraken_timestamp_missing"] is True
    assert quality["binance_funding_timestamp_stale"] is True
    assert quality["common_cross_venue_cutoff"] is False
    assert quality["multi_level_depth_available"] is False
    assert quality["point_in_time_feature_store_admission"] is False
    assert data["model_eligibility"]["admitted_to_point_in_time_feature_store"] is False


def test_no_forecast_or_external_action_is_created():
    data = load_artifact()
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["forecast_status"]["shadow_forecast_issued"] is False
    assert data["actions"]["paper_trade"] is False
    assert data["actions"]["real_money_action"] is False
    assert data["actions"]["deployment"] is False
    assert data["actions"]["secret_rotation"] is False
    assert data["actions"]["space_restart"] is False
    assert data["actions"]["kaggle_submission"] is False
