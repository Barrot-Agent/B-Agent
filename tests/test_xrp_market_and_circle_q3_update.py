"""Regression checks for the 2026-11-04 XRP market and Circle Q3 evidence update."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261104T180409Z-xrp-market-and-circle-q3-update.json"


def test_kraken_observation_keeps_utc_daily_open_and_single_venue_limits():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    market = data["market_observation"]
    assert market["last_usd"] == 1.31413
    assert market["best_bid_usd"] == 1.31408
    assert market["best_ask_usd"] == 1.31409
    assert market["utc_day_open_usd"] == 1.27513
    assert market["spread_basis_points"] < 0.1
    assert market["source_event_timestamp_utc"] is None
    assert market["model_eligible"] is False
    assert data["data_quality"]["exchange_depth_available"] is False
    assert data["data_quality"]["forecast_issued"] is False
    assert data["data_quality"]["prediction_status"] == "NOT_ISSUED"


def test_etf_provider_disagreement_is_preserved_without_averaging():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    flow = data["etf_flow_observation"]
    assert flow["trading_day"] == "2026-11-03"
    assert flow["daily_net_flow_usd"] == 0
    assert flow["settlement_status"] == "provisional_until_issuer_settlement"
    providers = {item["provider"] for item in data["etf_provider_disagreement"]["observations"]}
    assert providers == {"CryptoKeyhole", "CryptoETF.today", "XRP Insights", "ByKaranteli"}
    assert "Do not average" in data["etf_provider_disagreement"]["reconciliation"]


def test_circle_q3_filing_separates_recurring_reserve_income_from_arc_presale():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    q3 = data["circle_q3_2026"]
    financials = q3["financials"]
    assert financials["total_revenue_and_reserve_income_usd_m"] == 864.888
    assert financials["reserve_income_usd_m"] == 657.624
    assert financials["other_revenue_usd_m"] == 207.264
    assert financials["arc_token_presale_revenue_usd_m"] == 182
    assert financials["end_period_usdc_circulation_yoy_pct"] == 0
    assert financials["reserve_return_rate_yoy_change_bps"] == -61
    workforce = q3["workforce_and_cost_restructuring"]
    assert workforce["workforce_reduction_approx_pct"] == 5
    assert workforce["restructuring_expenses_usd_m"] == 9.145
    assert workforce["ai_causation_claim"] == "not stated in the filing"
    assert q3["model_eligible"] is False
    presentation = q3["presentation_metrics"]
    assert presentation["usdc_share_of_stablecoin_transaction_volume_pct"] == 79
    assert presentation["usdc_end_period_location_mix_pct"] == {"circle": 19, "coinbase": 31, "off_platform": 50}
    assert sum(presentation["usdc_end_period_location_mix_pct"].values()) == 100
    assert presentation["model_eligible"] is False
    assert data["data_quality"]["forecast_issued"] is False
    assert data["data_quality"]["prediction_status"] == "NOT_ISSUED"
