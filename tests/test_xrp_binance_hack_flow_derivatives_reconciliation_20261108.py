from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T211453Z-binance-hack-xrp-flow-derivatives-cross-ledger-reconciliation.json"
)


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_source_excerpt_receipts_match_and_respect_quote_limit(record: dict) -> None:
    receipts = record["source_receipts"]
    assert len(receipts) >= 15
    for receipt in receipts:
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"]
        assert len(receipt["excerpt"].split()) <= 25


def test_binance_distinguishes_stolen_xrp_from_stolen_op(record: dict) -> None:
    facts = record["event_facts"]["binance_official"]
    assert facts["xrp_stolen"] == 233_460_000
    assert facts["op_stolen"] == 44_200_000
    assert facts["xrp_stolen"] != facts["op_stolen"]
    assert facts["affected_assets_estimate_usd"] == 6_340_000_000


def test_fbi_attribution_and_dprk_denial_are_both_preserved(record: dict) -> None:
    fbi = record["event_facts"]["fbi"]
    independence = record["source_independence_and_disagreement"]
    assert fbi["attribution"] == "TraderTraitor"
    assert fbi["attributed_to"] == "Democratic People's Republic of Korea"
    assert "denied responsibility" in independence["geopolitical_disagreement"]


def test_elliptic_xrp_laundering_reconciles_with_remaining_balance(record: dict) -> None:
    facts = record["event_facts"]["elliptic_as_of_2026_11_07_0800_utc"]
    derived = record["derived_reconciliation"]["attacker_xrp_movement"]
    assert facts["original_xrp_stolen_rounded"] == 233_000_000
    assert facts["xrp_moved_by_2026_11_06_0845_utc"] == 42_000_000
    assert facts["additional_xrp_moved_overnight_to_2026_11_07_0800_utc"] == 44_000_000
    assert facts["xrp_remaining"] == 148_000_000
    assert derived["moved_2026_11_06_plus_2026_11_07"] == 86_000_000
    assert derived["difference_xrp"] == 540_000
    assert derived["difference_pct_of_moved"] < 1.0


def test_attacker_conversion_is_not_mislabeled_as_fiat_cashout(record: dict) -> None:
    facts = record["event_facts"]["elliptic_as_of_2026_11_07_0800_utc"]
    assert facts["likely_cashout"] == "negligible"
    assert "cannot prove who currently controls" in facts["controller_identity_limit"]
    assert record["derived_reconciliation"]["usd_value_crosscheck"]["illustrative_xrp_equivalent_at_usd_1_16"] == pytest.approx(86_206_896.55172414)


def test_binance_exchange_outflow_is_not_equated_to_stolen_xrp(record: dict) -> None:
    facts = record["event_facts"]["cryptoticker_as_of_2026_11_08"]
    derived = record["derived_reconciliation"]["exchange_outflow_vs_theft"]
    assert facts["binance_xrp_outflow_nov_04"] == 418_500_000
    assert facts["binance_xrp_outflow_oct_29"] == 315_000_000
    assert facts["internal_wallet_transfer_caveat"] is True
    assert derived["ratio"] == pytest.approx(1.792593165)
    assert "cannot be equated" in derived["conclusion"]


def test_cryptoquant_reserve_increase_is_separate_and_source_unverified(record: dict) -> None:
    facts = record["event_facts"]["cryptoquant_as_of_2026_11_05"]
    derived = record["derived_reconciliation"]["reserve_change_vs_exchange_outflow"]
    assert facts["reserve_change_xrp"] == 280_000_000
    assert facts["reserve_change_pct"] == pytest.approx(11.9)
    assert facts["source_of_latest_inflows"] == "unverified"
    assert "not netted" in derived["conclusion"]


def test_customer_restoration_is_not_the_same_as_onchain_recovery(record: dict) -> None:
    facts = record["event_facts"]["binance_official"]
    derived = record["derived_reconciliation"]["restoration_vs_recovery"]
    assert facts["affected_token_assets_restored_pct_as_of_2026_10_31"] == 98
    assert facts["frozen_or_intercepted_usd"] == 2_850_000_000
    assert "separate concepts" in derived["conclusion"]


def test_etf_week_data_keeps_upstream_dependency_and_zero_days(record: dict) -> None:
    facts = record["event_facts"]["cryptoticker_as_of_2026_11_08"]
    assert facts["xrpc_monday_outflow_usd"] == 529_500
    assert facts["other_etf_daily_net_flows_tuesday_friday_usd"] == 0
    assert "SoSoValue" in record["source_independence_and_disagreement"]["secondary_dependence"]
    assert facts["whale_purchase_claim_admission"].startswith("Excluded")


def test_derivatives_oi_dispersion_is_not_averaged(record: dict) -> None:
    facts = record["event_facts"]["derivatives_aggregators"]
    derived = record["derived_reconciliation"]["derivatives_provider_dispersion"]
    assert facts["coingecko"]["open_interest_usd"] == 4_075_989_283
    assert facts["tradradar"]["open_interest_usd"] == 1_890_000_000
    assert facts["kodexius"]["open_interest_usd"] == 781_470_000
    assert facts["optimistfi"]["open_interest_usd"] == 1_600_000_000
    assert derived["max_to_min_ratio"] == pytest.approx(5.215797513660154)
    assert "Do not average" in derived["conclusion"]


def test_funding_and_liquidations_keep_provider_universes(record: dict) -> None:
    facts = record["event_facts"]["derivatives_aggregators"]
    assert facts["coingecko"]["provider_timestamp_available"] is False
    assert facts["tradradar"]["stated_delay_minutes"] == 15
    assert facts["kodexius"]["contracts"] == 7
    assert facts["optimistfi"]["venues"] == 37
    assert facts["tradradar"]["long_liquidations_usd"] > facts["tradradar"]["short_liquidations_usd"]


def test_automated_laundering_is_not_mislabeled_as_ai_agent_decision(record: dict) -> None:
    facts = record["event_facts"]["elliptic_as_of_2026_11_07_0800_utc"]
    assert "no evidence of an AI agent making decisions" in facts["automation_limit"]


def test_no_flow_or_derivatives_feature_or_forecast_is_admitted(record: dict) -> None:
    admission = record["market_admission"]
    assert all(value is False for value in admission.values() if isinstance(value, bool))
    assert record["forecast"]["status"] == "NOT_ISSUED"
    assert record["forecast"]["directional_forecast"] is False
    assert record["forecast"]["paper_trade"] is False
    assert record["forecast"]["real_money_action"] is False
    assert record["external_actions"]["repository_main_write"] is False
    assert record["external_actions"]["deployment"] is False
