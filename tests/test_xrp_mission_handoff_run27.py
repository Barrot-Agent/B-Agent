import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "6229acd8367d9fedf73a86f8b5923dc480904aff"
RESEARCH_HEAD = "d0ba9aa89feba4cb6ace650c94c9f58a6584c340"


def test_run28_handoff_is_latest_and_preserves_verified_heads():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert handoff.startswith("# Current integrated Barrot handoff — ")
    assert re.search(r"(?m)^## Run \d+ — 2026-\d{2}-\d{2}T", handoff[:3_000])
    assert "## Exact-head handoff/map CI follow-up — 2026-11-07T18:39:19Z" in handoff
    assert "# Run 28 — 2026-11-07T18:28:03Z" in handoff
    for value in (MAIN_SHA, INTEGRATION_HEAD, RESEARCH_HEAD):
        assert value in handoff
    assert "1,152 passed, 8 subtests passed" in handoff
    assert "2,043 passed, 8 subtests passed" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
    assert "No merge performed" in handoff
    assert "SBI Group is a founding validator" in handoff
    assert "Coinbase is listed as an exchange participant" in handoff
    assert "not a direct SBI-Coinbase XRP partnership" in handoff


def test_run28_platform_map_is_preserved_and_run33_is_historical():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    run33 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 33)
    prior28 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 28)
    prior30 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 30)
    assert run33["run_id"] == 33
    prior34 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 34)
    assert prior34["run_id"] == 34
    assert data["current_run_observations"]["run_id"] >= 34
    prior31 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 31)
    assert run33["main_sha"] == MAIN_SHA
    assert run33["integration_head_before_map_commit"] == "073250e307ffdca29a68a888a6d9454e71ba8f4b"
    assert run33["research_head"] == "a3e9f537a0462b0583429fa3b9895be2fe7fc5cb"
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
    assert prior30["integration_head_before_map_commit"] == "7628c5db692124bfbe4a508a4810df4f699d3a87"
    assert prior30["research_head"] == "cdf2e32f22c5ee5abac6713aa94587fc47cff4a7"
    assert prior30["ci_evidence"]["integration"]["full_suite"].startswith("1,164 passed")
    assert prior30["ci_evidence"]["research"]["full_suite"] == "IN_PROGRESS; exact-head result not yet verified"
    assert prior30["ci_evidence"]["research"]["previous_verified_head"]["full_suite"].startswith("2,066 passed")
    assert run33["merge_state"]["merge_performed"] is False
    assert run33["merge_state"]["independent_approvals"] == 0
    assert run33["forecast_status"] == "NOT_ISSUED"
    assert run33["ci_evidence"]["integration"]["full_suite"].startswith("1,166 passed")
    assert run33["ci_evidence"]["research"]["full_suite"].startswith("2,188 passed")
    assert prior31["run_id"] == 31
    assert prior31["main_sha"] == MAIN_SHA
    assert any(item.get("run_id") == 26 for item in data["prior_run_observations"])
    assert run33["captured_at_utc"] == "2026-11-07T23:42:25Z"
    assert data["last_verified_at_utc"] == data["captured_at_utc"]
    assert data["platforms"]["ChatGPT"]["last_verified_at_utc"] <= data["last_verified_at_utc"]
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


def test_run31_handoff_records_exact_heads_market_and_sbi_reconciliation():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert "## Run 31 — 2026-11-07T20:49:41Z" in handoff
    assert "9100dbacb5f9f1b973b053a65ef1e91e96b64f72" in handoff
    assert "2d2e140c3bd4d09e20337caa6fc249a73916a63d" in handoff
    assert "f8b5f3031e1ae8f6fb19d07157ae732613434af0" in handoff
    assert "1,164 passed, 8 subtests passed" in handoff
    assert "2,100 passed, 8 subtests passed" in handoff
    assert "6,529,787" in handoff
    assert "1,633,180" in handoff
    assert "546,621" in handoff
    assert "E-jdY7gy7mQ" in handoff
    assert "NOT_ISSUED" in handoff
    assert "No merge was performed" in handoff


def test_run31_post_handoff_verification_records_exact_current_tip():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert "## Run 31 post-handoff verification — 2026-11-07T20:55:11Z" in handoff
    assert "a3cad42215b03e9d0e96219f393c655ee76fff75" in handoff
    assert "1,165 passed, 8 subtests passed" in handoff
    assert "58.49%" in handoff
    assert "installed wheel loaded Barrot V3, the XRP mission and canonical data assets" in handoff
    assert "GitHub Actions cache storage reaching its configured budget" in handoff
    assert "XRP perpetual futures, settled in USDC" in handoff
    assert "RLUSD collateral on Global Exchange as a future capability" in handoff
    assert "No merge or main-branch write is implied" in handoff
