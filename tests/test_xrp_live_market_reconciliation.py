from __future__ import annotations

import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261105T030131Z-live-market-etf-amendment-reconciliation.json"
)


def test_live_market_reconciliation_is_observational_only_and_not_model_eligible():
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert document["mission_priority"] == 1
    assert document["model_eligible"] is False
    assert document["forecast_issued"] is False
    assert document["paper_trade_executed"] is False
    assert document["prediction_status"] == "NOT_ISSUED"
    assert document["source_capture_policy"]["raw_http_bytes_captured"] is False
    assert document["source_capture_policy"]["independent_timestamp_anchor"] is False

    for source in document["source_registry"]:
        assert source["raw_capture_status"] == "web_rendered_extract_only"
        assert source["raw_http_bytes_sha256"] is None

    kraken = next(
        item for item in document["observations"]
        if item["observation_id"] == "kraken_xrpusd_top_of_book"
    )
    assert kraken["last_price_usd"] == 1.30546
    assert kraken["best_bid_quantity_xrp"] == 3417
    assert kraken["best_ask_quantity_xrp"] == 192
    assert 0.22 < kraken["displayed_top_of_book_spread_bps"] < 0.24
    assert "not a depth ladder" in " ".join(kraken["limitations"])


def test_binance_derivatives_snapshot_is_timestamped_and_stale():
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    item = next(
        item for item in document["observations"]
        if item["observation_id"] == "binance_xrpusdt_perpetual_premium"
    )

    assert item["exchange_response_time_utc"] == "2026-11-05T02:25:56Z"
    assert item["age_at_capture_seconds"] == 2135
    assert item["last_funding_rate"] == 0.0001
    assert item["next_funding_time_utc"] == "2026-11-05T08:00:00Z"
    assert any("Stale by 35m35s" in value for value in item["limitations"])


def test_xrpl_cleanup_activation_is_not_mislabeled_as_lending_activation():
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    item = next(
        item for item in document["observations"]
        if item["observation_id"] == "xrpl_governance_and_amendments"
    )

    assert item["fixCleanup3_4_0"]["status"] == "enabled"
    assert item["fixCleanup3_4_0"]["enabled_ledger"] == 108112129
    assert item["lending_activated"] is False
    assert item["activation_countdown_entries"] == 0
    assert item["current_votes"]["SingleAssetVault"] == 21
    assert item["current_votes"]["LendingProtocol"] == 19
    assert len(item["limitations"]) >= 3


def test_etf_flow_disagreement_preserves_unlike_universes_and_units():
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    by_id = {item["observation_id"]: item for item in document["observations"]}

    xrp_insights = by_id["xrp_insights_etf_flow"]
    cryptokeyhole = by_id["cryptokeyhole_etf_flow"]
    alpha = by_id["alpha_finance_etf_flow"]

    assert xrp_insights["net_flow_xrp"] == -194875
    assert "BITW" in xrp_insights["fund_universe"]
    assert xrp_insights["nov4_row_status"] == "provisional"

    assert cryptokeyhole["net_flow_xrp_2026_11_03"] == -3339
    assert cryptokeyhole["nov4_status"] == "partial_one_of_four_funds"
    assert "GXRP" not in cryptokeyhole["fund_universe"]
    assert "XRPR" not in cryptokeyhole["fund_universe"]
    assert "BITW" not in cryptokeyhole["fund_universe"]

    assert alpha["nov4_net_flow_usd"] == 0
    assert alpha["last_seven_sessions_net_flow_usd"] == 4800000
    assert alpha["holdings_and_aum_published"] is False

    disagreement = next(
        item for item in document["disagreements"]
        if item["topic"] == "ETF flows"
    )
    assert "Do not average" in disagreement["resolution"]
    assert "Different fund universes" in disagreement["resolution"]


def test_timestamp_and_source_disagreements_are_retained_without_directional_claim():
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    topics = {item["topic"] for item in document["disagreements"]}
    assert {
        "XRP spot reference",
        "ETF flows",
        "XRPL amendment timestamps",
        "Derivatives freshness",
    } <= topics

    assert document["prediction_status"] == "NOT_ISSUED"
    assert document["source_capture_policy"]["rendered_hashes_are_not_raw_source_hashes"] is True
