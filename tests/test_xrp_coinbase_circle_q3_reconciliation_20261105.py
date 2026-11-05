"""Regression checks for Coinbase/Circle Q3 2026 and actual-capital classification."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T132421Z-coinbase-circle-q3-sec-and-distribution-reconciliation.json"


def test_coinbase_q3_sec_filing_and_circle_relationship_are_primary_sourced():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sources = {item["id"]: item for item in data["source_registry"]}
    assert sources["coinbase_q3_2026_10q"]["accession_number"] == "0001679788-26-000122"
    assert sources["coinbase_q3_2026_10q"]["period_end"] == "2026-09-30"
    assert sources["circle_q3_2026_sec_ex991"]["accession_number"] == "0001876042-26-000309"
    assert sources["binance_circle_100m_equity_five_year_usdc"]["source_independence_group"] == "binance_exchange"
    assert sources["ripple_coinbase_rlusd_distribution"]["source_independence_group"] == "ripple_issuer"


def test_coinbase_balance_share_is_not_new_capital_or_xrp_demand():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    metrics = {item["id"]: item for item in data["financial_observations"]}
    assert metrics["COIN-Q3-AVG-USDC-2026"]["value_usd_billions"] == 22.0
    assert metrics["CIRCLE-Q3-AVG-USDC-2026"]["value_usd_billions"] == 73.3
    assert metrics["COIN-Q3-USDC-AVERAGE-SHARE-2026"]["value_pct"] == 30.0
    assert metrics["COIN-Q3-USDC-AVERAGE-SHARE-2026"]["model_eligible"] is False
    assert data["accounting_and_actual_capital"]["xrp_purchase_or_collateral_evidence_from_these_filings"] is False


def test_coinbase_reclassification_and_circle_arrangement_are_not_misread():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    reclassification = data["accounting_and_actual_capital"]["reclassification"]
    assert reclassification["status"] == "CONFIRMED_IN_COINBASE_10Q"
    assert "no change to its Circle arrangement" in reclassification["detail"]
    assert "recast values" in reclassification["consequence"]


def test_circle_gross_flows_and_annualized_metrics_are_not_actual_capital():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    metrics = {item["id"]: item for item in data["financial_observations"]}
    assert metrics["CIRCLE-Q3-ONCHAIN-VOLUME-2026"]["value_usd_trillions"] == 13.9
    assert metrics["CIRCLE-Q3-MINT-REDEEM-2026"]["minted_usd_billions"] == 104
    assert metrics["CIRCLE-Q3-MINT-REDEEM-2026"]["redeemed_usd_billions"] == 104
    assert metrics["CIRCLE-Q3-CPN-TPV-2026"]["definition"].startswith("Annualized TPV")
    assert metrics["BINANCE-CIRCLE-EQUITY-2026"]["xrp_capital"] is False


def test_no_directional_xrp_forecast_or_model_admission_from_issuer_metrics():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["prediction_status"] == "NOT_ISSUED"
    assert data["forecast_issued"] is False
    assert data["model_eligible"] is False
    assert data["xrp_implications"]["direct_xrp_purchase_or_collateral_evidence"] is False
    assert data["xrp_implications"]["directional_effect"] == "UNRESOLVED_NO_DIRECTIONAL_XRP_EFFECT_ADMITTED"
    assert data["data_quality"]["raw_source_bytes_captured"] is False
    assert data["data_quality"]["raw_content_sha256_available"] is False
