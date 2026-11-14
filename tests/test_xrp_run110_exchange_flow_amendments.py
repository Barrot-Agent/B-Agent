from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261110T020036Z-run110-exchange-flow-xrpl-amendment-etf-reconciliation.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run110_exchange_wallet_totals_are_not_tradable_float_or_corporate_holdings():
    data = load_artifact()
    exchange = data["exchange_balances"]
    assert exchange["total_xrp"] == 22_350_000_000
    assert exchange["wallets"] == 701
    assert exchange["exchanges"] == 24
    assert exchange["same_wallet_7d_xrp"] == -25_800_000
    assert exchange["same_wallet_30d_xrp"] == -138_100_000
    assert exchange["tradable_float"] is False
    assert exchange["model_eligible"] is False
    assert exchange["wrapped_reserves_xrp"] == 483_000_000
    assert exchange["cold_labeled_pct"] == 48.4
    assert exchange["unlabeled_hot_cold_pct"] == 40.0
    assert exchange["unresolved_internal_difference_xrp"] == 1_600_000
    venues = {item["name"]: item for item in exchange["venues"]}
    assert venues["Coinbase"]["balance_xrp"] == 5_800_000_000
    assert venues["SBI VC Trade"]["balance_xrp"] == 56_800_000
    assert venues["SBI VC Trade"]["change_7d_xrp"] == -3_200_000
    assert exchange["sbi_holdings_treasury_attribution"] is False


def test_run110_gross_binance_whale_inflow_is_not_netflow_or_proven_sales():
    data = load_artifact()
    whale = data["binance_whale_inflow"]
    incident = data["binance_incident"]
    assert whale["gross_whale_inflow_xrp"] == 691_000_000
    assert whale["netflow"] is False
    assert whale["sale_confirmed"] is False
    assert whale["event_cutoff_utc"] is None
    assert whale["model_eligible"] is False
    assert incident["xrp_stolen_xrp"] == 233_460_000
    assert incident["replenished_affected_assets_pct_by_2026_10_31"] == 98
    reconciliation = data["exchange_flow_reconciliation"]
    assert reconciliation["direct_comparison_valid"] is False
    assert reconciliation["averaged"] is False
    assert len(reconciliation["competing_hypotheses"]) == 3
    assert reconciliation["no_directional_conclusion"] is True


def test_run110_xrpl_amendments_remain_below_activation_threshold():
    data = load_artifact()["xrpl"]
    assert data["validators_heard"] == 35
    assert data["yes_required"] == 29
    assert data["enabled"] == 98
    assert data["in_flight"] == 9
    assert data["countdown"] == 0
    assert data["votes"]["LendingProtocol"] == 22
    assert data["votes"]["ConfidentialTransfer"] == 21
    assert data["lending_active"] is False
    assert data["confidential_transfer_active"] is False
    assert "more than 80%" in data["activation_rule"].lower()


def test_run110_etf_flow_scopes_and_sunday_anomaly_are_preserved():
    data = load_artifact()["etf"]["sources"]
    sources = {item["name"]: item for item in data}
    assert sources["XRP Insights"]["daily_flow_xrp"] == -663_043
    assert sources["XRP Insights"]["week_flow_xrp"] == -812_500
    assert sources["ByKaranteli"]["five_day_flow_usd"] == -530_000
    assert sources["Alpha Finance"]["latest_row_is_sunday"] is True
    assert sources["Alpha Finance"]["latest_row_flow_usd"] == 0
    assert sources["Alpha Finance"]["thirty_sessions_usd"] == 23_300_000
    assert load_artifact()["etf"]["averaging"] is False


def test_run110_excerpt_hashes_are_not_misrepresented_as_raw_http_receipts():
    data = load_artifact()
    assert data["provenance"]["raw_http_transport_bytes_preserved"] is False
    assert "normalized excerpt" in data["provenance"]["excerpt_hash_scope"]
    for key, item in [
        ("exchange", data["exchange_balances"]),
        ("whale", data["binance_whale_inflow"]),
        ("binance", data["binance_incident"]),
        ("xrpl", data["xrpl"]),
    ]:
        assert hashlib.sha256(item["excerpt"].encode("utf-8")).hexdigest() == item["excerpt_sha256"]
    for item in data["etf"]["sources"]:
        assert hashlib.sha256(item["excerpt"].encode("utf-8")).hexdigest() == item["excerpt_sha256"]


def test_run110_feature_taxonomy_and_forecast_gate_remain_separate():
    data = load_artifact()
    assert len(data["feature_taxonomy"]) == len(set(data["feature_taxonomy"]))
    assert "gross_whale_exchange_inflow_xrp" in data["feature_taxonomy"]
    assert "same_wallet_net_exchange_balance_change_xrp" in data["feature_taxonomy"]
    assert "wrapped_asset_reserve_xrp" in data["feature_taxonomy"]
    assert "etf_trading_volume_usd" in data["feature_taxonomy"]
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["no_directional_forecast"] is True
