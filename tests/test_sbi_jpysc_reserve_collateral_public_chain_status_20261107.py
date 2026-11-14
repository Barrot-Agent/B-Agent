import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107-sbi-jpysc-reserve-collateral-public-chain-status-reconciliation.json"
)


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_jpysc_issuer_operator_and_technology_partner_are_distinct():
    data = load()
    roles = data["sources"][0]["claims"]
    assert roles["issuer"] == "SBI Shinsei Trust Bank"
    assert roles["issuance_commissioner_and_distribution_operator"] == "SBI VC Trade Co., Ltd."
    assert roles["technology_partner"] == "Startale Group Pte. Ltd."
    assert roles["initial_access"] == "VCTRADE account-internal use only at launch"


def test_short_term_jgb_allocation_is_not_the_legal_maximum():
    data = load()
    claims = data["sources"][1]["claims"]
    assert claims["actual_short_term_jgb_allocation_jpy"] == 1_000_000_000
    assert claims["reported_jpysc_issuance_balance_jpy_approx"] == 20_100_000_000
    assert claims["maximum_allocation_pct_of_issuance"] == 50
    assert claims["maximum_eligible_government_security_maturity_days"] == 90
    assert round(claims["calculated_jgb_allocation_pct_of_reported_issuance"], 3) == 4.975
    assert claims["calculated_jgb_allocation_pct_of_reported_issuance"] < claims["maximum_allocation_pct_of_issuance"]


def test_september_lending_applications_are_not_relabelled_as_outstanding_balance():
    claims = load()["sources"][1]["claims"]
    assert claims["reported_lending_applications_jpy_approx"] == 6_900_000_000
    assert "APPLICATIONS_NOT_VERIFIED_OUTSTANDING" in claims["lending_applications_classification"]


def test_november_handled_balance_definition_is_preserved():
    claims = load()["sources"][2]["claims"]
    assert claims["jpysc_lending_balance_jpy"] == "greater_than_10000000000"
    assert claims["jpysc_handled_balance_jpy"] == "greater_than_30000000000"
    assert claims["handled_balance_definition"] == "On-chain balance plus lending balance"
    assert claims["handled_balance_is_market_cap"] is False


def test_public_chain_distribution_is_not_claimed_as_live():
    data = load()
    launch = data["sources"][0]["claims"]
    november = data["sources"][2]["claims"]
    assert launch["external_wallet_withdrawal"] == "Disabled at launch"
    assert november["public_chain_status"].startswith("Public-chain conversion remains a future step")
    assert data["reconciled_interpretation"][4].startswith("The June 24 launch was limited")
    assert data["model_admission"]["admitted_as_xrp_demand"] is False


def test_sbi_ripple_asia_xrpl_poc_is_separate_from_jpysc():
    claims = load()["sources"][3]["claims"]
    assert claims["contemplated_blockchain"] == "XRP Ledger (XRPL)"
    assert claims["status"] == "Conceptual PoC; not evidence of a production JPYSC deployment on XRPL"
    assert claims["relationship_to_jpysc"] == "Separate project; the announcement does not identify JPYSC as the token or product"


def test_sbi_primary_releases_are_not_counted_as_independent_publishers():
    data = load()
    assert data["source_independence"]["group"] == "SBI_GROUP_PRIMARY_RELEASES"
    assert data["source_independence"]["status"].startswith("Multiple first-party releases")
    assert data["receipt_limits"]["raw_full_page_bytes_retained"] is False


def test_jpysc_evidence_is_event_context_not_an_xrp_price_feature_or_forecast():
    data = load()
    assert data["model_admission"]["event_timeline_only"] is True
    assert data["model_admission"]["admitted_to_xrp_price_features"] is False
    assert data["model_admission"]["admitted_to_xrp_exchange_flow_features"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast_made"] is False
