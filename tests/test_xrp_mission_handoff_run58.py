import json
from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import ENDPOINTS, SCHEDULED_ENDPOINTS, WEEKLY_ENDPOINTS


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "eeb4950d6cbda6a32870dfe074f671c4ccbc843e"
RESEARCH_HEAD = "674919abe365e915877e7f1f4211df347dfc39a9"
HISTORICAL_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json"
CURRENT_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map_current.json"


def test_legacy_handoff_history_and_run111_current_handoff_bind_exact_heads_and_ci():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert handoff.startswith("# Current integrated Barrot handoff — ")
    assert "## Run 60 — current repository, exact-head verification and institutional-rails correction" in handoff[:3_000]
    assert "## Run 58 — current repository, endpoint inventory correction, exact-head verification and merge gate" in handoff[:3_000]
    for value in (MAIN_SHA, INTEGRATION_HEAD, RESEARCH_HEAD):
        assert value in handoff
    assert "1,208 passed, 8 subtests passed" in handoff
    assert "2,472 passed, 8 subtests passed" in handoff
    assert "42494136348" in handoff
    assert "42494136372" in handoff
    assert "42494136346" in handoff
    assert "42494763390" in handoff
    assert "42494763413" in handoff
    assert "42494763434" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
    assert "No merge was performed" in handoff

    current_handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF_CURRENT.md").read_text(encoding="utf-8")
    assert current_handoff.startswith("# Run 111 —")
    assert "1,343 passed" in current_handoff
    assert "59.48%" in current_handoff
    assert "Forecast status: NOT_ISSUED" in current_handoff
    assert "42743666268" in current_handoff


def test_run111_endpoint_registry_counts_match_current_map_and_preserves_prior_runs():
    assert len(ENDPOINTS) == 40
    assert len(SCHEDULED_ENDPOINTS) == 36
    assert len(WEEKLY_ENDPOINTS) == 2
    assert len({source_id for source_id, _ in ENDPOINTS}) == 40

    historical = json.loads(HISTORICAL_MAP.read_text(encoding="utf-8"))
    archived = historical["current_run_observations"]
    archived_engine = archived["prediction_engine"]
    assert archived["run_id"] == 70
    assert any(item.get("run_id") == 58 for item in historical["prior_run_observations"])
    assert archived_engine["endpoints"] == len(archived_engine["endpoint_ids"]) == 35
    assert archived_engine["scheduled_public_sources"] == len(archived_engine["scheduled_endpoint_ids"]) == 33

    current_data = json.loads(CURRENT_MAP.read_text(encoding="utf-8"))
    latest = current_data["latest_run_snapshot"]
    assert latest["run_id"] == 111
    assert latest["run"] == 111
    assert latest["mission"]
    assert "main_workflows" in latest
    assert "institutional_and_macro" in latest
    assert latest["handoff_map_descendant_parent_head"] == current_data["observed_integration_head_before_map_commit"]
    assert latest["prior_market_crosschecks"]
    assert "pages" in current_data["open_pr_inventory"]
    assert "main_active_privileged_writers" in current_data["workflow_safety_audit"]
    assert "additions" in current_data["branch_ancestry"]["pr_1640"]
    assert "blockers" in current_data["merge_state"]
    assert "circle_binance" in latest["institutional_and_macro"]
    assert latest["main_sha"] == "d4d43be3427375cf79d190e768976de062e20287"
    assert latest["integration_code_test_head"] == "d28612a2ac04e93338b0a8774a75fdc8181c3bbd"
    assert any(item.get("run") == 95 for item in current_data["run_history"])
    assert any(item.get("run") == 96 for item in current_data["run_history"])
    assert any(item.get("run") == 98 for item in current_data["run_history"])
    assert any(item.get("run") == 104 for item in current_data["run_history"])
    assert current_data["current_run_observations"]["run_id"] == 111
    assert any(item.get("run_id") == 104 for item in current_data["prior_run_observations"])
    assert any(item.get("run_id") == 82 for item in current_data["prior_run_observations"])
    assert latest["handoff_map_descendant_parent_head"] == "d28612a2ac04e93338b0a8774a75fdc8181c3bbd"
    assert latest["ci_evidence"]["full_suite"]["run_id"] == 42743666268
    assert latest["ci_evidence"]["full_suite"]["passed"] == 1343
    assert latest["ci_evidence"]["full_suite"]["failed"] == 0
    assert latest["ci_evidence"]["dependency_audit"]["run_id"] == 42743666428
    assert latest["ci_evidence"]["fail_closed_gate"]["run_id"] == 42743666412
    assert latest["institutional_and_macro"]["evernorth_sbi_ownership"]["sbi_ownership"]["percent_voting_power"] == 39.9

    engine = latest["prediction_engine"]
    assert engine["endpoints"] == len(ENDPOINTS) == 40
    assert engine["scheduled_public_sources"] == len(SCHEDULED_ENDPOINTS) == 36
    assert engine["weekly_sources"] == len(WEEKLY_ENDPOINTS) == 2
    assert engine["weekly_endpoint_ids"] == ["cftc_contract_status_index", "cftc_tff_financial_futures"]
    assert engine["excluded_xrpl_node_sources"] == 2
    assert latest["forecast_status"] == "NOT_ISSUED"
    assert latest["ci_evidence"]["full_suite"]["passed"] == 1343
    assert latest["ci_evidence"]["full_suite"]["failed"] == 0
    assert latest["ci_evidence"]["full_suite"]["subtests"] == 8
    assert latest["ci_evidence"]["full_suite"]["coverage_pct"] == 59.48
    assert latest["ci_evidence"]["latest_attempt"]["head_sha"] == latest["handoff_map_descendant_parent_head"]
    assert latest["ci_evidence"]["latest_attempt"]["full_suite"]["passed"] == 1343
    assert latest["ci_evidence"]["latest_attempt"]["full_suite"]["failed"] == 0
    assert latest["institutional_and_macro"]["sbi_ripple"]["sbi_ripple_asia_xrp_handling"].startswith("Ripple's official SBI Ripple Asia profile explicitly states")
    assert latest["institutional_and_macro"]["sbi_ripple"]["xrp_corridors"]["operational_entities"] == ["SBI Remit", "SBI VC Trade", "Coins.ph", "Tranglo"]
    assert latest["institutional_and_macro"]["sbi_ripple"]["sbi_group_ripple_equity"]["approximate_share_pct"] == 9
    assert latest["institutional_and_macro"]["xrpl_institutional_tokenization"]["aviva"]["issuer_seed_investment_gbp"] == 50000000
    assert latest["institutional_and_macro"]["xrpl_institutional_tokenization"]["franklin_templeton"]["cash_subscription_receipts_usd"] == 150000000
    assert latest["institutional_and_macro"]["xrpl_institutional_tokenization"]["franklin_templeton"]["xrp_purchase"] is False
    assert latest["xrpl_amendment_status"]["pending"]["ConfidentialTransfer"]["yes_votes"] == 21
    assert latest["xrpl_amendment_status"]["pending"]["Sponsor"]["yes_votes"] == 10
    assert latest["xrpl_amendment_status"]["threshold"]["minimum_votes_for_more_than_80pct"] == 29
    assert latest["identity_research"]["camilla_kamilah_stevenson"]["inventory_status"] == "CANDIDATE_LIST_ONLY_NOT_COUNTED_AS_VERIFIED_PERSONAL_UPLOADS"
    assert len(latest["identity_research"]["camilla_kamilah_stevenson"]["video_candidates"]) == 4


    assert latest["cftc_contract_universe"]["dropped_contract"]["code"] == "176LM2"
    assessment = latest["cftc_contract_universe"]["threshold_hypothesis"]["assessment"]
    assert assessment.startswith("PLAUSIBLE_UNCONFIRMED")
    assert "current-week reportable-trader count is unavailable" in assessment
    assert "status index does not state the reason" in assessment
    assert round(latest["cftc_contract_universe"]["comparable_change_pct"], 2) == -12.94
    assert latest["reviews"]["pr_1640"]["approved"] == 0
    assert latest["reviews"]["pr_1640"]["threads_unresolved"] == 0
    assert latest["merge_state"]["pages_deployment_authorized"] is False

    current_engine = current_data["prediction_engine"]
    assert current_engine["endpoints"] == 40
    assert current_engine["endpoint_ids"] == [source_id for source_id, _ in ENDPOINTS]
    assert current_engine["scheduled_public_sources"] == len(SCHEDULED_ENDPOINTS)
    assert current_engine["weekly_sources"] == len(WEEKLY_ENDPOINTS)
    assert current_engine["weekly_endpoint_ids"] == ["cftc_contract_status_index", "cftc_tff_financial_futures"]
    assert current_engine["endpoint_inventory_source_blob_sha"] == "2ec26865fddb75f87b9238dd343ee509386ca5c8"
    top_engine = current_data["top_prediction_engine"]
    assert top_engine["endpoints"] == len(top_engine["endpoint_ids"]) == len(ENDPOINTS) == 40
    assert top_engine["endpoint_ids"] == [source_id for source_id, _ in ENDPOINTS]
    assert top_engine["weekly_endpoint_ids"] == ["cftc_contract_status_index", "cftc_tff_financial_futures"]
    assert "40 total endpoint records" in top_engine["endpoint_inventory_correction"]
    assert current_data["workflow_safety_audit"]["xrp_public_ingestion"]["total_endpoints"] == 40
    assert current_data["workflow_safety_audit"]["xrp_public_ingestion"]["weekly_cftc_sources"] == 2
    assert latest["identity_research"]["japan_sbic"]["regional_entities"]["east"]["public_name"] == "SBIC East Japan"
    assert latest["identity_research"]["japan_sbic"]["regional_entities"]["central"]["public_name"] == "SBIC Central Japan"
    assert latest["identity_research"]["japan_sbic"]["regional_entities"]["west"]["public_name"] == "SBIC West Japan"
    assert latest["identity_research"]["japan_sbic"]["chatgpt_and_openai"]["sbi_holdings"].startswith("SBI Holdings")
    assert latest["identity_research"]["japan_sbic"]["chatgpt_and_openai"]["softbank_openai"].startswith("SB OAI Japan")
    assert "cash subscriptions into tokenized fund shares" in latest["identity_research"]["actual_capital"]["required_separation"]
    assert "cash actually used to buy XRP" in latest["identity_research"]["actual_capital"]["required_separation"]




def test_run58_merge_gate_remains_blocked_without_approvals_or_deployment_authority():
    data = json.loads(HISTORICAL_MAP.read_text(encoding="utf-8"))
    current = data["current_run_observations"]
    assert current["reviews"]["pr_1640"]["approving_reviews"] == 0
    assert current["reviews"]["pr_1643"]["approving_reviews"] == 0
    assert current["reviews"]["pr_1640"]["threads_unresolved"] == 0
    assert current["reviews"]["pr_1643"]["threads_unresolved"] == 0
    assert current["merge_state"]["branch_protection_status"] == "UNVERIFIED_HTTP_403"
    assert current["merge_state"]["pages_deployment_authorized"] is False
    assert current["merge_state"]["merge_performed"] is False
    assert current["external_actions"]["main_write"] is False
    assert current["external_actions"]["deployment"] is False
    assert current["forecast_status"] == "NOT_ISSUED"
