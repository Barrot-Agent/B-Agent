import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "xrp_intelligence"


def load(path):
    return json.loads((DATA / path).read_text(encoding="utf-8"))


def test_ask_identity_remains_a_candidate():
    snap = load("snapshots/20261101T135000Z-ask-coin-permission-candidate.json")
    assert snap["candidate"] == "Permission Coin (ASK)"
    assert snap["identity_status"] == "PLAUSIBLE_NOT_CONFIRMED"
    assert snap["xrp_relationship"] == "NO_DIRECT_INTEGRATION_IDENTIFIED"


def test_ask_official_contracts_are_base_and_polygon_not_xrpl():
    snap = load("snapshots/20261101T135000Z-ask-coin-permission-candidate.json")
    assert {x["network"] for x in snap["contracts"]} == {"Base", "Polygon"}
    assert snap["token_standard"] == "LayerZero OFT-20"


def test_coinbase_ask_link_is_wallet_infrastructure_not_capital():
    snap = load("snapshots/20261101T135000Z-ask-coin-permission-candidate.json")
    assert "embedded_wallet_infrastructure" in snap["coinbase_relationship"]
    assert snap["capital_classification"] == "wallet infrastructure, not investment or token purchase"


def test_ask_market_quotes_are_quarantined_when_sources_conflict():
    snap = load("snapshots/20261101T135000Z-ask-coin-permission-candidate.json")
    assert snap["market_data_status"] == "QUARANTINED"
    assert "zero 24h volume" in snap["market_data_discrepancy"]


def test_no_directional_ask_or_xrp_forecast_is_issued():
    snap = load("snapshots/20261101T135000Z-ask-coin-permission-candidate.json")
    assert snap["forecast_status"] == "NOT_ISSUED"
    assert snap["forecasts"] == []
