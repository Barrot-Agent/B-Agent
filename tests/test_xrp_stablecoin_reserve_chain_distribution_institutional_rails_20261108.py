"""Regression checks for the 2026-11-08 stablecoin and institutional-rails reconciliation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T112300Z-stablecoin-reserve-chain-distribution-and-institutional-rails.json"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_stablecoin_and_institutional_excerpt_hashes_match():
    artifact = _load()
    assert len(artifact["sources"]) == 20
    for source in artifact["sources"]:
        assert len(source["excerpt_sha256"]) == 64
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == source["excerpt_sha256"]
        assert source["model_eligible"] is False


def test_rlusd_issuer_balances_are_distinguished_from_latest_linked_attestation():
    metrics = _load()["calculated_metrics"]
    issuer = metrics["rlusd_issuer_dashboard_nov5"]
    attested = metrics["rlusd_latest_linked_attestation_aug31"]
    assert issuer["circulation_usd_millions"] == 2632.9
    assert issuer["reserve_funds_usd_millions"] == 2748.0
    assert issuer["reserve_coverage_pct"] > 104
    assert attested["outstanding_units"] == 2325969308
    assert attested["reserve_market_value_usd"] == 2446312864
    assert attested["report_dates"] == ["2026-08-17", "2026-08-31"]


def test_rlusd_cross_chain_supply_discrepancy_is_not_reconciled_or_averaged():
    artifact = _load()
    metrics = artifact["calculated_metrics"]["rlusd_cross_chain_dashboard_vs_issuer_nov5"]
    assert metrics["difference_usd_millions"] == 47.1
    assert metrics["reconciliation_status"] == "UNRESOLVED"
    assert artifact["unresolved_reconciliations"][0]["id"] == "rlusd_issuer_vs_cross_chain_dashboard"
    assert "Do not average" not in artifact["unresolved_reconciliations"][0]["decision"] if "decision" in artifact["unresolved_reconciliations"][0] else True


def test_rlusd_signed_snapshot_is_not_marked_cryptographically_verified():
    item = _load()["unresolved_reconciliations"][2]
    assert item["id"] == "rlusd_signed_snapshot"
    assert "not cryptographically verified" in item["issue"]


def test_coinbase_and_circle_financial_measures_are_not_netted():
    metrics = _load()["calculated_metrics"]
    coinbase = metrics["coinbase_q3_2026"]
    deck = metrics["coinbase_q3_earnings_deck"]
    circle = metrics["circle_q3_2026"]
    assert coinbase["stablecoin_revenue_usd_millions"] == 306.905
    assert deck["combined_stablecoin_and_corporate_balance_revenue_usd_millions"] == 328.0
    assert circle["distribution_costs_to_coinbase_q3_usd_millions"] == 331.3
    assert coinbase["stablecoin_revenue_usd_millions"] != deck["combined_stablecoin_and_corporate_balance_revenue_usd_millions"]
    assert "not a direct one-for-one comparison" in next(
        x["excerpt"] for x in _load()["sources"] if x["source_id"] == "circle_q3_2026_sec"
    )


def test_sbi_ripple_and_circle_relationships_are_dated_and_distinct():
    graph = _load()["relationship_graph"]
    ripple_stake = next(x for x in graph if x["from"] == "SBI Holdings" and x["to"] == "Ripple")
    circle = next(x for x in graph if x["from"] == "SBI Holdings and SBI Shinsei Bank" and x["to"] == "Circle")
    assert "June 2025" in ripple_stake["status"]
    assert "$50M" in circle["relationship"]
    assert any(x["from"] == "SBI Remit" and x["to"] == "XRP" for x in graph)


def test_sbi_rlusd_chain_support_is_secondary_corroborated_not_primary_verified():
    item = next(x for x in _load()["sources"] if x["source_id"] == "sbi_rlusd_vctrade_chain_status_20260624")
    assert "official release does not state a supported chain" in item["excerpt"]
    assert "secondary reports" in item["excerpt"]
    edge = next(x for x in _load()["relationship_graph"] if x["from"] == "SBI VC Trade" and x["to"] == "RLUSD")
    assert "secondary-reported Ethereum-only" in edge["status"]
    assert "not verified XRPL distribution" in item["excerpt"]


def test_jpysc_public_chain_status_and_onchain_wording_remain_unresolved():
    artifact = _load()
    metrics = artifact["calculated_metrics"]["sbi_jpysc"]
    assert metrics["nov2_handling_balance_jpy_billions"] == 30.0
    assert metrics["nov2_customer_lending_balance_jpy_billions"] == 10.0
    assert metrics["public_chain_circulation_status"].startswith("NOT_VERIFIED")
    issue = next(x for x in artifact["unresolved_reconciliations"] if x["id"] == "jpysc_onchain_definition")
    assert "unresolved" in issue["decision"]


def test_jpysc_customer_lending_is_not_mislabeled_as_external_credit():
    source = next(x for x in _load()["sources"] if x["source_id"] == "sbi_jpysc_nov2")
    assert "customers lend JPYSC to SBI VC Trade" in source["excerpt"]
    assert "not evidence of ¥10B in loans made to outside borrowers" in source["excerpt"]


def test_open_standard_blackrock_and_smfg_links_are_exploratory_not_live():
    graph = _load()["relationship_graph"]
    for target in ("BlackRock", "Open Standard", "Sumitomo Mitsui Financial Group"):
        edge = next(x for x in graph if x["to"] == target)
        assert "exploratory" in edge["status"] or "not live" in edge["status"] or "not production" in edge["status"]


def test_all_stablecoin_observations_remain_outside_model_and_forecast():
    artifact = _load()
    assert artifact["model_admission"]["all_sources_model_eligible"] is False
    assert artifact["model_admission"]["feature_store_write"] is False
    assert artifact["model_admission"]["directional_forecast_issued"] is False
    assert artifact["model_admission"]["forecast_status"] == "NOT_ISSUED"
