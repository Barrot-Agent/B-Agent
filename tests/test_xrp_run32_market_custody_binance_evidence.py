"""Run 32 XRP evidence-contract checks for market, custody and incident claims."""
from __future__ import annotations

import json
import re
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261119T004611Z-run32-market-custody-binance-institutional-reconciliation.json"
)


def load_artifact() -> dict:
    assert ARTIFACT.is_file(), f"missing Run 32 evidence artifact: {ARTIFACT}"
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run32_market_receipts_preserve_hash_scope_and_quality_flags() -> None:
    data = load_artifact()
    market = data["market_snapshot"]
    kraken = market["kraken_xrpusd"]
    okx = market["okx_xrpusdt"]

    assert kraken["last_trade_usd"] == 0.9645
    assert abs(kraken["spread_bps"] - 0.5182340656) < 1e-8
    assert kraken["raw_wire_bytes_captured"] is False
    assert re.fullmatch(r"[0-9a-f]{64}", kraken["raw_sha256"])
    assert "rendered JSON response text" in kraken["raw_sha256_scope"]

    assert okx["source_event_time_utc"] == "2026-11-19T00:20:49.771Z"
    assert okx["event_age_seconds_at_capture"] > 1000
    assert okx["raw_wire_bytes_captured"] is False
    assert re.fullmatch(r"[0-9a-f]{64}", okx["raw_sha256"])
    assert market["model_eligible"] is False


def test_run32_cross_venue_basis_and_depth_are_not_overstated() -> None:
    data = load_artifact()
    cross = data["market_snapshot"]["cross_venue_reconciliation"]

    assert cross["usd_normalization"] == "REJECTED"
    assert cross["synchronized_level2_depth_captured"] is False
    assert cross["sequence_reconstruction"] is False
    assert cross["directional_conclusion"] == "NONE"


def test_run32_binance_exchange_deposits_are_not_called_sales() -> None:
    data = load_artifact()
    incident = data["binance_security_incident"]

    assert incident["stolen_xrp"] == 233_460_000
    assert incident["onchain_trace"]["stolen_xrp_traced_to_exchange_or_swap_deposit_accounts"] == 216_000_000
    assert incident["onchain_trace"]["sale_proven"] is False
    assert incident["cryptoquant_observation"]["source_of_increase"] == "UNKNOWN"
    assert incident["cryptoquant_observation"]["sale_proven"] is False
    assert incident["court_recovery"]["hearing_date"] == "2026-12-01"


def test_run32_etf_flows_retain_partial_fund_coverage() -> None:
    data = load_artifact()
    flows = data["etf_flow_reconciliation"]

    assert flows["nov17"]["funds_reported"] == 3
    assert flows["nov17"]["funds_expected"] == 4
    assert flows["nov17"]["status"] == "PARTIAL"
    assert flows["nov17"]["net_flow_xrp"] == -3251
    assert flows["nov18"] == "no issuer files available at page update"
    assert flows["fund_holdings"]["xrp"] == 1_071_130_804


def test_run32_institutional_custody_is_not_equated_with_xrp_demand() -> None:
    data = load_artifact()
    relationships = {
        item["relationship_id"]: item
        for item in data["institutional_relationships"]
    }

    bny = relationships["ripple_bny_custody"]
    assert "XRP" in bny["executed"] and "RLUSD" in bny["executed"]
    assert bny["xrp_demand_proven"] is False
    assert "subject to" in bny["planned_or_conditional"]

    coinbase = relationships["ripple_coinbase_rlusd_distribution"]
    assert "will follow" in coinbase["planned_or_conditional"]
    assert coinbase["xrp_demand_proven"] is False

    world_bank = relationships["worldbank_citi_circle_usdc_exploration"]
    assert world_bank["xrp_mentioned"] is False
    assert world_bank["ripple_mentioned"] is False


def test_run32_regulatory_and_forecast_status_remain_qualified() -> None:
    data = load_artifact()
    regulatory = data["regulatory_status"]
    prediction = data["prediction_readiness"]

    assert regulatory["ripple_national_trust_bank"]["operational_opening_verified"] is False
    assert "Consummated/Effective 2026-10-26" in regulatory["ripple_national_trust_bank"]["occ_cas_status"]
    assert regulatory["coinbase_national_trust_company"]["authorized_opening_date"] == "2026-11-09"

    assert prediction["workflow_present_on_integration"] is True
    assert prediction["workflow_present_on_main"] is False
    assert prediction["forecast_status"] == "NOT_ISSUED"
    assert prediction["walk_forward_forecasts"] == 0
    assert prediction["no_directional_forecast"] is True
