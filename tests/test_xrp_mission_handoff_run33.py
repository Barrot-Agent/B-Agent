import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "073250e307ffdca29a68a888a6d9454e71ba8f4b"
RESEARCH_HEAD = "a3e9f537a0462b0583429fa3b9895be2fe7fc5cb"


def test_run33_handoff_records_exact_heads_and_full_suite_evidence():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert "## Run 33 follow-up — 2026-11-07T23:42:25Z" in handoff
    assert MAIN_SHA in handoff
    assert INTEGRATION_HEAD in handoff
    assert RESEARCH_HEAD in handoff
    assert "1,166 passed, 8 subtests passed" in handoff
    assert "2,188 passed, 8 subtests passed" in handoff
    assert "42426921909" in handoff
    assert "42426921796" in handoff
    assert "42426921810" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
    assert "No merge was performed" in handoff


def test_run33_platform_map_preserves_run31_and_records_current_research():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    run33 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 33)
    prior31 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 31)
    assert run33["run_id"] == 33
    assert run33["main_sha"] == MAIN_SHA
    assert run33["integration_head_before_map_commit"] == INTEGRATION_HEAD
    assert run33["research_head"] == RESEARCH_HEAD
    assert prior31["main_sha"] == MAIN_SHA
    assert run33["open_pr_inventory"] == {"total": 371, "drafts": 355, "non_drafts": 16}
    assert run33["branch_ancestry"]["integration"]["ahead"] == 607
    assert run33["branch_ancestry"]["research"]["ahead"] == 733
    assert run33["branch_ancestry"]["integration_only_paths"] == 168
    assert run33["branch_ancestry"]["research_only_paths"] == 517
    assert len(run33["branch_ancestry"]["shared_changed_paths"]) == 3
    assert run33["ci_evidence"]["integration"]["full_suite"].startswith("1,166 passed")
    assert run33["ci_evidence"]["research"]["full_suite"].startswith("2,188 passed")
    assert run33["ci_evidence"]["research"]["dependency_audit"].startswith("passed")
    assert run33["ci_evidence"]["research"]["fail_closed_gate"].startswith("passed")
    assert run33["reviews"]["pr_1640"]["approving_reviews"] == 0
    assert run33["reviews"]["pr_1643"]["approving_reviews"] == 0
    assert run33["merge_state"]["merge_performed"] is False
    assert run33["forecast_status"] == "NOT_ISSUED"
    assert any("20261107T234225Z-xrpl-depth-exchange-balance-rlusd-agentic-payments.json" in p for p in run33["research_artifacts_added"])


def test_run33_fuelmaps_candidate_is_not_misrepresented_as_a_connection():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    run33 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 33)
    candidate = run33["fuelmaps_mcp_candidate"]
    assert candidate["current_run_status"] == "NOT_CONNECTED_NOT_TESTED"
    assert candidate["endpoint"] == "https://fuelmaps.io/mcp"
    assert candidate["provider_claims"]["read_only"] is True
    assert "7d" in candidate["provider_claims"]["history_windows"]
    assert data["out_of_scope_provider_notes"]["Fuelmaps"]["current_run_status"] == "NOT_CONNECTED_NOT_TESTED"
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False


def test_run33_nine_platform_map_and_forecast_remain_fail_closed():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    assert data["platforms"]["ChatGPT"]["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert data["platforms"]["Copilot"]["authentication_status"] != "VERIFIED_CURRENT_SESSION"
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False
    run33 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 33)
    assert run33["prediction_engine"]["forecast_status"] == "NOT_ISSUED"
    assert run33["external_actions"]["real_money"] is False
    assert run33["captured_at_utc"] == "2026-11-07T23:42:25Z"
