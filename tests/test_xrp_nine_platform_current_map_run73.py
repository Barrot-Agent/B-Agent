from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json"


def load_current():
    return json.loads(CURRENT.read_text(encoding="utf-8"))


def test_current_map_schema_and_capture_timestamps_are_consistent():
    data = load_current()
    assert data["artifact_type"] == "nine_platform_capability_authentication_permission_dataflow_map"
    assert data["schema_version"] == "1.1.0"
    captured = datetime.fromisoformat(data["captured_at_utc"].replace("Z", "+00:00"))
    verified = datetime.fromisoformat(data["last_verified_at_utc"].replace("Z", "+00:00"))
    assert verified >= captured
    assert data["repository"] == "Barrot-Agent/B-Agent"
    assert data["observed_main_sha"] == data["repository_state"]["main_sha"]


def test_primary_mission_and_v3_foundation_are_explicit():
    data = load_current()
    assert data["mission_priority"] == 1
    assert data["mission"] == "XRP intelligence and prediction-engine mastery"
    assert data["foundation"].startswith("Barrot V3 execution, orchestration, safety and verification")
    assert data["forecast_status"] == "NOT_ISSUED"


def test_nine_platform_map_verifies_only_the_current_chatgpt_connector():
    data = load_current()
    expected = {"ChatGPT", "Claude", "Grok", "Gemini", "Copilot", "Codex", "Hugging Face", "Kaggle", "Databricks"}
    assert set(data["platforms"]) == expected
    chatgpt = data["platforms"]["ChatGPT"]
    assert chatgpt["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert chatgpt["data_flow"]["verified"] is True
    assert chatgpt["data_flow"]["persistent_agent_connection"] is False
    for name, platform in data["platforms"].items():
        if name != "ChatGPT":
            assert platform["data_flow"]["verified"] is False


def test_lunaroute_is_declared_but_not_authenticated():
    brain = load_current()["primary_brain_declared_by_repository"]
    assert brain["name"] == "LunaRoute"
    assert brain["status"] == "DECLARED_NOT_AUTHENTICATED"
    assert brain["verified"] is False


def test_nine_platform_coordination_is_design_only_without_external_exchange():
    data = load_current()
    status = data["coordination_status"]
    assert status["status"] == "DESIGNED_NOT_EXECUTED"
    assert status["no_external_model_data_transfer"] is True
    assert status["structured_evidence_exchange_across_nine_platforms"] is False
    assert status["no_external_model_data_transfer"] is True
    assignments = data["task_assignments_designed_not_executed"]
    assert len(assignments) == 9
    assert sum(item["status"] == "EXECUTED_IN_CURRENT_SESSION" for item in assignments) == 1


def test_least_privilege_and_external_action_gates_remain_closed():
    safety = load_current()["least_privilege_and_safety"]
    for key in (
        "secret_values_read",
        "credentials_exported",
        "unverified_platforms_used",
        "external_model_data_transfer",
        "external_publication",
        "deployment",
        "kaggle_submission",
        "paper_trade",
        "real_money_action",
        "main_branch_write_performed",
    ):
        assert safety[key] is False
    assert safety["pages_deployment_authorized"] is False
    assert safety["main_branch_protected_flag"] is True
    assert "HTTP 403" in safety["branch_protection_status"]
    assert "required checks and approval rules NOT_VISIBLE" in safety["branch_protection_status"]
    exposure = safety["credential_path_exposure"]
    assert exposure["path"] == ".config/gh/hosts.yml"
    assert exposure["main_branch_contains_path"] is False
    assert exposure["active_integration_branch_contains_path"] is False
    assert exposure["other_open_pr_tips_checked"] == 17
    assert exposure["other_open_pr_tips_containing_path"] == 17
    assert exposure["revocation_independently_verified"] is False


def test_repository_snapshot_matches_current_main_and_successor_branch():
    data = load_current()
    state = data["repository_state"]
    assert state["main_sha"] == "84f28ee7755607236231545a14f3d093c1baaa85"
    assert data["integration_branch"] == "integration/xrp-v3-unified-main-20261111"
    assert state["integration_pr"] == 1661
    assert state["integration_head_before_current_map_commit"] == data["integration_pr"]["head_sha"]
    assert state["integration_ahead_by"] == data["integration_pr"]["ahead_by"]
    assert state["integration_behind_by"] == data["integration_pr"]["behind_by"]
    assert state["changed_files"] == data["integration_pr"]["changed_files"]
    assert state["workflow_files_changed"] == 44
    assert state["non_workflow_paths_changed"] == data["integration_pr"]["other_changed_paths"]
    assert state["main_tree_entries"] == 1388
    assert state["integration_tree_entries"] > state["main_tree_entries"]
    assert state["orbit_paths_in_integration"] is False
    assert state["hf_space_app_py_changed"] is False


def test_superseded_pr_1660_is_retained_until_successor_merge():
    data = load_current()
    current = data["integration_pr"]
    old = data["superseded_integration_pr"]
    assert current["number"] == 1661
    assert current["state"] == "open"
    assert current["draft"] is True
    assert current["behind_by"] == 0
    assert old["number"] == 1660
    assert old["state"] == "open"
    assert old["draft"] is True
    assert old["behind_by"] == 3
    assert "RETAINED_UNTIL_SUCCESSOR_MERGE" in old["disposition"]
    assert current["head_sha"] == data["repository_state"]["integration_head_before_current_map_commit"]
    assert current["formal_approvals"] == 0


def test_exact_head_ci_evidence_is_scoped_to_the_tested_parent_head():
    data = load_current()
    ci = data["ci_evidence"]
    assert ci["integration_head_tested"] == "3b11e39f253ac8d07d02eb5da0c770155614f814"
    suite = ci["full_repository_suite"]
    assert suite["passed"] == 3407
    assert suite["failed"] == 0
    assert suite["subtests"] == 8
    assert suite["coverage_percent"] == 59.98
    assert suite["exact_head_verified"] is True
    latest = ci["latest_attempt"]
    assert latest["head_sha"] == data["integration_pr"]["head_sha"]
    suite = latest["full_repository_suite"]
    assert suite["passed"] > 0
    assert suite["failed"] == len(latest["failing_tests"])
    assert suite["subtests"] == 8
    assert suite["exact_head_verified"] is True
    assert latest["conclusion"] == ("failure" if suite["failed"] else "success")
    assert "current map schema regression" in latest["failure_classification"].lower()
    assert "not a runtime prediction-engine failure" in latest["failure_classification"].lower()
    assert ci["dependency_audit"]["manifests"] == 6
    assert ci["dependency_audit"]["known_vulnerabilities"] == 0
    assert ci["dependency_audit"]["passed"] is True
    assert ci["fail_closed_gate"]["passed"] is True
    assert ci["fail_closed_gate"]["automatic_merge_enabled"] is False


def test_workflow_review_counts_and_xrp_collector_branch_scope_are_explicit():
    audit = load_current()["workflow_safety_audit"]
    assert audit["changed_workflow_files"] == 44
    assert audit["quarantined_or_disabled"] == 25
    assert audit["active_changed_workflows"] == 19
    assert audit["xrp_public_ingestion_workflow_on_main"] is False
    assert audit["xrp_public_ingestion_workflow_on_integration"] is True
    assert audit["scheduled_ingestion_main_run_verified"] is False
    assert "no repository content write permission" in audit["xrp_collector_permissions"]
    assert audit["ci_trigger_optimization"]["committed_in_this_update"] is True
    assert audit["ci_trigger_optimization"]["new_push_branches"] == ["main"]
    assert audit["ci_trigger_optimization"]["full_suite_job_preserved"] is True


def test_prediction_engine_source_registry_counts_are_consistent():
    engine = load_current()["prediction_engine_status"]
    assert engine["source_definitions_total"] == 46
    assert engine["hourly_sources"] == 42
    assert engine["weekly_cftc_sources"] == 2
    assert engine["scheduled_sources"] == 44
    assert engine["excluded_noncommercial_xrpl_node_sources"] == 2
    assert len(engine["implemented"]) >= 8


def test_prediction_engine_production_gaps_keep_forecasts_disabled():
    engine = load_current()["prediction_engine_status"]
    for key in (
        "main_branch_ingestion_verified",
        "mature_synchronized_history",
        "out_of_sample_lift",
        "real_data_calibration",
        "shadow_outcomes",
        "trusted_evaluator_key",
        "independent_worm_archive",
    ):
        assert engine[key] is False
    gaps = " ".join(engine["not_production_verified"]).lower()
    assert "scenario and counter-hypothesis generation" in gaps
    assert "effective-sample-size correction" in gaps
    assert "synchronized multi-venue historical" in gaps
    assert engine["forecast_status"] == "NOT_ISSUED"


def test_spot_snapshot_preserves_provider_event_time_and_window_semantics():
    market = load_current()["current_market_snapshot"]
    okx = market["spot"]["okx"]
    kraken = market["spot"]["kraken"]
    assert okx["pair"] == "XRP-USDT"
    event_time = datetime.fromisoformat(okx["event_time_utc"].replace("Z", "+00:00"))
    retrieved_at = datetime.fromisoformat(market["retrieved_at_utc"].replace("Z", "+00:00"))
    assert event_time <= retrieved_at
    assert okx["last"] > 0
    assert 0 < okx["bid"] <= okx["ask"]
    assert okx["low_24h"] <= okx["last"] <= okx["high_24h"]
    assert okx["volume_24h_xrp"] > 0
    assert kraken["pair"] == "XRP/USD"
    assert kraken["utc_day_open"] > 0
    assert "UTC-day open" in kraken["field_semantics"]
    cross_venue_note = market["spot"]["cross_venue_note"].lower()
    assert "kraken utc-day open" in cross_venue_note
    assert "okx rolling 24-hour open" in cross_venue_note
    assert kraken["event_timestamp_available"] is False
    assert kraken["repeated_response_same_as_prior_capture"] is True


def test_spot_orderbook_is_resting_liquidity_not_guaranteed_support():
    market = load_current()["current_market_snapshot"]
    book = market["spot_order_book"]
    assert book["provider"] == "Fuelmaps"
    snapshot_time = datetime.fromisoformat(book["snapshot_time_utc"].replace("Z", "+00:00"))
    retrieved_at = datetime.fromisoformat(market["retrieved_at_utc"].replace("Z", "+00:00"))
    assert snapshot_time <= retrieved_at
    assert "6 of 6" in book["venues_coverage"]
    depth = book["depth_usd"]["within_1_percent"]
    assert depth["bids"] > 0
    assert depth["asks"] > 0
    assert 0 <= depth["bid_share_percent"] <= 100
    assert {"Binance", "Bitget"}.issubset(set(book["exclusions"]))
    limitations = " ".join(book["limitations"]).lower()
    assert "resting orders can be cancelled" in limitations
    assert "not executed volume" in limitations


def test_exchange_flow_snapshot_keeps_unattributed_transfer_separate():
    flows = load_current()["current_market_snapshot"]["exchange_flows"]
    assert flows["period"] == "preceding 7 days"
    assert flows["inflows_xrp"] == 501_720_000
    assert flows["outflows_xrp"] == 602_930_000
    assert flows["net_flow_xrp"] == flows["inflows_xrp"] - flows["outflows_xrp"]
    assert flows["largest_transfer_xrp"] == 368_480_000
    assert flows["largest_transfer_label"] == "unknown wallet; not attributed to an exchange"
    assert any("not comprehensive exchange-reserve accounting" in x for x in flows["limitations"])


def test_derivatives_provider_disagreement_is_preserved_without_averaging():
    d = load_current()["current_market_snapshot"]["derivatives"]
    oi = {
        d["coinglass"]["open_interest_usd"],
        d["tradradar"]["open_interest_usd"],
        d["liqwall_previous_snapshot"]["open_interest_usd"],
    }
    assert oi == {2_340_000_000, 1_560_000_000, 1_160_000_000}
    assert d["coinglass"]["funding_8h_percent"] > 0
    assert d["coinglass"]["long_liquidation_share_percent"] == 94
    assert "not averaged" in d["reconciliation"]
    assert "not a price-direction forecast" in d["reconciliation"]


def test_options_snapshot_keeps_near_and_deferred_expiry_skew_distinct():
    options = load_current()["current_market_snapshot"]["options"]
    assert options["snapshot_time_utc"] == "2026-11-11T05:00:00Z"
    assert options["atm_iv_30d_percent"] == 59
    assert options["skew_25d_30d_points"] == 0.3
    assert options["expiry_skews_points"]["2026-11-11"] == -11
    assert options["expiry_skews_points"]["2026-12-25"] == 0.9
    assert options["put_call_ratio"] == 0.55


def test_etf_flow_windows_and_holdings_limitations_are_separate():
    market = load_current()["current_market_snapshot"]
    etf = market["etf_flows"]
    alpha = etf["alpha_finance"]
    crypto = etf["cryptokeyhole_previous_capture"]
    assert alpha["through_session"] == "2026-11-10"
    assert alpha["daily_flow_nov10_usd"] == -7_600_000
    assert alpha["consecutive_daily_outflows"] == 2
    assert alpha["thirty_session_flow_usd"] == 1_300_000
    assert "RESEARCH_ONLY_NOT_MODEL_ELIGIBLE" in market["point_in_time_eligibility"]
    assert crypto["nov10_status"].startswith("partial")
    assert crypto["latest_complete_net_flow_xrp"] == -752_048
    assert "missing issuer data is unknown, not zero" in " ".join(crypto["limitations"]).lower()
    assert "do not average provider universes" in etf["reconciliation"].lower()


def test_cftc_contract_reconciliation_treats_dropped_contract_as_unknown():
    cftc = load_current()["current_market_snapshot"]["cftc"]
    assert cftc["source_as_of"] == "2026-11-03"
    assert cftc["report_updated"] == "2026-11-06"
    assert cftc["contract_equivalent_xrp"] == 396_248_500
    assert cftc["prior_week_equivalent_xrp"] == 455_163_000
    assert cftc["weekly_change_xrp"] == -58_914_500
    assert cftc["dropped_standard_coinbase_xrp_contract_code"] == "176LM2"
    assert cftc["missing_contract_handling"] == "missing is not zero"


def test_institutional_and_capital_relationships_keep_entities_and_categories_separate():
    inst = load_current()["institutional_and_capital"]
    assert inst["rlusd"]["circulating_usd"] == 2_632_900_000
    assert inst["rlusd"]["reserve_funds_usd"] == 2_748_000_000
    assert inst["rlusd"]["issuer"] == "Standard Custody & Trust Company, LLC"
    assert "Do not conflate RLUSD issuer Standard Custody" in inst["rlusd"]["note"]
    assert "future/coming" in inst["ripple_coinbase"]["collateral"]
    assert "50/50 Centre Consortium ownership" in inst["circle_coinbase"]["relationship"]
    assert "not XRP" in inst["pnc_coinbase_circle"]["status"]
    assert inst["sbi_ripple_circle"]["evernorth_cash_investment_usd"] == 200_000_000
    assert inst["sbi_ripple_circle"]["sbi_ripple_asia"] == "60/40 SBI/Ripple joint venture."
    ev = inst["evernorth"]
    assert ev["closing_gross_cash_usd"] == 272_600_000
    assert ev["xrp_contributed_in_kind"] == 388_910_554
    assert ev["xrp_purchased_with_advance_funding_cash"] == 84_365_876
    assert ev["separate_eloc_proceeds_received_as_of_2026_11_09"] == 0


def test_identity_research_keeps_sbic_ask_actual_capital_and_kamilah_gates():
    identity = load_current()["identity_research"]
    sbic = identity["sbic"]
    assert sbic["east"].startswith("Tokyo Small and Medium Business")
    assert sbic["central"].startswith("Nagoya Small and Medium Business")
    assert sbic["west"].startswith("Osaka Small and Medium Business")
    assert "not SBI Holdings" in sbic["distinction"]
    assert "not evidence of an OpenAI commercial partnership" in sbic["chatgpt_event"]
    assert "June 12-13, 2025" in sbic["chatgpt_event"] and "VOST" in sbic["chatgpt_event"]
    assert "No XRP-linked ASK Coin identity" in identity["ask_coin"]
    assert "UCID 4640" in identity["ask_coin"] and "UCID 7105" in identity["ask_coin"]
    assert "askcoin.net" in identity["ask_coin"] and "HugeDomains" in identity["ask_coin"]
    assert "not a standardized xrp metric" in identity["actual_capital"].lower()
    assert "remain unverified" in identity["kamilah_stevenson"]
    assert "No personal-channel inventory is attributed" in identity["kamilah_stevenson"]


def test_macro_and_geopolitical_observations_keep_competing_hypotheses():
    macro = load_current()["macro_geopolitics"]
    cpi = macro["us_cpi_october_2026"]
    assert cpi["headline_monthly_percent"] == 0.4
    assert cpi["core_monthly_percent"] == 0.3
    assert "not published" in cpi["year_over_year"]
    oil = macro["hormuz_and_oil"]
    assert oil["date"] == "2026-11-11"
    assert len(oil["competing_hypotheses"]) == 2
    assert "not automatic XRP directional signals" in macro["interpretation"]


def test_disagreements_and_counterhypotheses_are_preserved():
    items = load_current()["disagreement_and_counter_hypotheses"]
    assert len(items) >= 6
    combined = " ".join(items).lower()
    assert "no average is computed" in combined
    assert "counter-hypothesis" in combined or "counter hypothesis" in combined
    assert "neither is a directional forecast" in combined
    assert "etf flow coverage disagreement" in combined


def test_source_provenance_and_backlog_classification_are_explicit():
    data = load_current()
    sources = data["source_provenance"]
    assert len(sources) >= 15
    assert all(item.get("url") and item.get("source") for item in sources)
    assert any(item["source"] == "CFTC TFF" for item in sources)
    assert any(item["source"] == "SEC Evernorth 424B3" for item in sources)
    assert any(item["source"] == "CoinMarketCap Askcoin preview listing UCID 4640" for item in sources)
    assert any(item["source"] == "CryptoKeyhole ETF flows dashboard" for item in sources)
    assert any(item["source"] == "Tokyo SBIC official generative-AI training notice" for item in sources)
    backlog = data["backlog_classification"]
    assert backlog["1661"].startswith("BLOCKED_ACTIVE_INTEGRATION_DRAFT")
    assert "SUPERSEDED_SOURCE" in backlog["1660"]
    assert "UNIQUE_UNREVIEWED" in backlog["1653"]
    assert "UNIQUE_UNREVIEWED" in backlog["1614"]
    assert any("semantic review" in item.lower() for item in data["next_actions"])


def test_latest_market_refresh_is_research_only_and_preserves_provider_disagreement():
    refresh = load_current()["latest_market_refresh"]
    assert refresh["point_in_time_eligibility"].startswith("RESEARCH_ONLY_NOT_MODEL_ELIGIBLE")
    assert refresh["raw_source_receipts"]["captured_by_barrot"] is False
    captured = datetime.fromisoformat(refresh["captured_at_utc"].replace("Z", "+00:00"))
    okx = refresh["spot"]["okx"]
    event = datetime.fromisoformat(okx["event_time_utc"].replace("Z", "+00:00"))
    assert event <= captured
    assert 0 < okx["bid"] <= okx["ask"]
    kraken = refresh["spot"]["kraken"]
    assert kraken["event_timestamp_available"] is False
    assert "UTC-day open" in kraken["field_semantics"]
    assert 0 < abs(refresh["spot"]["normalized_spread_vs_kraken_mid_percent"]) < 1
    depth = refresh["spot_order_book"]["latest_primary_aggregated_snapshot"]
    assert depth["snapshot_time_utc"] <= refresh["captured_at_utc"]
    assert "resting orders can be cancelled or moved" in " ".join(depth["limitations"]).lower()
    derivatives = refresh["derivatives"]
    assert len({derivatives[k]["open_interest_usd"] for k in ("tradradar", "liqwall", "alpha_heatmap")}) == 3
    assert "not averaged" in derivatives["reconciliation"]
    etf = refresh["etf_flows"]
    assert etf["alpha_finance"]["funds_complete"] == "5 of 5 tracked"
    assert etf["cryptoetf_today"]["funds_reported"] == "4 of 5"
    assert "do not average" in etf["reconciliation"].lower()
    assert load_current()["forecast_status"] == "NOT_ISSUED"
