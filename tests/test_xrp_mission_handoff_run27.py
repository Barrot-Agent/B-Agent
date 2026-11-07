import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "6229acd8367d9fedf73a86f8b5923dc480904aff"
RESEARCH_HEAD = "d0ba9aa89feba4cb6ace650c94c9f58a6584c340"


def test_run28_handoff_is_latest_and_preserves_verified_heads():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert handoff.startswith("## Exact-head test follow-up — 2026-11-07T18:42:51Z")
    assert "## Exact-head handoff/map CI follow-up — 2026-11-07T18:39:19Z" in handoff[:2_000]
    assert "# Run 28 — 2026-11-07T18:28:03Z" in handoff[:3_000]
    for value in (MAIN_SHA, INTEGRATION_HEAD, RESEARCH_HEAD):
        assert value in handoff
    assert "1,152 passed, 8 subtests passed" in handoff
    assert "2,043 passed, 8 subtests passed" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
    assert "No merge performed" in handoff
    assert "SBI Group is a founding validator" in handoff
    assert "Coinbase is listed as an exchange participant" in handoff
    assert "not a direct SBI-Coinbase XRP partnership" in handoff


def test_run28_platform_map_is_preserved_and_run30_is_current():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    prior28 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 28)
    assert current["run_id"] == 30
    assert current["main_sha"] == MAIN_SHA
    assert current["integration_head_before_map_commit"] == "a68f90bb883bacca1a0c2a8a5570b19f6a179c09"
    assert current["research_head"] == "0c41821e387bb10692122e4c064d5ca40c4a88e3"
    assert prior28["integration_head_before_map_commit"] == INTEGRATION_HEAD
    assert prior28["research_head"] == RESEARCH_HEAD
    ci = prior28["ci_evidence"]
    assert ci["integration"]["full_suite"].startswith("1,152 passed")
    assert ci["integration"]["core_suite"].startswith("643 passed")
    assert ci["integration"]["coverage_pct"] == 58.41
    assert ci["integration"]["wheel_verification"] == "passed"
    assert ci["research"]["full_suite"].startswith("2,043 passed")
    assert ci["research"]["core_suite"].startswith("498 passed")
    assert ci["research"]["dependency_audit"].startswith("passed")
    assert ci["research"]["fail_closed_gate"].startswith("passed")
    assert current["merge_state"]["merge_performed"] is False
    assert current["merge_state"]["independent_approvals"] == 0
    assert current["forecast_status"] == "NOT_ISSUED"
    assert current["ci_evidence"]["integration"]["full_suite"].startswith("1,161 passed")
    assert current["ci_evidence"]["research"]["full_suite"].startswith("2,085 passed")
    assert any(item.get("run_id") == 26 for item in data["prior_run_observations"])
    assert data["platforms"]["ChatGPT"]["last_verified_at_utc"] == "2026-11-07T20:03:08Z"
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False


def test_run28_market_and_institutional_evidence_remains_preserved_as_prior_run():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = next(item for item in data["prior_run_observations"] if item.get("run_id") == 28)
    market = current["market_snapshot"]
    assert market["kraken"]["provider_timestamp"] is None
    assert market["okx"]["age_seconds"] > 300
    assert market["binance_perpetual"]["model_eligible"] is False
    assert market["binance_perpetual"]["status"] == "not_retrieved_http_451"
    assert market["limitations"]
    network = current["institutional_network"]
    assert "does not establish a direct SBI-Coinbase XRP partnership" in network["sbi_circle_arc"]
    assert "XRP-specific collateral balances" in network["coinbase_collateral"]
    assert "not disclosed" in network["coinbase_collateral"]
