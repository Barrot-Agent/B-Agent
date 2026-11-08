from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T141400Z-xrp-alpha-finance-derivatives-snapshot-vintage-correction.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_alpha_finance_uses_newer_1316_snapshot_without_erasing_prior_vintage():
    data = load_artifact()
    alpha = next(x for x in data["sources"] if x["source_id"] == "alpha_finance_xrp_liquidation_heatmap_1316")
    assert alpha["publisher_snapshot_utc"] == "2026-11-07T13:16:00Z"
    assert alpha["open_interest_usd"] == 2_750_000_000
    assert alpha["volume_24h_usd"] == 2_350_000_000
    assert alpha["long_liquidations_24h_usd"] == 10_200_000
    assert alpha["short_liquidations_24h_usd"] == 454_100
    assert data["supersedes_artifact_field"]["prior_publisher_update_utc"] == "2026-11-07T12:46:00Z"
    assert alpha["model_eligible"] is False


def test_tradradar_comparison_keeps_its_own_timestamp_and_venue_scope():
    data = load_artifact()
    trad = next(x for x in data["sources"] if x["source_id"] == "tradradar_xrp_futures_1320")
    assert trad["publisher_snapshot_utc"] == "2026-11-07T13:20:00Z"
    assert trad["open_interest_usd"] == 1_890_000_000
    assert trad["open_interest_venues"] == 7
    assert trad["weighted_funding_pct_per_8h"] == 0.009
    assert trad["liquidations_24h_minimum_usd"] == 8_630_000


def test_close_in_time_open_interest_snapshots_still_show_unresolved_860m_gap():
    reconciliation = load_artifact()["reconciliation"]
    assert reconciliation["open_interest_difference_usd"] == 860_000_000
    assert round(reconciliation["difference_pct_of_tradradar"], 2) == 45.50
    assert reconciliation["current_status"] == "UNRECONCILED_PROVIDER_SCOPE_DIFFERENCE"
    assert "Do not average" in reconciliation["interpretation"]


def test_alpha_liquidation_clusters_are_modelled_not_resting_orders():
    data = load_artifact()
    alpha = next(x for x in data["sources"] if x["source_id"] == "alpha_finance_xrp_liquidation_heatmap_1316")
    assert alpha["largest_short_cluster"] == {
        "notional_usd": 5_000_000,
        "price_usd": 1.2005,
        "distance_above_spot_pct": 3.5,
    }
    assert alpha["largest_long_cluster"] == {
        "notional_usd": 2_800_000,
        "price_usd": 1.1427,
        "distance_below_spot_pct": 1.5,
    }
    assert "not observed resting orders" in alpha["limitations"][0]


def test_no_derivatives_observation_is_admitted_as_a_model_feature_or_forecast():
    data = load_artifact()
    assert data["model_admission"]["admitted_to_live_price_features"] is False
    assert data["model_admission"]["admitted_to_open_interest_features"] is False
    assert data["model_admission"]["admitted_to_liquidation_features"] is False
    assert data["model_admission"]["eligible_for_event_timeline"] is True
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["paper_trade_executed"] is False
    assert data["forecast"]["real_money_action"] is False
    assert data["source_capture_contract"]["raw_http_sha256_claimed"] is False
