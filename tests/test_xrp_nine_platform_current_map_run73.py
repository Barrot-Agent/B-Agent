from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json"
HISTORICAL = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json"


def test_run76_current_snapshot_preserves_run75_and_historical_map():
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    observation = current["current_run_observations"]
    prior75 = next(item for item in current["prior_run_observations"] if item.get("run_id") == 75)
    prior73 = next(item for item in current["prior_run_observations"] if item.get("run_id") == 73)
    assert current["captured_at_utc"] == current["last_verified_at_utc"]
    assert observation["captured_at_utc"] == current["captured_at_utc"]
    assert observation["last_verified_at_utc"] == current["last_verified_at_utc"]
    assert observation["run_id"] == 76
    assert observation["main_sha"] == "d4d43be3427375cf79d190e768976de062e20287"
    assert observation["integration_head_before_handoff_commit"] == "a87af9c9a37d145994f425aa3e9746dce89c5bd8"
    assert observation["research_head"] == "8fc9813e15ed925c2e9bc0c689ab4091398a82fb"
    assert prior75["captured_at_utc"] == "2026-11-09T01:36:00Z"
    prior75_ci = prior75["ci_evidence"]["integration"]["current_handoff_map_test_commit"]
    assert prior75_ci["status"] == "success"
    assert prior75_ci["full_suite"]["passed"] == 1234
    assert prior73["captured_at_utc"] == "2026-11-09T00:23:14Z"
    assert historical["captured_at_utc"] == "2026-11-08T22:30:23Z"
    assert historical["current_run_observations"]["run_id"] == 70


def test_run76_prediction_engine_contract_remains_fail_closed():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    observation = data["current_run_observations"]
    engine = observation["prediction_engine"]
    assert engine["endpoints"] == 35
    assert engine["scheduled_public_sources"] == 33
    assert engine["excluded_xrpl_node_sources"] == 2
    assert engine["forecast_status"] == "NOT_ISSUED"
    assert engine["oos_lift"] is False
    assert engine["real_data_calibration"] is False
    assert engine["shadow_outcomes"] is False
    assert engine["trusted_evaluator_key"] is False
    assert observation["forecast_status"] == "NOT_ISSUED"


def test_run76_platform_map_keeps_external_data_flows_unverified():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    assert data["platforms"]["ChatGPT"]["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert data["platforms"]["ChatGPT"]["data_flow"]["verified"] is True
    for name, platform in data["platforms"].items():
        if name != "ChatGPT":
            assert platform["data_flow"]["verified"] is False
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False


def test_run76_market_receipt_preimages_match_sha256_and_staleness_gate():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    market = data["current_run_observations"]["latest_market_crosscheck"]
    bodies = market["raw_response_bodies"]
    assert hashlib.sha256(bodies["kraken_xrpusd"].encode()).hexdigest() == market["spot"]["kraken_xrpusd"]["receipt_sha256"]
    assert hashlib.sha256(bodies["okx_xrpusdt"].encode()).hexdigest() == market["spot"]["okx_xrpusdt"]["receipt_sha256"]
    assert market["spot"]["kraken_xrpusd"]["provider_event_time_utc"] is None
    assert market["spot"]["okx_xrpusdt"]["age_seconds_at_recheck"] > 300
    assert market["usd_usdt_normalized"] is False
    assert market["model_admission"] is False
    assert hashlib.sha256(bodies["coinpaprika_xrp"].encode()).hexdigest() == market["spot"]["coinpaprika_xrp"]["receipt_sha256"]
    assert market["spot"]["coinpaprika_xrp"]["age_seconds_at_recheck"] > 300
    assert market["spot"]["coinpaprika_xrp"]["model_eligible"] is False


def test_run76_merge_and_forecast_safety_gates_remain_closed():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    observation = data["current_run_observations"]
    assert observation["reviews"]["pr_1640"]["approving_reviews"] == 0
    assert observation["reviews"]["pr_1640"]["threads_resolved"] == 22
    assert observation["reviews"]["pr_1643"]["approving_reviews"] == 0
    assert observation["reviews"]["pr_1643"]["threads_resolved"] == 19
    assert observation["merge_state"]["merge_performed"] is False
    assert observation["external_actions"]["manual_deployment"] is False
    assert observation["external_actions"]["real_money"] is False
    assert observation["forecast_status"] == "NOT_ISSUED"


def test_run76_exact_head_ci_is_recorded_without_overstating_newer_commit():
    observation = json.loads(CURRENT.read_text(encoding="utf-8"))["current_run_observations"]
    integration = observation["ci_evidence"]["integration"]
    assert integration["verified_code_test_head"] == "a87af9c9a37d145994f425aa3e9746dce89c5bd8"
    assert integration["full_suite"]["result"] == "success"
    assert integration["full_suite"]["passed"] == 1234
    assert integration["full_suite"]["failed"] == 0
    assert integration["full_suite"]["subtests_passed"] == 8
    assert integration["full_suite"]["coverage_pct"] == 58.98
    assert integration["core_suite"]["passed"] == 660
    assert integration["installed_wheel"]["result"] == "success"
    assert integration["dependency_audit"]["result"] == "success"
    assert integration["dependency_audit"]["manifests"] == 6
    assert integration["fail_closed_gate"]["automatic_merge_disabled"] is True
    research = observation["ci_evidence"]["research"]
    assert research["head"] == "8fc9813e15ed925c2e9bc0c689ab4091398a82fb"
    assert len(research["check_suites"]) == 5
    assert all(item["status"] in {"queued","skipped"} for item in research["check_suites"])


def test_run76_sec_13f_cross_quarter_correction_is_referenced():
    observation = json.loads(CURRENT.read_text(encoding="utf-8"))["current_run_observations"]
    artifact = "research/xrp_intelligence/20261109T013133Z-goldman-sachs-xrp-etf-13f-manager-attribution-correction.json"
    assert artifact in observation["new_research_artifacts"]
    finding = next(x for x in observation["new_research_findings"] if x["topic"].startswith("Goldman Sachs Q1-to-Q2"))
    assert finding["q1"]["xrp_named_rows"] == 0
    assert finding["q2"]["xrp_named_rows"] == 5
    assert finding["q2"]["reported_value_usd"] == 86506129
    assert finding["interpretation"].startswith("First observed reportable appearance")
    assert finding["model_eligible"] is False


def test_run76_coinbase_derivatives_snapshot_is_timestamp_gated():
    observation = json.loads(CURRENT.read_text(encoding="utf-8"))["current_run_observations"]
    finding = next(x for x in observation["new_research_findings"] if x["topic"].startswith("Coinbase Nano XRP"))
    assert finding["contract_size_xrp"] == 500
    assert finding["open_interest_usd"] == 22660000
    assert finding["funding_rate_pct"] == -0.0008
    assert finding["provider_event_timestamp"] == "not surfaced"
    assert finding["model_eligible"] is False


def test_run76_sbi_start_bond_separates_jpy_coupon_from_xrp_reward():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    bond = data["current_run_observations"]["sbi_start_bond"]
    assert bond["issue_amount_jpy"] == 10000000000
    assert bond["sold_out"] is True
    assert bond["coupon_currency"] == "JPY"
    assert bond["coupon_rate_percent"] == 2.15
    assert bond["xrp_reward_separate_from_coupon"] is True
    assert bond["initial_reward_jpy_per_100k_face"] == 200
    assert bond["initial_reward_percent_of_face"] == 0.2
    assert bond["maximum_theoretical_initial_reward_jpy_if_full_issue_qualifies"] == 20000000
    assert bond["bond_token_ledger"] == "ibet for Fin (BOOSTRY)"
    assert bond["reward_asset_ledger"] == "XRP Ledger"
    assert bond["future_coupon_date_reward_asset_guaranteed"] is False
    assert bond["direct_ripple_involvement_verified"] is False
