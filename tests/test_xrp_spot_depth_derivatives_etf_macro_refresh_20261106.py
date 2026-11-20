from __future__ import annotations

import json
import math
import re
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T070228Z-xrp-spot-depth-derivatives-etf-macro-refresh.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_spot_hash_spread_and_utc_open_semantics():
    data = load_artifact()
    spot = data["market_snapshot"]["kraken_spot"]
    assert re.fullmatch(r"[0-9a-f]{64}", data["capture"]["rendered_kraken_response_text_sha256"])
    assert data["capture"]["raw_http_wire_bytes_captured"] is False
    assert spot["provider_event_timestamp_utc"] is None
    midpoint = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    expected_spread = (spot["best_ask_usd"] - spot["best_bid_usd"]) / midpoint * 10_000
    assert math.isclose(spot["displayed_spread_bps"], expected_spread, rel_tol=0, abs_tol=1e-12)
    assert spot["utc_day_open_usd"] == 1.20567
    assert spot["rolling_24h_vwap_usd"] == 1.24985258
    assert math.isclose(
        spot["derived_comparisons"]["last_vs_utc_day_open_percent"],
        (spot["last_trade_usd"] / spot["utc_day_open_usd"] - 1) * 100,
        abs_tol=1e-12,
    )
    assert math.isclose(
        spot["derived_comparisons"]["last_vs_rolling_24h_vwap_percent"],
        (spot["last_trade_usd"] / spot["rolling_24h_vwap_usd"] - 1) * 100,
        abs_tol=1e-12,
    )
    assert spot["quote_component_quality"]["components_synchronized"] is False


def test_retrieval_interval_does_not_fabricate_a_point_in_time_cutoff():
    capture = load_artifact()["capture"]
    assert capture["retrieval_interval_start_utc"] == "2026-11-06T07:02:28Z"
    assert capture["retrieval_interval_end_utc"] is None
    assert capture["exact_per_source_retrieval_timestamp_utc"] is None
    assert capture["conservative_data_cutoff_utc"] is None
    assert capture["raw_http_wire_bytes_captured"] is False
    assert "not a byte-exact" in capture["hash_scope"]


def test_fuelmaps_spot_depth_keeps_venue_coverage_and_bid_share():
    item = load_artifact()["market_snapshot"]["order_book"]["fuelmaps_spot_six_venue"]
    assert item["snapshot_timestamp_utc"] == "2026-11-06T06:00:00Z"
    assert len(item["venues"]) == 6
    assert "Binance" not in item["venues"] and "Bitget" not in item["venues"]
    bands = {row["within_percent"]: row for row in item["depth_bands_usd_millions"]}
    assert bands[0.5]["bids"] == 11.3 and bands[0.5]["asks"] == 5.6
    assert bands[1]["bids"] == 14.4 and bands[1]["asks"] == 8.7
    assert bands[10]["venues_covering"] == "5/6"
    for row in item["depth_bands_usd_millions"]:
        expected = row["bids"] / (row["bids"] + row["asks"]) * 100
        assert math.isclose(row["bid_share_percent"], expected, abs_tol=1e-12)


def test_edgeornot_mixed_spot_perpetual_book_is_not_pure_spot_depth():
    item = load_artifact()["market_snapshot"]["order_book"]["edgeornot_mixed_spot_perpetual"]
    assert item["venues"] == ["Binance spot", "OKX XRP-USDT perpetual"]
    assert item["snapshot_timestamp_utc"] == "2026-11-06T05:45:00Z"
    assert item["depth_within_1_percent_usd_millions"]["bids"] == 10.9
    assert item["depth_within_1_percent_usd_millions"]["asks"] == 10.3
    assert any("mixed spot/perpetual" in x for x in item["limitations"])
    comparison = load_artifact()["market_snapshot"]["order_book"]["asynchronous_level_comparison"]
    assert comparison["status"] == "DESCRIPTIVE_CROSS_SOURCE_LEVEL_COMPARISON_NOT_A_RETURN"
    assert "proof that market-wide support failed" in comparison["interpretation"]


def test_tradradar_oi_row_sum_and_derivatives_limits():
    item = load_artifact()["market_snapshot"]["tradradar_perpetuals"]
    assert sum(item["exchange_open_interest_usd"].values()) == item["exchange_open_interest_row_sum_usd"]
    assert item["exchange_open_interest_row_sum_usd"] == 1_883_510_000
    assert item["open_interest_change_24h_percent"] < 0
    assert item["funding_oi_weighted_percent_per_8h"] > 0
    assert item["long_liquidations_usd"] > item["short_liquidations_usd"]
    assert item["liquidations_24h_lower_bound_usd"] == 17_140_000
    assert item["long_account_share_percent"] == 79.9
    assert any("notional positioning" in x for x in item["limitations"])


def test_etf_vintage_is_provisional_and_not_direct_cash_flow():
    item = load_artifact()["etf_flow_vintage"]["xrp_insights"]
    assert item["generated_at_utc"] == "2026-11-06T06:27:36.267Z"
    assert item["data_as_of"] == "2026-11-04"
    assert item["latest_row_date"] == "2026-11-05"
    assert item["latest_row_status"] == "provisional"
    assert item["nov2_to_nov4_holdings_change_xrp"] == -259_701
    assert "not direct AP cash" in item["methodology"]
    assert load_artifact()["etf_flow_vintage"]["cryptokeyhole_vintage_reference"]["latest_direct_page_capture_in_prior_artifact"] == "2026-11-06T04:43:00Z"


def test_macro_event_is_scheduled_not_observed():
    macro = load_artifact()["macro_context"]
    assert macro["upcoming_bls_release"]["scheduled_release_utc"] == "2026-11-06T13:30:00Z"
    assert macro["upcoming_bls_release"]["status"] == "SCHEDULED_NOT_YET_RELEASED"
    assert macro["reuters_nov6"]["xrp_causality"] == "Not established."


def test_competing_hypotheses_retain_disconfirming_evidence_and_tests():
    hypotheses = load_artifact()["competing_hypotheses"]
    assert len(hypotheses) >= 5
    assert all(item["supporting_evidence"] for item in hypotheses)
    assert all(item["disconfirming_evidence"] for item in hypotheses)
    assert all(item["tests"] for item in hypotheses)


def test_no_model_admission_or_directional_forecast():
    data = load_artifact()
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["forecast_issued"] is False
    assert data["forecast"]["issued"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert len(data["model_admission"]["reasons"]) >= 6
