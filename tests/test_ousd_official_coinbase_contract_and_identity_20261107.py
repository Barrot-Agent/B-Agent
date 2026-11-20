import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107-ousd-official-coinbase-contract-and-same-ticker-identity-reconciliation.json"
)


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_official_ousd_contracts_and_networks_are_explicit_and_exclude_xrpl():
    data = load()
    official = data["official_ousd"]
    assert official["issuer"] == "Bridge Building Inc."
    assert official["operator"] == "Open Standard"
    assert official["supported_networks"] == ["Base", "Ethereum", "Solana", "Tempo"]
    assert official["xrpl_supported"] is False
    assert official["contracts"]["Solana"] == "ousd2mJsPEckLHcSCDxyKD7NDGARZcfLbDZkKiatYHB"


def test_coinbase_official_asset_page_confirms_centralized_exchange_availability():
    data = load()
    listing = data["coinbase_listing"]["claims"]
    assert listing["centralized_exchange_availability"].startswith("Coinbase page explicitly states")
    assert listing["symbol"] == "OUSD"
    assert listing["displayed_price_usd"] == 1.0
    assert data["official_ousd"]["contracts"]["Base"] == "0xB2000000000000000000002fEb517dFeC7415344"


def test_same_ticker_coinbase_dex_guide_is_not_the_official_openusd_contract():
    data = load()
    collision = data["same_ticker_token_collision"]
    official = data["official_ousd"]["contracts"]["Solana"]
    assert collision["identity_decision"] == "DISTINCT_TOKEN_SAME_TICKER_OR_NEAR_IDENTICAL_NAME"
    assert collision["solana_mint_in_url"] != official
    assert collision["displayed_price_usd"] < 0.00001
    assert collision["page_scope"] == "DEX-only token guide"


def test_solana_chain_supply_is_not_mixed_with_aggregate_supply():
    data = load()
    solana = data["solana_chain_observation"]
    coinbase = data["coinbase_listing"]["claims"]
    assert solana["official_mint"] == data["official_ousd"]["contracts"]["Solana"]
    assert solana["displayed_current_supply"] == 83453579.90664
    assert coinbase["displayed_total_supply_ousd"] == 909000000
    assert "not directly comparable" in solana["qualification"]


def test_tempo_zero_transfer_page_observation_is_scoped_not_generalized():
    data = load()
    tempo = data["tempo_chain_observation"]
    assert "No transactions found" in tempo["displayed_observation"]
    assert "does not prove" in tempo["qualification"]
    assert tempo["official_contract"] == data["official_ousd"]["contracts"]["Tempo"]


def test_excerpt_receipts_match_exact_utf8_text():
    data = load()
    for receipt in data["exact_excerpt_receipts"]:
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"]


def test_no_xrp_demand_or_directional_forecast_is_inferred():
    data = load()
    admission = data["model_admission"]
    assert admission["event_timeline_only"] is True
    assert admission["xrp_price_feature"] is False
    assert admission["xrp_exchange_flow_feature"] is False
    assert admission["xrp_demand_measure"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast"] is False
    assert data["forecast"]["paper_trade"] is False
    assert data["forecast"]["real_money_action"] is False
