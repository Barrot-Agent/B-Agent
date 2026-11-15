from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T184656Z-xrp-market-macro-protocol-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_normalized_source_receipts_reproduce_and_are_not_wire_capture():
    data = load_artifact()
    assert len(data["source_registry"]) == 13
    for source in data["source_registry"]:
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == source["receipt"]["digest"]
        assert source["receipt"]["algorithm"] == "SHA-256"
    assert data["capture_contract"]["original_http_wire_bytes_captured"] is False
    assert data["capture_contract"]["common_point_in_time_cutoff_utc"] is None


def test_market_wide_liquidations_are_not_attributed_to_xrp():
    data = load_artifact()
    row = data["market_context"]["broad_crypto_liquidations"]
    assert row["total_liquidations_at_least_usd"] == 1_270_000_000
    assert row["bullish_liquidations_at_least_usd"] == 1_100_000_000
    assert row["scope"] == "ALL_CRYPTO_NOT_XRP_SPECIFIC"
    okx = data["derivatives"]["okx_xrp_perpetuals_secondary"]
    assert okx["oi_thursday_midday_usd"] == 128_900_000
    assert okx["oi_friday_morning_usd"] == 117_400_000
    assert okx["oi_change_pct"] == -8.9
    assert okx["long_short_account_ratio_friday_morning"] == 3.91
    assert okx["funding_rate_pct_per_8h"] == 0.0024
    assert okx["provider_request_timestamps_exposed"] is False


def test_etf_flow_zeroes_and_cumulative_provider_difference_are_not_averaged():
    row = load_artifact()["etf_flow_reconciliation"]
    tokenpost = row["sosovalue_tokenpost"]
    alpha = row["alpha_finance"]
    assert tokenpost["fund_count"] == alpha["fund_count"] == 5
    assert tokenpost["zero_net_flow_sessions"] == ["2026-11-03", "2026-11-04", "2026-11-05"]
    assert tokenpost["cumulative_net_inflows_usd"] == 1_810_000_000
    assert tokenpost["net_assets_usd"] == 1_410_000_000
    assert alpha["nov5_net_flow_usd"] == 0
    assert alpha["seven_day_net_flow_usd"] == 4_800_000
    assert alpha["thirty_day_flow_usd"] == 60_800_000
    assert alpha["cumulative_net_inflows_usd"] == 1_730_000_000
    assert alpha["net_assets_published"] is False
    assert alpha["holdings_published"] is False
    assert row["reconciliation"]["sosovalue_vs_alpha_cumulative_difference_usd"] == 80_000_000
    assert row["reconciliation"]["aggregation"] == "do_not_average"
    assert row["xrp_insights_holdings"]["nov5_holdings_delta_xrp"] == 110_214
    assert row["xrp_insights_holdings"]["not_ap_cash_flow"] is True
    assert row["reconciliation"]["holdings_delta_vs_ap_flow_comparable"] is False


def test_macro_risk_off_is_mixed_not_a_universal_equity_outflow():
    macro = load_artifact()["macro_event"]["reuters_week_to_nov4"]
    assert macro["money_market_fund_net_inflows_usd"] == 117_970_000_000
    assert macro["equity_fund_net_inflows_usd"] == 14_810_000_000
    assert macro["thursday_nasdaq_change_pct"] == -5.52
    assert macro["thursday_sp500_change_pct"] == -4.36
    assert macro["thursday_dow_change_pct"] == -3.44
    bls = load_artifact()["macro_event"]["bls_october_release"]
    assert bls["release_time_utc"] == "2026-11-06T13:30:00Z"
    assert bls["payroll_change"] == 165_000
    assert bls["unemployment_rate_pct"] == 4.1
    assert bls["august_september_revisions_combined"] == 84_000


def test_fixcleanup_activation_and_paymentburn_scope_are_distinct_from_xrp_supply():
    fix = load_artifact()["protocol_events"]["fixCleanup3_4_0"]
    assert fix["status"] == "ENABLED"
    assert fix["enabled_at_utc"] == "2026-11-04T14:52:00Z"
    assert fix["enabled_ledger"] == 108_112_129
    assert fix["native_xrp_affected"] is False
    assert fix["publicly_confirmed_exploitation"] is False
    assert fix["issuer_specific_exposure"] == "UNKNOWN_NO_ISSUER_LEVEL_PUBLIC_AUDIT_IDENTIFIED"
    assert fix["documentation_lag"]["official_permission_values_page_still_shows_pre_activation_warning"] is True
    release = next(s for s in load_artifact()["source_registry"] if s["source_id"] == "XRPL_OFFICIAL_RELEASE_3_4_0_20260916")
    assert "LendingProtocolV1_1 is a separate amendment" in release["excerpt"]


def test_lending_and_vault_amendments_are_not_mislabeled_as_active():
    lending = load_artifact()["protocol_events"]["lending_and_vault_amendments"]
    assert lending["lending_protocol_v1_1"]["status"] == "VOTING"
    assert lending["lending_protocol_v1_1"]["yes_validators"] == 21
    assert lending["lending_protocol_v1_1"]["total_trusted_validators"] == 35
    assert lending["lending_protocol_v1_1"]["support_pct"] == 60.0
    assert lending["lending_protocol_v1_1"]["required_yes_votes"] == 29
    assert lending["single_asset_vault"]["status"] == "VOTING"
    assert lending["production_lending_or_collateral_activation_verified"] is False


def test_source_dependency_and_documentation_lag_are_explicit():
    data = load_artifact()
    tracker = [s for s in data["source_registry"] if s["independence_group"] == "xrplwin_ledger_tracker"]
    assert len(tracker) == 3
    coindesk = next(s for s in data["source_registry"] if s["source_id"] == "COINDESK_PAYMENTBURN_FIX_20261105T0525Z")
    assert "XRPLWin amendment tracker" in coindesk["upstream_dependencies"]
    assert "stale relative to the tracker-recorded nov 4 activation" in data["protocol_events"]["fixCleanup3_4_0"]["documentation_lag"]["interpretation"].lower()


def test_competing_hypotheses_retain_counterevidence_and_no_forecast_is_issued():
    data = load_artifact()
    ids = {h["hypothesis_id"] for h in data["competing_hypotheses"]}
    assert {"H1_BROAD_RISK_OFF", "H2_XRP_LEVERAGE_UNWIND", "H3_ETF_MARGINAL_BID_PAUSE", "H4_PROTOCOL_RISK_NOT_NATIVE_XRP_SUPPLY", "H5_XRPL_LENDING_NOT_YET_LIVE", "H6_SELECTIVE_ROTATION_COUNTER_HYPOTHESIS"} <= ids
    assert all(h["counter_evidence"] for h in data["competing_hypotheses"])
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["directional_forecast_issued"] is False


def test_no_paper_trade_real_money_deployment_or_external_submission():
    safety = load_artifact()["safety"]
    assert safety["paper_trade_executed"] is False
    assert safety["real_money_action"] is False
    assert safety["external_submission"] is False
    assert safety["external_ai_data_transfer"] is False
    assert safety["deployment"] is False


def test_prior_artifact_sources_keep_their_original_retrieval_vintage() -> None:
    sources = {s["source_id"]: s for s in load_artifact()["source_registry"]}
    for source_id in (
        "PREVIOUS_XRP_INSIGHTS_HOLDINGS_DELTA_20261106",
        "BLS_OCTOBER_EMPLOYMENT_20261106T1330Z",
    ):
        assert sources[source_id]["retrieval_time_upper_bound_utc"] == "2026-11-06T18:10:24Z"
        assert sources[source_id]["capture_method"] == "reused_prior_artifact"
