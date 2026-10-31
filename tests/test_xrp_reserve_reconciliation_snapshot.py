import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/xrp_intelligence/snapshots/20261031T052000Z-binance-reserve-stablecoin-freeze-reconciliation.json"
GRAPH = ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T052000Z-binance-reserve-stablecoin-issuer-graph.json"
MANIFEST = ROOT / "data/xrp_intelligence/bridge_handoff/20261031T052000Z-main-based-ledger-bridge.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_binance_reserve_decline_is_not_mislabeled_as_exact_theft_amount():
    snapshot = load(SNAPSHOT)
    rec = snapshot["reserve_reconciliation"]
    assert rec["cryptoquant_binance_xrp_reserves_oct28"] == 2_690_000_000
    assert rec["cryptoquant_binance_xrp_reserves_oct30"] == 2_470_000_000
    assert rec["decline_xrp"] == 220_000_000
    assert rec["incident_xrp_transfer_trm"] == 233_461_943.1
    assert rec["arithmetic_difference_xrp"] == 13_461_943.1
    assert rec["status"] == "STRONG_MAGNITUDE_AND_TIMING_ALIGNMENT_NOT_WALLET_LEVEL_PROOF"
    assert snapshot["prediction_engine"]["market_features_admitted"] is False
    assert snapshot["prediction_engine"]["forecast_status"] == "NOT_ISSUED"


def test_oct1_por_and_oct30_exchange_reserves_are_not_treated_as_same_snapshot():
    snapshot = load(SNAPSHOT)
    por = snapshot["official_por_comparison"]
    assert por["official_snapshot_date"] == "2026-10-01T00:00:00Z"
    assert por["xrp_customer_net_balances"] == 2_496_000_000
    assert por["xrp_reserve_coverage_percent"] == 100.77
    assert por["cryptoquant_oct30_exchange_reserves"] == 2_470_000_000
    assert por["comparable"] is False
    assert "Do not infer" in por["conclusion"]


def test_stablecoin_issuer_freezes_are_separate_from_native_xrp():
    snapshot = load(SNAPSHOT)
    graph = load(GRAPH)
    assert snapshot["issuer_control_vs_native_xrp"]["native_xrp_issuer_freezable"] is False
    amounts = {(x["issuer"], x["asset"]): x["amount"] for x in snapshot["stablecoin_freezes"]}
    assert amounts[("Circle", "USDC")] == 825_000_000
    assert amounts[("Ripple", "RLUSD")] == 40_500_000
    assert amounts[("Tether", "USDT")] == 1_770_000_000
    assert any(e["from"] == "CIRCLE" and e["to"] == "USDC" for e in graph["edges"])
    assert any(e["from"] == "RIPPLE" and e["to"] == "RLUSD" for e in graph["edges"])
    assert not any(e["from"] in {"CIRCLE", "RIPPLE", "TETHER"} and e["to"] == "XRP" and "froze" in e["relation"] for e in graph["edges"])


def test_original_diverged_ledger_branch_is_preserved_not_merged():
    manifest = load(MANIFEST)
    archive = manifest["original_archive"]
    assert archive["branch"] == "research/xrp-ledger-shard-migration-20261029T2210Z"
    assert archive["compare_status"] == "diverged"
    assert archive["ahead_by"] == 1185
    assert archive["behind_by"] == 351
    assert archive["merge_safety_decision"] == "DO_NOT_MERGE_AS_IS"
    assert archive["preserve_original_branch"] is True
    assert archive["rebase_or_force_push_prohibited"] is True
    assert manifest["migration_plan"]["full_archive_copied_to_main"] is False
    assert manifest["safety"]["main_modified_by_this_run"] is False


def test_all_snapshot_sources_have_unique_ids_and_provenance():
    snapshot = load(SNAPSHOT)
    refs = snapshot["source_refs"]
    ids = [item["source_id"] for item in refs]
    assert len(ids) >= 12
    assert len(ids) == len(set(ids))
    for item in refs:
        assert item["publisher"]
        assert item["title"]
        assert item["url"].startswith("https://")
        assert item["evidence_class"]
        assert item["independence_group"]
        assert item["retrieved_at_utc"]
