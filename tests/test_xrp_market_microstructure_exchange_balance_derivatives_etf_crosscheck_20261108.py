"""Regression checks for the 2026-11-08 XRP market cross-check artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T110240Z-xrp-market-microstructure-exchange-balance-derivatives-etf-crosscheck.json"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_exchange_receipts_match_exact_retained_json_hashes():
    artifact = _load()
    receipts = artifact["direct_market_receipts"]
    assert {item["source_id"] for item in receipts} == {
        "kraken_spot_ticker_xrp_usd",
        "okx_spot_ticker_xrp_usdt",
        "binance_perpetual_premium_index_xrp_usdt",
    }
    for item in receipts:
        assert len(item["sha256"]) == 64
        assert hashlib.sha256(item["raw_response_text"].encode("utf-8")).hexdigest() == item["sha256"]


def test_event_time_freshness_is_separate_from_capture_reference():
    receipts = {item["source_id"]: item for item in _load()["direct_market_receipts"]}
    assert receipts["kraken_spot_ticker_xrp_usd"]["provider_event_timestamp_utc"] is None
    assert receipts["kraken_spot_ticker_xrp_usd"]["freshness_status"] == "UNKNOWN_EVENT_TIME"
    assert receipts["okx_spot_ticker_xrp_usdt"]["age_seconds_at_capture"] > 300
    assert receipts["okx_spot_ticker_xrp_usdt"]["freshness_status"] == "STALE_BY_1_136_SECONDS"
    assert receipts["binance_perpetual_premium_index_xrp_usdt"]["age_seconds_at_capture"] > 300
    assert receipts["binance_perpetual_premium_index_xrp_usdt"]["freshness_status"] == "STALE"


def test_no_direct_or_secondary_observation_is_model_eligible():
    artifact = _load()
    assert all(item["model_eligible"] is False for item in artifact["direct_market_receipts"])
    assert all(item["model_eligible"] is False for item in artifact["secondary_observations"])
    assert artifact["model_admission"]["admitted_to_feature_store"] is False
    assert artifact["model_admission"]["directional_forecast_issued"] is False


def test_normalized_secondary_excerpt_hashes_are_preserved():
    for item in _load()["secondary_observations"]:
        assert len(item["excerpt_sha256"]) == 64
        assert hashlib.sha256(item["excerpt"].encode("utf-8")).hexdigest() == item["excerpt_sha256"]


def test_exchange_wallet_balances_are_not_mislabeled_as_tradable_float():
    item = next(x for x in _load()["secondary_observations"] if x["source_id"] == "xrp_insights_exchange_balances")
    values = item["values"]
    assert values["tracked_xrp"] == 22_340_000_000
    assert values["same_wallet_7d_change_xrp"] == -104_400_000
    assert values["naive_total_change_xrp"] == 362_700_000
    assert values["new_wallet_xrp"] == 512_000_000
    assert any("Not tradable float" in note for note in item["limitations"])


def test_derivatives_aggregator_disagreement_is_retained_not_averaged():
    item = _load()["disagreements_and_hypotheses"]["unresolved_derivatives_disagreement"]
    assert item["open_interest_difference_usd"] == 530_000_000
    assert item["decision"].startswith("Do not average")
    assert len(item["hypotheses"]) >= 2


def test_etf_holdings_deltas_preserve_partial_coverage_and_proxy_semantics():
    items = {x["source_id"]: x for x in _load()["secondary_observations"]}
    cryptokeyhole = items["cryptokeyhole_etf_partial"]
    insights = items["xrp_insights_etf_holdings_delta"]
    assert cryptokeyhole["values"]["reporting_funds"] == 3
    assert cryptokeyhole["values"]["total_daily_funds_expected"] == 4
    assert cryptokeyhole["values"]["missing_fund"] == "Franklin Templeton XRPZ"
    assert "not verified creations/redemptions" in insights["limitations"][0]
    assert items["alpha_finance_etf"]["values"]["nov6_reported_flow_usd"] == 0


def test_xrpl_lending_amendments_remain_below_threshold_and_unactivated():
    item = next(x for x in _load()["secondary_observations"] if x["source_id"] == "xrpl_dashboard_amendments")
    values = item["values"]
    assert values["validators_heard"] == 35
    assert values["threshold"] == 29
    assert values["lending_protocol_yes"] == 21
    assert values["single_asset_vault_yes"] == 23
    assert values["in_activation_countdown"] == 0


def test_depth_limitations_and_forecast_fail_closed_status_are_explicit():
    artifact = _load()
    assert artifact["orderbook_depth"]["captured_multi_level_depth"] is False
    assert artifact["orderbook_depth"]["only_level_one_quotes"] is True
    assert artifact["model_admission"]["forecast_status"] == "NOT_ISSUED"
