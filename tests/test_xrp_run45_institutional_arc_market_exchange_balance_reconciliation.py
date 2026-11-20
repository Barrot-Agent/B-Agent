import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261119T200428Z-run45-institutional-arc-market-exchange-balance-reconciliation.json"
MAP = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run228.json"


def _utc(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def _artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run45_provenance_and_forecast_boundary():
    data = _artifact()
    assert data["run_id"] == "run45"
    assert _utc(data["captured_at_utc"]) >= _utc(data["data_cutoff_utc"])
    sources = {item["id"]: item for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"])
    for source in sources.values():
        assert source["raw_content_sha256"] is None
        assert source["raw_receipt_id"] is None
        assert source["raw_capture_status"] == "web_rendered_extract_only"
        assert source["model_eligible"] is False
    for observation in data["observations"]:
        assert observation["evidence"]
        assert set(observation["evidence"]) <= set(sources)
        assert observation["model_eligible"] is False
    assert data["model_eligibility"]["eligible_observation_count"] == 0
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["prediction_engine_status"]["forecast_issuance_enabled"] is False


def test_run45_keeps_spot_and_derivatives_scopes_separate():
    market = _artifact()["market_snapshot"]
    kraken = market["spot"]["kraken_xrpusd"]
    assert kraken["market_type"] == "spot"
    assert kraken["last_trade_usd"] == 0.96133
    assert kraken["best_bid_usd"] < kraken["best_ask_usd"]
    assert kraken["quoted_spread_bps_approx"] > 0
    assert kraken["source_event_time_utc"] is None
    assert kraken["model_eligible"] is False
    cg = market["derivatives"]["coinglass"]
    liqwall = market["derivatives"]["liqwall"]
    assert cg["open_interest_usd"] == 1_890_000_000
    assert liqwall["open_interest_usd"] == 917_000_000
    assert cg["open_interest_usd"] != liqwall["open_interest_usd"]
    assert "Do not average" in market["derivatives"]["interpretation"]


def test_run45_distinguishes_exchange_wallet_universes_and_sbi_custody():
    exchange = _artifact()["market_snapshot"]["exchange_balances"]
    broad = exchange["xrp_insights_attributed_wallets"]
    narrow = exchange["narrow_reserve_series"]
    assert broad["total_xrp"] == 22_180_000_000
    assert broad["wallets"] == 707 and broad["exchanges"] == 24
    assert broad["same_wallet_change_7d_xrp"] == -155_700_000
    assert broad["same_wallet_change_30d_xrp"] == -444_300_000
    assert broad["sbi_vc_trade"]["attributed_xrp"] == 56_300_000
    assert broad["sbi_vc_trade"]["classification"].startswith("EXCHANGE_CUSTODY")
    assert narrow["reported_balance_xrp"] == 5_110_000_000
    assert "Do not average" not in exchange["reconciliation"]  # The non-comparability is stated explicitly.
    assert "not the same variable" in exchange["reconciliation"]


def test_run45_preserves_etf_flow_disagreement_and_fund_scope():
    etf = _artifact()["market_snapshot"]["etf_flows"]
    assert etf["cryptokeyhole"]["reporting_funds"] == "2/4"
    assert etf["cryptokeyhole"]["partial_net_flow_xrp"] < 0
    assert etf["xrp_insights"]["nov18_net_flow_xrp"] < -5_000_000
    assert etf["xrp_insights"]["fund_universe"][-1] == "BITW"
    assert etf["inflowscan"]["status"] == "WITHHELD_NOT_SETTLED"
    assert "Non-comparable" in etf["reconciliation"]
    assert "No averaging" in etf["reconciliation"]


def test_run45_relationship_graph_distinguishes_xrpl_arc_and_corporate_edges():
    data = _artifact()
    edges = data["relationship_graph"]
    assert any(e["from"] == "Circle" and e["to"] == "XRPL" and e["status"] == "verified_product_deployment" for e in edges)
    assert any(e["from"] == "SBI Group" and e["to"] == "Circle Arc" and e["status"] == "announced_phased_rollout" for e in edges)
    assert any(e["from"] == "Ripple" and e["to"] == "Coinbase" and e["status"] == "verified_product_partnership" for e in edges)
    assert any(e["from"] == "BNY" and e["to"] == "Ripple" and e["status"] == "verified_custody_announcement" for e in edges)
    assert not any("SBIC" in e["from"] or "SBIC" in e["to"] for e in edges if e["from"] not in {"SBIC East/Central/West"})


def test_run45_sbic_entities_and_chatgpt_reference_are_separate_from_sbi_holdings():
    sbic = _artifact()["sbic_identity"]
    assert sbic["status"] == "RESOLVED_FROM_PRIMARY_CORPORATE_PROFILES"
    assert sbic["entities"]["east"]["designation"] == "SBIC East Japan"
    assert sbic["entities"]["east"]["corporate_number"] == "9011001030621"
    assert sbic["entities"]["central"]["designation"] == "SBIC Central Japan"
    assert sbic["entities"]["west"]["designation"] == "SBIC West Japan"
    assert "distinct regional statutory investment companies" in sbic["distinction"]
    assert "separate listed financial group holding company" in sbic["distinction"]
    assert "not evidence of an OpenAI partnership" in sbic["chatgpt"]


def test_run45_exact_phrase_and_creator_identity_controls():
    data = _artifact()
    assert data["exact_phrase_followup"]["ASK Coin"].startswith("No new primary evidence")
    assert data["exact_phrase_followup"]["actual capital"].startswith("No exact-phrase")
    assert "no OpenAI partnership" in data["exact_phrase_followup"]["SBIC, ChatGPT SBIC"]
    identity = data["youtube_identity"]
    assert identity["canonical_channel"] == "UNVERIFIED"
    assert identity["verified_creator_uploads"] == 0
    assert identity["inventory_complete"] is False


def test_run228_nine_platform_map_does_not_fabricate_connections():
    data = json.loads(MAP.read_text(encoding="utf-8"))
    expected = {"ChatGPT", "Claude", "Grok", "Gemini", "Copilot", "Codex", "Hugging Face", "Kaggle", "Databricks"}
    assert set(data["platforms"]) == expected
    assert data["platforms"]["ChatGPT"]["authentication_status"] == "verified"
    assert data["platforms"]["ChatGPT"]["data_flow"]["status"] == "verified"
    for name in expected - {"ChatGPT"}:
        assert data["platforms"][name]["authentication_status"] == "unverified"
        assert data["platforms"][name]["permissions"] == []
        assert data["platforms"][name]["task_assignment"]["status"] == "PROPOSED_NOT_DISPATCHED"
    assert data["coordination"]["external_dispatch_performed"] is False
    assert data["coordination"]["external_data_transfer_performed"] is False
    assert data["coordination"]["red_team_status"] == "NOT_EXECUTED"


def test_run228_repository_and_ci_evidence_are_exact_head():
    data = json.loads(MAP.read_text(encoding="utf-8"))
    repo = data["repository_state"]
    assert repo["main_sha"] == "e1c3634df28f488819185b7d5697d474bc0bcb9e"
    integration = repo["integration"]
    assert integration["pr_number"] == 1663
    assert integration["code_head_sha"] == "e91cfc704031933004115d9f5cf9ed9006018c13"
    assert integration["ahead_by"] == 466 and integration["behind_by"] == 0
    assert repo["main_paths_missing_from_integration"] == 0
    ci = data["ci_evidence"]["full_suite"]
    assert ci["run_id"] == 44595135674 and ci["conclusion"] == "success"
    assert ci["passed"] == 4357 and ci["failed"] == 0 and ci["skipped"] == 1
    assert data["merge_decision"] == "NO_MERGE"
