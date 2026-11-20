import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T173050Z-xrp-spot-derivatives-macro-etf-vintage-update.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_late_kraken_spot_arithmetic_and_daily_open_semantics():
    data = load()
    spot = data["market_snapshot"]["kraken_spot"]
    midpoint = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    spread = (spot["best_ask_usd"] - spot["best_bid_usd"]) / midpoint * 10000
    assert spot["last_usd"] == 1.23809
    assert spot["midpoint_usd"] == midpoint
    assert abs(spot["spread_bps"] - spread) < 1e-12
    assert spot["utc_day_open_label"] == "current UTC-day open; not a rolling 24-hour open"
    assert spot["provider_event_time_utc"] is None


def test_cross_venue_comparison_is_asynchronous_and_not_a_return_series():
    data = load()["market_snapshot"]["earlier_cross_venue_composite"]
    assert data["updated_at_utc"] == "2026-11-05T11:26:40Z"
    assert data["elapsed_seconds"] == 21850
    assert data["comparison_to_later_kraken_pct"] < -6.0
    assert "not a synchronized return series" in data["interpretation_limit"]


def test_derivatives_snapshot_is_not_carried_forward_to_later_spot_cutoff():
    data = load()["market_snapshot"]["derivatives"]
    assert data["tradradar"]["open_interest_usd"] == 2_040_000_000
    assert data["tradradar"]["funding_rate_pct_per_8h"] == 0.01
    assert data["tradradar"]["long_liquidations_usd"] < data["tradradar"]["short_liquidations_usd"]
    assert "predates the later Kraken spot observation by 4h45m" in data["synchronization_warning"]


def test_etf_vintages_and_fund_universes_are_not_averaged():
    data = load()["market_snapshot"]["etf_flows"]
    assert data["xrp_insights"]["net_flow_xrp_nov2_to_nov3"] == -194_875
    assert data["xrp_insights"]["nov4_row_status"] == "provisional_until_re_settled"
    assert data["cryptokeyhole"]["latest_complete_holdings_date"] == "2026-11-03"
    assert data["alpha_finance"]["data_through"] == "2026-11-03"
    assert data["reconciliation"]["aggregation"] == "not_averaged"


def test_macro_and_security_context_remain_hypotheses_and_forecast_is_not_issued():
    data = load()
    assert data["macro_context"]["reported_observations"]["boe_policy_rate_pct"] == 4.0
    assert data["crypto_security_context"]["interpretation_limit"].startswith("Regulatory outreach is not evidence")
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["admission"]["directional_forecast_issued"] is False
    assert data["source_capture_policy"]["raw_source_sha256_receipts"] is None
