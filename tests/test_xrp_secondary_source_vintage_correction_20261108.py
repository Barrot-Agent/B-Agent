from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T094759Z-xrp-secondary-source-vintage-correction.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_normalized_source_receipt_hashes_match():
    data = load_artifact()
    for receipt in data["source_receipts"]:
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["excerpt_sha256"]


def test_webeconomia_nov8_search_snippet_is_quarantined_against_rendered_page_vintage():
    data = load_artifact()
    row = data["source_vintage_corrections"]["webeconomia"]
    assert row["status"] == "SEARCH_SNIPPET_QUARANTINED_RENDERED_PAGE_VINTAGE_CONFLICT"
    assert row["earlier_search_snippet_claimed_as_of_utc"] == "2026-11-08T03:13:00Z"
    assert row["current_rendered_page_as_of_utc"] == "2026-11-06T20:43:00Z"
    assert row["corrected_rendered_values"]["open_interest_usd"] == 1_610_000_000
    assert row["corrected_rendered_values"]["liquidations_24h_usd"] == 10_200_000
    assert row["quarantined_values_from_prior_search_snippet"]["stablecoin_total_supply_usd_headline"] == 292_300_000_000
    assert "Do not use" in row["disposition"]


def test_webeconomia_coverage_explains_aggregator_liquidation_disagreement():
    data = load_artifact()
    text = data["source_vintage_corrections"]["webeconomia"]["coverage_explanation"]
    assert "verifiable liquidations" in text
    assert "Hyperliquid" in text
    assert "estimate Binance" in text


def test_tradradar_newer_snapshot_is_separate_from_earlier_snapshot():
    data = load_artifact()
    row = data["source_vintage_corrections"]["tradradar"]
    assert row["page_updated_at_utc"] == "2026-11-08T09:05:00Z"
    assert row["open_interest_usd"] == 1_910_000_000
    assert row["funding_oi_weighted_pct_per_8h"] == 0.0073
    assert row["liquidations_24h_lower_bound_usd"] == 1_300_000
    assert row["short_liquidations_usd"] == 72_190
    assert "Preserve both" in row["change_from_0735_snapshot"]


def test_cryptokeyhole_partial_nov6_flow_is_not_added_to_complete_cumulative_total():
    data = load_artifact()
    row = data["source_vintage_corrections"]["cryptokeyhole"]
    assert row["page_updated_at_utc"] == "2026-11-08T09:47:00Z"
    assert row["nov6_flow_xrp"] == -752_048
    assert row["nov6_coverage"] == "3 of 4 daily-readable funds; Franklin XRPZ missing"
    assert row["oct23_to_nov5_ten_session_flow_xrp"] == 3_374_507
    assert row["partial_day_not_added_to_cumulative"] is True
    assert row["latest_file_dates"]["bitwise_issuer_stamp_utc"] == "2026-11-08T09:32:00Z"


def test_xrp_insights_live_dashboard_is_separated_from_dated_nov6_flow():
    data = load_artifact()
    row = data["source_vintage_corrections"]["xrp_insights"]
    assert row["total_aum_usd"] == 1_407_230_000
    assert row["xrp_locked"] == 1_195_180_000
    assert row["dated_nov6_flow_xrp"] == -663_043
    assert row["dated_nov2_to_nov6_week_flow_xrp"] == -812_500
    assert "undated current snapshot" in row["scope_note"]


def test_alpha_finance_scope_and_forecast_abstention_are_preserved():
    data = load_artifact()
    row = data["source_vintage_corrections"]["alpha_finance"]
    assert row["fund_count"] == 5
    assert row["nov6_flow_usd"] == 0
    assert row["thirty_session_flow_usd"] == 45_900_000
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
