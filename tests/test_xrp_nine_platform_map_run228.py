from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run228.json"


def test_run228_map_is_complete_and_uses_least_claims():
    data = json.loads(MAP.read_text(encoding="utf-8"))
    assert len(data["platforms"]) == 9
    assert data["platforms"]["ChatGPT"]["authentication_status"] == "verified"
    assert data["platforms"]["ChatGPT"]["permissions"] == ["admin", "maintain", "push", "pull", "triage"]
    assert "not introspected" in data["platforms"]["ChatGPT"]["least_privilege"]
    for name, platform in data["platforms"].items():
        if name != "ChatGPT":
            assert platform["authentication_status"] == "unverified"
            assert platform["data_flow"] == "not_verified"
            assert platform["permissions"] == []
    assert data["coordination"]["external_dispatch_performed"] is False
    assert data["coordination"]["external_data_transfer_performed"] is False


def test_run228_map_keeps_merge_blockers_and_pr_backlog():
    data = json.loads(MAP.read_text(encoding="utf-8"))
    assert data["repository_state"]["integration"]["draft"] is True
    assert data["security_and_governance"]["main_branch_protected"] is True
    assert "403" in data["security_and_governance"]["detailed_branch_protection"]
    assert data["security_and_governance"]["workflow_security_audit"]["definitions_remaining"] == 35
    assert data["open_pr_backlog_summary"] == {
        "total_open": 14, "ready": 0, "blocked": 4,
        "unique_unreviewed": 9, "duplicate": 1, "superseded": 0
    }
    assert data["merge_decision"] == "NO_MERGE"
