import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "6229acd8367d9fedf73a86f8b5923dc480904aff"
RESEARCH_HEAD = "d0ba9aa89feba4cb6ace650c94c9f58a6584c340"


def test_run28_handoff_is_latest_and_preserves_verified_heads():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert handoff.startswith("# Run 28 — 2026-11-07T18:28:03Z")
    for value in (MAIN_SHA, INTEGRATION_HEAD, RESEARCH_HEAD):
        assert value in handoff
    assert "1,152 passed, 8 subtests passed" in handoff
    assert "2,043 passed, 8 subtests passed" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
    assert "No merge performed" in handoff
    assert "SBI Group is a founding validator" in handoff
    assert "Coinbase is listed as an exchange participant" in handoff
    assert "not a direct SBI-Coinbase XRP partnership" in handoff


def test_run28_platform_map_has_exact_current_ci_and_preserves_run26():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    assert current["run_id"] == 28
    assert current["main_sha"] == MAIN_SHA
    assert current["integration_head_before_map_commit"] == INTEGRATION_HEAD
    assert current["research_head"] == RESEARCH_HEAD
    assert current["integration"]["full_suite"].startswith("1,152 passed")
    assert current["integration"]["core_suite"].startswith("643 passed")
    assert current["integration"]["coverage_pct"] == 58.41
    assert current["integration"]["wheel_verification"] == "passed"
    assert current["research"]["full_suite"].startswith("2,043 passed")
    assert current["research"]["core_suite"].startswith("498 passed")
    assert current["research"]["dependency_audit"].startswith("passed")
    assert current["research"]["fail_closed_gate"].startswith("passed")
    assert current["merge_state"]["merge_performed"] is False
    assert current["merge_state"]["independent_approvals"] == 0
    assert current["forecast_status"] == "NOT_ISSUED"
    assert any(item.get("run_id") == 26 for item in data["prior_run_observations"])
    assert data["platforms"]["ChatGPT"]["last_verified_at_utc"] == "2026-11-07T18:28:03Z"
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False


def test_run28_market_and_institutional_evidence_remains_excluded_from_numeric_forecast_features():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    market = current["market_snapshot"]
    assert market["kraken"]["provider_timestamp"] is None
    assert market["okx"]["age_seconds"] > 300
    assert market["binance_perpetual"]["model_eligible"] is False
    assert market["binance_perpetual"]["status"] == "not_retrieved_http_451"
    assert market["limitations"]
    network = current["institutional_network"]
    assert "does not establish a direct SBI-Coinbase XRP partnership" in network["sbi_circle_arc"]
    assert "no XRP-specific balance disclosed" in network["coinbase_collateral"]
