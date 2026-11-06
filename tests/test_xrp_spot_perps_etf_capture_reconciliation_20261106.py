from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T232031Z-xrp-spot-perps-etf-capture-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_spot_perpetual_and_etf_sources_keep_distinct_cutoffs_and_hash_scopes():
    data = load_artifact()
    sources = {item["id"]: item for item in data["sources"]}
    assert sources["KRAKEN_XRPUSD_20261106T232031Z"]["data_as_of_utc"] is None
    assert "not complete raw source bytes" in data["capture_contract"]["hash_scope"]
    assert sources["TRADRADAR_XRP_PERPS_20261106T222000Z"]["display_delay_minutes"] == 15
    assert sources["TRADRADAR_XRP_PERPS_20261106T222000Z"]["exact_underlying_data_cutoff_utc"] is None
    assert sources["XRP_INSIGHTS_ETF_20261106_PROVISIONAL"]["data_as_of"] == "2026-11-05"
    assert sources["XRP_INSIGHTS_ETF_20261106_PROVISIONAL"]["latest_row_status"].startswith("provisional")


def test_kraken_spot_values_are_not_promoted_to_synchronized_depth_features():
    data = load_artifact()
    spot = data["observations"]["spot"]
    assert spot["last"] == 1.17703
    assert spot["spread_bps"] == 0.0849599626
    assert spot["provider_timestamp"] is None
    assert spot["multi_level_depth_captured"] is False
    assert data["model_eligibility"]["admitted_to_point_in_time_feature_store"] is False


def test_derivatives_disagreement_and_long_liquidations_are_context_not_forecast():
    data = load_artifact()
    perps = data["observations"]["derivatives"]
    assert perps["open_interest_usd"] == 1900000000
    assert perps["open_interest_change_24h_pct"] == -1.93
    assert perps["oi_weighted_funding_pct_per_8h"] == 0.0022
    assert perps["long_liquidations_usd"] == 10130000
    assert perps["long_account_share_pct"] == 79.9
    assert len(perps["venue_oi_and_funding"]) == 7
    assert data["forecast_status"]["directional_forecast_issued"] is False


def test_etf_flow_remains_holdings_derived_and_nov6_is_provisional():
    data = load_artifact()
    etf = data["observations"]["etf"]
    assert etf["holdings_derived_net_flow_xrp"] == -149487
    assert etf["settled_days"] == 4
    assert etf["nov_6_row_provisional"] is True
    assert etf["nov_6_settled_flow_admitted"] is False
    assert any("not direct AP cash" in item for item in data["interpretation"]["observations"])
