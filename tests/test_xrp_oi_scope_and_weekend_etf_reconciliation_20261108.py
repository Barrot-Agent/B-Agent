import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T190139Z-xrp-oi-scope-and-weekend-etf-reconciliation.json"

def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))

def test_tradradar_seven_exchange_components_reconcile_to_displayed_total():
    data = load()["market_observations"]["derivatives"]["tradradar"]
    assert sum(data["exchanges"].values()) == data["component_sum_usd"] == 1_895_510_000
    assert data["component_sum_rounds_to_displayed_total"] is True
    assert data["exchange_count"] == 7

def test_fexr_193m_is_not_mislabeled_as_total_market_open_interest():
    data = load()["market_observations"]["derivatives"]
    fexr = data["fexr"]
    tradradar = data["tradradar"]
    assert fexr["search_result_oi_usd"] == 193_600_000
    assert tradradar["exchanges"]["Hyperliquid"] == 193_150_000
    assert fexr["current_search_result_vs_tradradar_hyperliquid_component_difference_usd"] == 450_000
    assert "hypothesis, not a verified fact" in fexr["interpretation"]
    assert data["scope_reconciliation"]["competing_hypotheses"]

def test_fexr_stale_rendered_page_is_not_substituted_for_newer_search_snapshot():
    fexr = load()["market_observations"]["derivatives"]["fexr"]
    assert fexr["search_result_updated_at_utc"] == "2026-11-08T16:43:00Z"
    assert fexr["rendered_page_capture_at_utc"] == "2026-11-05T20:22:00Z"
    assert fexr["rendered_page_oi_usd"] == 212_900_000
    assert fexr["search_result_oi_usd"] != fexr["rendered_page_oi_usd"]

def test_tradradar_funding_and_long_skew_units_are_explicit():
    data = load()["market_observations"]["derivatives"]["tradradar"]
    assert data["oi_weighted_funding_pct_per_8h"] == 0.0077
    assert data["long_account_share_pct"] == 79.4
    assert data["long_short_ratio"] == 3.86
    assert data["liquidations_24h_usd_minimum"] == 1_270_000
    assert data["long_liquidations_usd"] > data["short_liquidations_usd"]

def test_swiftedge_resting_walls_are_quarantined_not_executable_depth():
    data = load()["market_observations"]["displayed_liquidity"]
    assert data["provider"] == "Swiftedge"
    assert data["admission"] == "quarantined"
    assert "Resting walls can be cancelled" in data["limitations"][1]
    assert data["bid_wall"]["quantity_xrp"] == 5_157_838
    assert data["ask_wall"]["quantity_xrp"] == 5_579_459

def test_alpha_finance_etf_flow_scope_and_weekend_cutoff_are_bounded():
    data = load()["market_observations"]["etf_flows"]
    assert data["upstream_feed"] == "CoinGlass commercial API, per Alpha Finance methodology"
    assert data["latest_session_date"] == "2026-11-06"
    assert data["latest_session_flow_usd"] == 0
    assert data["funds_reporting_latest_session"] == 5
    assert data["thirty_session_flow_usd"] == 45_900_000
    assert data["cumulative_component_sum_usd"] == 1_730_400_000
    assert any("No weekend 7 or 8 Nov" in item for item in data["limitations"])

def test_alpha_finance_is_not_counted_as_independent_of_coinglass():
    data = load()["provenance"]
    assert data["source_independence_groups"]["alpha_finance"].startswith("COINGLASS_UPSTREAM")
    assert any(source.get("upstream_provider") == "CoinGlass" for source in data["sources"])

def test_normalized_excerpt_hashes_are_scoped_and_well_formed():
    sources = load()["provenance"]["sources"]
    for source in sources:
        digest = source.get("excerpt_sha256")
        if digest is not None:
            assert len(digest) == 64
            int(digest, 16)
            assert "normalized" in source["hash_scope"]

def test_no_model_admission_or_directional_forecast():
    data = load()
    assert data["model_admission"]["admitted"] is False
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["interpretation"]["no_directional_conclusion"] is True
