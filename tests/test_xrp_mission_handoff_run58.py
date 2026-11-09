import json
from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import ENDPOINTS, SCHEDULED_ENDPOINTS, WEEKLY_ENDPOINTS


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "eeb4950d6cbda6a32870dfe074f671c4ccbc843e"
RESEARCH_HEAD = "674919abe365e915877e7f1f4211df347dfc39a9"
HISTORICAL_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json"
CURRENT_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map_current.json"


def test_run58_handoff_binds_exact_repository_heads_and_ci():
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


def test_run103_endpoint_registry_counts_match_current_map():
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
    assert latest["run_id"] == 103
    assert latest["run"] == 103
    assert latest["mission"]
    assert "main_workflows" in latest
    assert "institutional_and_macro" in latest
    assert latest["handoff_map_descendant_head"] == "32bd1c8c1ce76c1112a0daa8450e624c94c927fa"
    assert latest["prior_market_crosschecks"]
    assert "pages" in current_data["open_pr_inventory"]
    assert "main_active_privileged_writers" in current_data["workflow_safety_audit"]
    assert "additions" in current_data["branch_ancestry"]["pr_1640"]
    assert "blockers" in current_data["merge_state"]
    assert "circle_binance" in latest["institutional_and_macro"]
    assert latest["main_sha"] == "d4d43be3427375cf79d190e768976de062e20287"
    assert latest["integration_code_test_head"] == "0cced5af3b673b5d39e45cfc18c53416e1ed394a"
    assert any(item.get("run") == 95 for item in current_data["run_history"])
    assert any(item.get("run") == 96 for item in current_data["run_history"])
    assert any(item.get("run") == 98 for item in current_data["run_history"])
    assert any(item.get("run") == 103 for item in current_data["run_history"])
    assert current_data["current_run_observations"]["run_id"] == 82

    engine = latest["prediction_engine"]
    assert engine["endpoints"] == len(ENDPOINTS) == 40
    assert engine["scheduled_public_sources"] == len(SCHEDULED_ENDPOINTS) == 36
    assert engine["weekly_sources"] == len(WEEKLY_ENDPOINTS) == 2
    assert engine["weekly_endpoint_ids"] == ["cftc_contract_status_index", "cftc_tff_financial_futures"]
    assert engine["excluded_xrpl_node_sources"] == 2
    assert latest["forecast_status"] == "NOT_ISSUED"
    assert latest["ci_evidence"]["full_suite"]["passed"] == 1316
    assert latest["ci_evidence"]["full_suite"]["failed"] == 0
    assert latest["ci_evidence"]["full_suite"]["subtests"] == 8
    assert latest["ci_evidence"]["full_suite"]["coverage_pct"] == 59.36
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
    assert current_engine["endpoint_inventory_source_blob_sha"] == "f5fc3c4a45aaf826241e32faf00443e98bfa341a"


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
