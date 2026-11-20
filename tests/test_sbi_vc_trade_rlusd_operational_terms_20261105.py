import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T145500Z-sbi-vc-trade-rlusd-operational-terms-and-holdings.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sbi_vc_trade_rlusd_terms_and_parent_relationship_are_distinct():
    data = load()
    edges = data["relationship_graph"]["edges"]
    assert any(e["from"] == "SBI Holdings, Inc." and e["to"] == "SBI VC Trade Co., Ltd." and e["type"] == "parent_consolidated_subsidiary" for e in edges)
    assert any(e["from"] == "SBI Holdings, Inc." and e["to"] == "Circle Internet Group, Inc." and e["type"] == "equity_investment" for e in edges)
    assert any(e["from"] == "SBI VC Trade Co., Ltd." and e["to"] == "Standard Custody & Trust Company" and e["type"] == "RLUSD_distribution_listing" for e in edges)
    terms = data["operational_terms"]
    assert terms["listing_start_date"] == "2026-06-24"
    assert terms["transfer_limit_jpy_per_transaction"] == 1_000_000
    assert terms["deposit_over_jpy_per_transaction_delayed"] == 1_000_000
    assert terms["daily_deposit_limit_disclosed"] is False
    assert "unverified" in terms["chain_support"].lower()


def test_rlusd_custody_growth_rank_is_not_an_absolute_capital_flow():
    signal = load()["holdings_signal"]
    assert signal["rank"] == 1
    assert signal["absolute_balance_disclosed"] is False
    assert signal["net_deposits_disclosed"] is False
    assert signal["net_purchases_disclosed"] is False
    assert signal["xrp_conversion_volume_disclosed"] is False


def test_sbi_rlusd_relationship_is_not_misclassified_as_xrp_demand_or_circle_ripple_deal():
    data = load()
    not_established = data["relationship_graph"]["not_established"]
    assert "Direct Circle-Ripple commercial agreement." in not_established
    assert "SBI VC Trade XRP purchases attributable to RLUSD distribution." in not_established
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["source_capture_policy"]["sha256_receipts"] is None
