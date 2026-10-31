import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "xrp_intelligence"


def _load(relative):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_rlusd_chain_supply_and_coinbase_network_scope_are_explicit():
    snapshot = _load("snapshots/20261031T180340Z-coinbase-rlusd-xrpl-supply-revision.json")
    graph = _load("relationship_graph_addenda/20261031T180340Z-coinbase-rlusd-xrpl-supply-graph.json")
    bundle = _load("sources/20261031T180340Z-coinbase-rlusd-xrpl-supply-source-bundle.json")
    assert snapshot["rlusd_supply"]["current_xrpl_supply_usd"] == 707358109.94
    assert snapshot["rlusd_supply"]["derived_daily_change_usd"] == -274401890.06
    rolling = snapshot["rlusd_supply"]["rolling_24h_observation"]
    assert rolling["xrpl_net_supply_change_usd"] + rolling["ethereum_net_supply_change_usd"] == rolling["combined_ethereum_xrpl_net_change_usd"]
    assert snapshot["coinbase_ripple_distribution"]["supported_deposit_withdrawal_networks"] == ["XRPL", "Base", "Ethereum"]
    assert snapshot["rlusd_supply"]["chain_scope"]["base"].startswith("EXCLUDED")
    source_ids = {source["source_id"] for source in bundle["sources"]}
    assert set(snapshot["source_ids"]) <= source_ids
    assert set(graph["source_ids"]) <= source_ids
    assert snapshot["prediction"]["forecast_status"] == "NOT_ISSUED"
    assert snapshot["prediction"]["directional_features_admitted"] == []


def test_exchange_wallets_are_not_tradable_float_and_revision_is_preserved():
    snapshot = _load("snapshots/20261031T180340Z-coinbase-rlusd-xrpl-supply-revision.json")
    exchange = snapshot["xrp_exchange_balances"]
    assert exchange["total_xrp"] == 22480000000
    assert exchange["same_wallet_change_7d_xrp"] == -133000000
    assert exchange["same_wallet_change_30d_xrp"] == -12300000
    assert exchange["non_customer_reserve_operational_xrp"] == 487200000
    assert exchange["previous_capture_conflict"]["status"] == "MATERIAL_PROVIDER_DISPLAY_REVISION; PRESERVE_BOTH_CAPTURES; CAUSE_UNKNOWN"
    assert exchange["semantics"] == "ATTRIBUTED_CUSTODY_WALLETS_NOT_TRADABLE_FLOAT"


def test_graph_retains_competing_rlusd_causality_hypotheses():
    graph = _load("relationship_graph_addenda/20261031T180340Z-coinbase-rlusd-xrpl-supply-graph.json")
    ids = {item["id"] for item in graph["hypotheses"]}
    assert {"H-RLUSD-CHAIN-MIGRATION", "H-RLUSD-REDEMPTION", "H-RLUSD-PROVIDER-SCOPE", "H-XRP-PRICE-CAUSALITY"} <= ids
    price = next(item for item in graph["hypotheses"] if item["id"] == "H-XRP-PRICE-CAUSALITY")
    assert price["status"] == "UNSUPPORTED_NO_FEATURE_ADMISSION"
