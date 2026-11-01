from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/xrp_intelligence/snapshots/20261101T220304Z-xrp-coinbase-circle-arc-rlusd-market.json"

def load_snapshot():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))

def test_xrp_snapshot_does_not_issue_unvalidated_forecast():
    data = load_snapshot()
    assert data["prediction"]["status"] == "NOT_ISSUED"
    assert data["prediction"]["probability"] is None
    assert data["prediction"]["paper_trading"] == "NOT_STARTED"

def test_derivatives_providers_keep_distinct_universes():
    d = load_snapshot()["market"]["derivatives"]
    assert d["tradradar"]["scope"] == "seven-exchange aggregate"
    assert d["seandra_binance_usdt_perpetual"]["scope"] == "Binance USDT perpetual only"
    assert d["comparability"] == "DO_NOT_AVERAGE_DIFFERENT_VENUE_UNIVERSES_OR_CONTRACT_DEFINITIONS"

def test_rlusd_supply_disagreement_blocks_feature_admission():
    s = load_snapshot()["stablecoins"]["rlusd_chain_split"]
    assert s["xrp_insights"]["xrpl_usd"] == 707_400_000
    assert s["xrpl_utilities"]["xrpl_outstanding_usd"] == 910_300_000
    assert s["reconciliation"]["status"] == "UNRESOLVED_DEFINITION_OR_TIME_CUTOFF"
    assert s["feature_admission"] == "BLOCKED_UNTIL_RECONCILED"

def test_x402_overlap_is_not_misrepresented_as_same_transaction_identity():
    a = load_snapshot()["agentic_payments"]["address_overlap"]
    assert a["status"] == "CONFIRMED_DESTINATION_ADDRESS_OVERLAP"
    assert a["transaction_identity_status"] == "UNVERIFIED"
    assert "SourceTag" in a["required_join"][2]

def test_coinbase_global_exchange_collateral_is_future_not_live():
    p = load_snapshot()["institutional_relationships"]["coinbase"]["ripple_rlusd_partnership"]
    assert p["global_exchange_collateral"] == "FUTURE_ANNOUNCED_NOT_LIVE"

def test_circle_agent_share_is_global_not_arc_specific():
    data = load_snapshot()
    global_metric = data["stablecoins"]["circle_agent_stack"]
    arc = data["stablecoins"]["arc_usdc"]
    assert global_metric["agent_driven_transaction_volume_usdc_pct"] == 98.8
    assert global_metric["scope"] == "GLOBAL_AGENT_STACK_X402_NOT_ARC_SPECIFIC"
    assert global_metric["evidence"] == "COMPANY_REPORTED"
    assert "agent_driven_transaction_volume_usdc_pct" not in arc

def test_ambiguous_etf_and_escrow_data_are_not_silently_merged():
    d = load_snapshot()
    assert d["market"]["etf_flows"]["reconciliation_status"] == "UNRESOLVED_COVERAGE_OR_METHODOLOGY_DIFFERENCE"
    flags = {x["id"]: x for x in d["data_quality_flags"]}
    assert flags["DQ3"]["feature_admission"] == "BLOCKED"
    assert flags["DQ5"]["feature_admission"] == "BLOCKED_FOR_COMBINED_FLOW"
