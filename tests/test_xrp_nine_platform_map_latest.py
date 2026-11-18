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
    assert data["coordination"]["external_dispatch_performed"] is False
    assert data["coordination"]["external_data_transfer_performed"] is False


def test_latest_map_matches_repository_and_forecast_admission_state():
    data = load_map()
    repo = data["repository_state"]
    assert repo["main_sha"] == "13c60af7079700a38b4226b9110d9c9377af7695"
    integration = repo["integration"]
    assert integration["pr_number"] == 1663
    assert integration["draft"] is True
    assert integration["snapshot_head_sha"] == "a87173273fdbab3c480b4d95bfec3a74db6f6621"
    assert integration["ahead_by"] == 304
    assert integration["changed_files"] == 1427
    assert integration["changed_workflow_files"] == 67
    assert integration["behind_by"] == 0
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
    current_ci = data["ci_evidence"]["current_head_full_suite"]
    assert current_ci["head_sha"] == integration["snapshot_head_sha"]
    assert current_ci["status"] == "completed"
    assert current_ci["conclusion"] == "failure"
    assert current_ci["passed"] == 4272
    assert current_ci["tests_failed"] == 2
    assert current_ci["skipped"] == 1
    previous_ci = data["ci_evidence"]["previous_verified_full_suite"]
    assert previous_ci["head_sha"] == "78ed0c1a2e6cec991f6069f4c624e5e40bc96fe0"
    assert previous_ci["passed"] == 4274
    assert previous_ci["failed"] == 0


def test_latest_map_preserves_security_gates_and_open_pr_classifications():
    data = load_map()
    security = data["security_and_governance"]
    assert security["main_branch_protected"] is True
    assert security["protection_details_verified"] is False
    assert security["fallback_ruleset"]["enforcement"] == "disabled"
    assert security["pr_1663"]["draft"] is True
    assert security["pr_1663"]["formal_reviews"] == 0
    assert security["transitive_script_security_review"] == "incomplete"
    assert security["transitive_script_review"] == security["transitive_script_security_review"]
    assert security["sensitive_branch_path"]["content_read"] is False
    assert security["automatic_main_writer"]["active"] is True
    assert len(data["open_pr_backlog"]) == 12
    assert next(item for item in data["open_pr_backlog"] if item["number"] == 1663)["classification"] == "blocked"
    assert next(item for item in data["open_pr_backlog"] if item["number"] == 1665)["classification"] == "blocked"
    assert next(item for item in data["open_pr_backlog"] if item["number"] == 1666)["classification"] == "blocked"
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
    assert capital["cash_and_in_kind"]["cash_used_to_purchase_xrp"] if "cash_used_to_purchase_xrp" in capital["cash_and_in_kind"] else capital["cash_and_in_kind"]["xrp_purchased_with_cash"] == 84365876
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
    assert market["price_usd"] == 0.9753
    assert market["source"] == "Kraken public ticker API — XRP/USD"
    assert market["model_eligible"] is False
    assert market["model_eligible"] is False
    assert data["prediction_engine"]["latest_ingestion"]["walk_forward_forecasts"] == 0
