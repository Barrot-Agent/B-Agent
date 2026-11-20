import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T090232Z-xrp-market-derivatives-etf-circle-macro-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_spot_ticker_arithmetic_and_scope_are_preserved():
    spot = load()["market_snapshot"]["spot"]
    mid = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    spread = (spot["best_ask_usd"] - spot["best_bid_usd"]) / mid * 10000
    assert math.isclose(spot["mid_usd"], mid, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(spot["displayed_spread_bps"], spread, rel_tol=0, abs_tol=1e-6)
    assert spot["low_24h_usd"] <= spot["last_usd"] <= spot["high_24h_usd"]
    assert spot["volume_24h_xrp"] > 0
    assert spot["utc_day_open_usd"] != spot["low_24h_usd"]


def test_derivatives_components_reconcile_but_binance_providers_are_not_averaged():
    derivatives = load()["market_snapshot"]["derivatives"]
    trad = derivatives["tradradar"]
    summed = sum(trad["exchange_open_interest_usd"].values())
    assert summed == trad["exchange_sum_open_interest_usd"] == 2082550000
    fib = derivatives["fibonomy_binance_xrpusdt"]
    difference = trad["exchange_open_interest_usd"]["Binance"] - fib["open_interest_usd"]
    assert difference == derivatives["comparison"]["absolute_difference_usd"] == 94780000
    assert derivatives["comparison"]["relative_difference_pct"] > 20
    assert trad["short_liquidations_usd"] > trad["long_liquidations_usd"]
    assert trad["long_account_share_pct"] > 70
    assert derivatives["comparison"]["status"] == "MATERIAL_PROVIDER_SCOPE_OR_VINTAGE_DISAGREEMENT"


def test_etf_flow_fund_universes_and_partial_rows_are_not_combined():
    etf = load()["market_snapshot"]["etf_flows"]
    insights = etf["xrp_insights"]
    keyhole = etf["cryptokeyhole"]
    today = etf["cryptoetf_today"]
    assert insights["net_flow_xrp_nov2_nov3"] == -194875
    assert "BITW" in insights["funds_reporting_universe"]
    assert "XRPR" in insights["funds_reporting_universe"]
    assert keyhole["net_flow_xrp_nov3"] == -3339
    assert keyhole["five_complete_day_net_flow_xrp"] == 6178705
    assert "BITW" not in keyhole["funds_reporting_universe"]
    assert today["funds_reporting"] == 2 and today["funds_total"] == 5
    assert today["net_flow_usd_reported_funds"] == 0
    assert today["not_reported"] == ["XRPZ", "XRPC", "GXRP"]
    assert insights["nov4_status"] == "provisional"
    assert "partial" in keyhole["nov4_status"]
    assert etf["no_averaging"] is True
    assert etf["cash_creation_redemption_records_captured"] is False


def test_circle_q3_metrics_separate_usdc_growth_from_revenue_and_gross_volume():
    circle = load()["institutional_and_stablecoin"]["circle_q3_2026"]
    assert circle["average_usdc_circulation_usd"] == 73300000000
    assert circle["end_period_usdc_circulation_yoy_pct"] == 0
    assert circle["q3_usdc_onchain_transaction_volume_usd"] == 13900000000000
    assert circle["reserve_income_yoy_pct"] == -8
    assert circle["other_revenue_usd"] == 207264000
    assert circle["arc_token_presale_revenue_usd"] == 182000000
    assert circle["circle_payments_network_annualized_tpv_usd"] == 41300000000
    assert "does not establish XRP demand" in " ".join(circle["interpretation"])


def test_binance_replenishment_is_not_mislabeled_as_xrp_recovery_or_organic_flow():
    event = load()["binance_security_event"]
    assert event["stolen_xrp_approx"] == 233461943.1
    assert event["source_wallet_count"] == 5
    assert event["impacted_token_assets_replenished_pct_as_of_2026_10_31"] == 98
    assert "not XRP-specific" in event["replenishment_scope"]
    assert "Quarantine" in event["feature_policy"]
    assert event["model_eligible"] is False


def test_xrpl_cleanup_activation_does_not_imply_lending_or_collateral_activation():
    protocol = load()["xrpl_protocol"]
    assert protocol["fixCleanup3_4_0"]["status"] == "ENABLED"
    votes = protocol["current_voting_snapshot"]
    assert votes["LendingProtocol_votes_for"] == 19
    assert votes["votes_required"] == 29
    assert votes["status"] == "LENDING_AND_VAULT_AMENDMENTS_NOT_ACTIVATED"
    assert "not LendingProtocol activation" in protocol["interpretation"]


def test_macro_event_conflict_and_future_bls_release_are_preserved():
    data = load()
    macro = data["macro_context"]
    release = macro["us_employment_situation"]
    assert release["scheduled_release_at_utc"] == "2026-11-06T13:30:00Z"
    assert release["status_at_cutoff"] == "FUTURE_SCHEDULED"
    assert macro["geopolitical_energy_risk"]["boe_decision_status"].startswith("market expectation")
    assert macro["geopolitical_energy_risk"]["guardian_brent_observation_usd_per_barrel"] == 100.83
    assert macro["us_midterm_market_event"]["wsj_dollar_index_nov4"] == 96.94
    assert macro["us_midterm_market_event"]["guardian_dollar_broad_basket_change_pct"] == -0.35
    assert "do not average" in macro["us_midterm_market_event"]["cross_source_rule"].lower()
    assert any(source["id"] == "ap_boe_inflation_iran_20261105" for source in data["source_registry"])


def test_all_rendered_sources_remain_model_ineligible_and_no_forecast_is_issued():
    data = load()
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["predictive_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["source_capture_policy"]["raw_http_bytes_captured"] is False
    assert data["source_capture_policy"]["raw_content_sha256"] is None
    assert all(source["raw_content_sha256"] is None for source in data["source_registry"])
    assert all(source["model_eligible"] is False for source in data["source_registry"])



def test_second_spot_capture_is_a_separate_vintage_not_a_rewritten_snapshot():
    spot = load()["market_snapshot"]["spot"]
    first = spot["last_usd"]
    latest = spot["latest_recheck"]
    mid = (latest["best_bid_usd"] + latest["best_ask_usd"]) / 2
    spread = (latest["best_ask_usd"] - latest["best_bid_usd"]) / mid * 10000
    assert latest["captured_at_utc"] == "2026-11-05T09:16:47Z"
    assert latest["last_usd"] == 1.31413
    assert math.isclose(latest["mid_usd"], mid, rel_tol=0, abs_tol=1e-12)
    # Preserve the originally recorded value; the append-only correction below
    # supersedes only this derived spread field, not the captured market snapshot.
    assert latest["displayed_spread_bps"] == 0.076106
    correction = json.loads(
        (ROOT / "research/xrp_intelligence/20261105T093117Z-xrp-market-snapshot-spread-correction.json").read_text(encoding="utf-8")
    )
    corrected = correction["correction"]
    assert corrected["original_value_bps"] == latest["displayed_spread_bps"]
    assert math.isclose(corrected["recomputed_exact_bps"], spread, rel_tol=0, abs_tol=2e-12)
    assert corrected["corrected_value_rounded_6dp"] == 0.076105
    observed_change = (latest["last_usd"] / first - 1) * 100
    assert math.isclose(latest["change_from_090232_snapshot_pct"], observed_change, abs_tol=0.002)
    assert latest["source_event_timestamp"].startswith("not returned")
    assert latest["model_eligible"] is False


def test_binance_xrp_drain_and_redistribution_are_separate_ledger_events():
    event = load()["binance_security_event"]
    transfers = event["initial_transfer_ctids"]
    assert len(transfers) == 5
    assert math.isclose(sum(x["amount_xrp"] for x in transfers), 233461943.1, abs_tol=1e-6)
    assert event["stolen_xrp_approx"] == 233461943.1
    redistribution = event["nov2_redistribution"]
    assert redistribution["bulk_transfer_count"] == 9
    assert redistribution["bulk_recipient_count"] == 6
    assert redistribution["test_transfer_count"] == 7
    assert redistribution["bulk_amount_xrp"] + redistribution["test_amount_xrp"] == redistribution["recipient_total_xrp"]
    assert redistribution["reconciliation_gap_xrp"] == 0.59905
    assert redistribution["exchange_deposit_pattern_as_of_snapshot"] is False
    assert redistribution["ownership"].startswith("unresolved")


def test_rlusd_ethereum_and_xrpl_incident_flows_are_not_conflated():
    flows = load()["binance_security_event"]["rlusd_flows"]
    eth = flows["ethereum"]
    xrpl = flows["xrpl"]
    assert eth["stolen_rlusd"] == eth["swapped_on_dex_rlusd"] + eth["frozen_by_ripple_rlusd"]
    assert eth["network"] == "Ethereum"
    assert xrpl["network"] == "XRP Ledger"
    assert xrpl["amount_rlusd"] == 51172508
    assert xrpl["purpose"] == "unresolved"
    assert "Do not conflate" in flows["separation_rule"]


def test_binance_replenishment_percentage_disagreement_is_preserved():
    event = load()["binance_security_event"]
    history = event["replenishment_history_disagreement"]
    assert [row["reported_pct"] for row in history] == [90, 98, 98]
    assert "Do not average" in event["replenishment_history_rule"]
    assert "not XRP-specific" in event["replenishment_scope"]
    assert "no evidence" in event["attack_chain_interpretation"].lower()


def test_latest_xrpl_node_views_do_not_claim_lending_activation():
    protocol = load()["xrpl_protocol"]
    votes = protocol["current_voting_snapshot"]
    disagreement = protocol["node_view_disagreement"]
    assert votes["ledger_index"] == 108128511
    assert votes["LendingProtocol_votes_for"] == 19
    assert votes["votes_required"] == 29
    assert disagreement["difference_ledgers"] == 214
    assert "Different explorer node/page views" in disagreement["interpretation"]



def test_binance_impact_and_freeze_totals_keep_source_cutoffs_separate():
    event = load()["binance_security_event"]
    binance = event["third_party_reconciliation"]["binance_nov3"]
    trm = event["third_party_reconciliation"]["trm_oct29"]
    assert binance["total_impacted_usd"] == 6340000000
    assert binance["frozen_or_intercepted_usd"] == 2850000000
    assert trm["total_outflow_usd_approx"] == 6360000000
    assert trm["frozen_onchain_usd_approx"] == 2700000000
    assert "Do not average" in event["third_party_reconciliation"]["rule"]
    attribution = event["attribution_disagreement"]
    assert "FBI" in attribution["law_enforcement"]
    assert "TRM" in attribution["independent_intelligence"]
    assert "denied" in attribution["state_denial"]
    assert "not a court judgment" in attribution["assessment"]
    assert any(source["id"] == "ap_north_korea_denial_binance_incident" for source in load()["source_registry"])


def test_spread_correction_is_append_only_and_limited_to_derived_metric():
    correction = json.loads(
        (ROOT / "research/xrp_intelligence/20261105T093117Z-xrp-market-snapshot-spread-correction.json").read_text(encoding="utf-8")
    )
    assert correction["applies_to"]["artifact_id"] == "20261105T090232Z-xrp-market-derivatives-etf-circle-macro-reconciliation"
    assert correction["applies_to"]["field_path"] == "market_snapshot.spot.latest_recheck.displayed_spread_bps"
    assert correction["applies_to"]["original_artifact_modified"] is False
    assert correction["correction"]["original_value_bps"] == 0.076106
    assert correction["correction"]["corrected_value_rounded_6dp"] == 0.076105
    assert correction["source_capture"]["raw_http_bytes_captured"] is False
    assert correction["model_eligible"] is False
    assert correction["forecast_issued"] is False



def test_current_perpetual_oi_providers_preserve_contract_universe_disagreement():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/20261105T1345Z-xrp-perpetual-oi-provider-reconciliation.json").read_text(encoding="utf-8")
    )
    market = data["market_snapshot"]
    kod = market["kodexius"]
    trad = market["tradradar"]
    comparison = data["comparison"]
    assert sum(kod["exchange_open_interest_usd"].values()) == 885790000
    assert sum(trad["exchange_open_interest_usd"].values()) == 2041730000
    assert comparison["overlapping_exchange_universe"] == ["Binance", "Bybit", "Hyperliquid", "OKX"]
    assert comparison["overlapping_venue_difference_usd"] == 377260000
    assert comparison["status"] == "MATERIAL_UNRESOLVED_PROVIDER_AND_CONTRACT_SCOPE_DISAGREEMENT"
    assert comparison["reported_total_ratio_tradradar_to_kodexius"] > 2.3
    assert comparison["rule"].startswith("Do not average")


def test_current_perpetual_oi_snapshot_preserves_positioning_semantics_and_quarantine():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/20261105T1345Z-xrp-perpetual-oi-provider-reconciliation.json").read_text(encoding="utf-8")
    )
    trad = data["market_snapshot"]["tradradar"]
    assert trad["long_account_share_pct"] == 76.2
    assert trad["long_short_account_ratio"] == 3.21
    assert trad["short_liquidations_usd"] == 3600000
    assert trad["long_liquidations_usd"] == 1750000
    assert trad["liquidations_24h_floor_usd"] == 5350000
    assert "not position notional" in trad["long_short_semantics"]
    assert data["raw_capture"]["raw_source_bytes_preserved"] is False
    assert data["raw_capture"]["sha256"] is None
    assert data["model_eligibility"]["eligible"] is False
    assert data["model_eligibility"]["forecast_issued"] is False
    assert data["model_eligibility"]["forecast_status"] == "NOT_ISSUED"
    assert data["source_independence"]["independent_economic_corroboration"] is False
