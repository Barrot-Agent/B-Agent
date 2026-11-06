from __future__ import annotations

import json
import re
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T070228Z-runstart-xrp-etf-issuer-custody-primary-update.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_primary_issuer_observations_keep_distinct_fund_dates():
    data = load_artifact()
    funds = data["fund_observations"]
    assert funds["bitwise_xrp"]["holdings_as_of_date"] == "2026-11-04"
    assert funds["franklin_xrpz"]["holdings_as_of_date"] == "2026-11-04"
    assert funds["canary_xrpc"]["holdings_as_of_date"] == "2026-11-06"
    assert funds["canary_xrpc"]["trust_details_as_of_date"] == "2026-11-04"
    assert data["reconciliation"]["cross_fund_total_calculated"] is False


def test_bitwise_custody_roles_are_separated():
    item = load_artifact()["fund_observations"]["bitwise_xrp"]
    assert item["digital_asset_custodian"] == "Coinbase Custody Trust Co., LLC"
    assert item["trust_custodian"] == "The Bank of New York Mellon"
    assert item["administrator"] == "Bank of New York Mellon"
    assert item["holdings_as_of_date"] != item["nav_market_price_as_of_date"]


def test_franklin_xrpz_custodian_and_holdings_are_issuer_attributed():
    item = load_artifact()["fund_observations"]["franklin_xrpz"]
    assert item["direct_xrp_units"] == 310430333.34
    assert item["total_net_assets_usd"] == 403940000
    assert item["shares_outstanding"] == 28600000
    assert item["custodian"] == "Coinbase Custody Trust Company, LLC"


def test_canary_xrpc_roles_and_mixed_vintages_are_preserved():
    item = load_artifact()["fund_observations"]["canary_xrpc"]
    assert item["holdings_as_of_date"] == "2026-11-06"
    assert item["direct_xrp_units"] == 243714802.03
    assert item["holdings_table_net_assets_usd"] == 301805823
    assert item["trust_details_summary_net_assets_usd"] == 317162340.48
    assert item["digital_asset_custodians"] == ["BitGo Bank & Trust, N.A.", "Gemini Trust Company LLC"]
    assert item["cash_custodian"] == "U.S. Bank National Association"
    assert item["administrator"] == "U.S. Bank Global Fund Services"
    assert item["difference_disposition"] == "PRESERVED_UNEXPLAINED_NOT_RECONCILED_BY_ASSUMPTION"


def test_canary_market_value_and_net_assets_difference_is_not_hidden():
    item = load_artifact()["fund_observations"]["canary_xrpc"]
    assert item["market_value_minus_holdings_table_net_assets_usd"] == -4035.06
    assert item["cash_and_other_usd"] == -103.14
    assert item["market_value_minus_holdings_table_net_assets_usd"] != item["cash_and_other_usd"]


def test_custody_edges_do_not_infer_execution_or_ownership():
    data = load_artifact()
    edges = data["custody_relationship_edges"]
    assert any(e["fund"] == "Franklin XRP ETF (XRPZ)" and e["provider"] == "Coinbase Custody Trust Company, LLC" and e["role"] == "custodian" for e in edges)
    assert any(e["fund"] == "Canary XRP ETF (XRPC)" and e["provider"] == "BitGo Bank & Trust, N.A." and e["role"] == "digital_asset_custodian" for e in edges)
    assert any(e["fund"] == "Canary XRP ETF (XRPC)" and e["provider"] == "Gemini Trust Company LLC" and e["role"] == "digital_asset_custodian" for e in edges)
    assert any(e["fund"] == "Canary XRP ETF (XRPC)" and e["provider"] == "U.S. Bank National Association" and e["role"] == "cash_custodian" for e in edges)
    assert "not evidence of ownership, execution venue" in data["reconciliation"]["custody_conclusion"]


def test_rendered_excerpt_hashes_are_not_misrepresented_as_raw_http_hashes():
    data = load_artifact()
    assert data["capture"]["raw_http_wire_bytes_captured"] is False
    for source in data["source_registry"][:3]:
        assert re.fullmatch(r"[0-9a-f]{64}", source["rendered_excerpt_sha256"])
        assert source["raw_http_wire_bytes_captured"] is False
    assert data["capture"]["exact_per_source_retrieval_timestamp_utc"] is None


def test_holdings_are_not_cash_flow_and_are_model_ineligible():
    data = load_artifact()
    assert data["reconciliation"]["flow_inference"] == "PROHIBITED"
    assert data["reconciliation"]["spot_purchase_inference"] == "PROHIBITED"
    assert data["reconciliation"]["actual_capital_status"] == "NOT_ESTABLISHED_BY_HOLDINGS_SNAPSHOTS"
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["issued"] is False
