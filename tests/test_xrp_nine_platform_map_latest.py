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
    assert next(item for item in backlog if item["number"] == 1665)["classification"] == "blocked"
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
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
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
