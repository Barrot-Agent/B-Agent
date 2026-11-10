import json
from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import ENDPOINTS, SCHEDULED_ENDPOINTS, WEEKLY_ENDPOINTS


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "eeb4950d6cbda6a32870dfe074f671c4ccbc843e"
RESEARCH_HEAD = "674919abe365e915877e7f1f4211df347dfc39a9"
HISTORICAL_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json"
CURRENT_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map_current.json"


def test_legacy_handoff_history_and_run112_current_handoff_bind_exact_heads_and_ci():
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
    assert current_handoff.startswith("# Run 112 —")
    assert "# Run 111 —" in current_handoff
    assert "1,347 passed" in current_handoff
    assert "59.48%" in current_handoff
    assert "Forecast status: NOT_ISSUED" in current_handoff
    assert "42747463986" in current_handoff
    assert "42747463965" in current_handoff
    assert "42747463968" in current_handoff
    assert "42743666268" in current_handoff


def test_current_endpoint_registry_matches_current_map_and_preserves_run111_history():
    assert len(ENDPOINTS) == 46
    assert len(SCHEDULED_ENDPOINTS) == 42
    assert len(WEEKLY_ENDPOINTS) == 2
    assert len({source_id for source_id, _ in ENDPOINTS}) == 46

    historical = json.loads(HISTORICAL_MAP.read_text(encoding="utf-8"))
    archived = historical["current_run_observations"]
    archived_engine = archived["prediction_engine"]
    assert archived["run_id"] == 70
    assert any(item.get("run_id") == 58 for item in historical["prior_run_observations"])
    assert archived_engine["endpoints"] == len(archived_engine["endpoint_ids"]) == 35
    assert archived_engine["scheduled_public_sources"] == len(archived_engine["scheduled_endpoint_ids"]) == 33

    current_data = json.loads(CURRENT_MAP.read_text(encoding="utf-8"))
    latest = current_data["latest_run_snapshot"]
    current = current_data["current_run_observations"]
    prior = current_data["prior_run_observations"]
    historical_111 = next(item for item in prior if item.get("run_id") == 111)
    run111 = historical_111["latest_run_snapshot"]

    # The current map must advance without rewriting the preserved Run111 record.
    assert latest["run_id"] == latest["run"] == current["run_id"] == current_data["run"]
    assert latest["captured_at_utc"] == current_data["captured_at_utc"] == current["captured_at_utc"]
    assert current_data["captured_at_utc"] <= current_data["last_verified_at_utc"]
    assert current["captured_at_utc"] <= current["last_verified_at_utc"]
    assert latest["mission"].startswith("XRP intelligence")
    assert latest["main_sha"] == current_data["main_sha"] == current["main_sha"]
    assert latest["handoff_map_descendant_parent_head"] == current["integration_head_before_map_commit"]
    assert "institutional_and_macro" in latest
    assert "workflow_safety" in latest
    assert latest["forecast_status"] == "NOT_ISSUED"
    assert any(item.get("run_id") == 82 for item in prior)
    assert any(item.get("run_id") == 104 for item in prior)
    assert any(item.get("run") == 95 for item in current_data["run_history"])
    assert any(item.get("run") == 96 for item in current_data["run_history"])
    assert any(item.get("run") == 98 for item in current_data["run_history"])
    assert any(item.get("run") == 104 for item in current_data["run_history"])

    assert current_data["open_pr_inventory"]["total"] == 373
    assert current_data["open_pr_inventory"]["drafts"] == 358
    assert current_data["open_pr_inventory"]["non_drafts"] == 15
    assert "pages" in current_data["open_pr_inventory"]
    assert current_data["branch_ancestry"]["pr_1660"]["changed_files"] == 950
    assert "blockers" in current_data["merge_state"]
    assert current_data["merge_state"]["pages_deployment_authorized"] is False
    assert current_data["merge_state"]["merge_performed"] is False
    assert current_data["reviews"]["pr_1660"]["approved"] == 0
    assert current_data["workflow_safety_audit"]["changed_workflow_files"] == 44
    assert current_data["workflow_safety_audit"]["quarantined_count"] == 25

    engine = current["prediction_engine"]
    expected_ids = [source_id for source_id, _ in ENDPOINTS]
    expected_scheduled_ids = [source_id for source_id, _ in SCHEDULED_ENDPOINTS]
    expected_weekly_ids = [source_id for source_id, _ in WEEKLY_ENDPOINTS]
    assert engine["endpoint_total"] == len(ENDPOINTS)
    assert engine["endpoint_ids"] == expected_ids
    assert engine["scheduled_endpoint_ids"] == expected_scheduled_ids
    assert engine["weekly_endpoint_ids"] == expected_weekly_ids
    assert engine["hourly_sources"] == len(SCHEDULED_ENDPOINTS)
    assert engine["weekly_cftc_sources"] == len(WEEKLY_ENDPOINTS)
    assert engine["excluded_noncommercial_xrpl_nodes"] == 2
    assert engine["forecast_status"] == "NOT_ISSUED"

    top_engine = current_data["top_prediction_engine"]
    assert top_engine["endpoint_total"] == len(ENDPOINTS)
    assert top_engine["hourly_sources"] == len(SCHEDULED_ENDPOINTS)
    assert top_engine["weekly_cftc_sources"] == len(WEEKLY_ENDPOINTS)
    assert top_engine["forecast_status"] == "NOT_ISSUED"
    assert top_engine["oos_lift"] == "NOT_DEMONSTRATED"
    assert top_engine["macro_event_adapters"] is False
    assert top_engine["event_timeline"] is False
    assert top_engine["scenario_counterhypothesis_runner"] is False

    ingestion = current_data["workflow_safety_audit"]["xrp_public_ingestion"]
    assert ingestion["total_endpoints"] == len(ENDPOINTS)
    assert ingestion["hourly_sources"] == len(SCHEDULED_ENDPOINTS)
    assert ingestion["weekly_cftc_sources"] == len(WEEKLY_ENDPOINTS)
    assert ingestion["active_on_main"] is False
    assert current_data["forecast_status"] == "NOT_ISSUED"

    # Run111 remains an immutable historical observation with its original counts and evidence.
    assert historical_111["captured_at_utc"] == "2026-11-10T02:37:25Z"
    assert run111["run_id"] == 111
    assert run111["main_sha"] == "d4d43be3427375cf79d190e768976de062e20287"
    assert run111["integration_code_test_head"] == "d28612a2ac04e93338b0a8774a75fdc8181c3bbd"
    historical_engine = run111["prediction_engine"]
    assert historical_engine["endpoints"] == 40
    assert historical_engine["scheduled_public_sources"] == 36
    assert historical_engine["weekly_sources"] == 2
    assert historical_engine["excluded_xrpl_node_sources"] == 2
    assert historical_engine["forecast_status"] == "NOT_ISSUED"
    assert run111["ci_evidence"]["full_suite"]["passed"] == 1343
    assert run111["ci_evidence"]["full_suite"]["failed"] == 0
    assert run111["ci_evidence"]["full_suite"]["subtests"] == 8
    assert run111["ci_evidence"]["full_suite"]["coverage_pct"] == 59.48
    assert run111["ci_evidence"]["dependency_audit"]["manifests"] == 6
    assert run111["ci_evidence"]["dependency_audit"]["known_vulnerabilities"] == 0
    assert run111["ci_evidence"]["fail_closed_gate"]["automatic_merge_disabled"] is True

    institution = run111["institutional_and_macro"]
    assert "circle_binance" in institution
    assert institution["evernorth_sbi_ownership"]["sbi_ownership"]["percent_voting_power"] == 39.9
    assert institution["sbi_ripple"]["sbi_ripple_asia_xrp_handling"].startswith("Ripple's official SBI Ripple Asia profile explicitly states")
    assert institution["sbi_ripple"]["xrp_corridors"]["operational_entities"] == ["SBI Remit", "SBI VC Trade", "Coins.ph", "Tranglo"]
    assert institution["sbi_ripple"]["sbi_group_ripple_equity"]["approximate_share_pct"] == 9
    assert institution["xrpl_institutional_tokenization"]["aviva"]["issuer_seed_investment_gbp"] == 50000000
    assert institution["xrpl_institutional_tokenization"]["franklin_templeton"]["cash_subscription_receipts_usd"] == 150000000
    assert institution["xrpl_institutional_tokenization"]["franklin_templeton"]["xrp_purchase"] is False

    amendments = run111["xrpl_amendment_status"]
    assert amendments["pending"]["ConfidentialTransfer"]["yes_votes"] == 21
    assert amendments["pending"]["Sponsor"]["yes_votes"] == 10
    assert amendments["threshold"]["minimum_votes_for_more_than_80pct"] == 29

    identity = run111["identity_research"]
    assert identity["camilla_kamilah_stevenson"]["inventory_status"] == "CANDIDATE_LIST_ONLY_NOT_COUNTED_AS_VERIFIED_PERSONAL_UPLOADS"
    assert len(identity["camilla_kamilah_stevenson"]["video_candidates"]) == 4
    assert identity["japan_sbic"]["regional_entities"]["east"]["public_name"] == "SBIC East Japan"
    assert identity["japan_sbic"]["regional_entities"]["central"]["public_name"] == "SBIC Central Japan"
    assert identity["japan_sbic"]["regional_entities"]["west"]["public_name"] == "SBIC West Japan"
    assert identity["japan_sbic"]["chatgpt_and_openai"]["sbi_holdings"].startswith("SBI Holdings")
    assert identity["japan_sbic"]["chatgpt_and_openai"]["softbank_openai"].startswith("SB OAI Japan")
    assert "cash subscriptions into tokenized fund shares" in identity["actual_capital"]["required_separation"]
    assert "cash actually used to buy XRP" in identity["actual_capital"]["required_separation"]

    cftc = run111["cftc_contract_universe"]
    assert cftc["dropped_contract"]["code"] == "176LM2"
    assessment = cftc["threshold_hypothesis"]["assessment"]
    assert assessment.startswith("PLAUSIBLE_UNCONFIRMED")
    assert "current-week reportable-trader count is unavailable" in assessment
    assert "status index does not state the reason" in assessment
    assert round(cftc["comparable_change_pct"], 2) == -12.94

    assert run111["reviews"]["pr_1640"]["approved"] == 0
    assert run111["reviews"]["pr_1640"]["threads_unresolved"] == 0
    assert run111["merge_state"]["pages_deployment_authorized"] is False


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
