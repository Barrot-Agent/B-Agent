import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T040649Z-xrp-market-etf-amendment-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_capture_does_not_claim_synchronized_or_exact_source_times():
    data = load_artifact()
    assert data["capture"]["exact_per_source_retrieval_timestamp_utc"] is None
    assert data["capture"]["synchronized_model_cutoff_utc"] is None
    assert data["capture"]["raw_http_wire_bytes_captured"] is False
    assert data["forecast"]["issued"] is False
    assert data["model_admission"]["eligible"] is False


def test_kraken_spread_and_daily_open_semantics_are_correct():
    spot = load_artifact()["spot_market"]
    expected = (
        (spot["best_ask_usd"] - spot["best_bid_usd"])
        / ((spot["best_ask_usd"] + spot["best_bid_usd"]) / 2)
        * 10000
    )
    assert abs(expected - spot["displayed_spread_bps"]) < 1e-9
    assert spot["utc_day_open_usd"] == 1.20567
    assert spot["rolling_24h_vwap_usd"] == 1.25406403
    assert spot["provider_event_timestamp_utc"] is None


def test_derivatives_scope_and_long_liquidation_imbalance_are_explicit():
    data = load_artifact()
    deriv = data["derivatives"]
    assert deriv["open_interest_venue_rows_usd"]["Binance"] > 0
    assert sum(deriv["open_interest_venue_rows_usd"].values()) == 1912610000
    assert deriv["long_liquidations_24h_usd"] > deriv["short_liquidations_24h_usd"]
    assert deriv["liquidations_24h_usd_lower_bound"] >= (
        deriv["long_liquidations_24h_usd"] + deriv["short_liquidations_24h_usd"]
    )
    assert deriv["funding_oi_weighted_percent_per_8h"] > 0
    assert "account long/short ratio" in " ".join(deriv["limitations"]).lower()


def test_xrpl_lending_amendments_remain_below_activation_threshold():
    governance = load_artifact()["xrpl_amendments"]
    assert governance["required_yes_votes"] == 29
    assert governance["validators_heard"] == 35
    assert governance["votes"]["LendingProtocol"] == 21
    assert governance["votes"]["SingleAssetVault"] == 23
    assert governance["publisher_reports_any_amendment_in_14_day_countdown"] is False
    assert "more than 80%" in governance["official_rule"]
    assert "not evidence of borrower collateral" in governance["collateral_boundary"]


def test_etf_provider_disagreement_is_not_mislabeled_as_cash_flow():
    etf = load_artifact()["etf_flows"]
    insight = etf["xrp_insights"]
    keyhole = etf["cryptokeyhole"]
    comparison = etf["aggregate_comparison"]
    assert insight["nov4_daily_holdings_change_xrp"] == -64826
    assert keyhole["nov4_daily_holdings_change_xrp"] == -3339
    assert comparison["nov4_daily_difference_xrp"] == -61487
    assert insight["latest_row_status"] == "provisional"
    assert keyhole["nov5_partial_funds_reporting"] == 2
    assert keyhole["nov5_partial_funds_total"] == 4
    assert comparison["reconciliation_status"] == (
        "UNRECONCILED_DIFFERENT_FUND_UNIVERSES_AND_METHODS"
    )
    assert "not direct ap cash" in insight["methodology"].lower()


def test_etf_source_methodology_preserves_indirect_and_excluded_exposure():
    registry = {x["id"]: x for x in load_artifact()["source_registry"]}
    insight = registry["XRP_INSIGHTS_ETF_DATA_20261106T025446Z"]
    keyhole = registry["CRYPTOKEYHOLE_ETF_DATA_20261106T0403Z"]
    assert any("indirect XRP exposure" in x for x in insight["limitations"])
    assert any("GXRP flow is excluded" in x for x in insight["limitations"])
    assert any("index rebalancing" in x for x in insight["limitations"])
    assert insight["independence_group"] == keyhole["independence_group"]


def test_competing_hypotheses_include_disconfirming_evidence():
    hypotheses = load_artifact()["competing_hypotheses"]
    assert len(hypotheses) >= 4
    assert len({item["id"] for item in hypotheses}) == len(hypotheses)
    assert all(item["supporting_evidence"] for item in hypotheses)
    assert all(item["disconfirming_evidence"] for item in hypotheses)
    assert len(load_artifact()["red_team_objections"]) >= 5
