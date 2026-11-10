from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261110T075851Z-run124-market-depth-derivatives-etf-macro-update.json"
PLATFORM_MAP = ROOT / "research/xrp_intelligence/nine_platform_coordination_snapshot_20261110T075851Z.json"
FEATURE_CONTRACT = ROOT / "research/xrp_intelligence/feature-store-contract.md"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run124_spot_receipts_are_hashed_but_not_admitted_as_wire_verified_features():
    data = load_artifact()
    spot = data["market"]["spot"]
    for name in ("kraken_xrpusd", "okx_xrpusdt", "kraken_usdtusd"):
        item = spot[name]
        assert hashlib.sha256(item["raw_response_text"].encode("utf-8")).hexdigest() == item["response_text_sha256"]
        assert item["raw_http_bytes_preserved"] is False
        assert item["model_admission"] is False
    assert spot["okx_xrpusdt"]["provider_event_time_utc"] == "2026-11-10T07:41:51.664Z"
    assert spot["kraken_xrpusd"]["provider_event_time_utc"] is None
    assert data["market"]["cross_venue_comparison"]["asynchronous"] is True
    assert data["market"]["cross_venue_comparison"]["model_admission"] is False


def test_run124_spot_depth_keeps_venue_coverage_and_resting_book_limits():
    depth = load_artifact()["market"]["spot_order_book"]
    assert depth["snapshot_time_utc"] == "2026-11-10T07:00:00Z"
    assert depth["venues_reporting_1pct"] == 6
    assert depth["depth_within_mid"]["1pct"]["bids_usd_m"] == 12.4
    assert depth["depth_within_mid"]["1pct"]["asks_usd_m"] == 10.0
    assert depth["depth_within_mid"]["1pct"]["bid_share_pct"] == 55.4
    assert "Binance" in depth["excluded_venues"]
    assert "Bitget" in depth["excluded_venues"]
    assert depth["resting_orders_not_executed"] is True
    assert depth["model_admission"] is False


def test_run124_derivatives_preserve_provider_disagreement_without_averaging():
    derivatives = load_artifact()["market"]["derivatives"]
    assert derivatives["liqwall"]["open_interest_usd_b"] == 1.23
    assert derivatives["tradradar"]["open_interest_usd_b"] == 1.66
    assert derivatives["disagreement"]["average_or_blend_performed"] is False
    assert derivatives["model_admission"] is False


def test_run124_etf_partial_reporting_does_not_zero_fill_missing_funds():
    etf = load_artifact()["market"]["etf_flows"]
    kh = etf["crypto_keyhole"]
    ce = etf["crypto_etf_today"]
    alpha = etf["alpha_finance"]
    assert kh["coverage_reported"] == {"reported": 3, "expected_daily_tracked": 4}
    assert kh["partial_net_flow_xrp"] == -9216553
    assert kh["missing_funds"] == ["Franklin_XRPZ"]
    assert kh["november_matrix_complete_days_usd"] == -903489
    assert kh["november_matrix_includes_partial_2026_11_09"] is False
    assert ce["coverage_reported"] == {"reported": 3, "expected": 5}
    assert set(ce["missing_funds"]) == {"Franklin_XRPZ", "Grayscale_GXRP"}
    assert alpha["coverage_reported"] == {"reported": 5, "expected": 5}
    assert alpha["reports_zero_for_funds_missing_from_issuer_file_trackers"]
    assert etf["reconciliation"]["source_independence_proven"] is False
    assert etf["reconciliation"]["do_not_average"] is True
    assert etf["model_admission"] is False


def test_run124_binance_rotation_is_not_misclassified_as_xrp_exchange_net_outflow():
    flow = load_artifact()["market"]["exchange_flows"]
    largest = flow["largest_transfer"]
    assert largest["amount_xrp"] == 368480000
    assert largest["from"] == largest["to"] == "Binance"
    assert largest["classification"] == "rotation"
    assert largest["excluded_from_netflow"] is True
    assert flow["evernorth_link_established"] is False
    assert flow["model_admission"] is False


def test_run124_macro_and_sentiment_cutoffs_do_not_leak_future_information():
    data = load_artifact()
    macro = data["macro"]
    assert macro["upcoming_releases"][0]["scheduled_utc"] == "2026-11-10T13:30:00Z"
    assert macro["upcoming_releases"][0]["status_at_cutoff"] == "FUTURE_NOT_RELEASED"
    sentiment = data["market"]["cross_analysis"]
    assert sentiment["sentiment_shift_status"] == "INSUFFICIENT_DATA"
    assert sentiment["sentiment_shift_recent_n"] == 0
    assert sentiment["sentiment_shift_prior_n"] == 0
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional"] is False


def test_run124_nine_platform_snapshot_only_verifies_chatgpt_data_flow():
    data = json.loads(PLATFORM_MAP.read_text(encoding="utf-8"))
    expected = {"ChatGPT", "Claude", "Grok", "Gemini", "Copilot", "Codex", "Hugging Face", "Kaggle", "Databricks"}
    assert set(data["platforms"]) == expected
    assert data["platforms"]["ChatGPT"]["data_flow"]["verified"] is True
    assert data["platforms"]["Copilot"]["authentication_status"] == "COMMENT_ONLY_ACTIVITY"
    for name, platform in data["platforms"].items():
        if name != "ChatGPT":
            assert platform["data_flow"]["verified"] is False
    assert data["coordination_policy"]["external_platform_data_exchange_performed"] is False


def test_run124_feature_store_contract_counts_weekly_cftc_sources():
    contract = FEATURE_CONTRACT.read_text(encoding="utf-8")
    assert "46 public endpoint records" in contract
    assert "46 public endpoint records: 42 hourly scheduled sources, two weekly scheduled CFTC sources" in contract
    assert "Thus 44 sources are scheduled (42 hourly plus two weekly) and two are excluded." in contract
    assert "40 endpoint records: 36 hourly scheduled sources" not in contract
