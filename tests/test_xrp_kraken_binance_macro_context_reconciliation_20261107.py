from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T114313Z-xrp-kraken-binance-macro-context-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_exchange_payload_hashes_match_exact_returned_json_text() -> None:
    data = load_artifact()
    for receipt in data["raw_source_receipts"]:
        digest = hashlib.sha256(receipt["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == receipt["raw_response_sha256"]
        assert "not original HTTP wire bytes" in receipt["hash_scope"]


def test_kraken_ticker_open_is_utc_daily_open_not_rolling_24h_open() -> None:
    spot = load_artifact()["market_snapshot"]["spot"]
    assert spot["utc_daily_open_usd"] == 1.17749
    assert spot["last_vs_utc_daily_open_pct"] == pytest.approx(-0.7261208163)
    assert spot["rolling_24h_vwap_usd"] == 1.17687018
    assert spot["last_vs_rolling_24h_vwap_pct"] == pytest.approx(-0.6738364294)
    assert spot["provider_event_timestamp_utc"] is None
    assert spot["freshness_status"] == "UNKNOWN_NO_PROVIDER_TIMESTAMP"


def test_kraken_level_one_spread_and_sizes_are_not_mislabeled_as_depth() -> None:
    spot = load_artifact()["market_snapshot"]["spot"]
    assert spot["best_bid_usd"] == 1.16879
    assert spot["best_ask_usd"] == 1.16880
    assert spot["bid_size_xrp"] == 3767
    assert spot["ask_size_xrp"] == 4278
    assert spot["level_1_spread_bps"] == pytest.approx(0.0855582031)
    assert "not a depth ladder" in spot["limitation"]


def test_binance_last_funding_observation_is_stale_and_not_a_live_feature() -> None:
    derivatives = load_artifact()["market_snapshot"]["derivatives"]
    assert derivatives["provider_timestamp_utc"] == "2026-11-07T11:22:50Z"
    assert derivatives["reference_time_utc"] == "2026-11-07T11:43:13Z"
    assert derivatives["minimum_age_at_reference_seconds"] == 1223
    assert derivatives["minimum_age_at_reference_seconds"] > 300
    assert derivatives["last_funding_rate_fraction"] == 0.0001
    assert derivatives["last_funding_rate_pct_per_8h"] == pytest.approx(0.01)
    assert derivatives["model_feature_eligible"] is False
    assert "lastFundingRate, not a forecast" in derivatives["limitation"]


def test_global_liquidations_and_bitcoin_etf_flows_are_not_attributed_to_xrp() -> None:
    context = load_artifact()["secondary_market_context"]
    coindesk = next(x for x in context if x["source_id"].startswith("coindesk_"))
    assert coindesk["reported_context"]["crypto_derivatives_liquidations_24h_usd_at_least"] == 1_270_000_000
    assert coindesk["reported_context"]["us_spot_bitcoin_etf_net_outflows_thursday_usd"] == 430_200_000
    assert coindesk["xrp_attribution_permitted"] is False


def test_okx_derivatives_analysis_is_secondary_and_not_an_exchange_receipt() -> None:
    item = next(x for x in load_artifact()["secondary_market_context"] if x["source_id"].startswith("cryptoticker_"))
    assert item["reported_context"]["okx_xrp_futures_open_interest_usd_from"] == 128_900_000
    assert item["reported_context"]["okx_xrp_futures_open_interest_usd_to"] == 117_400_000
    assert item["reported_context"]["long_to_short_account_ratio_latest_reported"] == 3.91
    assert item["model_feature_eligible"] is False
    assert "not a direct exchange receipt" in item["normalized_excerpt"]


def test_macro_sources_are_context_only_and_not_xrp_flows() -> None:
    item = next(x for x in load_artifact()["secondary_market_context"] if x["source_id"].startswith("reuters_"))
    assert item["reported_context"]["us_money_market_fund_net_inflows_week_to_2026_11_04_usd"] == 117_970_000_000
    assert item["reported_context"]["us_equity_fund_net_inflows_usd"] == 14_810_000_000
    assert item["xrp_attribution_permitted"] is False


def test_inaccessible_order_book_and_oi_endpoints_do_not_create_zero_features() -> None:
    data = load_artifact()
    assert any("depth" in x for x in data["retrieval_limitations"]["inaccessible_endpoints"])
    assert data["retrieval_limitations"]["no_synchronized_cross_venue_book"] is True
    assert data["retrieval_limitations"]["no_executable_depth_estimate"] is True
    assert data["model_admission"]["eligible_for_feature_store"] is False
    assert data["model_admission"]["eligible_for_directional_forecast"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
