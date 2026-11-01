import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/xrp_intelligence/sources/20261101T131100Z-cbxrp-morpho-usdc-market.json"
SNAPSHOT = ROOT / "data/xrp_intelligence/snapshots/20261101T131100Z-cbxrp-morpho-usdc-market.json"
GRAPH = ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261101T131100Z-cbxrp-morpho-credit.json"
HANDOFF = ROOT / "data/xrp_intelligence/hand_offs/20261101T131100Z-cbxrp-morpho-credit-reconciliation.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def test_snapshot_sources_resolve_and_market_identity_is_consistent():
    sources = load(SOURCE)
    snapshot = load(SNAPSHOT)
    known = {item["id"] for item in sources["sources"]}
    assert len(known) == len(sources["sources"])
    assert set(snapshot["source_ids"]).issubset(known)
    assert snapshot["market"]["market_id"] == "0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109"
    assert snapshot["market"]["chain_id"] == 8453
    assert snapshot["market"]["lltv_pct"] == 62.5
    assert snapshot["market"]["collateral_token_address"] == "0xcb585250f852c6c6bf90434ab21a00f02833a4af"
    assert "SRC-20261101T131100Z-COINBASE-LOAN-BACKUP-CBXRP-CONTRACT" in known
    assert "SRC-20261101T131100Z-COINBASE-WRAPPED-ASSET-CUSTODY-POLICY" in known

def test_supply_borrow_collateral_and_utilization_are_not_conflated():
    snapshot = load(SNAPSHOT)
    market = snapshot["market"]
    assert market["supplied_usdc"] == 65_460_000
    assert market["outstanding_borrowed_usdc"] == 59_200_000
    assert market["collateral_units"] == 118_550_000
    assert abs(market["utilization_pct"] - market["outstanding_borrowed_usdc"] / market["supplied_usdc"] * 100) < 0.1
    assert abs(snapshot["derived_metrics"]["aggregate_debt_to_collateral_pct"] - 40.0) < 0.2
    assert snapshot["derived_metrics"]["debt_collateral_ratio_is_aggregate_not_borrower_weighted_ltv"] is True

def test_cross_source_ratio_and_value_conflicts_fail_closed():
    snapshot = load(SNAPSHOT)
    assert snapshot["derived_metrics"]["collateral_share_is_approximate_due_to_unsynchronized_refresh_times"] is True
    assert snapshot["issuer_reserves"]["displayed_refresh_timezone"] == "NOT_STATED"
    assert snapshot["unresolved_conflicts"][0]["status"] == "EXCLUDED_UNRECONCILED"
    assert snapshot["unresolved_conflicts"][1]["status"] == "NOT_COMPARABLE"
    assert snapshot["feature_admission"]["status"] == "EXPLORATORY_ONLY_NOT_ADMITTED_TO_DIRECTIONAL_MODEL"
    assert snapshot["forecast"]["status"] == "NOT_ISSUED"

def test_coinbase_market_attribution_remains_an_inference():
    graph = load(GRAPH)
    edge = next(item for item in graph["edges"] if item["id"] == "EDGE-COINBASE-MORPHO-PRODUCT-20261101")
    assert edge["evidence_class"] == "INFERENCE"
    hypothesis = next(item for item in graph["hypotheses"] if item["id"] == "HYP-CBXRP-COINBASE-MARKET-20261101")
    assert hypothesis["status"] == "STRONG_INFERENCE_NOT_DIRECTLY_CONFIRMED"
    assert "Morpho is permissionless" in " ".join(hypothesis["disconfirming_evidence"])

def test_handoff_keeps_external_platforms_and_trading_status_accurate():
    handoff = load(HANDOFF)
    assert handoff["platform_coordination"]["status"] == "DESIGNED_NOT_LIVE"
    assert handoff["platform_coordination"]["verified_external_authentications"] == 0
    assert handoff["forecast"]["status"] == "NOT_ISSUED"
    assert handoff["safety"]["real_money_trade"] is False
    assert handoff["safety"]["paper_trading_mutation"] is False
