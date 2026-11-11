from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T050101Z-xrp-spot-derivatives-etf-depth-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def source_by_id(artifact: dict, source_id: str) -> dict:
    return next(
        source for source in artifact["source_records"]
        if source["source_id"] == source_id
    )


def test_all_source_receipts_match_recorded_sha256() -> None:
    artifact = load_artifact()
    for source in artifact["source_records"]:
        if "raw_response_text" in source:
            payload = source["raw_response_text"]
            expected = source["raw_response_sha256"]
        else:
            payload = source["normalized_excerpt"]
            expected = source["excerpt_sha256"]
        assert hashlib.sha256(payload.encode("utf-8")).hexdigest() == expected


def test_kraken_ticker_preserves_usd_fields_and_missing_event_time() -> None:
    artifact = load_artifact()
    spot = artifact["spot"]["kraken_xrp_usd"]
    source = source_by_id(artifact, "kraken_xrp_usd_ticker_20261107")
    assert spot["last_trade_usd"] == 1.15169
    assert spot["best_bid_usd"] == 1.15198
    assert spot["best_ask_usd"] == 1.15208
    assert spot["volume_24h_xrp"] == 30075957.06047015
    assert spot["provider_event_timestamp_utc"] is None
    assert spot["model_eligible"] is False
    assert source["provider_event_timestamp_utc"] is None


def test_okx_ticker_is_excluded_when_provider_timestamp_exceeds_live_age() -> None:
    artifact = load_artifact()
    spot = artifact["spot"]["okx_xrp_usdt"]
    source = source_by_id(artifact, "okx_xrp_usdt_ticker_20261107")
    assert spot["provider_timestamp_utc"] == "2026-11-07T04:52:50.769Z"
    assert spot["age_at_reference_clock_seconds"] > 300
    assert spot["stale_against_300_second_limit"] is True
    assert spot["model_eligible"] is False
    assert "USDT" in spot["exclusion_reason"]
    assert source["raw_response_sha256"] == (
        "b12f35e078136ef4b3ff08cf1b62a6bf6466731b467e19dde0aa60da3387643e"
    )


def test_cross_venue_last_price_difference_is_not_marked_comparable() -> None:
    artifact = load_artifact()
    spot = artifact["spot"]
    assert spot["raw_cross_venue_last_difference_pct"] > 0
    assert spot["cross_venue_status"] == "NOT_COMPARABLE"
    assert len(spot["cross_venue_limitations"]) >= 3


def test_derivatives_oi_coverage_gap_is_preserved_not_averaged() -> None:
    derivatives = load_artifact()["derivatives"]
    assert derivatives["tradradar"]["open_interest_usd"] == 1_870_000_000
    assert derivatives["alpha_finance_heatmap"]["open_interest_usd"] == 2_730_000_000
    assert derivatives["oi_difference_usd"] == 860_000_000
    assert derivatives["reconciliation_status"] == "UNRESOLVED_COVERAGE_DIFFERENCE"
    assert derivatives["do_not_average"] is True


def test_alpha_liquidation_clusters_are_labelled_as_modelled_not_resting_orders() -> None:
    alpha = load_artifact()["derivatives"]["alpha_finance_heatmap"]
    assert alpha["modelled_short_liquidation_clusters_above_usd"] == 106_300_000
    assert alpha["modelled_long_liquidation_clusters_below_usd"] == 29_400_000
    assert "modelled" in alpha["methodology_limit"].lower()
    assert "not observed resting orders" in alpha["methodology_limit"]


def test_etf_flow_provider_universes_and_internal_conflict_are_preserved() -> None:
    etf = load_artifact()["etf_flows"]
    assert etf["alpha_finance"]["fund_count"] == 5
    assert etf["alpha_finance"]["source_feed_per_methodology"] == "Coinglass"
    assert etf["cryptoetf_today"]["internal_consistency"] == "CONTRADICTORY"
    assert "2 of 5" in etf["cryptoetf_today"]["page_initial_coverage_statement"]
    assert "5 of 5" in etf["cryptoetf_today"]["page_later_coverage_statement"]
    assert etf["cryptoetf_today"]["daily_table"]["XRPZ"] is None
    assert etf["xrp_insights"]["fund_count"] == 7
    assert etf["xrp_insights"]["latest_row_status"] == "provisional"
    assert "not directly from issuer" in etf["xrp_insights"]["methodology"]
    assert "Do not average" in etf["reconciliation"]


def test_no_numeric_xrp_depth_is_not_promoted_to_a_depth_feature() -> None:
    depth = load_artifact()["order_book_depth"]["fuelmaps"]
    assert depth["xrp_numeric_depth_available"] is False
    assert depth["model_eligible"] is False
    assert "client-side JavaScript" in depth["reason"]


def test_hypotheses_retain_counterevidence_and_no_forecast_is_issued() -> None:
    artifact = load_artifact()
    assert all(item["counterevidence"] for item in artifact["hypotheses"])
    assert artifact["model_admission"]["eligible_as_point_in_time_feature"] is False
    assert artifact["model_admission"]["eligible_as_event_timeline_context"] is True
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["direction"] is None
    assert artifact["forecast"]["probabilities"] is None
    assert artifact["forecast"]["shadow_forecast_issued"] is False
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
    assert not any(artifact["external_actions"].values())
