from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T143102Z-post-bls-xrp-market-structure-followup.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_post_bls_followup_keeps_provider_time_unknown_and_forecast_disabled():
    data = _artifact()
    assert data["status"] == "RESEARCH_ONLY_MODEL_INELIGIBLE"
    assert data["capture_contract"]["common_point_in_time_cutoff_utc"] is None
    assert data["market"]["kraken_xrp_usd"]["provider_event_timestamp_utc"] is None
    assert data["market"]["kraken_xrp_usd"]["exact_retrieval_time_utc"] is None
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast_issued"] is False


def test_kraken_rendered_receipt_and_spread_are_reproducible():
    data = _artifact()
    source = next(x for x in data["source_registry"] if x["source_id"] == "kraken_xrp_usd_ticker_run_11")
    excerpt = source["excerpt"]
    assert len(excerpt) == source["receipt"]["characters"] == 320
    assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == source["receipt"]["digest"]
    market = data["market"]["kraken_xrp_usd"]
    midpoint = (market["best_bid_usd"] + market["best_ask_usd"]) / 2
    spread = (market["best_ask_usd"] - market["best_bid_usd"]) / midpoint * 10_000
    assert math.isclose(spread, market["spread_bps"], abs_tol=0.0001)
    assert market["model_eligible"] is False


def test_spot_depth_and_derivatives_are_kept_as_distinct_coverage_universes():
    data = _artifact()["market"]
    depth = data["fuelmaps_spot_depth"]
    assert depth["snapshot_time_utc"] == "2026-11-06T14:00:00Z"
    assert depth["venues"] == ["Coinbase", "OKX", "Kraken", "Bitstamp", "Bitfinex", "Gemini"]
    assert "Binance" in depth["excluded_venues"]
    assert depth["bands"]["1pct"]["bids_usd"] > depth["bands"]["1pct"]["asks_usd"]
    trad = data["tradradar_derivatives"]
    alpha = data["alpha_finance_derivatives"]
    assert trad["open_interest_venue_count"] == 7
    assert alpha["open_interest_usd"] != trad["open_interest_usd"]
    assert "not comparable" in alpha["limitations"][0]


def test_etf_universe_disagreement_and_corpstacking_nciq_conflict_are_preserved():
    etf = _artifact()["etf_flows"]
    assert etf["xrp_insights"]["net_flow_xrp_nov2_nov5"] == -149487
    assert etf["cryptokeyhole"]["nov5_reported_funds"] == 3
    assert etf["alpha_finance"]["thirty_day_flow_usd"] == 15_400_000
    corp = etf["corpstacking"]
    assert corp["displayed_total_xrp"] - corp["nciq_xrp_included_in_ten_row_sum"] == corp["ten_row_sum_excluding_nciq_xrp"]
    assert corp["methodology_text_says_nciq_is_excluded"] is True
    assert "not admitted" in corp["scope_conflict"]


def test_bls_actual_is_separated_from_survey_and_market_interpretation():
    macro = _artifact()["macro_event"]
    assert macro["publication_time_utc"] == "2026-11-06T13:30:00Z"
    assert macro["primary_actual"]["nonfarm_payroll_change"] == 165000
    assert macro["expectations"]["reuters_survey_payrolls"] == 65000
    assert macro["surprise_vs_reuters_payrolls"] == 100000
    assert macro["expectations"]["wsj_reported_survey_payrolls"] == 59000
    assert macro["market_reaction"]["causal_link_to_xrp"] == "Not established; no synchronized provider-timestamped XRP event return is available."
