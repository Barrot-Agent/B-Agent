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


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_incremental_delta_references_prior_snapshots_instead_of_repeating_them():
    data = load_artifact()
    refs = {item["path"] for item in data["prior_artifact_references"]}
    assert "research/xrp_intelligence/20261106T120807Z-xrp-spot-derivatives-etf-vintage-reconciliation.json" in refs
    assert "research/xrp_intelligence/20261106T134313Z-bls-october-employment-and-xrp-post-release-market-reconciliation.json" in refs
    assert "research/xrp_intelligence/20261106T140454Z-xrp-spot-depth-perps-etf-xrpl-governance-addendum.json" in refs
    assert "fuelmaps_14_00_depth" in data["referenced_unchanged_observations"]


def test_all_new_normalized_source_receipts_reproduce():
    data = load_artifact()
    for source in data["source_registry"]:
        assert len(source["normalized_excerpt"]) == source["characters"]
        assert hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest() == source["sha256"]
        assert source["raw_http_bytes_captured"] is False


def test_kraken_snapshot_preserves_unknown_provider_time_and_spread():
    data = load_artifact()
    market = data["new_market_observations"]["kraken_xrp_usd"]
    assert market["provider_event_timestamp_utc"] is None
    assert market["exact_retrieval_time_utc"] is None
    midpoint = (market["bid_usd"] + market["ask_usd"]) / 2
    spread = (market["ask_usd"] - market["bid_usd"]) / midpoint * 10_000
    assert math.isclose(spread, market["spread_bps"], abs_tol=0.0001)
    assert market["last_vs_24h_vwap_pct"] < 0


def test_tradradar_and_alpha_open_interest_are_not_averaged():
    data = load_artifact()["new_market_observations"]
    trad = data["tradradar"]
    alpha = data["alpha_finance_derivatives"]
    assert trad["open_interest_7_venues_usd"] == 1_900_000_000
    assert trad["open_interest_change_24h_pct"] == -7.60
    assert alpha["all_venue_open_interest_usd"] == 2_770_000_000
    assert alpha["note"].startswith("All-venue OI")
    assert trad["long_liquidations_usd"] > trad["short_liquidations_usd"]


def test_etf_page_vintages_and_corpstacking_nciq_conflict_remain_unresolved():
    data = load_artifact()["etf_vintage_conflicts"]
    alpha = data["alpha_finance"]
    assert "+$15.4M" in alpha["current_display"]
    assert "+$60.8M" in alpha["prior_display"]
    assert alpha["comparison_status"].startswith("UNRESOLVED")
    corp = data["corpstacking"]
    assert corp["headline_xrp"] - corp["nciq_xrp_included_in_row_sum"] == corp["sum_excluding_nciq_xrp"]
    assert corp["methodology_says_nciq_basket_funds_excluded"] is True
    assert corp["status"] == "INTERNAL_PUBLISHER_SCOPE_CONFLICT"


def test_bls_missing_october_2025_is_not_zero_or_imputed():
    data = load_artifact()["historical_series_quality"]
    gap = data["bls_october_2025"]
    assert gap["collected"] is False
    assert "do not encode zero" in gap["handling"]
    assert "establishment survey" in data["survey_separation"]["nonfarm_payrolls"]


def test_swiftedge_onchain_perps_are_not_mislabeled_as_spot_flow():
    data = load_artifact()["new_market_observations"]["swiftedge"]["onchain_perpetual_orders"]
    assert data["net_notional_usd"] == -2_300_000
    assert data["scope"].startswith("On-chain XRP perpetual futures")
    assert "not spot" in data["scope"]


def test_no_directional_forecast_is_issued_from_unsynchronized_observations():
    data = load_artifact()
    assert data["common_point_in_time_cutoff_utc"] is None
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast_issued"] is False
