import json
from pathlib import Path


ARTIFACT = Path(
    "research/xrp_intelligence/"
    "20261105T212200Z-institutional-network-reconciliation-q3-2026.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_institutional_relationship_graph_keeps_direct_and_shared_edges_distinct():
    data = _load()
    edges = {edge["id"]: edge for edge in data["direct_relationships"]}

    assert edges["RIPPLE_COINBASE_RLUSD"]["from"] == "Ripple"
    assert edges["RIPPLE_COINBASE_RLUSD"]["to"] == "Coinbase"
    assert edges["BNY_CIRCLE_USDC"]["from"] == "BNY"
    assert edges["BNY_RIPPLE_RLUSD_XRP"]["to"] == "Ripple"
    assert "CIRCLE_RIPPLE" not in edges
    assert data["relationship_interpretation"]["direct_circle_ripple_partnership_established"] is False
    assert data["shared_provider_relationships"][0]["provider"] == "BNY"


def test_sbi_ripple_and_sbi_circle_are_separate_nonexclusive_relationships():
    data = _load()
    edges = {edge["id"]: edge for edge in data["direct_relationships"]}

    assert edges["SBI_RIPPLE"]["to"] == "Ripple"
    assert edges["SBI_CIRCLE_MOU"]["to"] == "Circle"
    assert edges["SBI_CIRCLE_JV"]["to"] == "SBI_Circle_Holdings"
    assert edges["SBI_VCTRADE_RIPPLE_RLUSD"]["to"] == "Ripple"
    assert edges["RIPPLE_STANDARD_CUSTODY_RLUSD_ISSUER"]["to"] == "Standard_Custody_Trust_Company"
    assert edges["SBI_CIRCLE_EQUITY"]["amount_usd"] == 50_000_000
    assert edges["SBI_CIRCLE_EQUITY"]["cash_to_issuer_confirmed"] is None
    assert data["relationship_interpretation"]["sbi_strategy"].startswith("SBI Holdings has distinct direct relationships")


def test_japan_rlusd_service_chain_limits_and_operational_controls_are_preserved():
    data = _load()
    fact = next(x for x in data["facts"] if x["id"] == "SBI_RLUSD_JAPAN")

    assert data["chain_and_product_scope"]["RLUSD"]["sbi_vctrade_chains_at_launch"] == ["Ethereum"]
    assert data["chain_and_product_scope"]["RLUSD"]["coinbase_supported_at_launch"] == ["XRPL", "Ethereum", "Base"]
    assert any("redemption capacity" in x for x in fact["limitations"])
    assert any("BITPOINT" in x for x in fact["limitations"])


def test_coinbase_collateral_disclosure_does_not_invent_xrp_specific_balances():
    data = _load()
    fact = next(x for x in data["facts"] if x["id"] == "COINBASE_COLLATERAL")

    assert "No XRP-specific collateral amount is separately disclosed." in fact["limitations"]
    assert data["chain_and_product_scope"]["XRP"]["coinbase_xrp_collateral_amount_disclosed"] is None
    assert data["prediction_implications"]["missing_features_must_remain_null"] is True


def test_capital_ledger_separates_circle_capital_from_xrp_flows():
    data = _load()
    entries = data["capital_ledger"]

    assert any(x["to"] == "Circle" and x["amount_usd"] == 50_000_000 and x["xrp_related"] is False for x in entries)
    assert any(x["to"] == "Circle" and x["amount_usd"] == 100_000_000 and x["xrp_related"] is False for x in entries)
    assert all(x.get("xrp_related") is False for x in entries)
    assert data["model_admission"]["xrp_spot_flow_observed_usd"] is None


def test_company_claims_and_regulatory_status_are_not_misrepresented_as_operational_xrp_flows():
    data = _load()
    ripple_bank = next(x for x in data["facts"] if x["id"] == "RIPPLE_NATIONAL_TRUST_BANK")
    circle = next(x for x in data["facts"] if x["id"] == "CIRCLE_Q3_2026")

    assert "opening and commencement of services not independently established" in data["entities"]["Ripple_National_Trust_Bank"]["operational_status"]
    assert any("continues to be issued by Standard Custody" in x for x in ripple_bank["limitations"])
    assert any("annualized, not realized quarterly volume" in x for x in circle["limitations"])
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["directional_forecast_issued"] is False


def test_sources_have_dates_and_are_not_claimed_as_byte_complete_receipts():
    data = _load()
    assert data["exact_retrieval_timestamp_utc"] is None
    assert data["sources"]
    assert all(source["date"] and source["url"] for source in data["sources"])
    assert all(source["raw_bytes_captured"] is False for source in data["sources"])
    source_ids = {source["id"] for source in data["sources"]}
    assert all(set(fact["source_ids"]).issubset(source_ids) for fact in data["facts"])
    assert next(x for x in data["sources"] if x["id"] == "SBI_CIRCLE_JV_20250822")["url"].endswith("0822_15679.html")
    assert {"SBI_USDC_REGISTRATION_20250304", "SBI_USDC_BETA_20250312", "SBI_USDC_PUBLIC_20250325"}.issubset(source_ids)
