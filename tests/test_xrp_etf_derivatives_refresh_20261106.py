import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T051458Z-xrp-etf-and-derivatives-refresh.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_derivatives_refresh_preserves_timestamp_delay_and_venue_scope():
    data = load_artifact()
    deriv = data["derivatives"]
    assert deriv["provider_updated_at_utc"] == "2026-11-06T03:55:00Z"
    assert deriv["displayed_delay_minutes"] == 15
    assert len(deriv["open_interest_venue_rows_usd"]) == 7
    assert sum(deriv["open_interest_venue_rows_usd"].values()) == (
        deriv["open_interest_venue_row_sum_usd"]
    )
    assert deriv["open_interest_venue_row_sum_usd"] == 1907310000
    assert deriv["open_interest_change_24h_percent"] < 0
    assert deriv["funding_oi_weighted_percent_per_8h"] > 0


def test_long_liquidation_imbalance_keeps_counterevidence():
    deriv = load_artifact()["derivatives"]
    assert deriv["long_liquidations_24h_usd"] > deriv["short_liquidations_24h_usd"]
    assert deriv["liquidations_24h_usd_lower_bound"] >= (
        deriv["long_liquidations_24h_usd"] + deriv["short_liquidations_24h_usd"]
    )
    assert deriv["long_account_share_percent"] == 80.3
    assert any("account count" in x for x in deriv["limitations"])
    assert any("positive" in x for x in deriv["limitations"])


def test_etf_complete_and_partial_days_are_not_conflated():
    etf = load_artifact()["etf_flows"]
    keyhole = etf["cryptokeyhole"]
    insight = etf["xrp_insights"]
    assert keyhole["latest_complete_day"] == "2026-11-04"
    assert keyhole["latest_complete_day_net_flow_xrp"] == -3339
    assert keyhole["last_five_complete_days_net_flow_xrp"] == 1837670
    assert keyhole["nov5_partial_funds_reporting"] == 2
    assert keyhole["nov5_partial_funds_total"] == 4
    assert keyhole["nov5_waiting_funds"] == ["XRPZ", "XRPC"]
    assert insight["latest_row_date"] == "2026-11-05"
    assert insight["latest_row_status"] == "provisional"
    assert insight["data_as_of"] == "2026-11-04"


def test_etf_publisher_difference_is_reconciled_without_calling_it_cash_flow():
    comparison = load_artifact()["etf_flows"]["comparison"]
    assert comparison["nov4_daily_difference_xrp"] == -61487
    assert comparison["status"] == "UNRECONCILED_DIFFERENT_FUND_UNIVERSES_AND_METHODS"
    assert "not direct AP cash" in comparison["cash_flow_boundary"]
    registry = {x["id"]: x for x in load_artifact()["source_registry"]}
    assert (
        registry["CRYPTOKEYHOLE_XRP_ETF_20261106T0443Z"]["independence_group"]
        == registry["XRP_INSIGHTS_XRP_ETF_20261106T040632Z"]["independence_group"]
    )


def test_source_vintages_and_raw_capture_limits_are_explicit():
    data = load_artifact()
    assert data["capture"]["exact_per_source_retrieval_timestamp_utc"] is None
    assert data["capture"]["raw_http_wire_bytes_captured"] is False
    assert all(not x["model_eligible"] for x in data["source_registry"])
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["issued"] is False


def test_hypotheses_include_disconfirming_evidence_and_tests():
    hypotheses = load_artifact()["competing_hypotheses"]
    assert len(hypotheses) >= 3
    assert all(x["supporting_evidence"] for x in hypotheses)
    assert all(x["disconfirming_evidence"] for x in hypotheses)
    assert all(x["tests"] for x in hypotheses)
