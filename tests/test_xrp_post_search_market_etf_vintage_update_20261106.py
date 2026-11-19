from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T153504Z-xrp-post-search-market-etf-vintage-update.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_market_observations_remain_asynchronous_and_instrument_scoped():
    data = load_artifact()
    observations = data["spot_market"]["observations"]
    assert [x["source_id"] for x in observations] == [
        "swiftedge_market_brief",
        "tradradar_perpetuals",
        "alpha_finance_liquidations",
    ]
    assert observations[0]["display_time_utc"] == "2026-11-06T12:07:00Z"
    assert observations[1]["display_delay_minutes"] == 15
    assert observations[1]["mark_price_usd"] == 1.1835
    assert observations[2]["spot_price_usd"] == 1.1856
    assert data["common_point_in_time_cutoff_utc"] is None
    assert "not a synchronized return series" in data["spot_market"]["interpretation"]


def test_derivatives_provider_universes_are_not_averaged():
    data = load_artifact()["derivatives"]
    assert data["tradradar"]["venue_count"] == 7
    assert data["tradradar"]["open_interest_usd"] == 1_900_000_000
    assert data["alpha_finance"]["open_interest_usd"] == 2_770_000_000
    assert data["reconciliation"]["values_comparable"] is False
    assert data["reconciliation"]["values_may_be_averaged"] is False
    assert data["alpha_finance"]["liquidation_clusters_are_observed_orders"] is False


def test_etf_vintages_keep_provisional_and_partial_days_distinct():
    data = load_artifact()["etf_flows"]
    assert data["xrp_insights_homepage"]["daily_holdings_change_xrp"] == 110_214
    assert data["xrp_insights_downloads"]["nov5_row_status"] == "PROVISIONAL_UNTIL_RESETTLED"
    assert data["cryptokeyhole"]["nov5_published_funds"] == 2
    assert data["cryptokeyhole"]["nov5_expected_funds"] == 4
    assert data["cryptokeyhole"]["nov5_status"] == "PARTIAL_NOT_NEUTRAL"
    assert data["reconciliation"]["direct_ap_cash_creation_redemption_observed"] is False


def test_inconsistent_dashboard_product_count_is_excluded():
    row = load_artifact()["etf_flows"]["thexrpinvestor"]
    assert row["stated_product_count"] == 12
    assert sum(row["categories"].values()) == 11
    assert row["synthesis_status"] == "EXCLUDED_PENDING_PRODUCT_COUNT_RECONCILIATION"


def test_normalized_excerpt_hashes_match_and_raw_bytes_are_not_claimed():
    for source in load_artifact()["source_registry"]:
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]
        assert source["raw_http_bytes_captured"] is False


def test_hypotheses_retain_counterevidence_and_no_causality():
    data = load_artifact()
    assert len(data["competing_hypotheses"]) >= 4
    assert all(x.get("counterevidence") for x in data["competing_hypotheses"])
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["model_eligibility"]["eligible"] is False


def test_no_paper_or_real_money_actions():
    safety = load_artifact()["safety"]
    assert safety["research_only"] is True
    assert safety["no_paper_trade"] is True
    assert safety["no_real_money_action"] is True
