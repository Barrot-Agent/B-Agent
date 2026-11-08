import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T021417Z-us-treasury-fed-boj-liquidity-context.json"
)


def test_treasury_borrowing_and_tga_are_recorded_as_estimates_not_realized_flows():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    borrowing = next(x for x in data["sources"] if x["source_id"] == "treasury_nov2_borrowing_estimates")
    refunding = next(x for x in data["sources"] if x["source_id"] == "treasury_nov4_quarterly_refunding")
    assert borrowing["facts"]["privately_held_net_marketable_borrowing_oct_dec_2026_usd_bn"] == 618
    assert borrowing["facts"]["privately_held_net_marketable_borrowing_jan_mar_2027_usd_bn"] == 800
    assert refunding["facts"]["gross_refunding_offering_usd_bn"] == 125
    assert refunding["facts"]["estimated_new_cash_from_private_investors_usd_bn"] == 28
    assert refunding["facts"]["tga_peak_projection_usd_bn"] == 1025
    assert "not an observed current balance" in refunding["qualifications"][1]


def test_fed_and_boj_policy_votes_and_planned_etf_sales_are_distinguished():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    fed = next(x for x in data["sources"] if x["source_id"] == "federal_reserve_oct28_fomc")
    boj = next(x for x in data["sources"] if x["source_id"] == "boj_oct30_statement")
    assert fed["facts"]["federal_funds_target_low_pct"] == 3.75
    assert fed["facts"]["federal_funds_target_high_pct"] == 4.0
    assert fed["facts"]["vote_against"] == 2
    assert boj["facts"]["overnight_call_rate_target_pct"] == 1.25
    assert boj["facts"]["vote_against"] == 1
    assert boj["facts"]["dissenter_proposed_rate_pct"] == 1.5
    assert boj["facts"]["etf_sales_book_value_annual_yen_bn"] == 860
    assert boj["facts"]["etf_sales_change_implementation"] == "2027-01"


def test_boj_minutes_are_historical_and_preserve_dissent_and_geopolitical_context():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    boj = next(x for x in data["sources"] if x["source_id"] == "boj_sep17_18_minutes_published_nov5")
    assert boj["published_at"] == "2026-11-05"
    assert boj["meeting_dates"] == ["2026-09-17", "2026-09-18"]
    assert boj["facts"]["sep_vote_for_1_25pct"] == 7
    assert boj["facts"]["sep_votes_against"] == 2
    assert "not a November 8 real-time market snapshot" in boj["qualifications"][0]


def test_macro_context_is_not_promoted_to_an_xrp_forecast_or_feature():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["feature_policy"]["feature_store_admission"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
    assert all("No XRP-specific" in item["xrp_link"] or "only" in item["xrp_link"] or "No direct" in item["xrp_link"] for item in data["scenario_hypotheses"])
