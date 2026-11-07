from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


ARTIFACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T121239Z-xrp-market-and-sbi-multirail-reconciliation.json"
)


def artifact() -> dict:
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def event(document: dict, event_id: str) -> dict:
    return next(item for item in document["institutional_events"] if item["event_id"] == event_id)


def test_direct_exchange_payload_receipts_match_exact_stored_text() -> None:
    document = artifact()
    for source in document["market_snapshot"]["sources"]:
        raw = source["raw_payload_text"].encode("utf-8")
        assert hashlib.sha256(raw).hexdigest() == source["raw_payload_sha256"]
        registry = next(item for item in document["source_registry"] if item["source_id"] == source["source_id"])
        assert registry["raw_payload_sha256"] == source["raw_payload_sha256"]


def test_kraken_timestamp_is_missing_and_okx_ticker_is_stale() -> None:
    document = artifact()
    kraken, okx = document["market_snapshot"]["sources"]
    assert kraken["provider_event_time_utc"] is None
    assert kraken["provider_timestamp_status"] == "not_supplied"
    assert okx["provider_event_time_utc"] == "2026-11-07T11:48:54.274Z"
    assert okx["age_at_capture_seconds"] > okx["freshness_limit_seconds"]
    assert okx["freshness_status"] == "stale"


def test_level_one_spread_and_cross_venue_arithmetic_are_reproducible() -> None:
    document = artifact()
    observations = document["market_snapshot"]["normalized_observations"]
    kraken = observations["kraken_xrpusd"]
    okx = observations["okx_xrpusdt"]
    kraken_spread = (kraken["ask_usd"] - kraken["bid_usd"]) / (
        (kraken["ask_usd"] + kraken["bid_usd"]) / 2
    ) * 10_000
    okx_spread = (okx["ask_usdt"] - okx["bid_usdt"]) / (
        (okx["ask_usdt"] + okx["bid_usdt"]) / 2
    ) * 10_000
    gap = (okx["last_usdt"] - kraken["last_usd"]) / kraken["last_usd"] * 100
    assert abs(kraken_spread - kraken["level1_spread_bps"]) < 1e-6
    assert abs(okx_spread - okx["level1_spread_bps"]) < 1e-6
    assert abs(gap - observations["raw_cross_venue_last_difference_pct"]) < 1e-5
    assert observations["cross_venue_arbitrage_status"] == "not_established"


def test_ticker_quotes_do_not_invent_depth_or_model_eligibility() -> None:
    document = artifact()
    observations = document["market_snapshot"]["normalized_observations"]
    assert observations["order_book_depth_status"] == "not_captured"
    assert observations["model_feature_admission"] is False
    assert document["feature_admission"]["market_snapshot_model_eligible"] is False


def test_coinglass_liquidation_relay_is_not_double_counted() -> None:
    document = artifact()
    item = document["derivatives_and_flow_evidence"]["liquidation_observation"]
    assert item["upstream_source"] == "CoinGlass"
    assert item["independence_group"] == "coinglass"
    assert item["long_share_pct_reported"] == 95.54
    assert "not independent confirmations" in item["note"]


def test_okx_long_short_ratio_is_an_account_count_not_notional() -> None:
    document = artifact()
    item = document["derivatives_and_flow_evidence"]["okx_account_positioning"]
    assert item["denominator"] == "accounts"
    assert item["notional_exposure_inferred"] is False
    assert item["observations"][-1]["long_short_account_ratio"] == 4.3


def test_reported_open_interest_change_is_reproducible_but_not_model_eligible() -> None:
    document = artifact()
    item = document["derivatives_and_flow_evidence"]["okx_open_interest"]
    values = item["observations_usd_millions"]
    change = (values[-1]["open_interest"] / values[0]["open_interest"] - 1) * 100
    assert abs(change - item["reported_change_nov4_to_nov6_pct"]) < 0.01
    assert item["model_feature_admission"] is False
    assert item["contract_coverage"] == "not independently exposed in article"


def test_etf_recent_zero_flows_are_not_mislabeled_as_current_assets() -> None:
    document = artifact()
    items = document["derivatives_and_flow_evidence"]["etf_flow_disagreement"]
    assert len(items) == 2
    alpha = next(item for item in items if item["source_id"] == "alpha_finance_xrp_etf")
    sosovalue = next(item for item in items if item["source_id"] == "sosovalue_via_coingape")
    assert "USD 1.41 billion" in sosovalue["claim"]
    assert "USD 1.73B" in alpha["claim"]
    assert "net assets and holdings not published" in alpha["claim"]
    assert "do not average" in document["derivatives_and_flow_evidence"]["etf_reconciliation"]


def test_sbi_bitbank_completion_is_not_evidence_of_xrp_purchase() -> None:
    document = artifact()
    item = event(document, "sbi_bitbank_wholly_owned_completion")
    assert item["status"] == "completed"
    assert item["voting_ownership_after_completion_pct"] == 100
    assert item["entities"].count("Bitbank") == 1
    assert "No XRP-specific" in item["xrp_implication"]


def test_bitbank_jadat_transfer_is_not_marked_completed() -> None:
    document = artifact()
    item = event(document, "bitbank_jadat_transfer_announcement")
    assert item["status"] == "announced_completion_not_verified"
    assert "Do not assume" in item["xrp_implication"]


def test_open_standard_membership_does_not_create_direct_sbi_coinbase_contract() -> None:
    document = artifact()
    item = event(document, "sbi_startale_open_standard_jpysc_ousd")
    assert item["status"] == "membership_confirmed_poc_under_consideration"
    assert "no direct SBI-Coinbase commercial contract" in item["relationship_scope"]
    assert item["production_service_launched"] is False


def test_blackrock_tokenized_mmf_jpysc_agreement_is_exploratory() -> None:
    document = artifact()
    item = event(document, "sbi_startale_blackrock_tokenized_mmf_jpysc")
    assert item["status"] == "basic_agreement_exploratory"
    assert item["production_service_launched"] is False
    assert item["specific_fund_or_chain_named_in_release"] is False


def test_sbi_trust_custody_merger_is_future_and_conditional() -> None:
    document = artifact()
    item = event(document, "sbi_trust_custody_merger")
    assert item["status"] == "planned_subject_to_regulatory_approval"
    assert item["planned_effective_date"] == "2026-12-31"
    assert item["completed"] is False


def test_smfg_five_percent_stake_is_only_in_sbi_startale_marketing() -> None:
    document = artifact()
    item = event(document, "sbi_smfg_jpysc_alliance")
    assert item["equity_stake_scope"] == "5% of SBI Startale Marketing only"
    assert item["investment_amount_disclosed"] is False
    assert item["production_service_launched"] is False


def test_mesh_jv_is_planned_and_ownership_sums_to_one_hundred() -> None:
    document = artifact()
    item = event(document, "sbi_mesh_moneyforward_jv")
    assert item["status"] == "basic_agreement_pending_final_contract_and_regulatory_steps"
    assert sum(item["planned_ownership_pct"].values()) == 100
    assert item["xrp_support_confirmed"] is False


def test_jpysc_issuer_distributor_and_initial_distribution_scope_are_separate() -> None:
    document = artifact()
    item = event(document, "jpysc_issuance_and_distribution")
    assert item["issuer"] == "SBI Shinsei Trust Bank"
    assert item["distributor"] == "SBI VC Trade"
    assert item["technical_co_developer"] == "Startale Group"
    assert item["initial_public_chain_distribution"] is False


def test_rlusd_distribution_is_not_xrp_purchase_or_xrp_collateral() -> None:
    document = artifact()
    sbi = event(document, "sbi_vctrade_rlusd_distribution")
    coinbase = event(document, "coinbase_rlusd_multichain_launch")
    assert "does not establish XRP purchases" in sbi["xrp_implication"]
    assert coinbase["coinbase_global_exchange_rlusd_collateral_at_launch"] is False
    assert "RLUSD collateral must not be confused with XRP collateral" in coinbase["xrp_implication"]


def test_sbi_xrpl_poc_and_xrp_rewards_have_no_proven_production_volume() -> None:
    document = artifact()
    poc = event(document, "sbi_ripple_asia_xrpl_deposit_tokenization_poc")
    rewards = event(document, "sbi_xrp_rewards_card")
    assert poc["status"] == "conceptual_poc_announced"
    assert poc["production_deployment_confirmed"] is False
    assert rewards["aggregate_xrp_acquisition_volume_disclosed"] is False


def test_all_normalized_source_excerpt_hashes_are_bound_to_registry() -> None:
    document = artifact()
    excerpts = document["normalized_excerpts"]
    mapping = {
        "sbi_bitbank_completion": "bitbank_completion",
        "sbi_bitbank_terms": "bitbank_original_terms",
        "bitbank_jadat_transfer": "jadat_sale",
        "sbi_open_standard": "open_standard",
        "sbi_blackrock_jpysc": "blackrock_jpysc",
        "sbi_trust_merger": "trust_merger",
        "sbi_smfg_jpysc": "smfg_jpysc",
        "sbi_mesh_jv": "mesh_jv",
        "jpysc_launch": "jpysc_launch",
        "jpysc_reserves": "jpysc_reserves",
        "sbi_rlusd_distribution": "rlusd_sbi",
        "coinbase_rlusd_launch": "coinbase_rlusd",
        "sbi_xrpl_poc": "sbi_xrpl_poc",
        "sbi_xrp_rewards": "sbi_xrp_rewards",
        "u_today_coinglass_liquidations": "coinglass_liquidations",
        "cryptoticker_xrp_squeeze": "okx_positioning",
        "cryptoticker_xrp_oi": "okx_oi",
        "cryptoticker_sosovalue_etf_relay": "etf_sosovalue",
        "alpha_finance_xrp_etf": "alpha_finance_etf",
        "coinglass_methodology": "coinglass_method",
    }
    registry = {item["source_id"]: item for item in document["source_registry"]}
    assert set(mapping).issubset(registry)
    for source_id, excerpt_key in mapping.items():
        digest = hashlib.sha256(excerpts[excerpt_key].encode("utf-8")).hexdigest()
        assert digest == registry[source_id]["normalized_excerpt_sha256"]


def test_forecast_and_external_action_boundary_remains_fail_closed() -> None:
    document = artifact()
    boundary = document["prediction_boundary"]
    assert boundary["forecast_status"] == "NOT_ISSUED"
    assert boundary["directional_forecast_issued"] is False
    assert boundary["shadow_forecast_issued"] is False
    assert boundary["paper_trade_executed"] is False
    assert boundary["real_money_action"] is False
    assert document["feature_admission"]["institutional_events_model_eligible"] is False
