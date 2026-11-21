"""Validate the latest nine-platform capability/authentication map."""
import json
from pathlib import Path

MAP_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "nine_platform_capability_authentication_dataflow_map_latest.json"
)


def load_map():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def is_sha(value):
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def test_latest_map_covers_nine_platforms_without_fabricated_connections():
    data = load_map()
    expected = {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks",
    }
    assert set(data["platforms"]) == expected
    chatgpt = data["platforms"]["ChatGPT"]
    assert chatgpt["authentication_status"] == "verified"
    assert chatgpt["data_flow"]["status"] == "verified"
    assert chatgpt["data_flow"]["path"] == (
        "ChatGPT session -> GitHub connector -> Barrot-Agent/B-Agent"
    )
    assert set(chatgpt["permissions"]) == {
        "admin", "maintain", "push", "pull", "triage"
    }
    assert "token scopes were not introspected" in chatgpt["least_privilege"]
    for name in expected - {"ChatGPT"}:
        platform = data["platforms"][name]
        assert platform["authentication_status"] == "unverified"
        assert platform["data_flow"] == "not_verified"
        assert platform["permissions"] == []
        assert platform["task_assignment"]["status"] == "PROPOSED_NOT_DISPATCHED"
        assert platform["capability_evidence_status"] == "public_product_category_only_unverified"
    assert data["coordination"]["external_dispatch_performed"] is False
    assert data["coordination"]["external_data_transfer_performed"] is False
    assert data["coordination"]["task_assignments_status"] == "PROPOSED_NOT_DISPATCHED_FOR_EIGHT_EXTERNAL_PLATFORMS"
    assert "raw_sha256" in data["coordination"]["evidence_packet_schema"]
    assert data["coordination"]["red_team_status"].startswith("NOT_EXECUTED")


def test_latest_map_matches_repository_and_forecast_admission_state():
    data = load_map()
    repo = data["repository_state"]
    assert repo["repository"] == "Barrot-Agent/B-Agent"
    assert is_sha(repo["main_sha"])
    integration = repo["integration"]
    assert integration["pr_number"] == 1673
    assert integration["state"] == "closed"
    assert integration["draft"] is False
    assert integration["merged"] is True
    assert integration["classification"] == "MERGED_WITH_GOVERNANCE_EXCEPTION"
    assert integration["merge_commit_sha"] == repo["main_sha"]
    assert is_sha(integration["snapshot_head_sha"])
    assert is_sha(integration["code_head_sha"])
    assert is_sha(integration["current_pr_head_sha"])
    assert integration["ahead_by"] == 0
    assert integration["commits"] == 556
    assert integration["pr_commit_count"] == 556
    assert integration["changed_files"] == 1492
    assert integration["current_main_sha"] == repo["main_sha"]
    assert integration["base_sha_matches_current_main"] is False
    assert integration["base_sha"] != repo["main_sha"]
    assert integration["behind_by"] == 0
    assert integration["changed_files"] >= 1
    assert 0 <= integration["changed_workflow_files"] <= integration["changed_files"]
    assert repo["main_paths_missing_from_integration"] == 0
    assert repo["tree_counts"]["integration"]["entries"] >= repo["tree_counts"]["main"]["entries"]

    registry = data["prediction_engine"]["source_registry"]
    assert registry == {
        "public_endpoint_records": 53,
        "hourly_sources": 48,
        "weekly_sources": 3,
        "noncommercial_nodes_excluded": 2,
        "scheduled_sources": 51,
    }
    ingestion = data["prediction_engine"]["latest_ingestion"]
    assert ingestion["run_id"] == data["latest_ingestion_run_id"]
    assert ingestion["run_number"] > 0
    assert ingestion["captured_at_utc"] == data["latest_ingestion_run_captured_at_utc"]
    assert ingestion["code_head_sha"] == repo["main_sha"]
    assert ingestion["receipt_count"] == 34
    assert ingestion["raw_retained"] == 22
    assert ingestion["digest_only"] == 12
    assert ingestion["raw_payload_hashes_verified"] == 22
    assert ingestion["raw_payload_hash_mismatches"] == 0
    assert ingestion["receipt_chain_verified"] is True
    assert ingestion["receipt_chain_sequence"] > 0
    assert ingestion["previous_run_id"] > 0
    assert ingestion["external_anchor"] == "NOT_ANCHORED"
    assert ingestion["source_failures"] == 18
    assert ingestion["raw_only_sources"] == 23
    assert ingestion["feature_store_history_record_count"] > 0
    assert ingestion["feature_store_snapshot_count"] > 0
    assert (
        ingestion["eligible_feature_record_count"]
        + ingestion["excluded_feature_record_count"]
        == ingestion["delta_feature_record_count"]
    )
    assert ingestion["input_feature_record_count"] >= ingestion["delta_feature_record_count"]
    assert ingestion["sqlite_integrity"] == "ok"
    assert ingestion["event_count"] == 150
    assert ingestion["event_declared_independence_group_count"] == 112
    assert ingestion["event_canonical_publisher_lineage_group_count"] is None
    assert ingestion["event_exact_publisher_timestamp_count"] == 59
    assert ingestion["event_missing_exact_publisher_timestamp_count"] == 91
    assert ingestion["event_raw_hash_present_count"] == 0
    assert ingestion["event_receipt_complete"] is False
    assert ingestion["event_model_eligible"] is False
    assert ingestion["scenario_count"] == 117
    assert ingestion["drift_feature_count"] == 204
    assert ingestion["drift_evaluated_feature_count"] == 0
    assert ingestion["walk_forward_forecast_count"] == 0
    assert ingestion["forecast_status"] == "NOT_ISSUED"
    assert ingestion["sec_edgar"]["status"] == "BLOCKED_CONFIGURATION"
    assert ingestion["sec_edgar"]["contact_identity_configured"] is False
    assert ingestion["feature_store_rebuild_from_raw_artifacts_implemented"] is False


    current_ci = data["ci_evidence"]["current_head_full_suite"]
    assert is_sha(current_ci["head_sha"])
    assert current_ci["run_id"] > 0
    assert current_ci["status"] in {"queued", "in_progress", "completed"}
    assert current_ci["conclusion"] in {"success", "failure", "cancelled", None}
    assert current_ci["passed"] >= 0
    assert current_ci["tests_failed"] >= 0
    assert current_ci["skipped"] >= 0
    assert current_ci["inclusive_coverage_percent"] >= 0
    current_pr_ci = data["ci_evidence"]["current_pr_head_ci"]
    assert is_sha(current_pr_ci["head_sha"])
    assert current_pr_ci["push_ci_run_id"] > 0
    assert current_pr_ci["push_ci_conclusion"] in {"success", "failure", "cancelled", None}
    assert current_pr_ci["pr_event_run_id"] > 0
    assert current_pr_ci["pr_event_conclusion"] in {"success", "failure", "cancelled", None}
    assert current_pr_ci["pr_event_full_suite_status"] in {"success", "failure", "skipped", "in_progress", "queued"}
    assert data["prediction_engine"]["walk_forward_forecasts"] == 0
    assert data["prediction_engine"]["forecast_issuance"] == "NOT_ISSUED"




def test_run250_records_per_run_integrity_but_rejects_forked_cross_run_continuity():
    data = load_map()
    run = data["latest_run_250"]
    ingestion = data["latest_run_250"]["latest_ingestion"]
    assert run["main_sha"] == data["repository_state"]["main_sha"]
    assert run["main_tree_entries"] == 3115
    assert ingestion["run_id"] == 44848909814
    assert ingestion["receipt_chain"] == "PASS"
    assert ingestion["raw_payload_hashes_verified"] == 25
    assert ingestion["raw_payload_hash_mismatches"] == 0
    assert ingestion["continuity"] == "FORKED"
    assert ingestion["artifact_reported_continuity"] == "CONTINUED"
    fork = ingestion["cross_run_fork_audit"]
    assert fork["status"] == "FORKED"
    assert fork["run25"]["previous_run_id"] == 44844499889
    assert fork["run26"]["previous_run_id"] == 44844499889
    assert fork["skipped_successful_run_id"] == 44844953105
    gap = ingestion["feature_store_gap"]
    assert gap["status"] == "REPAIR_REQUIRED"
    assert gap["omitted_snapshot_eligible_records"] == 118
    assert gap["run25_cumulative_records"] == 1981
    assert gap["run26_cumulative_records"] == 1969
    assert ingestion["walk_forward_forecasts"] == 0
    assert ingestion["drift_status"] == "INSUFFICIENT_DATA"
    assert ingestion["forecast_issuance"] == "NOT_ISSUED"
    assert data["run250_merge_decision"] == "NO_MERGE"
    assert data["run250_no_external_actions"] is True
    assert data["open_pr_backlog_summary"]["blocked"] == 2
    current_pr = next(item for item in data["open_pr_inventory"] if item["number"] == 1684)
    assert current_pr["head_sha"] == data["current_pr_head_sha"]

def test_latest_map_preserves_security_gates_and_open_pr_classifications():
    data = load_map()
    security = data["security_and_governance"]
    assert security["main_branch_protected"] is True
    assert security["protection_details_verified"] is False
    assert "403" in security["protection_details_api"]
    assert security["fallback_ruleset"]["enforcement"] == "disabled"
    assert security["pr_1673"]["draft"] is False
    assert security["pr_1673"]["merged"] is True
    assert security["pr_1673"]["formal_reviews"] == 0
    assert security["transitive_script_security_review"].lower() == "incomplete"
    assert security["transitive_script_review"] == security["transitive_script_security_review"]
    assert security["sensitive_branch_path"]["content_read"] is False
    writer = security["automatic_main_writer"]
    assert writer["active"] is False
    assert writer["permission"] == "permissions: {}"
    assert writer["direct_push_to_main"] is False
    assert writer["latest_run_id"] == 44903860656
    assert writer["latest_run_conclusion"] == "skipped"
    assert security["pages_publication_authorization"] == "NOT_GRANTED"
    backlog = data["open_pr_backlog"]
    summary = data["open_pr_backlog_summary"]
    assert len(backlog) == summary["total_open"]
    counts = {}
    for item in backlog:
        counts[item["classification"]] = counts.get(item["classification"], 0) + 1
    assert counts.get("blocked", 0) == summary["blocked"]
    assert counts.get("unique/unreviewed", 0) == summary["unique_unreviewed"]
    assert counts.get("ready", 0) == summary["ready"]
    assert counts.get("duplicate", 0) == summary["duplicate"]
    assert counts.get("superseded", 0) == summary["superseded"]
    expected_open_prs = {1684, 1685}
    assert {item["number"] for item in backlog} == expected_open_prs
    assert next(item for item in backlog if item["number"] == 1684)["classification"] == "blocked"
    assert next(item for item in backlog if item["number"] == 1685)["classification"] == "blocked"
    assert data["merge_decision"] == "POST_MERGE_VERIFIED_WITH_GOVERNANCE_EXCEPTION"
    assert data["run263_merge_decision"]["decision"] == "DO_NOT_MERGE"
    prior_ci = data["ci_evidence"]["pre_fix_pr_head_ci"]
    assert prior_ci["head_sha"] == "bdc77944fb6de3b2ce036a5cc26d0af2538ddb92"
    assert prior_ci["result"] == "failure"
    assert prior_ci["tests_failed"] == 2


def test_latest_map_preserves_evidence_qualified_capital_and_sbic_identity():
    data = load_map()
    capital = data["institutional_capital_reconciliation"]
    assert capital["pre_close_evernorth_xrp"]["units"] == 346284972
    assert capital["pre_close_evernorth_xrp"]["cumulative_impairment_usd"] == 504687812
    assert capital["cash_and_in_kind"]["xrp_purchased_with_cash"] == 84365876
    assert capital["cash_and_in_kind"]["ripple_direct_contribution_historical_carrying_value_usd"] == 0
    assert capital["post_close_pathfinder"]["combined_xrp"] == 473276430
    assert capital["sbi_holdings_ownership"]["class_a_shares"] == 9431914
    assert capital["sbi_holdings_ownership"]["class_c_shares"] == 2359038

    # Run254 preserves the newer SEC reconciliation without treating in-kind XRP,
    # debt, warrant proceeds, or optional equity-line capacity as spot purchases.
    run254 = data["run254_primary_source_reconciliation"]
    assert run254["artifact_path"] == (
        "research/xrp_intelligence/20261121T100955Z-run254-evernorth-q3-capital-and-institutional-network-reconciliation.json"
    )
    assert run254["source_count"] == 19
    assert run254["model_eligible"] is False
    assert run254["raw_http_bytes_captured"] is False
    assert run254["evernorth"]["cash_used_to_buy_xrp_usd"] == 214050000
    assert run254["evernorth"]["xrp_purchased_with_cash"] == 84365876
    assert run254["evernorth"]["investor_in_kind_xrp"] == 261919096
    assert run254["evernorth"]["in_kind_xrp_at_close"] == 388910554
    assert run254["evernorth"]["pathfinder_combined_xrp_derived"] == 473276430
    assert run254["sbi_holdings_ownership"]["class_a_shares"] == 9431914
    assert run254["sbi_holdings_ownership"]["class_c_shares"] == 2359038
    assert "not 473.276M of open-market buying" in run254["caveat"]

    sbic = data["sbic_identity_reconciliation"]
    assert sbic["entities"]["east"]["alias"] == "SBIC East Japan"
    assert sbic["entities"]["central"]["alias"] == "SBIC Central Japan"
    assert sbic["entities"]["west"]["alias"] == "SBIC West Japan"
    assert sbic["xrp_or_ripple_relationship"] == "No verified relationship found."

    # The market summary is diagnostic only. Raw payload hashes live in the
    # separate receipt artifacts; this summary must not imply per-book receipts.
    market = data["prediction_engine"]["latest_market_snapshot"]
    ingestion = data["prediction_engine"]["latest_ingestion"]
    assert market["source"].startswith(
        f"Barrot main scheduled ingestion run {ingestion['run_number']}"
    )
    assert market["data_cutoff_utc"] == ingestion["data_cutoff_utc"]
    assert market["model_eligible_for_directional_forecast"] is False
    normalized_prices = [
        venue.get("mid_usd", venue.get("normalized_mid_usd"))
        for venue in market["venue_books"]
        if venue.get("mid_usd") is not None or venue.get("normalized_mid_usd") is not None
    ]
    assert market["price_cluster_usd"]["low"] == min(normalized_prices)
    assert market["price_cluster_usd"]["high"] == max(normalized_prices)
    assert {item["venue"] for item in market["venue_books"]} == {
        "Coinbase", "Bitstamp", "Kraken", "OKX", "Bitbank"
    }
    bitbank = next(item for item in market["venue_books"] if item["venue"] == "Bitbank")
    assert bitbank["usd_normalized"] is False
    assert all("raw_sha256" not in item for item in market["venue_books"])
    assert ingestion["raw_payload_hashes_verified"] == 22
    assert ingestion["raw_payload_hash_mismatches"] == 0
    # Quote-basis evidence is stored separately from the market display summary.
    # It is top-of-book-only and shares one OKX publisher-independence group.
    quote_basis = data["prediction_engine"]["quote_basis"]
    assert quote_basis["status"] == "VERIFIED_TOP_OF_BOOK_ONLY"
    assert quote_basis["method"] == "same_venue_synchronized_top_of_book_product"
    assert quote_basis["usdt_usd_mid"] == 0.998045
    assert quote_basis["normalization_overstatement_if_usdt_assumed_usd_bps"] == 19.58829243797089
    assert quote_basis["depth_levels_normalized"] is False
    assert quote_basis["publisher_independence_group_count"] == 1
    assert "not consolidated executable liquidity" in market["interpretation"]


def test_latest_map_preserves_bny_custody_without_overclaiming_xrp_demand():
    graph = load_map()["institutional_relationship_graph"]
    bny = graph["bny_ripple"]
    assert bny["evidence_status"] == "verified_primary_source"
    assert "supports XRP and RLUSD" in bny["relationship"]
    assert any("XRP purchases" in item for item in bny["not_established"])
    assert graph["bny_c2fo_ripple"]["evidence_status"] == "announced_exploration"


def test_latest_map_preserves_unresolved_phrase_and_creator_identity_controls():
    phrases = load_map()["research_phrase_status"]
    assert "unresolved" in phrases["ASK Coin"].lower()
    assert "literal phrase is not established as a formal accounting term" in phrases["actual capital"].lower()
    assert "not evidence of xrp purchases" in phrases["actual capital"].lower()
    assert "sbic east japan" in phrases["SBIC, ChatGPT SBIC"].lower()
    assert "no formal openai partnership" in phrases["SBIC, ChatGPT SBIC"].lower()
    assert "exact-phrase corroboration is established" in phrases["SBIC, ChatGPT SBIC"].lower()
    assert "channel" in phrases["Camilla/Kamilah Stevenson"].lower()
    assert "ownership unverified" in phrases["Camilla/Kamilah Stevenson"].lower()



def test_run29_preserves_evernorth_capital_and_sbi_entity_boundaries():
    root = Path(__file__).resolve().parents[1]
    evidence_path = (
        root
        / "research"
        / "xrp_intelligence"
        / "20261118T230834Z-run29-market-institutional-reconciliation.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    evernorth = evidence["institutional"]["evernorth"]
    cash = evernorth["cash_flow_reconciliation"]
    assert evernorth["reported_total_xrp_at_close"] == 473276430
    assert cash["xrp_in_kind_contributions_at_close"] == 388910554
    assert cash["xrp_purchased_with_cash"] == 84365876
    assert (
        cash["xrp_in_kind_contributions_at_close"]
        + cash["xrp_purchased_with_cash"]
        == evernorth["reported_total_xrp_at_close"]
    )
    assert evernorth["sbi_group_cash_investment_usd"] == 200000000
    assert evernorth["sbi_group_voting_rights_percent"] == 36.1
    assert evernorth["sbi_group_economic_interest_percent"] == 20.5
    assert evernorth["model_eligible"] is False

    sbi = evidence["institutional"]["sbi_relationship_graph"]
    assert sbi["ripple_equity"]["stake_percent"] == 9
    assert sbi["ripple_equity"]["as_of_date"] == "2025-06-09"
    assert sbi["sbi_ripple_asia"]["sbi_group_voting_rights_percent"] == 60
    assert "does not handle XRP" in sbi["sbi_ripple_asia"]["caveat"]
    circle_jv = sbi["circle_sbi_japan"]
    assert circle_jv["ownership"] == {"circle_percent": 50, "sbi_percent": 50}
    assert "no significant operating results" in circle_jv["operating_status"]
    assert "not SBI Holdings corporate XRP ownership" in sbi["sbi_vc_trade"]["xrp_wallet_balance_note"]

    regulatory = evidence["regulatory"]
    assert regulatory["occ_trust_charters"]["ripple"]["effective_date"] == "2026-10-26"
    assert regulatory["occ_trust_charters"]["coinbase"]["effective_date"] == "2026-11-06"
    assert regulatory["ripple_sec_case"]["final_judgment_penalty_usd"] == 125035150
    assert regulatory["ripple_sec_case"]["injunction"] == "remains in effect"
    assert evidence["prediction_readiness"]["forecast_status"] == "NOT_ISSUED"


def test_run29_preserves_market_disagreement_and_wallet_coverage_effects():
    root = Path(__file__).resolve().parents[1]
    evidence_path = (
        root
        / "research"
        / "xrp_intelligence"
        / "20261118T230834Z-run29-market-institutional-reconciliation.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    derivatives = evidence["derivatives"]
    assert derivatives["liqwall"]["open_interest_usd"] != derivatives["tradradar"]["open_interest_usd"]
    assert derivatives["xrpsonar"]["open_interest_usd"] != derivatives["tradradar"]["open_interest_usd"]
    assert "do not average" in derivatives["reconciliation"].lower()
    assert "Do not average" in evidence["etf_flows"]["reconciliation"]

    balances = evidence["exchange_wallet_balances"]
    assert balances["same_wallet_change_30d_xrp"] == -390100000
    assert balances["naive_total_change_30d_xrp"] == 132200000
    assert balances["new_wallet_balances_30d_xrp"] == 522200000
    xrpsonar = balances["xrpsonar_crosscheck"]
    assert xrpsonar["tracked_exchange_wallets_xrp"] == 24670000000
    assert xrpsonar["tracked_exchange_wallets_xrp"] != balances["gross_attributed_balance_xrp"]

    kraken = evidence["market_snapshot"]["kraken_xrp_usd"]
    assert kraken["model_eligible"] is False
    assert kraken["raw_wire_bytes_captured"] is False
    assert "not independently captured HTTP wire bytes" in kraken["raw_sha256_scope"]
    assert evidence["prediction_readiness"]["forecast_status"] == "NOT_ISSUED"

def test_run31_primary_source_reconciliation_separates_supply_capital_and_distribution():
    root = Path(__file__).resolve().parents[1]
    evidence_path = (
        root
        / "research"
        / "xrp_intelligence"
        / "20261119T001700Z-run31-primary-source-capital-supply-circle-sbi-creator-reconciliation.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    capture = evidence["source_capture_status"]
    assert capture["raw_wire_bytes_captured"] is False
    assert capture["raw_source_sha256_receipts"] == "NOT_CAPTURED"
    assert capture["external_worm_anchor"] == "NOT_ANCHORED"

    sbi = evidence["sources"][0]["observations"]
    supply = sbi["xrp_supply_distribution_as_of"]
    assert supply == "2026-10-28"
    category_sum = (
        sbi["market_circulation_xrp_approx"]
        + sbi["ripple_holdings_not_in_circulation_xrp_approx"]
        + sbi["xrp_under_escrow_approx"]
        + sbi["burned_xrp_approx"]
    )
    assert category_sum == sbi["category_sum_xrp_approx"] == 99990000000
    assert sbi["unreconciled_rounding_residual_xrp_approx"] == 10000000
    assert sbi["maximum_supply_xrp"] - category_sum == 10000000
    assert sbi["evernorth_xrp_holdings_approx"] == 473000000
    assert sbi["sbi_group_voting_rights_percent"] == 36.1
    assert sbi["sbi_group_economic_interest_percent"] == 20.5
    assert "not establish barrot" in sbi["sbi_claude_deployment"]["barrot_connection"].lower()

    evernorth = evidence["sources"][1]["observations"]
    assert (
        evernorth["xrp_contributed_in_kind_at_close"]
        + evernorth["cash_used_to_purchase_xrp"]
        == evernorth["total_xrp_at_close_reconciled"]
    )
    assert evernorth["sbi_cash_attributed_to_total_purchase"].find("not attribute all") >= 0
    assert evernorth["operating_results"]["revenue_generated_to_date"] == "none reported"
    assert evernorth["dilution"]["remaining_warrants_shares"] == 8666279

    circle = evidence["sources"][3]["observations"]
    assert circle["coinbase_distribution_cost_q3_2026_usd"] == 331300000
    assert circle["coinbase_distribution_cost_nine_months_2026_usd"] == 986600000
    assert "not 50% of gross" in circle["economics_caveat"].lower()
    assert circle["circle_sbi_japan"]["circle_ownership_percent"] == 50
    assert circle["circle_sbi_japan"]["sbi_ownership_percent"] == 50

    videos = evidence["sources"][4:]
    assert videos[0]["attribution_status"] == "VIDEO_LEVEL_GUEST_MATCH_SUPPORTED"
    assert videos[1]["attribution_status"] == "UNVERIFIED"
    assert videos[2]["attribution_status"] == "UNVERIFIED_THIRD_PARTY_ATTRIBUTION"
    assert evidence["prediction_admission"]["model_eligible"] is False
    assert evidence["prediction_admission"]["directional_forecast_issued"] is False


def test_run227_ingestion_receipts_and_market_snapshot_are_not_forecast_signals():
    data = load_map()
    run = data["run227_snapshot"]
    assert run["run_id"] == 44565285365
    assert run["receipt_integrity"]["receipt_count"] == 34
    assert run["receipt_integrity"]["raw_retained"] == 22
    assert run["receipt_integrity"]["digest_only"] == 12
    assert run["receipt_integrity"]["raw_hashes_verified"] == 22
    assert run["receipt_integrity"]["raw_hash_mismatches"] == 0
    assert run["receipt_integrity"]["external_anchor"] == "NOT_ANCHORED"
    assert run["feature_store"]["latest_eligible"] == 128
    assert run["feature_store"]["latest_excluded"] == 367
    assert run["feature_store"]["point_in_time_violations"] == 0
    assert run["market"]["spot_orderbook_midpoints_usd"]["coinbase"]["mid"] == 0.97215
    assert run["market"]["spot_orderbook_midpoints_usd"]["bitstamp"]["mid"] == 0.97230
    assert run["market"]["spot_orderbook_midpoints_usd"]["kraken"]["mid"] == 0.972125
    assert run["market"]["spot_orderbook_midpoints_usd"]["okx"]["mid"] == 0.9720039715
    assert run["forecast"]["status"] == "NOT_ISSUED"
    assert run["forecast"]["walk_forward_forecasts"] == 0


def test_run227_main_workflow_differential_and_publication_gate_are_preserved():
    data = load_map()
    diff = data["run227_workflow_differential"]
    assert diff["main_paid_issue_hunter_run"] == 44523988640
    assert diff["main_paid_issue_publisher_run"] == 44524050218
    assert is_sha(diff["publisher_commit_main_sha"])
    assert diff["publisher_commit_main_sha"] != data["repository_state"]["main_sha"]
    assert diff["main_paid_issue_publisher"]["active"] is True
    assert diff["main_paid_issue_publisher"]["integration_disabled"] is True
    assert diff["pages"]["run_id"] == 44524140421
    assert diff["pages"]["authorized"] is False
    assert diff["main_sync_self_hosted_brain"]["pr_changes_self_hosted_brain_paths"] is True
    assert diff["main_deploy_a2a_worker"]["pr_changes_a2a_paths"] is False
    assert diff["main_coinbase_paper_trader"]["run_performed"] is False
    assert diff["main_barrot_sync"]["push_result"] == "Everything up-to-date"
    assert diff["pillars_check"]["conclusion"] == "failure"
    assert data["merge_decision"] == "POST_MERGE_VERIFIED_WITH_GOVERNANCE_EXCEPTION"
    assert data["run227_no_external_actions"] is True


def test_run227_nine_platform_map_does_not_invent_external_connections():
    data = load_map()
    state = data["run227_platform_status"]
    assert state["verified_live_platforms"] == [
        "ChatGPT session -> GitHub connector -> Barrot-Agent/B-Agent"
    ]
    assert state["unverified_platforms"] == [
        "Claude", "Grok", "Gemini", "Copilot", "Codex",
        "Hugging Face", "Kaggle", "Databricks"
    ]
    assert state["external_dispatches"] == 0
    assert state["external_data_transfers"] == 0
    assert state["independent_red_team_quorum"] is False


def test_run230_franklin_xrp_etf_cash_and_in_kind_flows_reconcile():
    root = Path(__file__).resolve().parents[1]
    evidence_path = (
        root
        / "research"
        / "xrp_intelligence"
        / "20261120T023122Z-run230-franklin-xrp-etf-sec-flow-reconciliation.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["model_eligible"] is False
    assert evidence["source_capture"]["raw_http_bytes_captured"] is False
    assert evidence["source_capture"]["raw_sha256_receipt"] == "NOT_CAPTURED"

    flows = evidence["six_months_ended_2026_09_30"]
    holdings = evidence["holdings_reconciliation"]
    assert flows["cash_xrp_purchases_usd"] == 83835501
    assert flows["cash_xrp_purchases_xrp"] == 62439066.2461
    assert flows["in_kind_contributions_usd"] == 95638129
    assert flows["in_kind_contributions_xrp"] == 71122292.9683
    assert flows["xrp_sold_for_fund_expenses"] == 108833.83
    assert flows["xrp_redemptions"] == 0
    assert flows["in_kind_xrp_redemptions"] == 0
    assert holdings["net_increase_xrp"] == 133452525.3844
    assert abs((holdings["ending_xrp"] - holdings["beginning_xrp"]) - holdings["net_increase_xrp"]) < 1e-6
    valuation = evidence["valuation_interpretation"]
    expected_discount = (holdings["ending_cost_usd"] - holdings["ending_fair_value_usd"]) / holdings["ending_cost_usd"] * 100
    assert abs(valuation["fair_value_discount_to_cost_percent"] - expected_discount) < 1e-9
    assert (
        holdings["cash_purchased_xrp"]
        + holdings["in_kind_contributed_xrp"]
        - holdings["xrp_sold_for_fund_expenses"]
        == holdings["net_increase_xrp"]
    )
    roles = evidence["custody_and_prime_broker_roles"]
    assert roles["xrp_custodian"] == "Coinbase Custody Trust Company, LLC"
    assert roles["prime_broker"] == "Coinbase Inc. (affiliate of XRP custodian)"
    assert roles["cash_custodian"] == "BNY Mellon Asset Servicing"


def test_run230_circle_coinbase_distribution_economics_keep_accounting_boundaries():
    root = Path(__file__).resolve().parents[1]
    evidence_path = (
        root
        / "research"
        / "xrp_intelligence"
        / "20261120T025053Z-run230-circle-coinbase-usdc-distribution-economics.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["model_eligible"] is False
    assert evidence["source_capture"]["raw_http_bytes_captured"] is False
    assert evidence["source_capture"]["raw_sha256_receipt"] == "NOT_CAPTURED"

    circle = evidence["circle_filing"]
    coinbase = evidence["coinbase_filing"]
    assert circle["distribution_costs_to_coinbase_usd"]["q3_2026"] == 331300000
    assert circle["distribution_costs_to_coinbase_usd"]["q3_2025"] == 361300000
    assert circle["distribution_costs_to_coinbase_usd"]["nine_months_2026"] == 986600000
    assert circle["distribution_costs_to_coinbase_usd"]["nine_months_2025"] == 996800000
    assert circle["nine_month_decrease_to_coinbase_usd"] == -10200000
    assert coinbase["stablecoin_revenue_usd"]["q3_2026"] == 306905000
    assert coinbase["stablecoin_revenue_usd"]["nine_months_2026"] == 904487000
    assert coinbase["higher_average_usdc_balance_effect_usd"]["q3"] == 84600000
    assert coinbase["higher_average_usdc_balance_effect_usd"]["nine_months"] == 201600000
    assert coinbase["lower_interest_rate_effect_usd"]["q3"] == 52800000
    assert coinbase["lower_interest_rate_effect_usd"]["nine_months"] == 166200000
    assert evidence["interpretation"]["circle_distribution_costs_equal_coinbase_revenue"] is False
    assert evidence["interpretation"]["xrp_as_required_bridge_evidenced"] is False


def test_run258_records_ingestion_recovery_and_run259_exact_head_state():
    data = load_map()
    run = data["latest_run_258"]
    assert run["main_sha"] == data["repository_state"]["main_sha"]
    assert run["main_tree_entries"] == 3115
    assert run["integration_tree_entries"] == 3115
    assert run["main_paths_missing_from_integration"] == 0
    assert run["ingestion_run_id"] == 44869770831

    ingestion = run["latest_ingestion"]
    assert ingestion["receipt_count"] == 34
    assert ingestion["raw_retained"] == 22
    assert ingestion["digest_only"] == 12
    assert ingestion["raw_payload_hashes_verified"] == 22
    assert ingestion["raw_payload_hash_mismatches"] == 0
    assert ingestion["feature_history_records"] == 2446
    assert ingestion["snapshots"] == 6
    assert ingestion["eligible_features"] == 123
    assert ingestion["excluded_features"] == 367
    assert ingestion["cross_run_fork_audit"]["status"] == "FORKED"
    assert ingestion["cross_run_fork_audit"]["skipped_successful_run_id"] == 44844953105
    assert ingestion["artifact_reported_continuity"] == "CONTINUED"
    assert ingestion["event_receipt_complete"] is False
    assert ingestion["walk_forward_forecasts"] == 0
    assert ingestion["forecast_issuance"] == "NOT_ISSUED"

    recovery = run["local_feature_store_reconciliation"]
    assert recovery["status"] == "LOCAL_ONLY_VERIFIED_NOT_COMMITTED"
    assert recovery["recovered_records"] == 118
    assert recovery["pre_recovery_main_records"] == 2446
    assert recovery["reconciled_local_records"] == 2564
    assert recovery["reconciled_local_snapshots"] == 7
    assert recovery["reconciled_local_source_snapshot_rows"] == 81
    assert recovery["sqlite_integrity"] == "ok"
    assert recovery["all_snapshot_manifests_verified"] is True
    assert recovery["all_feature_record_rows_verified"] is True
    assert recovery["all_source_lineage_rows_verified"] is True
    assert recovery["backfill_hidden_before_store_receipt"] is True
    assert recovery["backfill_visible_at_store_receipt"] is True
    assert recovery["not_committed_to_repository"] is True

    market = run["market_snapshot"]
    assert market["research_only"] is True
    assert market["bitstamp_24h_change_percent"] == -8.98
    assert market["price_cluster_usd"]["low"] == 0.874585
    assert market["price_cluster_usd"]["high"] == 0.8749190095
    assert run["research_only_observations"]["bitbank_latest_60_trade_sample"]["model_eligible"] is False
    assert run["research_only_observations"]["xrp_etf_flows"]["model_eligible"] is False
    assert run["forecast"]["status"] == "NOT_ISSUED"
    assert run["no_external_actions"] is True

    pr = next(item for item in run["open_pr_inventory"] if item["number"] == 1684)
    assert pr["head_sha"] == run["current_pr_before_handoff_head_sha"]
    assert pr["full_suite"]["passed"] == 4536
    assert pr["full_suite"]["failed"] == 0
    assert pr["fail_closed"]["conclusion"] == "failure"
    assert data["run258_merge_decision"] == "NO_MERGE"
    assert data["run259_evidence_record"]["full_suite_passed"] == 4539
    assert data["run259_evidence_record"]["full_suite_failed"] == 0
    assert data["run259_evidence_record"]["full_suite_skipped"] == 1
    assert data["run259_merge_decision"] == "NO_MERGE"
    assert data["run259_no_external_actions"] is True


def test_run260_records_latest_main_ingestion_and_real_artifact_backfill():
    data = load_map()
    run = data["latest_run_260"]
    assert run["main_sha"] == data["repository_state"]["main_sha"]
    assert run["current_pr"]["head_sha"] == run["current_pr_ci"]["head_sha"]
    assert run["current_pr_ci"]["full_suite"]["passed"] == 4542
    assert run["current_pr_ci"]["full_suite"]["failed"] == 0
    assert run["current_pr_ci"]["full_suite"]["skipped"] == 1
    assert run["current_pr_ci"]["backfill_replay_conclusion"] == "success"

    ingestion = run["latest_ingestion"]
    assert ingestion["run_id"] == 44888553926
    assert ingestion["receipt_count"] == 34
    assert ingestion["raw_retained"] == 22
    assert ingestion["digest_only"] == 12
    assert ingestion["feature_store_snapshots"] == 10
    assert ingestion["feature_store_records"] == 16094
    assert ingestion["event_receipt_complete"] is False
    assert ingestion["walk_forward_forecasts"] == 0
    assert ingestion["forecast_issuance"] == "NOT_ISSUED"

    backfill = run["backfill_replay"]
    assert backfill["status"] == "CI_REAL_ARTIFACT_REPLAY_VERIFIED_NOT_APPLIED_TO_MAIN"
    assert backfill["recovered_records"] == 118
    assert backfill["recovered_source_count"] == 11
    assert backfill["after_snapshot_count"] == 11
    assert backfill["after_record_count"] == 16212
    assert backfill["sqlite_integrity"] == "ok"
    assert backfill["all_snapshot_manifests_verified"] is True
    assert backfill["all_feature_record_rows_verified"] is True
    assert backfill["all_source_lineage_rows_verified"] is True
    assert backfill["visible_before_receipt"] is False
    assert backfill["visible_after_receipt"] is True
    assert backfill["not_committed_to_main"] is True
    assert backfill["receipt_sha256"] == "9f1c73684f548bfb07893cb57f5d3603bb61b6b83246ed903e2a85674aeeec2e"
    assert run["forecast"]["status"] == "NOT_ISSUED"
    assert run["no_external_actions"] is True


def test_run254_evernorth_capital_and_sbi_ownership_are_typed_and_model_ineligible():
    root = Path(__file__).resolve().parents[1]
    evidence_path = (
        root
        / "research"
        / "xrp_intelligence"
        / "20261121T100955Z-run254-evernorth-q3-capital-and-institutional-network-reconciliation.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["model_eligible"] is False
    assert evidence["raw_capture"]["raw_http_bytes_captured"] is False

    capital = evidence["capital_reconciliation"]
    preclose = capital["as_of_2026_09_30"]
    assert preclose["xrp_held"] == 346284972
    assert preclose["advance_funding_cash_received_usd"] == 214050000
    assert preclose["xrp_purchased_with_that_cash"] == 84365876
    assert preclose["investor_in_kind_xrp_subscriptions"] == 261919096
    close = capital["at_2026_10_09_close"]
    assert close["in_kind_xrp_total"] == 388910554
    assert close["combined_pathfinder_xrp_derived"] == 473276430

    sbi = evidence["ownership_and_control"]["sbi_holdings_evernorth_beneficial_ownership"]
    assert sbi["class_a_shares"] == 9431914
    assert sbi["class_c_shares"] == 2359038
    assert sbi["class_a_percentage_derived"] == 39.9
    assert sbi["class_c_percentage_derived"] == 7.5
    assert "not separately reconcile" in evidence["ownership_and_control"]["sbi_cash_amount"]["caveat"].lower()

    relationships = evidence["institutional_relationship_graph"]
    assert any(x["from"] == "Ripple" and x["to"] == "Coinbase" for x in relationships)
    assert any(x["from"] == "Circle" and x["to"] == "BNY" for x in relationships)
    assert any(x["from"] == "SBIC East/Central/West" and x["to"] == "SBI Holdings" for x in relationships)
    assert evidence["model_admission"]["forecast_status"] == "NOT_ISSUED"


def test_run262_backfill_network_and_freshness_evidence_remain_non_forecast_eligible():
    data = load_map()
    root = Path(__file__).resolve().parents[1]

    backfill = data["latest_backfill_verification"]
    assert backfill["workflow_run_id"] == 44897424185
    assert backfill["workflow_head_sha"] == "373721be6bc00c81ae25e8ea7c7be21abdde7992"
    assert backfill["status"] == "VERIFIED_IN_CI_ISOLATED_COPY_NOT_APPLIED_TO_MAIN"
    assert backfill["records_before"] == 16200
    assert backfill["records_after"] == 16318
    assert backfill["recovered_records"] == 118
    assert backfill["snapshots_before"] == 11
    assert backfill["snapshots_after"] == 12
    assert backfill["sqlite_integrity"] == "ok"
    assert backfill["visible_before_receipt"] is False
    assert backfill["visible_after_receipt"] is True
    assert backfill["external_anchor_status"] == "NOT_ANCHORED"
    backfill_artifact = json.loads((root / backfill["artifact_path"]).read_text(encoding="utf-8"))
    assert backfill_artifact["reconciliation_sha256"] == backfill["reconciliation_sha256"]
    assert backfill_artifact["backfill_applied_to_main"] is False

    network = data["run262_institutional_network_reconciliation"]
    assert network["model_eligible"] is False
    network_artifact = json.loads((root / network["artifact_path"]).read_text(encoding="utf-8"))
    assert network_artifact["model_eligible"] is False
    assert network_artifact["source_capture"]["raw_http_bytes_captured"] is False
    ripple_coinbase = next(edge for edge in network_artifact["network_edges"] if edge["edge_id"] == "ripple_coinbase_rlusd")
    assert ripple_coinbase["collateral_support_status"] == "FUTURE_NOT_LIVE_AT_ANNOUNCEMENT"
    circle_ripple = next(edge for edge in network_artifact["network_edges"] if edge["edge_id"] == "bny_shared_node")
    assert "No direct Circle-Ripple partnership" in circle_ripple["details"][0] or circle_ripple["status"] == "INDIRECT_COMMON_NODE"

    freshness = data["run262_cross_analysis_quality"]["sentiment_profile"]
    assert freshness["XRP"]["forecast_eligible"] is False
    assert freshness["XRP"]["latest_sentiment_age_hours"] > 48
    assert freshness["BTC"]["forecast_eligible"] is False
    assert data["run262_cross_analysis_quality"]["entity_cooccurrence"]["per_asset_separation"] is False

    creator = data["run262_creator_identity_review"]
    assert creator["person_identity_status"] == "VERIFIED_WITH_HIGH_CONFIDENCE"
    assert creator["channel_ownership_status"] == "UNVERIFIED"
    assert len(creator["verified_youtube_videos"]) == 1
    assert creator["xrp_youtube_video_inventory_status"] == "NONE_VERIFIED"

    assert data["run262_exact_head_ci"]["full_repository_suite"]["passed"] == 4544
    assert data["run262_exact_head_ci"]["full_repository_suite"]["failed"] == 0
    assert data["run262_exact_head_ci"]["full_repository_suite"]["skipped"] == 1
    assert data["run262_merge_decision"]["decision"] == "DO_NOT_MERGE"
    assert data["run262_no_external_actions"]["merge_performed"] is False




def test_run265_binds_current_pr_ci_backfill_and_forecast_gate():
    data = load_map()
    run = data["run265_evidence_record"]
    assert run["main_sha"] == data["current_main_sha"]
    # Run265 is a historical capture. Its head must not be compared with the later current PR head.
    assert run["head_sha"] == "85ebfb943edd19999331c1890ced02767d134a6a"
    assert run["head_sha"] != data["current_pr_head_sha"]
    assert run["full_suite_passed"] == 4539
    assert run["full_suite_failed"] == 6
    assert run["full_suite_skipped"] == 1
    assert run["forecast_status"] == "NOT_ISSUED"

    # Current PR state is validated in Run271. This historical Run265 test
    # must not bind itself to whichever PR head happens to be open later.

    backfill = data["run265_backfill_verification"]
    assert backfill["run_id"] == 44911087849
    assert backfill["records_before"] == 16570
    assert backfill["records_after"] == 16688
    assert backfill["visible_before_receipt"] is False
    assert backfill["visible_after_receipt"] is True

    assert data["run265_merge_decision"]["decision"] == "DO_NOT_MERGE"
    assert data["run265_no_external_actions"]["main_modified"] is False
    assert data["run265_no_external_actions"]["merge_performed"] is False


def test_run269_binds_main_run46_microstructure_and_prediction_gates():
    data = load_map()
    run = data["latest_run_269"]
    root = Path(__file__).resolve().parents[1]
    artifact = json.loads((root / run["artifact_path"]).read_text(encoding="utf-8"))

    assert artifact["run_id"] == 269
    assert data["current_main_sha"] == "550a647ee7269a704d4600ff337b2145acc90473"
    assert run["main_ingestion_run_id"] == 44928553996
    assert run["pr_exact_head_ci_run_id"] == 44926486835
    assert run["pr_exact_head_full_suite"]["passed"] == 4556
    assert run["pr_exact_head_full_suite"]["failed"] == 0
    assert run["main_ingestion"]["feature_store_history_record_count"] == 17062
    assert run["main_ingestion"]["receipt_count"] == 34
    assert run["main_ingestion"]["raw_payload_hashes_verified"] == 22
    assert run["main_ingestion"]["raw_payload_hash_mismatches"] == 0
    assert run["market_snapshot"]["price_cluster_usd"]["low"] == 0.930215
    assert run["market_snapshot"]["quote_basis"]["usdt_usd_mid"] == 0.998275
    assert run["market_snapshot"]["model_eligible_for_directional_forecast"] is False
    assert run["event_and_drift_quality"]["raw_hash_present"] == 0
    assert run["event_and_drift_quality"]["walk_forward_origins"] == 0
    assert run["merge_decision"] == "DO_NOT_MERGE"
    assert run["post_evidence_commit_ci_pending"] is True

    assert artifact["model_eligible"] is False
    assert artifact["raw_payload_integrity"]["raw_payload_hashes_verified"] == 22
    assert artifact["raw_payload_integrity"]["raw_payload_hash_mismatches"] == 0
    assert artifact["event_timeline"]["raw_hash_present_count"] == 0
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["prediction_readiness"]["directional_forecast"] == "NOT_ISSUED"
    assert artifact["prediction_readiness"]["walk_forward_origins"] == 0
    assert artifact["historical_batch"]["binance_hourly_close"]["known_at_utc"] == "2026-11-21T07:13:43.810048Z"
    assert artifact["historical_batch"]["binance_hourly_close"]["historical_values_available_before_known_at"] is False
    assert artifact["backfill_replay"]["receipt_clock"]["store_receipt_time_is_actual_recovery_time"] is False
    assert artifact["backfill_replay"]["receipt_clock"]["store_receipt_time_is_post_append_availability_bound"] is True
    assert artifact["institutional_and_collateral_data"]["model_eligible_features"] == 0

    assert artifact["receipt_chain"]["cross_run_chain_sha256"] == "db278839e9f44c32a7c0203ea8ef447efef2a15f852b28324953210b46dddaa8"
    assert artifact["receipt_chain"]["current_receipt_chain"]["chain_head_sha256"] == "bac4e2ab3b0329eaa13d8a37f16145801650a8409517115774199ac4d57b9f1a"
    assert run["main_ingestion"]["cross_run_chain_sha256"] == "db278839e9f44c32a7c0203ea8ef447efef2a15f852b28324953210b46dddaa8"
    assert run["main_ingestion"]["receipt_chain_head_sha256"] == "bac4e2ab3b0329eaa13d8a37f16145801650a8409517115774199ac4d57b9f1a"



def test_run270_binds_main_run47_and_current_pr_head_evidence():
    data = load_map()
    run = data["run270_evidence_record"]

    assert run["captured_at_utc"] == "2026-11-21T19:02:47Z"
    assert run["main_sha"] == data["current_main_sha"] == "550a647ee7269a704d4600ff337b2145acc90473"
    assert run["head_sha"] == "4b5b5d9aa32259914ebc45a79fc2ea59368af29f"
    assert run["head_sha"] != data["current_pr_head_sha"]
    assert run["main_tree_entries"] == 3115
    assert run["integration_tree_entries"] == 3123
    assert run["main_paths_missing_from_integration"] == 0
    assert run["integration_ahead_by"] == 108
    assert run["integration_behind_by"] == 0

    ci = run["pr_exact_head_ci"]
    assert ci["run_id"] == 44935321192
    assert ci["conclusion"] == "failure"
    assert ci["full_suite"]["passed"] == 4555
    assert ci["full_suite"]["failed"] == 2
    assert ci["full_suite"]["skipped"] == 1
    assert ci["full_suite"]["failing_tests"] == [
        "tests/test_xrp_nine_platform_map_latest.py::test_run265_binds_current_pr_ci_backfill_and_forecast_gate",
        "tests/test_xrp_nine_platform_map_latest.py::test_run269_binds_main_run46_microstructure_and_prediction_gates",
    ]

    ingestion = run["main_ingestion"]
    assert ingestion["run_id"] == 44934364490
    assert ingestion["run_number"] == 47
    assert ingestion["feature_store_history_record_count"] == 17168
    assert ingestion["feature_store_snapshot_count"] == 19
    assert ingestion["receipt_count"] == 34
    assert ingestion["retained_raw_payload_count"] == 22
    assert ingestion["digest_only_receipt_count"] == 12
    assert ingestion["cross_run_continuity_status"] == "CONTINUED"
    assert ingestion["cross_run_continuity_verified"] is True
    assert ingestion["cross_run_sequence"] == 19
    assert ingestion["event_receipt_complete"] is False
    assert ingestion["walk_forward_forecast_count"] == 0
    assert ingestion["forecast_status"] == "NOT_ISSUED"

    backfill = run["backfill_replay"]
    assert backfill["status"] == "VERIFIED_IN_ISOLATED_CI_COPY_NOT_APPLIED_TO_MAIN"
    assert backfill["records_before"] == 17168
    assert backfill["records_after"] == 17286
    assert backfill["snapshots_before"] == 19
    assert backfill["snapshots_after"] == 20
    assert backfill["recovered_records"] == 118
    assert backfill["recovered_source_lineages"] == 11
    assert backfill["visible_before_receipt"] is False
    assert backfill["visible_after_receipt"] is True
    assert backfill["reconciliation_sha256"] == "0ef48bcea7541895733ab74dbf33a6b85b71cdca96aad877696dc3f44b99deee"

    assert run["merge_decision"] == "DO_NOT_MERGE"
    assert run["main_unchanged"] is True
    assert run["no_external_actions"] is True


def test_run271_historical_record_binds_main_run48_market_flow_backfill_and_historical_pr_head():
    data = load_map()
    run = data["run271_evidence_record"]
    root = Path(__file__).resolve().parents[1]
    artifact = json.loads((root / run["artifact_path"]).read_text(encoding="utf-8"))

    assert artifact["run_id"] == 271
    assert run["main_sha"] == data["current_main_sha"] == "550a647ee7269a704d4600ff337b2145acc90473"
    assert run["head_sha"] == "d82b9127472efc96008cd3269de198e1611eefca"
    assert run["integration_ahead_by"] == 109
    assert run["integration_behind_by"] == 0
    assert run["changed_files"] == 19
    assert run["main_tree_entries"] == 3115
    assert run["integration_tree_entries"] == 3123

    ingestion = run["main_ingestion"]
    assert ingestion["run_id"] == 44939486791
    assert ingestion["run_number"] == 48
    assert ingestion["receipt_count"] == 34
    assert ingestion["raw_retained"] == 22
    assert ingestion["digest_only"] == 12
    assert ingestion["raw_payload_hashes_verified"] == 22
    assert ingestion["raw_payload_hash_mismatches"] == 0
    assert ingestion["receipt_chain_verified"] is True
    assert ingestion["receipt_chain_sequence"] == 20
    assert ingestion["feature_store_history_record_count"] == 17291
    assert ingestion["feature_store_snapshot_count"] == 20
    assert ingestion["eligible_feature_record_count"] == 123
    assert ingestion["excluded_feature_record_count"] == 367
    assert ingestion["delta_feature_record_count"] == 490
    assert ingestion["input_feature_record_count"] == 2230
    assert ingestion["event_count"] == 150
    assert ingestion["event_declared_independence_group_count"] == 112
    assert ingestion["event_canonical_publisher_lineage_group_count"] is None
    assert ingestion["event_raw_hash_present_count"] == 0
    assert ingestion["event_exact_publisher_timestamp_count"] == 59
    assert ingestion["event_missing_exact_publisher_timestamp_count"] == 91
    assert ingestion["drift_evaluated_feature_count"] == 0
    assert ingestion["walk_forward_forecast_count"] == 0
    assert ingestion["forecast_status"] == "NOT_ISSUED"

    market = run["market_snapshot"]
    assert market["price_cluster_usd"]["low"] == 0.93472
    assert market["price_cluster_usd"]["high"] == 0.9350966365
    assert market["quote_basis"]["usdt_usd_mid"] == 0.998235
    assert market["quote_basis"]["normalization_overstatement_if_usdt_assumed_usd_bps"] == 17.681207330939106
    assert market["model_eligible_for_directional_forecast"] is False

    etf = run["research_only_observations"]["xrp_etf_flows"]
    assert etf["data_as_of"] == "2026-11-20"
    assert etf["latest_date_direct_spot_flow_usd"] == -7452638
    assert etf["flow_method"] == "holdings_delta_not_issuer_ap_cash_flow"
    assert etf["model_eligible"] is False
    bitbank = run["research_only_observations"]["bitbank_latest_60_trade_sample"]
    assert bitbank["net_taker_flow_xrp"] < 0
    assert bitbank["sample_window_seconds"] == 418.818
    assert bitbank["model_eligible"] is False

    backfill = run["backfill_replay"]
    assert backfill["status"] == "VERIFIED_IN_ISOLATED_CI_COPY_NOT_APPLIED_TO_MAIN"
    assert backfill["records_before"] == 17291
    assert backfill["records_after"] == 17409
    assert backfill["recovered_records"] == 118
    assert backfill["recovered_source_lineages"] == 11
    assert backfill["sqlite_integrity"] == "ok"
    assert backfill["visible_before_receipt"] is False
    assert backfill["visible_after_receipt"] is True
    assert backfill["artifact_inventory_verified_count"] == 23
    assert backfill["artifact_inventory_digest_mismatches"] == 0
    assert backfill["store_receipt_time_is_actual_recovery_time"] is False

    ci = run["pr_head_ci"]
    assert ci["full_suite"]["passed"] == 4556
    assert ci["full_suite"]["failed"] == 2
    assert ci["full_suite"]["skipped"] == 1
    assert ci["backfill_replay"]["conclusion"] == "success"
    assert ci["dependency_audit"]["conclusion"] == "success"
    assert ci["fail_closed"]["conclusion"] == "failure_by_design"
    assert run["merge_decision"] == "DO_NOT_MERGE"
    assert run["main_unchanged"] is True
    assert run["no_external_actions"] is True

    assert artifact["run_id"] == 271
    assert artifact["main_ingestion"]["run_id"] == 44939486791
    assert artifact["backfill_replay"]["reconciliation_sha256"] == backfill["reconciliation_sha256"]
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["model_eligible"] is False

def test_run272_binds_current_main_run49_market_flow_backfill_and_pr_snapshot():
    data = load_map()
    run = data["run272_evidence_record"]
    root = Path(__file__).resolve().parents[1]
    artifact = json.loads((root / run["artifact_path"]).read_text(encoding="utf-8"))

    # This test binds immutable Run272 evidence. Global PR-head fields are
    # mutable and are validated by the latest-run test, not this historical one.
    assert data["latest_run_id"] >= 273
    assert run["main_sha"] == data["current_main_sha"] == "550a647ee7269a704d4600ff337b2145acc90473"
    assert run["head_sha"] == "460561ba6091d407c6ff3d10eb69145445c7e997"
    assert run["integration_ahead_by"] == 111
    assert run["integration_behind_by"] == 0
    assert run["changed_files"] == 21
    assert run["main_tree_entries"] == 3115
    assert run["integration_tree_entries"] == 3124

    assert artifact["run_id"] == 272
    assert artifact["model_eligible"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    ingestion = artifact["main_ingestion"]
    assert ingestion["run_id"] == 44944994673
    assert ingestion["receipts"] == 34
    assert ingestion["retained_raw_payloads"] == 22
    assert ingestion["digest_only_receipts"] == 12
    assert ingestion["retained_payload_hashes_verified"] == 22
    assert ingestion["retained_payload_hash_mismatches"] == 0
    assert ingestion["feature_store"]["history_records"] == 17397
    assert ingestion["feature_store"]["snapshots"] == 21
    assert ingestion["feature_store"]["latest_snapshot_records"] == 106
    assert ingestion["source_failures"]["total"] == 18
    assert ingestion["raw_only_sources"] == 23

    backfill = data["run272_backfill_verification"]
    assert backfill["records_before"] == 17397
    assert backfill["records_after"] == 17515
    assert backfill["recovered_records"] == 118
    assert backfill["snapshots_before"] == 21
    assert backfill["snapshots_after"] == 22
    assert backfill["artifact_zip_digests_verified"] == 24
    assert backfill["main_modified"] is False

    quality = data["run272_event_and_drift_quality"]
    assert quality["events"] == 150
    assert quality["scenarios"] == 117
    assert quality["raw_source_hash_present"] == 0
    assert quality["receipt_link_present"] == 0
    assert quality["receipt_complete"] is False
    assert quality["drift_features_considered"] == 204
    assert quality["drift_features_evaluated"] == 0
    assert quality["walk_forward_origins"] == 0
    assert quality["forecast_status"] == "NOT_ISSUED"
    assert data["run272_merge_decision"]["status"] == "BLOCKED"
    assert data["run272_no_external_actions"] is True


def test_full_repository_suite_is_not_duplicated_on_integration_push():
    workflow = (
        Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")
    lines = workflow.splitlines()
    full_suite_start = lines.index("  full-suite:")
    full_suite_block = []
    for line in lines[full_suite_start + 1 :]:
        if line.startswith("  ") and not line.startswith("    "):
            break
        full_suite_block.append(line)
    assert "    if: github.event_name != 'push' || github.ref == 'refs/heads/main'" in full_suite_block
    assert "  pull_request:" in lines
    assert "  workflow_dispatch:" in lines

