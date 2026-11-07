from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T230526Z-xrp-etf-flow-methodology-disagreement-and-coinbase-custody.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_xrp_etf_flow_reconciliation_preserves_units_vintages_and_methodology() -> None:
    data = _artifact()

    assert data["data_as_of"] == "2026-11-06"
    totals = next(
        source for source in data["sources"]
        if source["source_id"] == "xrp_insights_daily_totals_json"
    )
    values = totals["reported_values"]
    assert values["total_xrp_holdings"] == 1_195_787_657
    assert values["nov_6_net_flow_xrp"] == -663_043
    assert values["nov_5_net_flow_xrp"] == 110_214
    assert values["nov_2_to_nov_6_net_flow_xrp"] == -812_529
    assert values["six_spot_funds_holdings_approx_xrp"] == 1_170_000_000


def test_etf_flow_methodology_does_not_mislabel_holdings_delta_as_issuer_flow() -> None:
    data = _artifact()
    source = next(
        source for source in data["sources"]
        if source["source_id"] == "xrp_insights_daily_flows_json"
    )
    method = source["methodology"]

    assert "BITW" in method["universe"]
    assert any("GXRP" in item for item in method["excluded_flow_series"])
    assert "BITW index rebalancing" in method["non_creation_changes_counted"]
    assert "XRP-denominated fee accruals" in method["non_creation_changes_counted"]
    assert method["reconstructed_periods"]
    assert data["feature_admission"]["model_feature_eligible"] is False


def test_bitwise_primary_custody_edge_is_scoped_to_one_issuer_fund() -> None:
    data = _artifact()
    bitwise = next(
        source for source in data["sources"]
        if source["source_id"] == "bitwise_xrp_etf_issuer_page"
    )
    assert bitwise["data_as_of"] == "2026-11-05"
    assert bitwise["reported_values"]["xrp_in_trust"] == 415_365_129.04
    assert bitwise["relationships"]["digital_asset_custodian"] == "Coinbase Custody Trust Co., LLC"
    assert bitwise["relationships"]["trust_custodian"] == "Bank of New York Mellon"
    edge = next(
        item for item in data["institutional_relationships"]
        if item["predicate"] == "digital_asset_custody_by"
    )
    assert edge["status"] == "PRIMARY_SOURCE_CONFIRMED"
    assert "does not prove Coinbase Exchange purchased the XRP" in edge["scope_limit"]


def test_flow_disagreements_keep_shared_upstream_sources_and_minority_views() -> None:
    data = _artifact()
    assert any(
        item["status"] == "UNRESOLVED_NOT_COMPARABLE"
        for item in data["disagreement_register"]
    )
    assert any(
        "SoSoValue" in item
        for item in data["source_independence"]["sosovalue_group"]
    )
    assert any(
        "not an independent confirmation" in item
        for item in data["source_independence"]["derived_republication_group"]
    )
    assert any("BITW" in item for item in data["counter_hypotheses"])


def test_web_excerpt_hashes_are_not_misrepresented_as_raw_source_hashes() -> None:
    data = _artifact()
    assert data["raw_capture_policy"]["raw_source_sha256"] is None
    assert data["raw_capture_policy"]["no_raw_source_hash_claim"] is True

    for source in data["sources"]:
        excerpt = source["normalized_excerpt_text"]
        digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]
        assert source["raw_source_sha256"] is None
        assert source["raw_capture_status"].startswith("WEB_RENDERED")


def test_etf_reconciliation_never_issues_forecasts_or_trades() -> None:
    data = _artifact()
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["no_paper_trade"] is True
    assert data["no_real_money_action"] is True
