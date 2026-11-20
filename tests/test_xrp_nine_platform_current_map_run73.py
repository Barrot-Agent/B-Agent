from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import ENDPOINTS, SCHEDULED_ENDPOINTS, WEEKLY_ENDPOINTS
from barrot_agent.evolution.forecast_ledger import (
    READINESS_POLICY_ID,
    _MAX_WEIGHTED_CALIBRATION_ERROR,
    _MIN_HORIZON_MULTIPLE,
    _MIN_OOS_SAMPLES,
    _MIN_SHADOW_SAMPLES,
    _MIN_SOURCE_GROUPS,
)

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
    assert exposure["other_open_pr_tips_checked"] == 15
    assert exposure["other_open_pr_tips_containing_path"] == 15
    assert exposure["path_absent_from_all_current_pr_file_inventories"] is True
    assert exposure["other_closed_pr_tips_checked"] == 2
    assert exposure["other_closed_pr_tips_containing_path"] == 2
    assert exposure["all_17_target_prs_open_and_base_main"] is False
    assert exposure["all_17_target_prs_base_main"] is True
    assert exposure["same_blob_sha"] == "f58b27f14436088db99662d3a45c59b8437ec3a1"
    assert exposure["same_blob_size_bytes"] == 216
    assert exposure["provider_side_revocation_verified"] is False
    assert exposure["revocation_independently_verified"] is False
    assert exposure["branch_tip_presence_verified_via_recursive_tree"] is True
    assert exposure["credential_contents_read"] is False
    assert exposure["affected_pr_numbers"] == [1653, 1650, 1649, 1648, 1647, 1646, 1645, 1644, 1643, 1642, 1640, 1320, 1318, 1317, 1269, 1255, 1254]


def test_repository_snapshot_matches_current_main_and_successor_branch():
    data = load_current()
    state = data["repository_state"]
    assert state["main_sha"] == data["observed_main_sha"]
    assert data["integration_branch"] == "integration/xrp-v3-unified-main-20261112"
    assert state["integration_pr"]["number"] == 1662
    assert state["integration_pr"] == data["integration_pr"]
    assert state["integration_head_before_current_map_commit"] == data["integration_pr"]["head_sha"]
    assert state["integration_ahead_by"] == data["integration_pr"]["ahead_by"]
    assert state["integration_behind_by"] == data["integration_pr"]["behind_by"]
    assert state["changed_files"] == data["integration_pr"]["changed_files"]
    assert state["workflow_files_changed"] == 48
    assert state["non_workflow_paths_changed"] == data["integration_pr"]["other_changed_paths"]
    assert state["main_tree_entries"] == 1393
    assert state["integration_tree_entries"] > state["main_tree_entries"]
    assert state["orbit_paths_in_integration"] is False
    assert state["hf_space_app_py_changed"] is True
    assert state["hf_space_app_font_preserved"] is True
    assert state["orbit_paths_changed_in_pr"] is False
    assert state["active_orbit_runtime_reintroduced"] is False


def test_superseded_pr_1660_is_retained_until_successor_merge():
    data = load_current()
    current = data["integration_pr"]
    old = data["superseded_integration_pr"]
    assert current["number"] == 1662
    assert current["state"] == "open"
    assert current["draft"] is True
    assert current["behind_by"] == 0
    assert old["number"] == 1660
    assert old["state"] == "open"
    assert old["draft"] is True
    assert old["behind_by"] == 52
    assert "retained until successor merge" in old["disposition"].lower().replace("_", " ")
    assert "exact main-file verification" in old["disposition"].lower()
    assert current["head_sha"] == data["repository_state"]["integration_head_before_current_map_commit"]
    assert current["formal_approvals"] == 0


def test_exact_head_ci_evidence_is_scoped_to_the_tested_parent_head():
    data = load_current()
    ci = data["ci_evidence"]
    latest = ci["latest_attempt"]
    suite = ci["full_repository_suite"]
    latest_suite = latest["full_repository_suite"]
    assert ci["integration_head_tested"] == latest["head_sha"]
    assert suite["passed"] == latest_suite["passed"]
    assert suite["failed"] == latest_suite["failed"]
    assert suite["subtests"] == latest_suite["subtests"]
    assert suite["coverage_percent"] == latest_suite["coverage_percent"]
    assert suite["exact_head"] is True
    latest = ci["latest_attempt"]
    run162_parent = data["run162_snapshot"]
    parent_suite = run162_parent["ci"]["full_repository_suite"]
    assert parent_suite["head_sha"] == run162_parent["integration_head_before_map_commit"]
    assert parent_suite["passed"] == 3781
    assert parent_suite["failed"] == 7
    assert parent_suite["exact_head"] is True
    assert len(parent_suite["failing_tests"]) == 7
    assert any("current_map" in name for name in parent_suite["failing_tests"])
    assert "exact-head full-suite failed" in run162_parent["ci"]["failure_classification"].lower()
    assert ci["dependency_audit"]["manifests"] == 6
    assert ci["dependency_audit"]["known_vulnerabilities"] == 0
    assert ci["dependency_audit"]["passed"] is True
    assert ci["fail_closed_gate"]["passed"] is True
    assert ci["fail_closed_gate"]["automatic_merge_enabled"] is False


def test_workflow_review_counts_and_xrp_collector_branch_scope_are_explicit():
    audit = load_current()["workflow_safety_audit"]
    assert audit["changed_workflow_files"] == 50
    assert audit["quarantined_or_disabled"] == 26
    assert audit["active_changed_workflows"] == 24
    # Recorded patch-body count; the historical changed-workflow inventory is 50.
    assert audit["patch_scan_workflows_reviewed"] == 47
    assert audit["manual_dispatch_additions"] == 29
    assert audit["secondary_brain_deployment_quarantined"] is True
    assert audit["xrp_public_ingestion_workflow_on_main"] is False
    assert audit["xrp_public_ingestion_workflow_on_integration"] is True
    assert audit["scheduled_ingestion_main_run_verified"] is False
    assert "no repository content write permission" in audit["xrp_collector_permissions"]
    assert audit["ci_trigger_optimization"]["committed_in_this_update"] is True
    assert audit["ci_trigger_optimization"]["new_push_branches"] == ["main"]
    assert audit["ci_trigger_optimization"]["full_suite_job_preserved"] is True


def test_lunaroute_only_architecture_quarantines_secondary_brain_deployment():
    workflow = ROOT / ".github/workflows/sync-self-hosted-brain.yml"
    content = workflow.read_text(encoding="utf-8")
    assert "if: ${{ false &&" in content
    permissions = content.split("permissions:", 1)[1].split("jobs:", 1)[0]
    assert "contents: read" in permissions
    assert "write" not in permissions
    assert "inputs.confirm == 'YES'" in content
    assert "inputs.confirm_secret_rotation == 'YES'" in content
    assert "inputs.expected_main_sha == github.sha" in content
    audit = load_current()["workflow_safety_audit"]
    assert audit["secondary_brain_deployment_quarantined"] is True
    assert audit["self_hosted_brain_workflow_status"] == "DISABLED_LUNAROUTE_ONLY"


def test_current_collector_expands_preserved_run175_registry_snapshot():
    snapshot = load_current()
    engine = snapshot["prediction_engine_status"]
    # The map was captured on Nov 15; its 51/46/49 counts remain historical, not current.
    assert snapshot["captured_at_utc"] == "2026-11-15T21:29:23Z"
    assert engine["source_definitions_total"] == 51
    assert engine["hourly_sources"] == 46
    assert engine["weekly_cftc_sources"] == 3
    assert engine["scheduled_sources"] == 49
    # Current registry: 48 hourly + 3 weekly + 2 non-commercial public-node endpoints.
    assert len(ENDPOINTS) == 53
    assert len(SCHEDULED_ENDPOINTS) == 48
    assert len(WEEKLY_ENDPOINTS) == 3
    assert len(ENDPOINTS) == len(SCHEDULED_ENDPOINTS) + len(WEEKLY_ENDPOINTS) + 2
    scheduled_ids = {source_id for source_id, _url in SCHEDULED_ENDPOINTS}
    assert {"bitstamp_spot_ticker", "bitstamp_spot_depth"} <= scheduled_ids
    assert engine["excluded_noncommercial_xrpl_node_sources"] == 2
    assert engine["raw_only_derivatives_sources"] == 2
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
    assert "scenario outputs remain authored research hypotheses without forecast probabilities" in gaps
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
    data = load_current()
    capital = data["institutional_and_capital"]["evernorth"]
    assert capital["advance_funding_cash_exact_usd"] == 214049995
    assert capital["sbi_200m_included_in_advance_funding_pool"] is True
    assert capital["cantor_eloc"]["proceeds_received_as_of_2026_11_09_usd"] == 0
    assert capital["resale_registration_detail"]["company_proceeds_from_selling_holder_resales_usd"] == 0
    assert capital["convertible_senior_pik_note"]["principal_usd"] == 30000000
    assert capital["in_kind_share_of_reported_closing_xrp_percent"] == 82.17
    sbi = data["institutional_and_capital"]["sbi_ripple_circle"]
    assert sbi["circle_equity_investment_usd"] == 50000000
    assert sbi["circle_investment_split_usd"] == {"SBI Holdings": 25000000, "SBI Shinsei Bank": 25000000}
    assert "remain unverified" in identity["kamilah_stevenson"]
    assert "no personal-channel video inventory is attributed" in identity["kamilah_stevenson"].lower()


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


def test_source_provenance_and_current_backlog_classification_are_explicit():
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
    assert backlog["1662"].startswith("BLOCKED_ACTIVE_INTEGRATION_DRAFT")
    assert "SUPERSESSION_CANDIDATE" in backlog["1661"]
    assert "50 blob differences" in backlog["1661"]
    assert "SUPERSESSION_CANDIDATE" in backlog["1660"]
    assert "59 blob differences" in backlog["1660"]
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


def test_run20_snapshot_is_append_only_and_preserves_original_branch_identity():
    data = load_current()
    run20 = data["run20_snapshot"]
    repo = run20["repository_state"]
    assert repo["main_sha"] == "84f28ee7755607236231545a14f3d093c1baaa85"
    assert data["repository_state"]["main_sha"] == data["observed_main_sha"]
    assert repo["integration_branch"] == "integration/xrp-v3-unified-main-20261111"
    assert data["repository_state"]["integration_branch"] == "integration/xrp-v3-unified-main-20261112"
    assert repo["integration_head_before_run20_map_commit"] == "0529030acf0df84e68d7626564b3d206dd95946b"
    assert repo["current_head_before_corrective_commit"] == "c39cc80591e257beb563aff1bf2a85d368edcb3b"
    assert repo["changed_files_after_run20_docs_commit"] == 995
    assert repo["workflow_files_changed"] == 44
    assert repo["non_workflow_paths_changed"] == 951
    current_head = data["repository_state"]["integration_head_before_current_map_commit"]
    assert current_head == data["integration_pr"]["head_sha"]
    assert len(current_head) == 40 and all(ch in "0123456789abcdef" for ch in current_head)
    assert data["latest_market_refresh"]["point_in_time_eligibility"].startswith("RESEARCH_ONLY_NOT_MODEL_ELIGIBLE")


def test_run20_market_refresh_preserves_point_in_time_and_provider_disagreement():
    run20 = load_current()["run20_snapshot"]
    refresh = run20["latest_market_refresh"]
    assert refresh["point_in_time_eligibility"].startswith("RESEARCH_ONLY_NOT_MODEL_ELIGIBLE")
    assert refresh["raw_source_receipts"]["captured_by_barrot"] is False
    assert refresh["spot"]["okx"]["event_time_utc"] <= refresh["captured_at_utc"]
    assert refresh["spot"]["kraken"]["event_timestamp_available"] is False
    assert "UTC-day open" in refresh["spot"]["kraken"]["field_semantics"]
    assert 0 < abs(refresh["spot"]["normalized_spread_vs_kraken_mid_percent"]) < 1
    depth = refresh["spot_order_book"]["latest_primary_aggregated_snapshot"]
    assert depth["snapshot_time_utc"] <= refresh["captured_at_utc"]
    assert "orders can be cancelled" in " ".join(depth["limitations"]).lower()


def test_run20_ci_failure_is_classified_as_map_schema_not_runtime_failure():
    ci = load_current()["run20_snapshot"]["ci_evidence"]
    parent = ci["parent_head_full_suite"]
    assert parent["passed"] == 3417
    assert parent["failed"] == 0
    assert parent["exact_head_verified"] is True
    latest = ci["latest_docs_head_attempt"]
    assert latest["passed"] == 3413
    assert latest["failed"] == 4
    assert latest["subtests"] == 8
    assert latest["conclusion"] == "failure"
    assert "map schema regression" in latest["failure_classification"].lower()
    assert "not a runtime prediction-engine failure" in latest["failure_classification"].lower()
    assert ci["dependency_audit"]["passed"] is True
    assert all(gate["passed"] for gate in ci["fail_closed_gates"])


def test_run20_evernorth_capital_reconciles_without_double_counting():
    capital = load_current()["run20_snapshot"]["actual_capital"]
    assert capital["sbi_group_cash_investment_usd"] == 200000000
    assert capital["sbi_group_cash_investment_usd"] <= capital["advance_funding"]["cash_usd"]
    assert capital["gross_cash_at_close_usd"] == 272600000
    assert capital["advance_funding_cash_used_to_purchase_xrp_usd"] == 214050000
    assert capital["xrp_purchased_with_advance_funding_cash"] == 84365876
    assert abs(capital["xrp_in_kind_sum_check"] - capital["total_xrp_in_kind"]) < 0.001
    assert capital["reported_xrp_holdings_as_of_2026_10_09_approx"] == 473000000
    assert capital["cantor_eloc"]["proceeds_as_of_2026_11_09_usd"] == 0
    assert capital["resale_registration"]["issuer_resale_proceeds_usd"] == 0
    assert capital["ownership_limits"]["arrington_sponsor_series_c_percent"] == 19.9
    assert "not a direct 19.9% owner" in capital["rippleworks"]


def test_run20_collateral_distinguishes_wrapped_cbxrp_from_native_xrpl_lending():
    collateral = load_current()["run20_snapshot"]["collateral"]
    cbxrp = collateral["coinbase_cbxrp"]
    assert cbxrp["reserves_xrp"] > cbxrp["supply_cbxrp"]
    assert abs(cbxrp["excess_reserve_xrp"] - 2246.54) < 0.01
    morpho = collateral["morpho_base_cbxrp"]
    assert morpho["debt_exposed_within_10_percent_usd"] == 8840000
    assert morpho["debt_exposed_within_5_percent_usd"] == 3230000
    lending = collateral["xrpl_lending"]
    assert lending["active"] is False
    assert lending["lending_protocol_yes"] == 22
    assert lending["validators"] == 35
    assert "uncollateralized" in lending["design"].lower()


def test_run20_sbi_and_sbic_entity_relationships_remain_separate():
    run20 = load_current()["run20_snapshot"]
    assert run20["identity"]["sbic_japan"]["entities"][0]["company"].startswith("Tokyo")
    assert run20["identity"]["sbic_japan"]["entities"][1]["company"].startswith("Nagoya")
    assert run20["identity"]["sbic_japan"]["entities"][2]["company"].startswith("Osaka")
    assert "not SBI Holdings" in run20["identity"]["sbic_japan"]["distinction"]
    assert run20["institutional"]["sbi_circle"]["ownership"] == {"sbi": 50, "circle": 50}
    assert run20["institutional"]["sbi_ripple"]["sbi_ripple_asia_sbi_group_voting_percent"] == 60
    assert run20["nine_platforms"]["Claude"] == "unverified"
    assert run20["nine_platforms"]["Databricks"] == "prior HTTP 403; no workspace write"
    assert run20["prediction_engine"]["forecast_status"] == "NOT_ISSUED"


def test_github_connector_admin_scope_is_explicitly_flagged():
    safety = load_current()["least_privilege_and_safety"]
    permissions = safety["github_connector_permissions"]
    assert permissions["admin"] is True
    assert permissions["maintain"] is True
    assert permissions["push"] is True
    assert safety["least_privilege_target_met"] is False
    assert safety["main_branch_write_performed"] is False
    assert safety["secret_values_read"] is False


def test_run23_research_remains_non_model_eligible_and_preserves_disagreement():
    run = load_current()["run23_snapshot"]
    assert run["model_eligible"] is False
    assert run["raw_source_receipts"]["captured_by_barrot"] is False
    balances = run["exchange_balances"]["xrp_insights"]
    assert balances["same_wallet_change_7d_xrp"] == 1_300_000
    assert balances["same_wallet_change_30d_xrp"] == -155_700_000
    assert run["external_flow_tracker"]["net_flow_xrp"] == -101_210_000
    assert run["flow_reconciliation"]["must_not_average"] is True
    evernorth = run["evernorth"]
    assert evernorth["on_chain_attributed_xrp"] == 103_129_905
    assert evernorth["moved_outside_attributed_set_xrp"] == 370_346_663
    assert evernorth["unattributed_destination_is_not_proof_of_sale"] is True
    assert run["forecast_status"] == "NOT_ISSUED"


def test_hf_space_safety_update_preserves_orbitron_typography():
    app = (ROOT / "hf_space/app.py").read_text(encoding="utf-8")
    assert "Orbitron" in app
    assert "Share+Tech+Mono" in app
    assert "BARROT_ALLOW_EXTERNAL_INFERENCE" in app
    assert "def _operator_allows_external_inference" in app
    assert "NOT_ISSUED" in app


def test_xrp_ingestion_artifact_retention_is_not_mislabeled_worm():
    engine = load_current()["prediction_engine_status"]
    retention = engine["scheduled_workflow_retention"]
    assert retention["raw_receipts_days"] == 90
    assert retention["per_run_feature_store_days"] == 7
    assert retention["daily_feature_store_days"] == 90
    assert retention["independent_worm"] is False
    assert engine["main_branch_ingestion_verified"] is False


def test_run67_snapshot_is_additive_and_preserves_model_eligibility_gates():
    data = load_current()
    snap = data["run67_snapshot"]
    assert snap["repository"]["main_sha"] == "b4e36c91c380da89e7b60d00f984bd7ac123ce74"
    assert snap["repository"]["integration_pr"] == 1662
    assert snap["repository"]["changed_files"] == 1075
    assert snap["ci"]["successful_code_head"] == "07aa7959b42f04832e1f328d1da86f392e8e54d8"
    assert snap["ci"]["full_suite_passed"] == 3543
    assert snap["ci"]["full_suite_failed"] == 0
    assert snap["ci"]["docs_head_failed"] == 15
    assert "schema regression" in snap["ci"]["docs_head_failure"].lower()
    assert snap["prediction"]["event_registry_events"] == 70
    assert snap["prediction"]["raw_source_sha256_present"] == 0
    assert snap["prediction"]["model_eligible_events"] == 0
    assert snap["prediction"]["forecast_status"] == "NOT_ISSUED"
    assert snap["market"]["no_fresh_l2"] is False
    assert snap["market"]["order_book"]["snapshot_time_utc"] == "2026-11-12T20:00:00Z"
    assert snap["market"]["order_book"]["mid_usd"] == 1.0315
    assert snap["market"]["order_book"]["bands"][0]["bids_usd"] == 8900000
    assert snap["market"]["order_book"]["excluded_venues"] == ["Binance", "Bitget"]
    assert snap["market"]["perpetual_order_book"]["open_interest_usd"] == 319000000
    assert snap["market"]["xrpl_dex_book_health"]["funded_quoted_ask_share_percent"]["Bitstamp_USD"] == 18.3
    no_external_actions = snap["no_external_actions"]
    expected_external_actions = {
        "merge", "source_pr_closure", "deployment", "secret_rotation",
        "space_restart", "databricks_write", "kaggle_submission", "paper_trade",
        "funds_transfer", "real_money", "force_push", "history_rewrite",
        "external_model_transfer",
    }
    assert set(no_external_actions) == expected_external_actions
    assert all(value is False for value in no_external_actions.values())
    assert data["current_market_snapshot"]["spot"]["okx"]["event_time_utc"] == "2026-11-11T07:50:55.569Z"
    assert data["current_market_snapshot"]["spot"]["kraken"]["event_timestamp_available"] is False
    assert data["current_market_snapshot"]["spot"]["kraken"]["repeated_response_same_as_prior_capture"] is True
    assert "stale" in data["current_market_snapshot"]["spot"]["kraken"]["staleness_note"].lower()
    assert isinstance(data["institutional_and_capital"]["rlusd"], dict)
    assert isinstance(data["identity_research"]["sbic"], dict)
    assert isinstance(data["source_provenance"], list)

def test_run152_run153_run154_run155_run158_run159_run162_run165_run167_run168_run169_and_run172_remain_historical_while_run173_is_current():
    data = load_current()
    run152 = data["run152_snapshot"]
    run153 = data["run153_snapshot"]
    run154 = data["run154_snapshot"]
    run155 = data["run155_snapshot"]
    run158 = data["run158_snapshot"]
    run159 = data["run159_snapshot"]
    corrective = run154["corrective_attempt"]
    final_verification = run154["final_verification"]
    latest = data["ci_evidence"]["run172_map_test_correction_attempt"]
    latest_current = data["ci_evidence"]["latest_attempt"]
    assert "run173_snapshot" in data
    assert latest_current["head_sha"] == data["run173_snapshot"]["integration_head_before_run173_commit"]
    assert latest_current["conclusion"] == "success"
    assert latest_current["full_repository_suite"]["passed"] == 3805
    assert latest_current["full_repository_suite"]["failed"] == 0
    run165 = data["run165_snapshot"]
    assert run165["main_sha"] == data["repository_state"]["main_sha"]
    assert run165["pr_number"] == 1662
    assert run165["open_prs"] == 373
    assert run165["drafts"] == 361
    assert run165["non_drafts"] == 12
    run165_suite = data["run165_ci_evidence"]["full_suite"]
    assert run165_suite["head_sha"] == run165["integration_head_before_run165_commit"]
    assert run165_suite["tests_passed"] == 3796
    assert run165_suite["tests_failed"] == 0
    assert run165_suite["exact_head"] is True
    run167 = data["run167_snapshot"]
    assert run167["main_sha"] == data["repository_state"]["main_sha"]
    assert run167["integration_head_before_run167_map_commit"] != data["integration_pr"]["head_sha"]
    assert run167["pr_number"] == 1662
    assert run167["open_prs"] == 373
    assert run167["drafts"] == 361
    assert run167["non_drafts"] == 12
    run167_suite = data["run167_ci_evidence"]["full_suite"]
    assert run167_suite["head_sha"] == run167["integration_head_before_run167_map_commit"]
    assert run167_suite["tests_passed"] == 3796
    assert run167_suite["tests_failed"] == 0
    assert run167_suite["exact_head"] is True
    assert run167["map_update_commit_ci_pending"] is True
    run168 = data["run168_snapshot"]
    assert run168["main_sha"] == data["repository_state"]["main_sha"]
    assert run168["integration_head_before_run168_commit"] == "fd6ea9a759874f9d0043a4eeda87668696a8fcb9"
    run168_suite = data["run168_ci_evidence"]["full_suite"]
    assert run168_suite["head_sha"] == run168["integration_head_before_run168_commit"]
    assert run168_suite["tests_passed"] == 3797
    assert run168_suite["failed"] == 0
    followup = data["run168_followup_snapshot"]
    assert followup["integration_head_before_followup_commit"] == followup["ci"]["full_repository_suite"]["head_sha"]
    assert followup["ci"]["full_repository_suite"]["failed"] == 12
    assert followup["ci"]["full_repository_suite"]["exact_head"] is True
    assert run152["integration_head_at_capture"] == "2e9ddebe2220025b0f9ae731a304c06580c73742"
    assert run152["documentation_commit_head_sha"] == "3ffda1a61bb2586c3c750b314595ba9666cbd765"
    assert run152["documentation_commit_head_sha"] != run153["integration_head_at_capture"]
    assert run152["main_sha"] == data["repository_state"]["main_sha"]
    assert run152["full_suite"]["head_sha"] == run152["documentation_commit_head_sha"]
    assert run152["full_suite"]["passed"] == 3787
    assert run152["full_suite"]["failed"] == 1
    assert run152["full_suite"]["exact_head"] is True
    assert run152["last_known_good_full_suite"]["passed"] == 3787
    assert run152["last_known_good_full_suite"]["failed"] == 0
    assert run152["last_known_good_full_suite"]["head_sha"] == run152["integration_head_at_capture"]
    assert run152["followup_ci"]["head_sha"] == run153["integration_head_at_capture"]
    assert run152["followup_ci"]["passed"] == 3788
    assert run152["followup_ci"]["failed"] == 0
    assert run152["followup_ci"]["conclusion"] == "success"
    assert run152["changed_workflow_files"] == 48
    assert run152["patch_scan_workflows_reviewed"] == 50
    assert run152["open_pr_inventory"]["total"] == 373
    assert run152["forecast_status"] == "NOT_ISSUED"
    assert run152["accuracy_status"] == "NOT_EVALUATED"
    assert run152["merge_decision"] == "NO_MERGE"
    assert run152["market"]["raw_source_sha256_captured"] is False
    assert run153["integration_head_at_capture"] == run153["full_suite"]["head_sha"]
    assert run153["full_suite"]["passed"] == 3788
    assert run153["full_suite"]["failed"] == 0
    assert run153["full_suite"]["skipped"] == 1
    assert run153["full_suite"]["subtests"] == 19
    assert run153["full_suite"]["exact_head"] is True
    assert run153["dependency_audit"]["manifests"] == 6
    assert run153["dependency_audit"]["known_vulnerabilities"] == 0
    assert run153["forecast_status"] == "NOT_ISSUED"
    assert run153["accuracy_status"] == "NOT_EVALUATED"
    assert run153["merge_decision"] == "NO_MERGE"
    assert run153["handoff_commit_ci_pending"] is True
    assert run154["integration_head_at_capture"] == run154["full_suite"]["head_sha"]
    assert run154["full_suite"]["head_sha"] == run154["integration_head_at_capture"]
    assert run154["full_suite"]["passed"] == 3787
    assert run154["full_suite"]["failed"] == 1
    assert run154["full_suite"]["skipped"] == 1
    assert run154["full_suite"]["subtests"] == 19
    assert run154["full_suite"]["exact_head"] is True
    assert run154["full_suite"]["failing_tests"] == [
        "tests/test_xrp_nine_platform_current_map_run73.py::test_exact_head_ci_evidence_is_scoped_to_the_tested_parent_head"
    ]
    assert corrective["head_sha"] == "ee7a02e4ca4f8993b629ab10e396cfbe80cc38d5"
    assert corrective["run_id"] == 43684270127
    assert corrective["full_suite"]["passed"] == 3787
    assert corrective["full_suite"]["failed"] == 1
    assert corrective["full_suite"]["skipped"] == 1
    assert corrective["full_suite"]["subtests"] == 19
    assert "exact-head full-suite failed" in corrective["failure_classification"].lower()
    assert "test-contract regression" in corrective["failure_classification"].lower()
    assert corrective["dependency_audit"]["manifests"] == 6
    assert corrective["dependency_audit"]["known_vulnerabilities"] == 0
    assert corrective["fail_closed_gate"]["passed"] is True
    assert corrective["correction"]["failure_classification_phrase_fixed"] is True
    assert corrective["correction"]["tests_weakened"] is False
    assert final_verification["head_sha"] == run154["final_verification"]["head_sha"]
    assert final_verification["head_sha"] == "956dcf0882e85555d0a62b51646cea5285ec5169"
    assert final_verification["run_id"] == 43684755093
    assert final_verification["full_suite"]["passed"] == 3788
    assert final_verification["full_suite"]["failed"] == 0
    assert final_verification["full_suite"]["skipped"] == 1
    assert final_verification["full_suite"]["subtests"] == 19
    assert final_verification["full_suite"]["coverage_percent"] == 64.02
    assert final_verification["full_suite"]["legacy_core_coverage_percent"] == 77
    assert final_verification["full_suite"]["exact_head"] is True
    assert final_verification["full_suite"]["conclusion"] == "success"
    assert final_verification["wheel_build_verified"] is True
    assert final_verification["installed_wheel_primary_mission_verified"] is True
    assert final_verification["dependency_audit"]["manifests"] == 6
    assert final_verification["dependency_audit"]["known_vulnerabilities"] == 0
    assert final_verification["fail_closed_gate"]["passed"] is True
    assert final_verification["fail_closed_gate"]["automatic_merge_enabled"] is False
    assert final_verification["correction"]["tests_weakened"] is False
    run162_parent = data["run162_snapshot"]
    parent_suite = run162_parent["ci"]["full_repository_suite"]
    assert parent_suite["head_sha"] == run162_parent["integration_head_before_map_commit"]
    assert parent_suite["passed"] == 3781
    assert parent_suite["failed"] == 7
    assert parent_suite["exact_head"] is True
    assert len(parent_suite["failing_tests"]) == 7
    assert any("current_map" in name for name in parent_suite["failing_tests"])
    assert "exact-head full-suite failed" in run162_parent["ci"]["failure_classification"].lower()
    assert run154["forecast_status"] == "NOT_ISSUED"
    assert run154["accuracy_status"] == "NOT_EVALUATED"
    assert run154["merge_decision"] == "NO_MERGE"

    last_good = data["ci_evidence"]["run162_last_fully_passing_full_suite"]
    assert run155["integration_head_before_map_handoff_commit"] == run155["full_suite"]["head_sha"]
    assert run155["full_suite"]["head_sha"] == run155["integration_head_before_map_handoff_commit"]
    assert run155["full_suite"]["passed"] == 3788
    assert run155["full_suite"]["failed"] == 0
    assert run155["full_suite"]["skipped"] == 1
    assert run155["full_suite"]["subtests"] == 19
    assert run155["full_suite"]["exact_head"] is True
    assert run155["dependency_audit"]["manifests"] == 6
    assert run155["dependency_audit"]["known_vulnerabilities"] == 0
    assert run155["fail_closed_gate"]["passed"] is True
    assert last_good["head_sha"] == "35270afdac9a61e17c777dca534184a4acb8db2b"
    assert last_good["passed"] == 3794
    assert last_good["failed"] == 0
    assert latest["full_repository_suite"]["head_sha"] == latest["head_sha"]
    assert latest["full_repository_suite"]["skipped"] == 1
    assert latest["full_repository_suite"]["subtests"] == 19
    assert latest["full_repository_suite"]["coverage_percent"] == 64.02
    assert latest["full_repository_suite"]["failed"] == 4
    assert latest["full_repository_suite"]["failing_tests"] == ["tests/test_xrp_nine_platform_current_map_run73.py::test_prediction_engine_production_gaps_keep_forecasts_disabled","tests/test_xrp_nine_platform_current_map_run73.py::test_source_provenance_and_current_backlog_classification_are_explicit","tests/test_xrp_nine_platform_current_map_run73.py::test_run152_run153_run154_run155_run158_run159_run162_run165_and_run167_remain_historical_while_run168_and_run169_are_historical_and_run172_is_current","tests/test_xrp_nine_platform_current_map_run73.py::test_run162_current_head_verification_snapshot_tracks_latest_ci"]
    assert latest["dependency_audit"]["manifests"] == 6
    assert latest["dependency_audit"]["known_vulnerabilities"] == 0
    assert latest["fail_closed_gate"]["passed"] is True
    assert latest["fail_closed_gate"]["automatic_merge_enabled"] is False
    assert data["run155_test_correction"]["head_sha"] == data["run155_current_head_ci_failure"]["head_sha"]
    assert data["run155_test_correction"]["correction"]["tests_weakened"] is False
    assert data["run155_test_correction"]["corrected_in_next_commit"] is True
    assert data["run155_map_handoff_commit_ci"].startswith("FAILED_ON_6757c")
    assert data["run155_forecast_status"]["forecast_status"] == "NOT_ISSUED"
    assert data["run155_forecast_status"]["accuracy_status"] == "NOT_EVALUATED"
    assert data["run155_no_external_actions"]["merge"] is False
    assert data["run155_no_external_actions"]["deployment"] is False
    assert data["run155_no_external_actions"]["external_model_transfer"] is False



    assert run158["integration_head_at_capture"] == run158["full_suite"]["head_sha"]
    assert run158["full_suite"]["head_sha"] == "68c228ce0e17d214b235b146d0e266726bd1ae16"
    assert run158["full_suite"]["run_id"] == 43697979219
    assert run158["full_suite"]["passed"] == 3788
    assert run158["full_suite"]["failed"] == 0
    assert run158["full_suite"]["skipped"] == 1
    assert run158["full_suite"]["subtests"] == 19
    assert run158["full_suite"]["coverage_percent"] == 64.02
    assert run158["full_suite"]["wheel_build"] is True
    assert run158["full_suite"]["installed_mission"] is True
    assert run158["dependency_audit"]["manifests"] == 6
    assert run158["dependency_audit"]["known_vulnerabilities"] == 0
    assert run158["fail_closed_gate"]["passed"] is True
    assert run159["integration_head_at_capture"] == run159["full_suite"]["head_sha"]
    assert run159["full_suite"]["head_sha"] == "30d9aba3b433b806f0d96e4264e4d8838a8a105a"
    assert run159["full_suite"]["run_id"] == 43698623827
    assert run159["full_suite"]["passed"] == 3745
    assert run159["full_suite"]["failed"] == 43
    assert run159["full_suite"]["skipped"] == 1
    assert run159["full_suite"]["subtests"] == 19
    assert run159["full_suite"]["coverage_percent"] == 64.0
    assert run159["full_suite"]["exact_head"] is True
    assert len(run159["full_suite"]["failing_tests"]) == 43
    assert run159["core_tests"]["passed"] == 742
    assert run159["core_tests"]["failed"] == 0
    assert run159["dependency_audit"]["passed"] is True
    assert run159["dependency_audit"]["manifests"] == 6
    assert run159["dependency_audit"]["known_vulnerabilities"] == 0
    assert run159["fail_closed_gate"]["passed"] is True
    assert run159["pr_event"]["full_suite"] == "skipped by integration-branch condition"
    assert run159["map_schema_regression"]["failed_tests"] == 43
    assert run159["map_schema_regression"]["tests_weakened"] is False
    assert run159["forecast_status"] == "NOT_ISSUED"
    assert run159["accuracy_status"] == "NOT_EVALUATED"
    assert run159["merge_decision"] == "NO_MERGE"
    assert last_good["head_sha"] == "35270afdac9a61e17c777dca534184a4acb8db2b"
    assert last_good["passed"] == 3794
    assert last_good["failed"] == 0
    current = data["run162_current_head_verification_snapshot"]
    assert latest_current["head_sha"] == data["run173_snapshot"]["integration_head_before_run173_commit"]
    assert latest["head_sha"] == data["run172_map_test_correction_snapshot"]["integration_head_before_correction_commit"]
    assert latest["head_sha"] != current["integration_head_before_map_commit"]
    assert latest["conclusion"] == "failure"
    assert latest["full_repository_suite"]["head_sha"] == latest["head_sha"]
    assert latest["full_repository_suite"]["passed"] == 3800
    assert latest["full_repository_suite"]["failed"] == 4
    assert latest["full_repository_suite"]["skipped"] == 1
    assert latest["full_repository_suite"]["subtests"] == 19
    assert latest["full_repository_suite"]["coverage_percent"] == 64.02
    assert latest["full_repository_suite"]["failing_tests"] == ["tests/test_xrp_nine_platform_current_map_run73.py::test_prediction_engine_production_gaps_keep_forecasts_disabled","tests/test_xrp_nine_platform_current_map_run73.py::test_source_provenance_and_current_backlog_classification_are_explicit","tests/test_xrp_nine_platform_current_map_run73.py::test_run152_run153_run154_run155_run158_run159_run162_run165_and_run167_remain_historical_while_run168_and_run169_are_historical_and_run172_is_current","tests/test_xrp_nine_platform_current_map_run73.py::test_run162_current_head_verification_snapshot_tracks_latest_ci"]
    assert data["ci_evidence"]["full_repository_suite"]["head_sha"] == latest_current["head_sha"]
    assert data["ci_evidence"]["full_repository_suite"]["failed"] == 0
    assert data["schema_version"] == "1.1.0"
    assert data["run158_compact_map_snapshot"]["schema_version"] == "1.2.0"
    assert data["run158_map_schema_regression"]["full_v1_1_schema_restored"] is True
    assert data["run158_map_schema_regression"]["compact_snapshot_preserved_additively"] is True
    assert data["run158_map_schema_regression"]["tests_weakened"] is False


def test_run162_snapshot_is_append_only_and_research_remains_model_ineligible():
    data = load_current()
    run = data["run162_snapshot"]
    assert run["run_id"] == "Run162"
    assert run["repository"]["main_sha"] == data["observed_main_sha"]
    assert run["integration_head_before_map_commit"] == run["integration_pr"]["head_sha"]
    assert run["ci"]["full_repository_suite"]["head_sha"] == run["integration_head_before_map_commit"]
    assert run["ci"]["full_repository_suite"]["failed"] == 7
    assert run["ci"]["full_repository_suite"]["exact_head"] is True
    assert run["market"]["model_eligible"] is False
    assert run["market"]["raw_source_receipts"]["captured_by_barrot"] is False
    assert run["forecast_status"] == "NOT_ISSUED"
    assert run["accuracy_status"] == "NOT_EVALUATED"
    assert run["institutional"]["trust_bank_convergence"].startswith("Coinbase National Trust")
    assert run["workflow_safety"]["main_barrot_sync"]["external_call_observed"] is False
    assert run["no_external_actions"]["merge"] is False
    assert run["no_external_actions"]["real_money"] is False


def test_run162_corrective_commit_snapshot_tracks_exact_head_ci_and_research_addendum():
    data = load_current()
    run = data["run162_corrective_commit_snapshot"]
    assert run["integration_head_before_map_commit"] == run["integration_pr"]["head_sha"]
    assert run["repository"]["main_sha"] == data["observed_main_sha"]
    assert run["ci"]["full_repository_suite"]["head_sha"] == run["integration_head_before_map_commit"]
    assert run["ci"]["full_repository_suite"]["passed"] == 3786
    assert run["ci"]["full_repository_suite"]["failed"] == 3
    assert run["ci"]["full_repository_suite"]["exact_head"] is True
    assert run["ci"]["latest_attempt"]["failing_tests"] == run["test_failures"]
    assert "evidence-contract mismatches" in run["failure_classification"].lower()
    assert run["ci"]["latest_attempt"]["head_sha"] == run["integration_head_before_map_commit"]
    assert run["ci"]["latest_attempt"]["conclusion"] == "failure"
    assert run["ci"]["latest_attempt"]["full_repository_suite"]["failed"] == 3
    assert data["run162_snapshot"]["ci"]["full_repository_suite"]["failed"] == 7
    assert run["research_addendum"]["binance_circle"]["equity"]["gross_proceeds_to_circle_usd"] == 100000000
    assert run["research_addendum"]["circle_usdc_xrpl"]["bridge_required"] is False
    assert run["research_addendum"]["identity"]["sbic"]["conclusion"].startswith("Recurring training events")
    assert run["research_addendum"]["identity"]["kamilah_stevenson"]["video_inventory_status"] == "NOT_STARTED_IDENTITY_UNVERIFIED"


def test_run162_map_minification_commit_snapshot_tracks_current_exact_head():
    data = load_current()
    current = data["run162_map_minification_commit_snapshot"]
    assert current["integration_head_before_map_commit"] == current["integration_pr"]["head_sha"]
    assert current["repository"]["main_sha"] == data["observed_main_sha"]
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["full_repository_suite"]["passed"] == 3788
    assert current["ci"]["full_repository_suite"]["failed"] == 3
    assert current["ci"]["full_repository_suite"]["exact_head"] is True
    assert current["ci"]["latest_attempt"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["latest_attempt"]["conclusion"] == "failure"
    assert current["map_minification"]["current_newline_count"] == 1
    assert current["research_addendum"]["circle_arc_token_presale"]["presale"]["gross_proceeds_usd"] == 242200000
    assert current["research_addendum"]["circle_arc_sbi"]["sbi_vc_trade_usdc_distribution"].startswith("Circle states")
    assert current["research_addendum"]["identity"]["kamilah_stevenson"]["video_inventory_status"] == "NOT_STARTED_IDENTITY_UNVERIFIED"


def test_run162_handoff_update_commit_snapshot_tracks_latest_ci():
    data = load_current()
    current = data["run162_handoff_update_commit_snapshot"]
    assert current["integration_head_before_map_commit"] == current["integration_pr"]["head_sha"]
    assert current["repository"]["main_sha"] == data["observed_main_sha"]
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["full_repository_suite"]["passed"] == 3788
    assert current["ci"]["full_repository_suite"]["failed"] == 3
    assert current["ci"]["full_repository_suite"]["exact_head"] is True
    assert current["ci"]["latest_attempt"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["latest_attempt"]["conclusion"] == "failure"
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["workflow_safety"]["main_barrot_sync"]["external_call_observed"] is False
    assert current["research_addendum"]["identity"]["sbic"]["companies"]["central"]["english_name"] == "SBIC Central Japan"
    assert current["research_addendum"]["circle_arc_token_presale"]["presale"]["gross_proceeds_usd"] == 242200000


def test_run162_test_correction_commit_snapshot_tracks_latest_ci_and_market_quality():
    data = load_current()
    current = data["run162_test_correction_commit_snapshot"]
    assert current["integration_head_before_map_commit"] == current["integration_pr"]["head_sha"]
    assert current["repository"]["main_sha"] == data["observed_main_sha"]
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["full_repository_suite"]["passed"] == 3788
    assert current["ci"]["full_repository_suite"]["failed"] == 2
    assert current["ci"]["full_repository_suite"]["exact_head"] is True
    assert current["ci"]["latest_attempt"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["latest_attempt"]["conclusion"] == "failure"
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["market"]["model_eligible"] is False
    assert current["market"]["usdt_basis"]["gate_passed"] is False
    assert current["market"]["raw_source_receipts"]["captured_by_barrot"] is False
    assert current["research_addendum"]["identity"]["sbic"]["companies"]["east"]["english_name"] == "SBIC East Japan"
    assert current["research_addendum"]["circle_arc_token_presale"]["presale"]["gross_proceeds_usd"] == 242200000


def test_run162_exact_head_correction_commit_snapshot_tracks_latest_ci():
    data = load_current()
    current = data["run162_exact_head_correction_commit_snapshot"]
    assert current["integration_head_before_map_commit"] == current["integration_pr"]["head_sha"]
    assert current["repository"]["main_sha"] == data["observed_main_sha"]
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["full_repository_suite"]["passed"] == 3790
    assert current["ci"]["full_repository_suite"]["failed"] == 3
    assert current["ci"]["full_repository_suite"]["exact_head"] is True
    assert current["ci"]["latest_attempt"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["latest_attempt"]["conclusion"] == "failure"
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["market"]["model_eligible"] is False
    assert current["workflow_safety"]["main_barrot_sync"]["external_call_observed"] is False
    assert current["research_addendum"]["identity"]["sbic"]["companies"]["east"]["english_name"] == "SBIC East Japan"
    assert current["research_addendum"]["circle_arc_token_presale"]["presale"]["gross_proceeds_usd"] == 242200000


def test_run162_final_verified_head_snapshot_tracks_current_pass_and_main_blockers():
    data = load_current()
    current = data["run162_final_verified_head_snapshot"]
    assert current["integration_head_before_map_commit"] == current["integration_pr"]["head_sha"]
    assert current["repository"]["main_sha"] == data["observed_main_sha"]
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["full_repository_suite"]["passed"] == 3794
    assert current["ci"]["full_repository_suite"]["failed"] == 0
    assert current["ci"]["full_repository_suite"]["exact_head"] is True
    assert current["ci"]["full_repository_suite"]["wheel_build_verified"] is True
    assert current["ci"]["full_repository_suite"]["installed_wheel_primary_mission_verified"] is True
    assert current["ci"]["latest_attempt"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["latest_attempt"]["conclusion"] == "success"
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["workflow_safety"]["main_pillars_consistency_check"]["conclusion"] == "failure"
    assert current["workflow_safety"]["main_pillars_consistency_check"]["read_only"] is True
    assert current["workflow_safety"]["main_pages_build"]["conclusion"] == "failure"
    assert current["workflow_safety"]["main_barrot_sync"]["external_call_observed"] is False
    assert current["forecast_status"] == "NOT_ISSUED"
    assert current["accuracy_status"] == "NOT_EVALUATED"


def test_run162_current_head_verification_snapshot_tracks_latest_ci():
    data = load_current()
    current = data["run162_current_head_verification_snapshot"]
    assert current["integration_head_before_map_commit"] == current["integration_pr"]["head_sha"]
    assert current["repository"]["main_sha"] == data["observed_main_sha"]
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["full_repository_suite"]["passed"] == 3794
    assert current["ci"]["full_repository_suite"]["failed"] == 1
    assert current["ci"]["full_repository_suite"]["failing_tests"] == current["test_failures"]
    assert current["ci"]["latest_attempt"]["head_sha"] == current["integration_head_before_map_commit"]
    assert current["ci"]["latest_attempt"]["conclusion"] == "failure"
    assert current["ci"]["full_repository_suite"]["head_sha"] == current["integration_head_before_map_commit"]
    assert data["ci_evidence"]["run172_map_test_correction_attempt"]["head_sha"] == data["run172_map_test_correction_snapshot"]["integration_head_before_correction_commit"]
    assert data["ci_evidence"]["run172_map_test_correction_attempt"]["conclusion"] == "failure"
    assert current["workflow_safety"]["main_pillars_consistency_check"]["read_only"] is True
    assert current["forecast_status"] == "NOT_ISSUED"
    assert current["accuracy_status"] == "NOT_EVALUATED"


def test_run167_platform_map_workflow_review_and_xrpl_stablecoin_evidence_remain_historical():
    data = load_current()
    run = data["run167_snapshot"]
    assert run.get("run_id") == "Run167"
    assert run["pr_changed_files"] == 1255
    assert run["current_pr_changed_files_at_capture"] == 1256
    assert data["integration_pr"]["changed_files"] == 1259
    assert run["integration_head_before_run167_map_commit"] != data["integration_pr"]["head_sha"]
    assert data["run167_workflow_review"]["changed_workflow_files"] == 48
    assert data["run167_workflow_review"]["workflow_definition_triage_complete"] is True
    assert data["run167_workflow_review"]["called_script_semantic_review_complete"] is False
    assert data["run167_workflow_review"]["no_external_dispatch"] is True
    market = data["run167_xrpl_stablecoin_research"]
    assert market["model_eligible"] is False
    assert "Do not average" in market["reconciliation"]
    assert market["raw_bytes_captured"] is False
    assert market["forecast_status"] == "NOT_ISSUED"
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["accuracy_status"] == "NOT_EVALUATED"
    assert data["run167_platform_status"]["verified_external_platforms_beyond_chatgpt_github_connector"] == 0
    assert data["run167_no_external_actions"]["merge"] is False
    assert data["run167_no_external_actions"]["real_money_action"] is False
    tokenpost = next(x for x in data["source_provenance"] if x["source"] == "TokenPost XRPL stablecoin and DEX snapshot (Nov 13)")
    defillama = next(x for x in data["source_provenance"] if x["source"] == "DefiLlama XRPL chain dashboard snapshot (Nov 15)")
    assert tokenpost["raw_sha256"] is None and tokenpost["model_eligible"] is False
    assert defillama["raw_sha256"] is None and defillama["model_eligible"] is False


def test_run168_historical_snapshot_security_hold_and_identity_resolution_are_explicit():
    data = load_current()
    assert data["run168_snapshot"]["run_id"] == "Run168"
    initial = data["run168_snapshot"]
    assert initial["main_sha"] == data["observed_main_sha"]
    assert initial["integration_head_before_run168_commit"] == data["run168_ci_evidence"]["full_suite"]["head_sha"]
    assert data["run168_ci_evidence"]["full_suite"]["tests_passed"] == 3797
    assert data["run168_ci_evidence"]["full_suite"]["failed"] == 0
    followup = data["run168_followup_snapshot"]
    assert followup["integration_head_before_followup_commit"] == followup["ci"]["full_repository_suite"]["head_sha"]
    assert followup["ci"]["full_repository_suite"]["passed"] == 3785
    assert followup["ci"]["full_repository_suite"]["failed"] == 12
    assert followup["ci"]["full_repository_suite"]["exact_head"] is True
    assert data["run168_corrective_commit_snapshot"]["tests_weakened"] is False
    assert data["run168_workflow_review"]["changed_workflow_files"] == 48
    assert data["run168_workflow_review"]["workflow_definition_triage_complete"] is True
    assert data["run168_workflow_review"]["called_script_semantic_review_complete"] is False
    assert data["run168_workflow_review"]["no_external_dispatch"] is True
    market = data["run168_market_research"]
    assert market["model_eligible"] is False
    assert market["freshness_status"] == "STALE_AT_RECHECK"
    assert market["raw_http_bytes_captured"] is False
    assert market["quality_gates"]["normalized_usd_quote_admitted"] is False
    assert set(("spot", "spot_order_book", "exchange_flows", "derivatives", "options", "etf_flows", "cftc")).issubset(data["current_market_snapshot"])
    security = data["run168_security_hold"]
    assert security["branch_tips_checked"] == 17
    assert security["open_pr_tips_containing_path"] == 15
    assert security["closed_pr_tips_containing_path"] == 2
    assert security["same_blob_sha"] == "f58b27f14436088db99662d3a45c59b8437ec3a1"
    assert security["credential_contents_read"] is False
    assert security["provider_side_revocation_verified"] is False
    assert data["run168_platform_status"]["verified_external_platforms_beyond_chatgpt_github_connector"] == 0
    assert data["run168_no_external_actions"]["merge"] is False
    assert data["run168_no_external_actions"]["real_money_action"] is False
    identity = data["run168_identity_research"]
    assert identity["sbic"]["companies"]["east"]["english_name"] == "SBIC East Japan"
    assert identity["sbic"]["companies"]["central"]["english_name"] == "SBIC Central Japan"
    assert identity["sbic"]["companies"]["west"]["english_name"] == "SBIC West Japan"
    assert identity["sbic"]["sbi_holdings_is_separate"] is True
    assert identity["sb_oai_japan"]["ownership"]["OpenAI_percent"] == 50
    assert identity["kamilah_stevenson"]["video_inventory_status"] == "NOT_INVENTORIED_IDENTITY_LINK_UNVERIFIED"
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["accuracy_status"] == "NOT_EVALUATED"


def test_run169_exact_head_regression_market_security_and_forecast_gates():
    data = load_current()
    assert data["run169_snapshot"]["run_id"] == "Run169"
    run = data["run169_snapshot"]
    assert run["main_sha"] == data["observed_main_sha"]
    assert run["integration_head_before_run169_commit"] == run["pr_head_sha"]
    assert run["pr_number"] == 1662
    assert run["pr_changed_files"] == 1256
    assert run["open_prs"] == 373
    ci = data["run169_ci_evidence"]["pre_correction"]
    assert ci["head_sha"] == run["integration_head_before_run169_commit"]
    assert ci["exact_head"] is True
    assert ci["passed"] == 3796
    assert ci["failed"] == 2
    assert ci["skipped"] == 1
    assert ci["failing_tests"] == data["run169_ci_evidence"]["pre_correction"]["failing_tests"]
    correction = data["run169_ci_evidence"]["corrective_commit"]
    assert correction["tests_removed"] == 0
    assert correction["tests_disabled"] == 0
    assert correction["tests_weakened"] is False
    market = data["run169_market_research"]
    assert market["point_in_time_eligibility"] == "RESEARCH_ONLY_NOT_MODEL_ELIGIBLE"
    assert market["raw_http_bytes_captured"] is False
    assert market["spot"]["same_venue_basis_skew_seconds"] > market["spot"]["allowed_basis_skew_seconds"]
    assert market["spot"]["usd_normalization_admitted"] is False
    assert market["derivatives"]["reconciliation"].endswith("do not establish direction.")
    security = data["run169_security_hold"]
    assert security["branch_tips_checked"] == 17
    assert security["branch_tips_containing_path"] == 17
    assert security["same_blob_sha"] == "f58b27f14436088db99662d3a45c59b8437ec3a1"
    assert security["size_bytes"] == 216
    assert security["credential_contents_read"] is False
    assert security["provider_side_revocation_verified"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["accuracy_status"] == "NOT_EVALUATED"
    assert all(value is False for value in data["run169_no_external_actions"].values())


def test_run169_evernorth_actual_capital_components_reconcile_without_double_counting():
    data = load_current()
    e = data["run169_institutional_research_update"]["evernorth"]
    assert e["cash_purchased_xrp"] == 84365876
    assert e["private_placement_xrp"] == 261919096
    assert e["delayed_funding_xrp"] == 200000
    assert e["ripple_direct_contribution_xrp"] == 126791458
    assert e["total_xrp_reconciled"] == 473276430
    assert e["cash_purchased_xrp"] + e["private_placement_xrp"] == e["reported_preclose_holdings_xrp"]
    assert e["reported_preclose_holdings_xrp"] + e["delayed_funding_xrp"] == e["postclose_pathfinder_transfer_xrp"]
    assert e["private_placement_xrp"] + e["delayed_funding_xrp"] + e["ripple_direct_contribution_xrp"] == e["in_kind_total_xrp"]
    assert e["postclose_pathfinder_transfer_xrp"] + e["ripple_direct_contribution_xrp"] == e["total_xrp_reconciled"]
    assert e["components_reconcile"] is True
    assert e["delayed_200k_difference_resolved"] is True
    assert e["gross_closing_cash_proceeds_usd"] == 272600000
    assert e["gross_cash_components_usd"]["private_placement_investments"] + e["gross_cash_components_usd"]["spac_trust_release"] == 272600000
    assert e["advance_cash_used_for_xrp_is_already_inside_gross_closing_cash"] is True
    assert e["sbi"]["individual_sbi_cash_amount_reconciled_in_10q"] is False
    assert e["raise_target_over_1b"]["verified_as_realized_cash_in_2026_10q"] is False
    assert e["eloc"]["capacity_is_cash"] is False
    assert e["eloc"]["actual_draw_reported"] is False
    assert e["warrant_exercises"]["proceeds_used_to_buy_xrp_verified"] is False


def test_run169_sbic_identity_and_kamilah_attribution_remain_source_bounded():
    data = load_current()
    identity = data["run169_identity_research_update"]
    sbic = identity["sbic"]
    assert sbic["east"]["english_name"] == "SBIC East Japan"
    assert sbic["central"]["english_name"] == "SBIC Central Japan"
    assert sbic["west"]["english_name"] == "SBIC West Japan"
    assert sbic["sbi_holdings_is_separate"] is True
    assert identity["chatgpt_sbic"]["commercial_openai_partnership_established"] is False
    assert identity["ask_coin"]["xrpl_issuer_verified"] is False
    kam = identity["kamilah_stevenson"]
    assert kam["person_identity_status"] == "FIRST_PERSON_SELF_IDENTIFICATION_VERIFIED"
    assert kam["candidate_channel_first_party_crosslink"] is False
    assert kam["video_inventory_status"] == "NOT_INVENTORIED_CHANNEL_LINK_UNVERIFIED"
    assert kam["videos_attributed"] == 0


def test_run169_circle_arc_bny_pnc_and_xrpl_metrics_are_not_misclassified_as_xrp_demand():
    data = load_current()
    institutional = data["run169_institutional_research_update"]
    assert institutional["circle_arc_sbi"]["founding_validator_cohort_includes"].count("SBI Group") == 1
    assert institutional["circle_arc_sbi"]["xrp_relationship"].startswith("No direct XRP")
    assert institutional["pnc_coinbase"]["rail"] == "incoming USDC on Ethereum"
    assert institutional["pnc_coinbase"]["xrp_settlement"] is False
    assert institutional["ripple_coinbase"]["coinbase_global_exchange_collateral"] == "FUTURE_NOT_LIVE"
    assert institutional["ripple_bny"]["tokenized_trade_finance"].startswith("EXPLORATORY")
    market = data["run169_market_research"]
    xrpl = market["xrpl_onchain_metrics"]
    assert xrpl["stablecoin_market_cap_usd"] == 850850000
    assert xrpl["stablecoin_change_7d_pct"] == -12.81
    assert xrpl["rlusd_dominance_pct"] == 89.65
    assert xrpl["dex_volume_7d_change_pct"] == 93.60
    assert xrpl["dex_vs_cex_dominance_pct"] == 0.04
    assert market["raw_http_bytes_captured"] is False
    assert market["point_in_time_eligibility"] == "RESEARCH_ONLY_NOT_MODEL_ELIGIBLE"
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["accuracy_status"] == "NOT_EVALUATED"


def test_run169_current_pr_snapshot_does_not_rewrite_run167_historical_counts():
    data = load_current()
    assert data["run167_snapshot"]["current_pr_changed_files_at_capture"] == 1256
    assert data["integration_pr"]["changed_files"] == 1259
    assert data["integration_pr"]["head_sha"] == data["repository_state"]["integration_head_before_current_map_commit"]
    assert data["run169_followup_snapshot"]["integration_head_before_followup_commit"] != data["integration_pr"]["head_sha"]
    assert data["forecast_status"] == "NOT_ISSUED"


def test_run172_snapshot_remains_historical_after_run173_map_update():
    data = load_current()
    assert "run173_snapshot" in data
    run = data["run172_snapshot"]
    assert run["main_sha"] == data["observed_main_sha"]
    assert run["integration_head_before_run172_map_commit"] == run["pr_head_sha"]
    assert run["pr_number"] == 1662
    assert run["open_prs"] == 373
    assert run["drafts"] == 361
    assert run["non_drafts"] == 12
    assert data["integration_pr"]["head_sha"] == data["repository_state"]["integration_head_before_current_map_commit"]
    assert data["integration_pr"]["changed_files"] == 1259
    assert data["repository_state"]["integration_tree_entries"] == 2502
    assert data["event_timeline_registry_version"] == "run157-20261115"
    assert data["event_timeline_registry_event_count"] == 85
    assert data["event_timeline_registry_raw_hashes"] == 0
    assert data["event_timeline_model_eligible"] is False
    assert data["event_registry"]["registry_version"] == "run157-20261115"
    assert data["event_registry"]["event_count"] == 85
    assert data["event_registry"]["raw_source_sha256_count"] == 0
    assert data["event_registry"]["model_eligible"] is False
    engine = data["prediction_engine_status"]
    policy = engine["readiness_policy"]
    assert policy["id"] == READINESS_POLICY_ID
    assert policy["minimum_oos_samples"] == _MIN_OOS_SAMPLES == 100
    assert policy["minimum_shadow_samples"] == _MIN_SHADOW_SAMPLES == 100
    assert policy["minimum_horizon_multiple"] == _MIN_HORIZON_MULTIPLE == 10
    assert policy["minimum_source_groups"] == _MIN_SOURCE_GROUPS == 5
    assert policy["maximum_weighted_calibration_error"] == _MAX_WEIGHTED_CALIBRATION_ERROR == 0.05
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["accuracy_status"] == "NOT_EVALUATED"
    market = data["run172_market_research"]
    assert market["point_in_time_eligibility"] == "RESEARCH_ONLY_NOT_MODEL_ELIGIBLE"
    assert market["spot"]["usd_normalization_admitted"] is False
    assert "do not average" in market["derivatives"]["reconciliation"].lower()
    assert "do not average" in market["etf_flows"]["reconciliation"].lower()
    assert "future-dated" in market["etf_flows"]["cryptokeyhole"]["future_dated_issuer_file_anomaly"].lower()
    assert all(value is False for value in data["run172_no_external_actions"].values())


def test_run172_map_test_correction_attempt_is_recorded_without_weakening_tests():
    data = load_current()
    correction = data["run172_map_test_correction_snapshot"]
    assert correction["integration_head_before_correction_commit"] == data["observed_integration_head_before_map_commit"]
    suite = correction["ci"]["full_repository_suite"]
    assert suite["head_sha"] == correction["integration_head_before_correction_commit"]
    assert suite["passed"] == 3800
    assert suite["failed"] == 4
    assert suite["skipped"] == 1
    assert suite["subtests"] == 19
    assert suite["conclusion"] == "failure"
    assert suite["failing_tests"] == ["tests/test_xrp_nine_platform_current_map_run73.py::test_prediction_engine_production_gaps_keep_forecasts_disabled","tests/test_xrp_nine_platform_current_map_run73.py::test_source_provenance_and_current_backlog_classification_are_explicit","tests/test_xrp_nine_platform_current_map_run73.py::test_run152_run153_run154_run155_run158_run159_run162_run165_and_run167_remain_historical_while_run168_and_run169_are_historical_and_run172_is_current","tests/test_xrp_nine_platform_current_map_run73.py::test_run162_current_head_verification_snapshot_tracks_latest_ci"]
    assert correction["last_fully_passing_head"] == "ad2ac1b072afbc710fdcc4b26a888f7351e0ea86"
    assert correction["last_fully_passing_tests"] == 3803
    assert correction["tests_removed"] == 0
    assert correction["tests_disabled"] == 0
    assert correction["assertions_weakened"] == 0
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["accuracy_status"] == "NOT_EVALUATED"


def test_run173_current_map_records_exact_head_ci_and_preserves_prediction_gates():
    data = load_current()
    run = data["run173_snapshot"]
    assert "run173_snapshot" in data
    assert run["main_sha"] == data["observed_main_sha"]
    assert run["integration_head_before_run173_commit"] == "754e7d1e28e97f00cb43f9fdfa5adf1de1a1a21c"
    assert run["pr_number"] == 1662
    assert run["open_prs"] == 373
    assert run["drafts"] == 361
    assert run["non_drafts"] == 12
    suite = run["exact_head_full_suite"]
    assert suite["head_sha"] == run["integration_head_before_run173_commit"]
    assert suite["tests_passed"] == 3805
    assert suite["tests_failed"] == 0
    assert suite["skipped"] == 1
    assert suite["subtests"] == 19
    assert suite["coverage_percent"] == 64.02
    assert suite["legacy_core_coverage_percent"] == 77
    assert suite["wheel_build_verified"] is True
    assert suite["installed_wheel_primary_mission_verified"] is True
    assert run["dependency_audit"]["manifests"] == 6
    assert run["dependency_audit"]["known_vulnerabilities"] == 0
    assert run["fail_closed_gate"]["passed"] is True
    assert run["fail_closed_gate"]["automatic_merge_enabled"] is False
    assert data["run173_market_research"]["point_in_time_eligibility"] == "RESEARCH_ONLY_NOT_MODEL_ELIGIBLE"
    assert data["run173_market_research"]["raw_http_bytes_captured"] is False
    assert data["event_registry"]["event_count"] == 85
    assert data["event_registry"]["raw_source_sha256_count"] == 0
    assert data["event_registry"]["model_eligible"] is False
    assert data["run173_forecast_status"]["forecast_status"] == "NOT_ISSUED"
    assert data["run173_forecast_status"]["accuracy_status"] == "NOT_EVALUATED"
    assert all(value is False for value in data["run173_no_external_actions"].values())


def test_run212_map_summary_is_preserved_as_a_timestamped_artifact():
    path = ROOT / "research/xrp_intelligence/20261117T105932Z-run212-nine-platform-map-summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks",
    }
    assert data["schema_version"] == "1.0.0"
    assert data["captured_at_utc"] == "2026-11-17T10:59:32Z"
    assert data["coordination_status"] == "NO_NINE_PLATFORM_LIVE_QUORUM"
    assert {item["platform"] for item in data["platforms"]} == expected
    assert all(item["external_provider_dispatch"] is False for item in data["platforms"])
    assert data["least_privilege"].startswith("NOT_VERIFIED")
