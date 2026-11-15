from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T1342Z-bls-october-employment-xrp-event-window.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_official_bls_release_and_revisions_are_recorded_without_overstatement():
    data = load_artifact()
    event = data["event"]
    actual = event["actual"]
    assert event["release_id"] == "USDL-26-1632"
    assert event["scheduled_and_embargo_release_time_utc"] == "2026-11-06T13:30:00Z"
    assert actual["nonfarm_payroll_change"] == 165000
    assert actual["unemployment_rate_pct"] == 4.1
    assert actual["average_hourly_earnings_monthly_change_pct"] == 0.4
    assert actual["average_hourly_earnings_12_month_change_pct"] == 3.1
    assert actual["combined_prior_month_revision_thousands"] == 84
    assert actual["part_time_for_economic_reasons_increase_thousands"] == 339


def test_pre_release_estimates_remain_separate_and_surprise_is_a_range():
    expectations = load_artifact()["event"]["pre_release_expectations"]
    values = {item["source_id"]: item["payroll_consensus"] for item in expectations["sources"]}
    assert values == {"ap_october_jobs_preview": 65000, "wsj_october_jobs_preview": 59000}
    assert expectations["payroll_surprise_range"] == {"low": 100000, "high": 106000}


def test_kraken_rendered_response_hash_and_quote_arithmetic_are_reproducible():
    market = load_artifact()["xrp_market_observation"]
    rendered = market["raw_response_rendered"]
    assert hashlib.sha256(rendered.encode("utf-8")).hexdigest() == market["raw_response_rendered_sha256"]
    payload = json.loads(rendered)["result"]["XXRPZUSD"]
    quote = market["quote"]
    last = float(payload["c"][0])
    bid = float(payload["b"][0])
    ask = float(payload["a"][0])
    vwap_24h = float(payload["p"][1])
    daily_open = float(payload["o"])
    assert last == pytest.approx(quote["last_usd"])
    assert bid == pytest.approx(quote["best_bid_usd"])
    assert ask == pytest.approx(quote["best_ask_usd"])
    assert (ask / bid - 1) * 10000 == pytest.approx(quote["spread_bps"], abs=1e-5)
    assert (last / vwap_24h - 1) * 100 == pytest.approx(quote["last_vs_vwap_24h_pct"], abs=1e-5)
    assert (last / daily_open - 1) * 100 == pytest.approx(quote["last_vs_utc_day_open_pct"], abs=1e-5)
    assert float(payload["v"][1]) == pytest.approx(quote["volume_24h_xrp"])


def test_missing_provider_timestamp_blocks_event_window_model_admission():
    data = load_artifact()
    market = data["xrp_market_observation"]
    quality = data["data_quality"]
    assert market["provider_event_timestamp"] is None
    assert market["retrieval_timestamp_utc"] is None
    assert market["raw_http_bytes_captured"] is False
    assert market["eligibility"] == "quarantined_context_only"
    assert quality["synchronized_multi_asset_event_window"] is False
    assert quality["model_eligible"] is False


def test_competing_macro_hypotheses_retain_counterevidence():
    hypotheses = load_artifact()["competing_hypotheses"]
    assert len(hypotheses) >= 4
    for hypothesis in hypotheses:
        assert hypothesis["support"]
        assert hypothesis["counterevidence"]


def test_forecast_remains_not_issued_without_synchronized_event_data():
    forecast = load_artifact()["forecast"]
    assert forecast["status"] == "NOT_ISSUED"
    assert forecast["target"] is None
    assert forecast["horizon"] is None
    assert forecast["probabilities"] is None
    assert forecast["confidence"] is None
    assert len(forecast["next_required_evidence"]) >= 4
