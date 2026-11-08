import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T143550Z-xrp-etf-flow-lineage-and-cftc-anprm-reconciliation.json"
)


def _artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_normalized_source_excerpt_receipts_match_sha256():
    data = _artifact()
    assert data["raw_http_bytes_retained"] is False
    assert "not raw HTTP wire bytes" in data["hash_scope"]
    for receipt in data["source_excerpt_receipts"]:
        digest = hashlib.sha256(receipt["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == receipt["sha256"]


def test_xrp_insights_flow_is_issuer_holdings_delta_not_creation_redemption():
    data = _artifact()["xrp_insights_measurement"]
    assert data["nov6_holdings_delta_xrp"] == -663000
    assert data["week_2026_10_30_to_2026_11_06_holdings_delta_xrp"] == -813000
    assert "holdings" in data["flow_method"]
    assert "GXRP" in data["declared_universe"]
    assert "BITW" in data["declared_universe"]
    assert "not verified net creations/redemptions" in data["limitations"][0]


def test_alpha_fund_rows_reconcile_net_total_and_positive_share_denominator():
    data = _artifact()["alpha_finance_measurement"]
    rows = data["cumulative_fund_flows_usd_m"]
    positive = sum(value for value in rows.values() if value > 0)
    net = sum(rows.values())
    assert round(positive, 1) == 1748.8
    assert round(net, 1) == 1730.4
    assert data["displayed_share_denominator_usd_m"] == 1750
    assert data["headline_cumulative_net_inflow_usd"] == 1_730_000_000
    expected = {
        "XRP": 38.9,
        "XRPZ": 30.3,
        "XRPC": 27.4,
        "GXRP": 3.5,
    }
    for ticker, share in expected.items():
        assert data["displayed_share_percent"][ticker] == share
        assert round(rows[ticker] / positive * 100, 1) == share
    assert data["displayed_share_percent"]["TOXR"] is None
    assert rows["TOXR"] == -18.4


def test_alpha_provider_lineage_and_source_independence_are_not_overstated():
    data = _artifact()
    assert "Coinglass" in data["alpha_finance_measurement"]["provider_lineage"]
    independence = data["reconciliation"]["source_independence"]
    assert independence["publisher_level"].startswith("XRP Insights and Alpha Finance are distinct")
    assert independence["upstream_level"].startswith("Not established as independent")
    assert "Do not count" in independence["rule"]


def test_daily_flow_disagreement_and_unmatched_fund_universes_are_preserved():
    data = _artifact()["reconciliation"]
    mismatch = data["nov6_daily_disagreement"]
    assert mismatch["xrp_insights_holdings_delta_xrp"] == -663000
    assert mismatch["alpha_finance_flow_usd"] == 0
    assert mismatch["status"] == "unresolved_non_comparable"
    assert data["universe_difference"]["status"] == "not_same_fund_universe"


def test_price_close_conflict_and_search_index_only_value_are_quarantined():
    data = _artifact()
    price = data["reconciliation"]["price_close_disagreement"]
    assert price["xrp_insights_weekly_close_usd_rounded"] == 1.17
    assert price["alpha_finance_nov6_close_usd"] == 1.2067
    assert price["awebanalysis_search_index_nov6_close_usd"] == 1.181
    assert price["status"] == "unresolved_vintage_or_definition_mismatch"
    assert data["retrieval_observations"]["awebanalysis_search_index"]["status"] == "SEARCH_INDEX_ONLY_QUARANTINED"
    assert data["retrieval_observations"]["awebanalysis_live_page"]["latest_visible_row"] == "2026-11-04"


def test_cftc_anprm_is_not_a_final_rule_or_new_xrp_classification():
    event = _artifact()["regulatory_event"]
    assert event["docket"] == "FR Doc 2026-20888"
    assert event["published_date"] == "2026-10-13"
    assert event["comment_deadline"] == "2026-12-14"
    assert event["action"] == "Advanced notice of proposed rulemaking"
    assert event["status"] == "ANPRM_NOT_FINAL_RULE"
    assert "not a new XRP-specific classification" in event["xrp_relevance"]
    assert "section 2(c)(2)(D)" in event["statutory_scope"]


def test_exchange_balances_rlusd_and_rwa_are_not_mislabeled_as_xrp_demand():
    data = _artifact()["reconciliation"]["adjacent_supply_context"]
    assert data["seven_day_same_wallet_set_balance_change_xrp"] == -150700000
    assert "not automatically proof" in data["limitations"][0]
    assert data["rlusd_total_usd"] == 2670000000
    component_sum = data["rlusd_xrpl_usd"] + data["rlusd_ethereum_usd"]
    assert round(component_sum / 1_000_000_000, 2) == 2.67
    assert component_sum != data["rlusd_total_usd"]  # displayed components are rounded; exact supply is not disclosed
    assert "not XRP demand" in data["limitations"][1]


def test_no_feature_admission_or_directional_forecast():
    data = _artifact()
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast"] is False
