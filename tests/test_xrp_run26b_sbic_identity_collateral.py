import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261111T140301Z-run26b-sbic-identity-chatgpt-and-sbi-collateral-primary-source-addendum.json"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sbic_act_names_three_regional_companies_separate_from_sbi_holdings() -> None:
    data = _load()
    companies = data["identity_resolution"]["sbic_japan"]["companies"]
    assert {item["id"] for item in companies} == {
        "SBIC East Japan", "SBIC Central Japan", "SBIC West Japan"
    }
    assert len({item["legal_name"] for item in companies}) == 3
    assert all(item["founded"].startswith("1963-11-") for item in companies)
    sbi = data["identity_resolution"]["sbi_holdings"]
    assert sbi["legal_name"] == "SBI Holdings, Inc."
    assert sbi["established"] == "1999-07-08"
    assert "SBI Holdings" not in {item["legal_name"] for item in companies}
    assert "do not establish a parent/subsidiary relationship" in data[
        "identity_resolution"
    ]["sbic_japan"]["ownership_boundary"]


def test_sbi_vc_trade_is_sbi_group_owned_not_an_sbic_regional_company() -> None:
    data = _load()
    vc = data["identity_resolution"]["sbi_vc_trade"]
    assert vc["shareholder"] == "SBI Group"
    assert vc["shareholder_percentage"] == 100
    assert "consolidated subsidiary" in vc["parent_status"]
    assert "not one of the three regional SBIC companies" in vc["distinction"]


def test_sbi_vc_trade_xrp_access_and_collateral_factors_are_scoped() -> None:
    data = _load()
    product = data["sbi_vc_trade_xrp_and_collateral"]["product_status"]
    assert product["xrp_spot_retail"] == "Listed"
    assert product["xrp_spot_exchange"] == "Listed"
    assert product["xrp_leverage"] == "Listed"
    assert product["rlusd_current_network"] == "Ethereum"
    assert "future" in product["rlusd_xrpl_network"].lower()
    margin = data["sbi_vc_trade_xrp_and_collateral"]["margin_and_collateral"]
    assert margin["crypto_asset_valuation_factor_pct"] == 50
    assert margin["electronic_payment_instrument_valuation_factor_pct"] == 100
    assert margin["rlusd_specific_collateral_eligibility"] == "NOT_INDEPENDENTLY_CONFIRMED"


def test_sbic_chatgpt_references_are_educational_or_investee_not_partnership() -> None:
    data = _load()
    refs = data["sbic_chatgpt_references"]
    assert refs["east_japan_training"]["status"] == "COMPLETED_EDUCATIONAL_TRAINING"
    assert "ChatGPT usage" in refs["east_japan_training"]["content_includes"]
    assert refs["west_japan_seminar"]["status"] == "COMPLETED_EDUCATIONAL_SEMINAR"
    assert "not an SBIC product" in refs["investee_company_example"]["relation_to_sbic"]
    assert "No OpenAI-SBIC commercial partnership" in refs["conclusion"]


def test_sbic_addendum_preserves_primary_source_lineage_and_blocks_forecasts() -> None:
    data = _load()
    ids = [item["id"] for item in data["source_registry"]]
    assert len(ids) == len(set(ids))
    known = set(ids)
    for node in data["identity_graph"]["nodes"]:
        assert set(node["evidence"]) <= known
    for edge in data["identity_graph"]["edges"]:
        assert set(edge["evidence"]) <= known
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"
    assert data["model_eligibility"]["status"] == "EXCLUDED"
    assert data["model_eligibility"]["raw_receipts_created"] is False
    assert data["safety"]["no_real_money"] is True
