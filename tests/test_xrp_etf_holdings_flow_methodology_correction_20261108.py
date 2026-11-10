from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T100358Z-xrp-etf-holdings-flow-methodology-correction.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_xrp_insights_methodology_receipt_hash_matches():
    data = load_artifact()
    receipt = data["source_receipts"][0]
    assert hashlib.sha256(receipt["normalized_excerpt"].encode("utf-8")).hexdigest() == receipt["normalized_excerpt_sha256"]
    assert receipt["normalized_excerpt_sha256"] == "366ee79f862869a016a56ba2df51e0cee3283a9be74efe59a0e76409e3e57e3b"


def test_etf_flow_is_explicitly_a_holdings_delta_proxy_not_verified_redemptions():
    data = load_artifact()
    row = data["semantic_correction"]
    assert row["canonical_feature_name"] == "issuer_reported_xrp_holdings_delta_proxy"
    assert row["do_not_label_as"] == "verified_net_creation_redemption"
    assert "BITW index rebalancing can change its XRP sleeve holdings." in row["non_creation_components_counted_as_flow"]
    assert "Fee accrual paid in XRP can reduce reported holdings." in row["non_creation_components_counted_as_flow"]


def test_gxrp_gap_and_reconstructed_rows_are_not_silently_treated_as_primary():
    data = load_artifact()
    quality = data["data_quality_exceptions"]
    assert quality["gxrp"]["flow_status"] == "excluded"
    assert quality["gxrp"]["access_gap_start"] == "2026-09-02"
    assert quality["gxrp"]["access_gap_end"] == "2026-09-28"
    reconstructed = quality["reconstructed_rows"]
    assert len(reconstructed["date_ranges"]) == 3
    assert "day-by-day allocation remains an estimate" in reconstructed["limitation"]


def test_settlement_availability_and_nav_implied_price_are_preserved():
    data = load_artifact()
    quality = data["data_quality_exceptions"]
    assert "provisional and rewritten" in quality["settlement"]["rule"]
    assert quality["usd_valuation"]["missing_spot_snapshot_range"] == "2025-12-24/2026-04-14"
    assert "NAV-implied values" in quality["usd_valuation"]["limitation"]


def test_cross_publisher_flow_disagreement_is_not_averaged_or_called_independent():
    data = load_artifact()
    cross = data["cross_publisher_reconciliation"]
    assert cross["xrp_insights"]["nov6_flow_xrp"] == -663043
    assert cross["cryptokeyhole"]["nov6_partial_flow_xrp"] == -752048
    assert cross["cryptokeyhole"]["nov6_coverage"] == "3 of 4 daily-readable funds; Franklin XRPZ missing"
    assert cross["alpha_finance"]["nov6_flow_usd"] == 0
    assert cross["reconciliation_status"] == "UNRESOLVED_DIFFERENT_UNIVERSES_AND_CAPTURE_VINTAGES"
    assert "not independent confirmations" in cross["source_independence"]


def test_research_only_and_forecast_abstention_are_enforced():
    data = load_artifact()
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_probability_issued"] is False
    assert data["external_actions"]["paper_trade"] is False
    assert data["licensing"]["commercial_redistribution_of_dataset_requires_written_permission"] is True
