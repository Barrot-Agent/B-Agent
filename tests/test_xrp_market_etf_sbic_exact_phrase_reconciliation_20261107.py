from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T160204Z-xrp-market-etf-sbic-exact-phrase-reconciliation.json"
)


@pytest.fixture(scope="module")
def evidence() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _source(evidence: dict, source_id: str) -> dict:
    return next(item for item in evidence["sources"] if item["source_id"] == source_id)


def test_exact_exchange_payload_and_excerpt_hashes_reproduce(evidence: dict) -> None:
    for source in evidence["sources"]:
        if "raw_response_text" in source:
            digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
            assert digest == source["raw_response_sha256"]
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]


def test_spot_provider_timestamp_quality_fails_closed(evidence: dict) -> None:
    kraken = _source(evidence, "kraken_xrpusd_ticker")
    okx = _source(evidence, "okx_xrpusdt_ticker")
    assert kraken["provider_event_time_utc"] is None
    assert kraken["model_eligible"] is False
    assert okx["provider_age_seconds_at_capture"] == pytest.approx(1264.637)
    assert okx["freshness"] == "stale_over_300_seconds"
    assert okx["model_eligible"] is False


def test_level_one_spreads_and_cross_venue_gap_recompute(evidence: dict) -> None:
    kraken = json.loads(_source(evidence, "kraken_xrpusd_ticker")["raw_response_text"])
    okx = json.loads(_source(evidence, "okx_xrpusdt_ticker")["raw_response_text"])
    k = kraken["result"]["XXRPZUSD"]
    o = okx["data"][0]
    kb, ka = float(k["b"][0]), float(k["a"][0])
    ob, oa = float(o["bidPx"]), float(o["askPx"])
    k_spread = (ka - kb) / ((ka + kb) / 2) * 10_000
    o_spread = (oa - ob) / ((oa + ob) / 2) * 10_000
    gap = (float(o["last"]) / float(k["c"][0]) - 1) * 100
    assert k_spread == pytest.approx(0.7787319648)
    assert o_spread == pytest.approx(0.8643415878)
    assert gap == pytest.approx(0.0977703176)
    assert "not comparable" in evidence["reconciliations"]["spot"]


def test_depth_snapshots_are_stale_and_product_scopes_are_distinct(evidence: dict) -> None:
    fuel = _source(evidence, "fuelmaps_xrp_spot_depth")
    edge = _source(evidence, "edgeornot_xrp_depth")
    assert fuel["page_snapshot_time_utc"] == "2026-11-07T09:00:00Z"
    assert edge["page_snapshot_time_utc"] == "2026-11-07T14:30:00Z"
    assert fuel["model_eligible"] is False and edge["model_eligible"] is False
    assert "spot plus OKX perpetual" in edge["normalized_excerpt"]
    assert evidence["calculations"]["fuelmaps_snapshot_age_seconds"] > 25_000


def test_secondary_taker_flow_is_context_not_current_feature(evidence: dict) -> None:
    source = _source(evidence, "swiftedge_xrp_market_brief")
    assert source["provider_age_seconds_at_capture"] == 10_504
    assert source["model_eligible"] is False
    assert "negative taker flow" in source["normalized_excerpt"]
    assert "nearly three hours old" in evidence["hypotheses"][0]["counterevidence"][0]


def test_etf_fund_universes_and_flow_methods_are_not_averaged(evidence: dict) -> None:
    alpha = _source(evidence, "alpha_finance_xrp_etf_flows")
    insights = _source(evidence, "xrp_insights_etf_totals_metadata")
    keyhole = _source(evidence, "crypto_keyhole_xrp_etf_flows")
    assert alpha["fund_count"] == 5
    assert alpha["nov6_flow_usd"] == 0
    assert insights["spot_funds"] == 6
    assert insights["additional_index_fund"] == "BITW"
    assert insights["flow_method"].startswith("issuer-reported XRP holdings delta")
    assert keyhole["fund_count"] == 4
    assert keyhole["nov6_reporting_funds"] == 2
    assert keyhole["nov6_expected_funds"] == 4
    assert "do not average" in evidence["reconciliations"]["etf_flows"]


def test_sbic_east_central_west_are_distinct_from_sbi_holdings(evidence: dict) -> None:
    east = _source(evidence, "sbic_east_official_profile")
    central = _source(evidence, "sbic_central_official_profile")
    west = _source(evidence, "sbic_west_official_profile")
    seminar = _source(evidence, "sbic_tokyo_chatgpt_seminar")
    assert "SBIC East Japan" in east["normalized_excerpt"]
    assert "SBIC Central Japan" in central["normalized_excerpt"]
    assert "SBIC West Japan" in west["normalized_excerpt"]
    assert "SBI Holdings affiliation" in east["limitations"][0]
    assert "not an OpenAI partnership" in seminar["limitations"][0]


def test_actual_capital_phrase_is_secondary_and_not_proof_of_cash_received(evidence: dict) -> None:
    source = _source(evidence, "phemex_evernorth_actual_capital_phrase")
    assert source["source_type"] == "secondary_news_article"
    assert "actual capital raised" in source["normalized_excerpt"]
    assert "not issuer-primary" in source["limitations"][0]
    assert "not a draw, settled cash or XRP purchase" in source["limitations"][1]


def test_measurement_hypotheses_keep_counterevidence_and_no_forecast(evidence: dict) -> None:
    assert len(evidence["hypotheses"]) == 3
    assert all(item["counterevidence"] for item in evidence["hypotheses"])
    assert evidence["model_admission"]["all_new_observations_eligible"] is False
    assert evidence["forecast"]["status"] == "NOT_ISSUED"
    assert evidence["forecast"]["directional_probabilities"] is None
    assert evidence["forecast"]["real_money_actions"] is False
    assert evidence["forecast"]["paper_trade"] is False
