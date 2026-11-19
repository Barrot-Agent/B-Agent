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
    assert integration["pr_number"] == 1663
    assert integration["state"] == "open"
    assert integration["draft"] is True
    assert is_sha(integration["snapshot_head_sha"])
    assert is_sha(integration["code_head_sha"])
    assert is_sha(integration["current_pr_head_sha"])
    assert integration["ahead_by"] == integration["commits"] > 0
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
    assert ingestion["run_id"] == 44301868145
    assert ingestion["receipt_count"] == 34
    assert ingestion["receipts"] == ingestion["receipt_count"]
    assert ingestion["source_failures"] == 21
    assert ingestion["walk_forward_forecasts"] == 0
    assert ingestion["forecast_issuance"] == "disabled"
    assert ingestion["external_anchor"] == "NOT_ANCHORED"
    assert ingestion["drift_status"] == "INSUFFICIENT_DATA"

    current_ci = data["ci_evidence"]["current_head_full_suite"]
    assert is_sha(current_ci["head_sha"])
    assert current_ci["run_id"] > 0
    assert current_ci["status"] in {"queued", "in_progress", "completed"}
    assert current_ci["conclusion"] in {"success", "failure", "cancelled"}
    assert current_ci["passed"] >= 0
    assert current_ci["tests_failed"] >= 0
    assert current_ci["skipped"] >= 0
    assert current_ci["inclusive_coverage_percent"] >= 0
    current_pr_ci = data["ci_evidence"]["current_pr_head_ci"]
    assert is_sha(current_pr_ci["head_sha"])
    assert current_pr_ci["push_ci_run_id"] > 0
    assert current_pr_ci["push_ci_conclusion"] in {"success", "failure", "cancelled"}
    assert current_pr_ci["pr_event_run_id"] > 0
    assert current_pr_ci["pr_event_conclusion"] in {"success", "failure", "cancelled"}
    assert current_pr_ci["pr_event_full_suite_status"] in {"success", "failure", "skipped", "in_progress", "queued"}
    assert data["prediction_engine"]["walk_forward_forecasts"] == 0
    assert data["prediction_engine"]["forecast_issuance"] == "disabled"


def test_latest_map_preserves_security_gates_and_open_pr_classifications():
    data = load_map()
    security = data["security_and_governance"]
    assert security["main_branch_protected"] is True
    assert security["protection_details_verified"] is False
    assert "403" in security["protection_details_api"]
    assert security["fallback_ruleset"]["enforcement"] == "disabled"
    assert security["pr_1663"]["draft"] is True
    assert security["pr_1663"]["formal_reviews"] == 0
    assert security["transitive_script_security_review"] == "incomplete"
    assert security["transitive_script_review"] == security["transitive_script_security_review"]
    assert security["sensitive_branch_path"]["content_read"] is False
    assert security["automatic_main_writer"]["active"] is True
    assert security["automatic_main_writer"]["integration_workflow_disabled"] is True
    assert security["automatic_main_writer"]["main_run_id"] == 44369074831
    assert security["automatic_main_writer"]["pages_deployment_run_id"] == 44396362354
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
    assert next(item for item in backlog if item["number"] == 1663)["classification"] == "blocked"
    assert next(item for item in backlog if item["number"] == 1665)["classification"] == "duplicate"
    assert next(item for item in backlog if item["number"] == 1666)["classification"] == "blocked"
    assert next(item for item in backlog if item["number"] == 1668)["classification"] == "blocked"
    assert data["merge_decision"] == "NO_MERGE"
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
    sbic = data["sbic_identity_reconciliation"]
    assert sbic["entities"]["east"]["alias"] == "SBIC East Japan"
    assert sbic["entities"]["central"]["alias"] == "SBIC Central Japan"
    assert sbic["entities"]["west"]["alias"] == "SBIC West Japan"
    assert sbic["xrp_or_ripple_relationship"] == "No verified relationship found."
    market = data["prediction_engine"]["latest_market_snapshot"]
    evidence_path = Path(__file__).resolve().parents[1] / market["artifact_path"]
    assert market["artifact_path"] == (
        "research/xrp_intelligence/20261119T000522Z-run31-exact-head-ci-and-market-evidence.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    provenance = evidence["market_snapshot"]["provenance"]
    assert provenance["raw_wire_bytes_captured"] is False
    assert provenance["external_worm_anchor"] == "NOT_ANCHORED"
    kraken_receipt = evidence["market_snapshot"]["kraken_xrp_usd"]
    assert market["price_usd"] == kraken_receipt["last_usd"]
    assert market["source"] == "Kraken public ticker API — XRP/USD"
    assert market["model_eligible"] is False
    assert market["raw_sha256"] == kraken_receipt["raw_response_sha256"]


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
    assert "unresolved" in phrases["actual capital"].lower()
    assert "unresolved" in phrases["SBIC, ChatGPT SBIC"].lower()
    assert "channel" in phrases["Camilla/Kamilah Stevenson"].lower()
    assert "ownership" in phrases["Camilla/Kamilah Stevenson"].lower()



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
    assert (
        sbi["market_circulation_xrp_approx"]
        + sbi["ripple_holdings_not_in_circulation_xrp_approx"]
        + sbi["xrp_under_escrow_approx"]
        + sbi["burned_xrp_approx"]
        == sbi["maximum_supply_xrp"]
    )
    assert sbi["evernorth_xrp_holdings_approx"] == 473000000
    assert sbi["sbi_group_voting_rights_percent"] == 36.1
    assert sbi["sbi_group_economic_interest_percent"] == 20.5
    assert "not establish Barrot" in sbi["sbi_claude_deployment"]["barrot_connection"].lower()

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
    assert circle["circle_sbi_japan"]["ownership_percent"] if "ownership_percent" in circle["circle_sbi_japan"] else circle["circle_sbi_japan"]["circle_ownership_percent"] == 50

    videos = evidence["sources"][4:]
    assert videos[0]["attribution_status"] == "VIDEO_LEVEL_GUEST_MATCH_SUPPORTED"
    assert videos[1]["attribution_status"] == "UNVERIFIED"
    assert videos[2]["attribution_status"] == "UNVERIFIED_THIRD_PARTY_ATTRIBUTION"
    assert evidence["prediction_admission"]["model_eligible"] is False
    assert evidence["prediction_admission"]["directional_forecast_issued"] is False
