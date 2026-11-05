import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T050700Z-primary-xrp-etf-holdings-and-custody-reconciliation.json"


def test_primary_issuer_holdings_keep_direct_xrp_and_indirect_etp_units_separate():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    funds = data["fund_observations"]
    assert funds["bitwise_xrp"]["direct_xrp_units"] == 415365129.04
    assert funds["grayscale_gxrp"]["direct_xrp_units"] == 64839534.7913
    assert funds["rex_osprey_xrpr"]["direct_xrp_units"] == 19885382
    assert funds["rex_osprey_xrpr"]["indirect_coinshares_xrp_etp_shares"] == 362750
    assert data["cross_fund_reconciliation"]["direct_xrp_units_subtotal"] == 500090045.8313
    assert data["cross_fund_reconciliation"]["indirect_etp_shares_added_to_xrp_units"] is False
    assert data["cross_fund_reconciliation"]["net_flow_inference"] == "PROHIBITED"


def test_custody_roles_are_fund_specific_and_not_execution_claims():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    relationships = data["custody_relationships"]
    roles = {(item["fund"], item["entity"]): item["role"] for item in relationships}
    assert roles[("Bitwise XRP", "Coinbase Custody Trust Co., LLC")] == "digital_asset_custodian"
    assert roles[("Bitwise XRP", "The Bank of New York Mellon")] == "trust_custodian"
    assert roles[("Grayscale GXRP", "Coinbase Custody Trust Company, LLC")] == "digital_asset_custodian"
    assert roles[("Grayscale GXRP", "Anchorage Digital Bank N.A.")] == "additional_digital_asset_custodian"
    assert roles[("Grayscale GXRP", "BNY")] == "fund_administrator"
    assert all(item.get("execution_relationship") != "established" for item in relationships)


def test_primary_issuer_artifact_is_model_ineligible_and_preserves_vintages():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sources = data["source_registry"]
    assert len(sources) == 3
    assert len({item["independence_group"] for item in sources}) == 3
    assert all(item["raw_content_sha256"] is None for item in sources)
    assert all(item["model_eligible"] is False for item in sources)
    assert {item["source_data_as_of_date"] for item in sources} == {"2026-11-03", "2026-11-04"}
    assert data["cross_fund_reconciliation"]["status"] == "ASYNCHRONOUS_CROSS_SECTIONAL_SUBTOTAL"
    assert data["source_capture_policy"]["exact_primary_page_bytes_captured"] is False
    assert data["forecast_issued"] is False
    assert data["paper_trade_executed"] is False
    assert data["mission_priority"] == 1
