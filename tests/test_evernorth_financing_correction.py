import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_eloc_correction_uses_sec_gross_proceeds_and_no_net_estimate():
    snap = load("data/xrp_intelligence/snapshots/20261101T154500Z-evernorth-financing-and-custody-correction.json")
    f = snap["capital_stack"]["cantors_committed_equity_facility"]
    assert f["shares_available"] == 5218935
    assert f["max_gross_proceeds_usd_if_all_sold_at_cover_price"] == 80700000
    assert f["net_proceeds_estimate_usd"] is None
    assert f["draw_verified"] is False


def test_related_party_facility_is_subsidiary_debt_not_xrp_purchase():
    snap = load("data/xrp_intelligence/snapshots/20261101T154500Z-evernorth-financing-and-custody-correction.json")
    f = snap["capital_stack"]["ripple_related_company_facility"]
    assert f["facility_limit_usd"] == 10000000
    assert f["drawn_as_of_2026_10_07_usd"] == 9700000
    assert f["borrower"] == "Pathfinder / operating Company subsidiary"
    assert f["current_repayment_status"] == "UNKNOWN"


def test_separate_evernorth_facility_is_not_conflated():
    snap = load("data/xrp_intelligence/snapshots/20261101T154500Z-evernorth-financing-and-custody-correction.json")
    f = snap["capital_stack"]["separate_evernorth_facility"]
    assert f["facility_limit_usd"] == 1000000
    assert f["borrowed_as_of_2026_06_30_usd"] == 0


def test_tracker_to_sec_holdings_difference_is_preserved():
    snap = load("data/xrp_intelligence/snapshots/20261101T154500Z-evernorth-financing-and-custody-correction.json")
    c = snap["custody_migration_reconciliation"]
    assert c["tracker_sum_xrp"] > c["sec_reported_closing_xrp"]
    assert round(c["difference_xrp"], 2) == 200137.78
    assert c["reconciliation_status"] == "UNRESOLVED_200137_78_XRP_DIFFERENCE_AND_DESTINATION_OWNERSHIP"


def test_custody_migration_is_not_called_a_sale():
    snap = load("data/xrp_intelligence/snapshots/20261101T154500Z-evernorth-financing-and-custody-correction.json")
    assert snap["custody_migration_reconciliation"]["bitgo_activation_confirmed_by_bithomp"] == 9
    assert snap["custody_migration_reconciliation"]["classification"].startswith("STRONGLY_SUPPORTED_BITGO_CUSTODY_REALLOCATION")


def test_deployment_partners_remain_planned_not_executed():
    corr = load("data/xrp_intelligence/source_revisions/20261101T154500Z-evernorth-deployment-source-and-financing-correction.json")
    src = next(s for s in corr["corrected_sources"] if s["id"] == "evernorth-deployment-partners-20261014-corrected")
    assert "Q4 2026" in " ".join(src["claims"])
    assert any("does not prove" in x or "not evidence" in x or "does not establish" in x for x in src["limitations"])
