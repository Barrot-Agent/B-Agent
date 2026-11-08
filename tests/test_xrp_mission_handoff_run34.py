from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "fdd5e60d971ff3e0f21cd574d860cd5281fdced7"
RESEARCH_HEAD = "06769f1d9667d5cb877e6e0321f9d9a9694b1dd6"
RESEARCH_HEAD_AFTER_FOLLOWUP = "a554dc3814fb0a9ed935fa83a2805caa3544915e"


def test_run34_handoff_records_exact_current_heads_and_ci():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert "## Run 34 — 2026-11-08T01:08:03Z" in handoff
    assert MAIN_SHA in handoff
    assert INTEGRATION_HEAD in handoff
    assert RESEARCH_HEAD in handoff
    assert RESEARCH_HEAD_AFTER_FOLLOWUP in handoff
    assert "20261108T011925Z-xrp-etf-flow-universe-and-sec-docket-reconciliation.json" in handoff
    assert "Coinbase's October 20, 2026 comment letter is on proposed Regulation Crypto Assets, **S7-2026-27**" in handoff
    assert "Ripple's May 7, 2026 letter is on the separate March 2026 interpretive release, **S7-2026-09**" in handoff
    assert "1,170 passed, 8 subtests passed" in handoff
    assert "2,214 passed, 8 subtests passed" in handoff
    for run_id in ("42429304866", "42429304980", "42429304893", "42429625747", "42429625684", "42429625687"):
        assert run_id in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
    assert "No merge was performed" in handoff


def test_run34_map_preserves_run33_and_records_current_tree_and_heads():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    prior33 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 33)
    assert current["run_id"] == 34
    assert current["main_sha"] == MAIN_SHA
    assert current["integration_head_before_map_commit"] == INTEGRATION_HEAD
    assert current["research_head"] == RESEARCH_HEAD
    assert current["research_head_after_followup"] == RESEARCH_HEAD_AFTER_FOLLOWUP
    assert current["research_updates_after_capture"][0]["new_head"] == RESEARCH_HEAD_AFTER_FOLLOWUP
    assert "research/xrp_intelligence/20261108T011925Z-xrp-etf-flow-universe-and-sec-docket-reconciliation.json" in current["research_artifacts_added"]
    assert prior33["captured_at_utc"] == "2026-11-07T23:42:25Z"
    assert current["open_pr_inventory"] == {"total": 371, "drafts": 355, "non_drafts": 16, "pages": [100, 100, 100, 71]}
    assert current["branch_ancestry"]["integration"] == {"ahead": 609, "behind": 0, "changed_paths": 172}
    assert current["branch_ancestry"]["research"] == {"ahead": 738, "behind": 0, "changed_paths": 527}
    assert current["branch_ancestry"]["integration_only_paths"] == 169
    assert current["branch_ancestry"]["research_only_paths"] == 524
    assert len(current["branch_ancestry"]["shared_changed_paths"]) == 3
    assert current["repository_tree"]["main"]["entries"] == 1403
    assert current["repository_tree"]["integration"]["test_modules"] == 126
    assert current["repository_tree"]["research"]["test_modules"] == 301


def test_run34_endpoint_count_and_fail_closed_prediction_status_are_current():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    engine = current["prediction_engine"]
    assert engine["endpoint_registry"] == {
        "total": 29,
        "scheduled": 27,
        "excluded_noncommercial_xrpl_node_sources": 2,
    }
    assert engine["forecast_status"] == "NOT_ISSUED"
    assert engine["demonstrated_out_of_sample_lift"] is False
    assert engine["validated_real_data_calibration"] is False
    assert engine["sufficient_shadow_outcomes"] is False
    assert current["merge_state"]["merge_performed"] is False
    assert current["external_actions"]["deployment"] is False
    assert current["external_actions"]["real_money"] is False


def test_run34_nine_platform_map_remains_truthful_and_least_privilege():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    assert data["last_verified_at_utc"] == "2026-11-08T01:08:03Z"
    assert data["platforms"]["ChatGPT"]["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert data["platforms"]["ChatGPT"]["data_flow"]["verified"] is True
    for name, platform in data["platforms"].items():
        if name != "ChatGPT":
            assert platform["data_flow"]["verified"] is False
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False
