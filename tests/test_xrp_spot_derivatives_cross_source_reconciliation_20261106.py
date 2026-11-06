from __future__ import annotations

import json
import math
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T005949Z-xrp-spot-derivatives-cross-source-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_spot_observations_preserve_provider_scope_and_missing_timestamps():
    item = load_artifact()
    observations = {row["source_id"]: row for row in item["spot_market"]["observations"]}
    kraken = observations["KRAKEN_XRPUSD_TICKER_CAPTURE_20261106T000233Z"]
    assert kraken["provider_event_timestamp_utc"] is None
    assert kraken["retrieval_timestamp_utc"] is None
    assert kraken["raw_http_wire_bytes_captured"] is False
    assert kraken["rolling_24h_volume_xrp"] > 40_000_000
    assert math.isclose(
        kraken["displayed_spread_bps"],
        (kraken["best_ask_usd"] - kraken["best_bid_usd"])
        / ((kraken["best_ask_usd"] + kraken["best_bid_usd"]) / 2)
        * 10_000,
        rel_tol=0,
        abs_tol=1e-9,
    )
    investing = observations["INVESTING_XRP_HISTORICAL_20261106"]
    assert investing["daily_observations"][0]["date"] == "2026-11-05"
    assert investing["daily_observations"][1]["partial_day"] is True
    assert investing["page_displayed_time_timezone"] is None


def test_cross_provider_shared_venue_open_interest_reconciles_without_averaging():
    item = load_artifact()["derivatives"]
    radar = item["tradradar"]
    cg = item["coingecko"]
    comparison = item["same_venue_reconciliation"]
    assert radar["open_interest_exchange_count"] == 7
    assert cg["derivatives_rows_reported"] == 130
    assert cg["shared_seven_venue_sum_usd"] == 1_773_594_227
    assert comparison["tradradar_shared_venue_sum_usd"] == 1_926_420_000
    assert comparison["coingecko_shared_venue_sum_usd"] == 1_773_594_227
    assert math.isclose(
        comparison["trad_radar_above_coingecko_percent"],
        8.616727020954608,
        abs_tol=1e-9,
    )
    assert "must not be compared directly" in comparison["interpretation"]


def test_liquidation_and_long_short_metrics_keep_their_coverage_limits():
    item = load_artifact()["derivatives"]["tradradar"]
    assert math.isclose(
        item["liquidations_24h_lower_bound_usd"],
        item["long_liquidations_usd"] + item["short_liquidations_usd"],
        abs_tol=10_000,
    )
    assert item["long_short_account_ratio"] == 4.13
    assert item["long_account_share_percent"] == 80.5
    assert any("account-count based" in x for x in item["limitations"])


def test_institutional_announcements_are_not_xrp_flow_features():
    item = load_artifact()["institutional_nonprice_evidence"]
    c2fo = item["c2fo_ripple_instant_pay"]
    assert c2fo["announced_settlement_asset"] == "RLUSD"
    assert c2fo["xrp_bridge_usage"] == "Not disclosed."
    assert c2fo["historical_early_pay_is_not_instant_pay_volume"] is True
    bny = item["bny_ripple_custody"]
    assert bny["xrp_specific_assets_under_custody_usd"] is None
    assert bny["xrp_collateral_acceptance_terms"] is None
    assert item["evernorth"]["holdings_as_of"] == "2026-10-09"


def test_bls_release_is_scheduled_not_observed():
    item = load_artifact()["macro_context"]["upcoming_us_employment_situation"]
    assert item["scheduled_release_utc"] == "2026-11-06T13:30:00Z"
    assert item["status"] == "SCHEDULED_NOT_YET_RELEASED"


def test_artifact_is_not_model_eligible_and_no_forecast_is_issued():
    item = load_artifact()
    assert item["model_eligible"] is False
    assert item["forecast_status"] == "NOT_ISSUED"
    assert item["capture"]["model_cutoff_utc"] is None
    assert len(item["competing_hypotheses"]) >= 4
    assert len(item["model_ineligibility_reasons"]) >= 5
