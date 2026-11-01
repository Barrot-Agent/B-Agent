import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_xrp_market_structure_snapshot_preserves_provider_limits():
    snapshot = load("data/xrp_intelligence/snapshots/20261101T142000Z-xrp-market-exchange-etf-derivatives-snapshot.json")
    graph = load("data/xrp_intelligence/relationship_graph_addenda/20261101T142000Z-xrp-market-custody-etf-derivatives-graph.json")
    decision = load("data/xrp_intelligence/architecture_decisions/20261101T142000Z-xrp-exchange-etf-derivatives-feature-gating.json")
    handoff = load("data/xrp_intelligence/hand_offs/20261101T142000Z-xrp-market-liquidity-custody-etf-derivatives-handoff.json")
    ledger = load("data/xrp_intelligence/research_ledger_addenda/20261101T142000Z-xrp-market-structure-ledger-addendum.json")

    exchange = snapshot["latest_available_observations"]["exchange_wallets"]
    assert exchange["total_xrp"] == 22450000000
    assert exchange["same_wallet_change_7d_xrp"] == -161100000
    assert exchange["same_wallet_change_30d_xrp"] == -12700000
    assert exchange["known_wrapped_or_fund_reserves_xrp"]["total"] == 487900000
    assert "not tradable float" in exchange["interpretation"]

    etf = snapshot["latest_available_observations"]["etfs"]
    assert etf["net_flow_week_2026_10_26_to_30_xrp"] == 3390000
    assert etf["gxrp_flow_status"].startswith("excluded")

    derivatives = snapshot["latest_available_observations"]["derivatives"]
    assert derivatives["kodexius"]["open_interest_usd"] != derivatives["liqwall"]["open_interest_usd"]
    assert "do not average" in derivatives["reconciliation"]

    assert decision["feature_admission"] == "none"
    assert handoff["forecast_status"] == "NOT_ISSUED"
    assert ledger["forecast_status"] == "NOT_ISSUED"
    assert any(edge["relation"] == "transaction_fee_burn" for edge in graph["edges"])
