from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261107T000451Z-xrp-live-spot-perps-etf-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_exchange_receipts_are_exact_and_content_addressed():
    data = load_artifact()
    sources = {item["publisher"]: item for item in data["sources"]}
    for publisher in ("Kraken", "OKX"):
        source = sources[publisher]
        raw = source["raw_response_text"]
        encoded = raw.encode("utf-8")
        assert len(encoded) == source["raw_response_bytes"]
        assert hashlib.sha256(encoded).hexdigest() == source["raw_response_sha256"]
        assert json.loads(raw)
        assert source["raw_response_hash_scope"].startswith("SHA-256 of the exact")

    assert sources["Kraken"]["data_as_of_utc"] is None
    assert sources["OKX"]["data_as_of_utc"] == "2026-11-06T23:38:50.666Z"
    assert sources["OKX"]["provider_timestamp_age_seconds_at_capture"] == 1560.334
    assert data["capture_contract"]["original_wire_bytes_captured"] is False


def test_spot_quotes_keep_quote_currency_and_freshness_separate():
    data = load_artifact()
    spot = data["observations"]["spot"]
    by_venue = {item["venue"]: item for item in spot["venues"]}
    kraken = by_venue["Kraken"]
    okx = by_venue["OKX"]

    assert kraken["instrument"] == "XRP/USD"
    assert kraken["last_usd"] == 1.17999
    assert kraken["spread_bps"] == 0.0847461218
    assert kraken["provider_timestamp_utc"] is None
    assert kraken["multi_level_depth_captured"] is False

    assert okx["instrument"] == "XRP-USDT"
    assert okx["last_usdt"] == 1.1812
    assert okx["spread_bps"] == 0.8466325192
    assert okx["fresh_for_300_second_live_feature_admission"] is False
    assert spot["cross_venue"]["consolidated_order_book"] is False
    assert "not an executable arbitrage" in spot["cross_venue"]["execution_warning"]


def test_derivatives_oi_disagreement_is_preserved_and_not_averaged():
    data = load_artifact()
    perps = data["observations"]["derivatives"]
    assert perps["tradradar"]["open_interest_usd"] == 1_900_000_000
    assert perps["alpha_finance"]["open_interest_usd"] == 2_760_000_000
    assert perps["reconciliation"]["open_interest_difference_usd"] == 860_000_000
    assert perps["reconciliation"]["do_not_average"] is True
    assert perps["alpha_finance"]["liquidation_clusters_are_modelled_not_observed_orders"] is True

    tradradar_source = next(x for x in data["sources"] if x["publisher"] == "TradRadar")
    alpha_source = next(x for x in data["sources"] if x["publisher"] == "Alpha Finance")
    for source in (tradradar_source, alpha_source):
        excerpt = source["normalized_excerpt"]
        assert len(excerpt.encode("utf-8")) == source["receipt_bytes"]
        assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == source["receipt_sha256"]


def test_etf_universes_and_flow_cutoffs_remain_unreconciled():
    data = load_artifact()
    etf = data["observations"]["etf"]
    assert etf["xrp_insights"]["xrp_holdings"] == 1_196_540_000
    assert etf["xrp_insights"]["week45_cutoff_and_settled_completeness"] == "not_explicit_in_dashboard_excerpt"
    assert etf["thexrpinvestor"]["stated_product_count"] == 12
    assert etf["thexrpinvestor"]["category_product_count"] == 11
    assert etf["thexrpinvestor"]["count_reconciliation"] == "UNRESOLVED"
    assert etf["cryptokeyhole"]["latest_complete_date"] == "2026-11-04"
    assert etf["reconciliation"]["do_not_average"] is True

    for source in data["sources"]:
        if "normalized_excerpt" in source:
            excerpt = source["normalized_excerpt"]
            assert len(excerpt.encode("utf-8")) == source["receipt_bytes"]
            assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == source["receipt_sha256"]


def test_snapshot_is_not_model_eligible_and_issues_no_forecast_or_trade():
    data = load_artifact()
    assert data["model_eligibility"]["admitted_to_point_in_time_feature_store"] is False
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["forecast_status"]["shadow_forecast_issued"] is False
    assert data["actions"]["paper_trade"] is False
    assert data["actions"]["real_money_action"] is False
    assert data["actions"]["deployment"] is False
    assert data["actions"]["secret_rotation"] is False
    assert data["actions"]["kaggle_submission"] is False
