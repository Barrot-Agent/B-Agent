from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T093925Z-xrp-spot-perpetuals-etf-macro-vintage-update.json"
)


@pytest.fixture(scope="module")
def data() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_rendered_response_hash_and_ticker_arithmetic(data: dict) -> None:
    text = data["source_captures"]["kraken_rendered_response_text"]
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert digest == data["source_captures"]["kraken_rendered_response_sha256"]
    quote = data["spot_market"]["kraken_xrpusd"]
    assert quote["last_trade_usd"] == 1.19905
    assert quote["best_bid_usd"] == 1.1989
    assert quote["best_ask_usd"] == 1.19897
    assert quote["spread_bps"] == pytest.approx(0.5838515015)
    assert quote["last_vs_rolling_24h_vwap_pct"] == pytest.approx(-3.3959282010)
    assert quote["last_vs_utc_day_open_pct"] == pytest.approx(-0.5490723000)
    assert quote["last_above_rolling_24h_low_pct"] == pytest.approx(1.9556991625)


def test_kraken_retrieval_interval_and_response_limits_are_explicit(data: dict) -> None:
    capture = data["capture_contract"]
    source = next(x for x in data["source_registry"] if x["source_id"].startswith("KRAKEN_"))
    assert capture["exact_common_point_in_time_cutoff"] is False
    assert source["provider_event_time_utc"] is None
    assert source["raw_http_bytes_captured"] is False
    assert len(source["rendered_response_sha256"]) == 64
    assert source["model_eligible"] is False
    assert source["retrieved_between_utc"] == [
        "2026-11-06T09:34:50Z",
        "2026-11-06T09:36:53Z",
    ]


def test_tradradar_open_interest_components_and_units_reconcile(data: dict) -> None:
    item = data["derivatives"]["tradradar"]
    assert sum(item["venue_open_interest_usd"].values()) == item["venue_open_interest_sum_usd"]
    assert item["venue_open_interest_sum_usd"] == 1874660000
    assert item["open_interest_7_exchanges_usd"] == 1870000000
    assert item["liquidations_24h_lower_bound_usd"] == 19810000
    assert item["long_liquidations_usd"] + item["short_liquidations_usd"] == pytest.approx(19806910)
    assert item["long_short_account_ratio"] == 3.99
    assert item["long_account_share_pct"] == 80.0
    assert item["model_eligible"] is False


def test_spot_and_derivatives_price_difference_is_not_a_return(data: dict) -> None:
    item = data["spot_market"]["asynchronous_price_comparison"]
    assert item["arithmetic_difference_pct"] == pytest.approx(1.3053396418)
    assert item["comparison_type"] == "asynchronous_cross_provider_level_difference"
    assert item["is_return_series"] is False
    assert item["model_eligible"] is False


def test_etf_fund_universes_and_partial_vintages_remain_separate(data: dict) -> None:
    etf = data["etf_flow_reconciliation"]
    assert etf["xrp_insights"]["fund_universe"] == "six US spot XRP funds plus BITW"
    assert etf["xrp_insights"]["nov2_to_nov4_net_holdings_change_xrp"] == -259701
    assert etf["xrp_insights"]["nov5_status"] == "provisional"
    assert etf["cryptokeyhole"]["fund_universe"] == "four US spot XRP funds"
    assert etf["cryptokeyhole"]["nov4_net_holdings_change_xrp"] == -3339
    assert etf["cryptokeyhole"]["nov5_status"] == "partial_two_of_four_funds"
    assert etf["cryptokeyhole"]["visible_five_day_row_sum_xrp"] == -394960
    assert etf["cryptokeyhole"]["page_headline_five_day_flow_xrp"] == 1837670
    assert etf["cryptokeyhole"]["headline_minus_visible_rows_xrp"] == 2232630
    assert etf["cryptokeyhole"]["five_day_headline_status"] == "INTERNALLY_UNRECONCILED_QUARANTINED"
    assert etf["cryptoetf_today"]["nov5_status"] == "partial_two_of_five_funds"
    assert etf["cryptoetf_today"]["complete_five_fund_zero_flow"] is False
    assert etf["comparability"]["values_must_not_be_averaged"] is True
    assert etf["comparability"]["model_eligible"] is False


def test_depth_is_historical_and_bls_is_scheduled_not_observed(data: dict) -> None:
    depth = data["historical_depth_context"]
    assert depth["latest_cited_snapshot_time_utc"] == "2026-11-06T03:00:00Z"
    assert depth["current_synchronized_orderbook_depth_captured"] is False
    event = data["macro_event_timeline"][0]
    assert event["scheduled_utc"] == "2026-11-06T13:30:00Z"
    assert event["status_at_cutoff"] == "SCHEDULED_NOT_YET_RELEASED"


def test_competing_hypotheses_keep_disconfirming_evidence_and_no_causality(data: dict) -> None:
    hypotheses = data["competing_hypotheses"]
    assert {x["id"] for x in hypotheses} == {
        "leveraged_long_unwind",
        "broader_crypto_risk_repricing",
        "etf_flow_causality_unproven",
        "near_low_spot_repricing_or_stabilization",
        "scheduled_macro_event_risk",
    }
    assert all(x["disconfirming_evidence"] for x in hypotheses)
    assert all(x["status"] in {"HYPOTHESIS_NOT_CAUSAL_FINDING", "EVENT_ANNOTATION_ONLY"} for x in hypotheses)


def test_reuters_security_context_has_its_own_source_record_and_is_not_xrp_regulation(data: dict) -> None:
    registry = {x["source_id"]: x for x in data["source_registry"]}
    source = registry["REUTERS_BINANCE_BANK_SUPERVISORY_OUTREACH_20261105"]
    assert source["publisher"] == "Reuters"
    assert source["independence_group"] == "reuters_reporting"
    assert "not an XRP-specific regulatory action" in source["limitations"][0]
    hypothesis = next(x for x in data["competing_hypotheses"] if x["id"] == "broader_crypto_risk_repricing")
    assert "REUTERS_BINANCE_BANK_SUPERVISORY_OUTREACH_20261105" in hypothesis["source_ids"]


def test_no_forecast_or_model_admission_is_created(data: dict) -> None:
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["forecast_status"]["paper_trade_executed"] is False
    assert data["forecast_status"]["real_money_action"] is False
