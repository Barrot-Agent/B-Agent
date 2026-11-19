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
    assert "JSON response text" in kraken["raw_sha256_scope"]

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
    assert "future functionality" in coinbase["planned_or_conditional"]
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



def test_run32a_corrects_occ_dates_and_circle_usdc_economics() -> None:
    path = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261119T005505Z-run32a-corrections-ingestion-failure-and-circle-usdc-rail.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    coinbase = data["regulatory_corrections"]["coinbase_national_trust_company"]
    assert coinbase["occ_preliminary_conditional_approval_date"] == "2026-04-02"
    assert coinbase["occ_cas_approved_date"] == "2026-04-02"
    assert coinbase["occ_cas_consummated_effective_date"] == "2026-11-06"
    assert coinbase["coinbase_announcement_date"] == "2026-11-09"
    assert coinbase["separate_final_occ_decision_letter_located"] is False

    ripple = data["regulatory_corrections"]["ripple_national_trust_bank"]
    assert ripple["occ_cas_approved_date"] == "2025-12-12"
    assert ripple["occ_cas_consummated_effective_date"] == "2026-10-26"
    assert ripple["separate_final_occ_decision_letter_located"] is False

    circle = data["circle_q3_2026_primary_financials"]
    assert circle["source_url"].endswith("crcl-20260930.htm")
    assert circle["gross_mint_redeem_flows"]["q3_net_mint_less_redeem_usdc"] == 610_000_000
    assert circle["distribution_economics"]["coinbase_distribution_cost_q3_usd"] == 331_300_000
    assert circle["distribution_economics"]["coinbase_distribution_cost_nine_months_usd"] == 986_600_000
    assert circle["distribution_economics"]["not_50_percent_of_gross_reserve_income"] is True

    dbs = data["new_circle_distribution_rail"]
    assert dbs["relationship_id"] == "dbs_circle_direct_usdc_institutional_access"
    assert "24/7 USD-USDC settlement" in dbs["executed_or_announced"]
    assert dbs["xrp_mentioned"] is False
    assert dbs["ripple_mentioned"] is False

    macro = data["macro_context"]
    assert macro["observations"]["canada"] == "Canadian dollar reached a 19-month low against USD."
    assert "No XRP-specific causal estimate" in macro["interpretation"]


def test_run32a_ingestion_failures_receipt_chain_and_drift_are_qualified() -> None:
    path = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261119T005505Z-run32a-corrections-ingestion-failure-and-circle-usdc-rail.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    ingestion = data["ingestion_diagnostics"]

    assert ingestion["source_failure_breakdown"] == {
        "binance_http_451": 8,
        "bybit_http_403": 5,
        "sec_user_agent_configuration": 6,
        "grayscale_http_429": 1,
        "franklin_xrpz_parser_failure": 1,
    }
    assert ingestion["no_proxy_or_region_bypass"] is True
    assert ingestion["receipt_chain"]["verification_status"] == "PASS"
    assert ingestion["receipt_chain"]["external_anchor"] == "NOT_ANCHORED"
    assert ingestion["quote_basis"]["status"] == "VERIFIED"
    assert ingestion["quote_basis"]["publisher_independence_groups"] == 1
    assert ingestion["drift_report"]["evaluated_feature_count"] == 0
    assert ingestion["drift_report"]["status"] == "INSUFFICIENT_DATA"

    ci = data["full_suite_failure_diagnostics"]
    assert ci["head_sha"] == "bd0f564c122ed4ef8ce3cf4b764f1152e368e250"
    assert ci["passed"] == 4282
    assert ci["failed"] == 4
    assert ci["classification"].startswith("Evidence/test-contract failures")
