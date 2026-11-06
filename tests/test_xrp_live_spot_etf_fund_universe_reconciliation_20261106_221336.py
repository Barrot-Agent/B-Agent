from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T221336Z-xrp-live-spot-etf-fund-universe-reconciliation.json"
)


def test_fresh_spot_receipts_are_hashed_and_units_are_not_mixed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["captured_at_utc"] == "2026-11-06T22:13:36Z"
    observations = artifact["market_snapshot"]["spot_observations"]
    assert len(observations) == 2
    by_venue = {item["venue"]: item for item in observations}
    for item in observations:
        raw = item["raw_response_text"]
        assert len(raw.encode("utf-8")) == item["raw_response_bytes"]
        assert hashlib.sha256(raw.encode("utf-8")).hexdigest() == item["raw_response_sha256"]
        assert json.loads(raw)
    assert by_venue["Kraken"]["instrument"] == "XRP/USD"
    assert by_venue["Kraken"]["parsed"]["last_usd"] == 1.18002
    assert by_venue["OKX"]["instrument"] == "XRP-USDT"
    assert by_venue["OKX"]["parsed"]["last_usdt"] == 1.1808
    assert by_venue["OKX"]["freshness"]["provider_timestamp_age_seconds"] == 450.626
    assert by_venue["OKX"]["freshness"]["fresh_for_live_feature_admission"] is False
    assert artifact["market_snapshot"]["derived"]["okx_last_vs_kraken_last_pct"] == 0.0661
    assert "not an executable arbitrage" in artifact["market_snapshot"]["derived"]["quote_currency_warning"]


def test_etf_receipts_preserve_distinct_fund_universes_and_methods():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    by_provider = {x["provider"]: x for x in artifact["etf_observations"]}
    insights = by_provider["XRP Insights"]
    for key, text_key, hash_key, bytes_key in [
        ("dashboard", "dashboard_normalized_excerpt", "dashboard_receipt_sha256", "dashboard_receipt_bytes"),
        ("metadata", "metadata_normalized_excerpt", "metadata_receipt_sha256", "metadata_receipt_bytes"),
    ]:
        excerpt = insights[text_key]
        assert len(excerpt.encode("utf-8")) == insights[bytes_key]
        assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == insights[hash_key]
    assert insights["parsed"]["nov5_holdings_delta_xrp"] == 110214
    assert insights["parsed"]["nov2_to_nov5_net_holdings_delta_xrp"] == -149487
    assert insights["parsed"]["fund_universe"] == ["XRPC", "XRP", "XRPZ", "GXRP", "TOXR", "XRPR", "BITW"]
    assert insights["parsed"]["gxrp_flow_status"] == "excluded_due_to_capture_gap"
    assert insights["parsed"]["non_creation_redemption_changes_counted"] is True

    keyhole = by_provider["CryptoKeyhole"]
    excerpt = keyhole["normalized_excerpt"]
    assert len(excerpt.encode("utf-8")) == keyhole["receipt_bytes"]
    assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == keyhole["receipt_sha256"]
    assert keyhole["parsed"]["fund_universe"] == ["XRP", "XRPZ", "XRPC", "TOXR"]
    assert keyhole["parsed"]["nov5_partial_funds_reporting"] == 3
    assert keyhole["parsed"]["nov5_partial_funds_total"] == 4
    assert keyhole["parsed"]["nov5_partial_flow_xrp"] == -3339
    assert keyhole["parsed"]["nov6_funds_published_at_update"] == 0
    assert keyhole["parsed"]["bitw_included"] is False
    assert keyhole["parsed"]["xrpr_included"] is False

    reconciliation = artifact["etf_reconciliation"]
    assert reconciliation["status"] == "NOT_COMPARABLE_DIFFERENT_FUND_UNIVERSES_AND_COMPLETENESS"
    assert "not a direct contradiction" in reconciliation["nov5_difference"]
    assert "not independent economic confirmation" in reconciliation["independence_warning"]


def test_derivatives_age_and_forecast_gate_remain_fail_closed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    derivatives = artifact["derivatives_freshness"]
    assert derivatives["tradradar_age_at_capture_seconds"] == 4716
    assert derivatives["aperiodic_age_at_capture_seconds"] == 12816
    assert derivatives["new_search_render_is_older_than_archived_observation"] is True
    assert derivatives["admission"] == "no_newer_derivatives_observation_admitted"
    assert artifact["model_eligibility"] == "research_context_only_not_admitted_as_a_point_in_time_model_feature"
    assert artifact["forecast_issued"] is False
    assert artifact["directional_forecast_eligible"] is False
    assert artifact["paper_trade_or_real_money_action"] is False
