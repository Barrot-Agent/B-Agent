from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json"
HISTORICAL = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json"


def load_current():
    return json.loads(CURRENT.read_text(encoding="utf-8"))


def test_run77_current_snapshot_preserves_run76_and_historical_map():
    current = load_current()
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    observation = current["current_run_observations"]
    prior76 = next(item for item in current["prior_run_observations"] if item.get("run_id") == 76)
    prior75 = next(item for item in current["prior_run_observations"] if item.get("run_id") == 75)
    prior73 = next(item for item in current["prior_run_observations"] if item.get("run_id") == 73)

    assert current["captured_at_utc"] == current["last_verified_at_utc"]
    assert observation["captured_at_utc"] == current["captured_at_utc"]
    assert observation["last_verified_at_utc"] == current["last_verified_at_utc"]
    assert observation["run_id"] == 77
    assert observation["captured_at_utc"] == "2026-11-09T02:01:02Z"
    assert observation["main_sha"] == "d4d43be3427375cf79d190e768976de062e20287"
    assert observation["integration_head_before_handoff_commit"] == "e31a951939bcdd638f190d9d2ff8c5faae9b2091"
    assert observation["research_head"] == "238f3ff4a69420882c77d225626a352ba19a412c"
    assert prior76["captured_at_utc"] == "2026-11-09T01:50:00Z"
    assert prior76["ci_evidence"]["integration"]["full_suite"]["passed"] == 1234
    assert prior75["captured_at_utc"] == "2026-11-09T01:36:00Z"
    assert prior73["captured_at_utc"] == "2026-11-09T00:23:14Z"
    assert historical["captured_at_utc"] == "2026-11-08T22:30:23Z"
    assert historical["current_run_observations"]["run_id"] == 70


def test_run77_prediction_engine_contract_remains_fail_closed():
    observation = load_current()["current_run_observations"]
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


def test_run77_platform_map_keeps_external_data_flows_unverified():
    data = load_current()
    assert data["platforms"]["ChatGPT"]["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert data["platforms"]["ChatGPT"]["data_flow"]["verified"] is True
    for name, platform in data["platforms"].items():
        if name != "ChatGPT":
            assert platform["data_flow"]["verified"] is False
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False


def test_run77_market_receipt_preimages_match_sha256_and_staleness_gate():
    market = load_current()["current_run_observations"]["latest_market_crosscheck"]
    bodies = market["raw_response_bodies"]
    assert hashlib.sha256(bodies["kraken_xrpusd"].encode()).hexdigest() == market["spot"]["kraken_xrpusd"]["receipt_sha256"]
    assert hashlib.sha256(bodies["okx_xrpusdt"].encode()).hexdigest() == market["spot"]["okx_xrpusdt"]["receipt_sha256"]
    assert hashlib.sha256(bodies["coinpaprika_xrp"].encode()).hexdigest() == market["spot"]["coinpaprika_xrp"]["receipt_sha256"]
    assert market["spot"]["kraken_xrpusd"]["provider_event_time_utc"] is None
    assert market["spot"]["okx_xrpusdt"]["provider_event_time_utc"] == "2026-11-09T01:36:03.075Z"
    assert market["spot"]["okx_xrpusdt"]["age_seconds_at_recheck"] > 300
    assert market["spot"]["coinpaprika_xrp"]["age_seconds_at_recheck"] > 300
    assert abs(market["raw_last_gap_pct"] - 0.3245) < 0.0001
    assert market["usd_usdt_normalized"] is False
    assert market["level2_depth"] is False
    assert market["synchronized_trades"] is False
    assert market["model_admission"] is False


def test_run77_xrpl_amendment_snapshot_does_not_claim_lending_activation():
    data = load_current()["current_run_observations"]["latest_xrpl_governance_snapshot"]
    assert data["validators_heard"] == 35
    assert data["yes_votes_required"] == 29
    assert data["amendments"]["LendingProtocol"]["yes_with_24h_carry"] == 21
    assert data["amendments"]["SingleAssetVault"]["yes_with_24h_carry"] == 23
    assert data["amendments_in_14_day_countdown"] == 0
    assert data["native_lending_activated"] is False
    assert data["fixCleanup3_4_0"]["enabled_ledger"] == 108112129
    assert data["fixCleanup3_4_0"]["enable_amendment_tx"] == "F2E0342BC2419508DBAB9E869B7057941A07782426167396F87C7D0CA008FA6C"
    assert "own-node" in data["source"]["source_independence"]


def test_run77_etf_holdings_delta_remains_a_flagged_proxy():
    data = load_current()["current_run_observations"]["etf_flow_methodology"]
    assert data["data_as_of"] == "2026-11-06"
    assert data["trading_days"] == 231
    assert data["rows"] == 1597
    assert data["net_holdings_delta_xrp"] == -812529
    assert data["reported_total_holdings_xrp"] == 1195787657
    assert data["model_eligible"] is False
    assert any("GXRP" in item for item in data["exclusions_and_caveats"])
    assert any("BITW" in item for item in data["exclusions_and_caveats"])


def test_run77_merge_and_forecast_safety_gates_remain_closed():
    observation = load_current()["current_run_observations"]
    assert observation["reviews"]["pr_1640"]["approving_reviews"] == 0
    assert observation["reviews"]["pr_1640"]["threads_resolved"] == 22
    assert observation["reviews"]["pr_1643"]["approving_reviews"] == 0
    assert observation["reviews"]["pr_1643"]["threads_resolved"] == 19
    assert observation["merge_state"]["merge_performed"] is False
    assert observation["merge_state"]["branch_protection_status"] == "UNVERIFIED_HTTP_403"
    assert observation["merge_state"]["pages_deployment_authorized"] is False
    assert observation["external_actions"]["manual_deployment"] is False
    assert observation["external_actions"]["real_money"] is False
    assert observation["forecast_status"] == "NOT_ISSUED"


def test_run77_exact_head_ci_is_recorded_without_overstating_research_branch():
    observation = load_current()["current_run_observations"]
    integration = observation["ci_evidence"]["integration"]
    assert integration["verified_code_test_head"] == "e31a951939bcdd638f190d9d2ff8c5faae9b2091"
    assert integration["full_suite"]["run_id"] == 42547603193
    assert integration["full_suite"]["result"] == "success"
    assert integration["full_suite"]["passed"] == 1235
    assert integration["full_suite"]["failed"] == 0
    assert integration["full_suite"]["subtests_passed"] == 8
    assert integration["full_suite"]["coverage_pct"] == 58.98
    assert integration["core_suite"]["passed"] == 660
    assert integration["installed_wheel"]["result"] == "success"
    assert integration["dependency_audit"]["run_id"] == 42547603245
    assert integration["dependency_audit"]["manifests"] == 6
    assert integration["dependency_audit"]["known_vulnerabilities"] == 0
    assert integration["fail_closed_gate"]["run_id"] == 42547603095
    assert integration["fail_closed_gate"]["automatic_merge_disabled"] is True
    research = observation["ci_evidence"]["research"]
    assert research["head"] == "238f3ff4a69420882c77d225626a352ba19a412c"
    assert research["full_suite"] == "NOT_RUN"
    assert research["dependency_audit"] == "NOT_RUN"
    assert research["fail_closed_gate"] == "NOT_RUN"
    assert research["github_actions_workflow_runs"] == []
    assert research["combined_status_checks"] == []


def test_run76_sec_13f_cross_quarter_correction_is_preserved():
    prior76 = next(item for item in load_current()["prior_run_observations"] if item.get("run_id") == 76)
    artifact = "research/xrp_intelligence/20261109T013133Z-goldman-sachs-xrp-etf-13f-manager-attribution-correction.json"
    assert artifact in prior76["new_research_artifacts"]
    finding = next(x for x in prior76["new_research_findings"] if x["topic"].startswith("Goldman Sachs Q1-to-Q2"))
    assert finding["q1"]["xrp_named_rows"] == 0
    assert finding["q2"]["xrp_named_rows"] == 5
    assert finding["q2"]["reported_value_usd"] == 86506129
    assert finding["interpretation"].startswith("First observed reportable appearance")
    assert finding["model_eligible"] is False


def test_run76_coinbase_derivatives_snapshot_is_preserved_as_timestamp_gated():
    prior76 = next(item for item in load_current()["prior_run_observations"] if item.get("run_id") == 76)
    finding = next(x for x in prior76["new_research_findings"] if x["topic"].startswith("Coinbase Nano XRP"))
    assert finding["contract_size_xrp"] == 500
    assert finding["open_interest_usd"] == 22660000
    assert finding["funding_rate_pct"] == -0.0008
    assert finding["provider_event_timestamp"] == "not surfaced"
    assert finding["model_eligible"] is False


def test_run76_sbi_start_bond_separates_jpy_coupon_from_xrp_reward():
    prior76 = next(item for item in load_current()["prior_run_observations"] if item.get("run_id") == 76)
    bond = prior76["sbi_start_bond"]
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


def test_run77_workflow_safety_audit_distinguishes_main_from_integration():
    audit = load_current()["current_run_observations"]["workflow_safety_audit"]
    assert audit["integration_changed_workflow_files"] == 41
    assert any("cross-analysis.yml" in item and "read-only" in item for item in audit["main_read_only_or_disabled_workflows"])
    assert any("barrot-agent.yml" in item and "contents:write" in item for item in audit["main_currently_active_risks"])
    assert any("barrot-agent.yml" in item and "quarantined" in item for item in audit["integration_branch_mitigations"])
    assert audit["workflows_dispatched"] is False
    assert audit["secrets_read_or_rotated"] is False
    assert audit["external_deployments_performed"] is False
