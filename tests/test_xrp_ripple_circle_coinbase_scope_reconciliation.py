from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261101T230122Z-ripple-circle-and-coinbase-collateral-scope-correction.json"
LEDGER = ROOT / "data/xrp_intelligence/research_ledger_addenda/20261101T230122Z-ripple-circle-coinbase-sbic-ask-collateral-reconciliation.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_direct_ripple_circle_product_partnership_supersedes_old_non_edge():
    d = load(GRAPH)
    prior = d["supersedes"][0]
    assert prior["prior_non_edge"]["status"] == "NO_DIRECT_PARTNERSHIP_ESTABLISHED"
    edge = next(e for e in d["edges"] if e["from"] == "RIPPLE" and e["to"] == "CIRCLE")
    assert edge["status"] == "CONFIRMED"
    assert edge["type"] == "direct_product_integration_partnership"
    assert edge["date"] == "2025-06-12"
    assert "not an equity relationship" in edge["limits"][0]


def test_coinbase_collateral_products_are_separated_by_customer_and_region():
    d = load(GRAPH)
    non_us = next(e for e in d["edges"] if e["to"] == "COINBASE_ADVANCED_GLOBAL_NON_US" and e["from"] == "XRP" and e["type"] == "cross_collateral_for_cross_margined_derivatives")
    assert non_us["terms"]["standard_margin_haircut_pct"] == 15
    assert non_us["terms"]["portfolio_margin_haircut"] == "DASH_NOT_INTERPRETED_AS_ZERO"
    us_prime = next(e for e in d["edges"] if e["to"] == "XRP" and e["from"] == "COINBASE_PRIME_GLOBAL_US")
    assert us_prime["status"] == "NOT_IN_CURRENT_PUBLIC_ELIGIBLE_LIST"
    us_cash = next(e for e in d["edges"] if e["from"] == "COINBASE_US_DERIVATIVES" and e["to"] == "XRP")
    assert us_cash["status"] == "NOT_IN_CURRENT_PUBLIC_ELIGIBLE_LIST"


def test_cftc_26_17_is_pathway_not_proof_of_xrp_product_use():
    d = load(LEDGER)
    c = next(x for x in d["material_corrections"] if x["id"] == "CORR_CFTC_26_17")
    assert c["classification"] == "LEGAL_PATHWAY_CONFIRMED_ACTUAL_XRP_USE_UNVERIFIED"
    assert any("120% cap is the Regulation 30.7(c) limit" in x for x in c["clarifications"])
    assert any("not one of the numbered no-action conditions" in x for x in c["clarifications"])


def test_circle_agent_metrics_are_not_merged_or_mislabeled_arc_specific():
    d = load(LEDGER)["circle_arc_metric_quality"]
    assert d["arc_launch_release_agent_volume_usdc_pct"] == 98.8
    assert d["agent_stack_page_x402_transaction_value_usdc_pct"] == 99.8
    assert d["agents_circle_october_2026_agent_transaction_volume_x402_usdc_pct"] == 99.6
    assert d["feature_admission"] == "BLOCKED_FROM_SINGLE_COMBINED_SERIES"


def test_sbic_and_permission_ask_are_not_conflated_with_xrp():
    d = load(LEDGER)["identity_research"]
    assert d["sbic"]["resolved_identity"].startswith("Tokyo Small and Medium Business")
    assert d["sbic"]["xrp_or_circle_relationship"] == "NOT_ESTABLISHED"
    assert d["ask_coin"]["candidate_identity"] == "Permission Coin (ASK)"
    assert "NO_XRPL_CONTRACT_LISTED" in d["ask_coin"]["xrp_relationship"]


def test_no_unverified_xrp_forecast_is_issued():
    d = load(LEDGER)["prediction"]
    assert d["status"] == "NOT_ISSUED"
    assert d["verified_xrp_forecasts"] == 0
    assert d["calibration"] == "NOT_ESTIMABLE"
    assert d["real_money"] == "NOT_AUTHORIZED"
