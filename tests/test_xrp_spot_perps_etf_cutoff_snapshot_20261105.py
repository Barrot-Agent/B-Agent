import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T220437Z-xrp-spot-perps-etf-cutoff-snapshot.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_response_body_hash_and_spot_arithmetic():
    data = load()
    spot = data["market_snapshot"]["kraken_spot"]
    raw = spot["raw_response_body_text"]
    assert hashlib.sha256(raw.encode("utf-8")).hexdigest() == spot["raw_response_body_text_sha256"]
    payload = json.loads(raw)["result"]["XXRPZUSD"]
    ask, bid = float(payload["a"][0]), float(payload["b"][0])
    last = float(payload["c"][0])
    midpoint = (ask + bid) / 2
    assert abs(spot["market"]["spread_bps"] - ((ask - bid) / midpoint * 10000)) < 1e-9
    assert spot["market"]["last_trade_usd"] == last
    assert spot["market"]["rolling_24h_volume_xrp"] == float(payload["v"][1])
    assert spot["market"]["rolling_24h_vwap_usd"] == float(payload["p"][1])
    assert spot["provider_event_timestamp_utc"] is None
    assert spot["model_eligible"] is False


def test_derivatives_keep_venue_universes_and_units_separate():
    data = load()
    kraken = data["market_snapshot"]["kraken_perpetuals"]
    aggregate = data["market_snapshot"]["tradradar_aggregate"]
    assert kraken["source_type"] == "exchange-published futures page"
    assert aggregate["venue_count"] == 7
    assert kraken["open_interest_usd"] != aggregate["open_interest_usd"]
    assert aggregate["long_liquidations_24h_usd"] > aggregate["short_liquidations_24h_usd"]
    assert aggregate["long_short_account_ratio"] > 1
    assert kraken["model_eligible"] is False
    assert aggregate["model_eligible"] is False


def test_etf_aggregates_are_not_misrepresented_as_comparable_cash_flows():
    data = load()
    etf = data["etf_flow_reconciliation"]
    assert etf["values_comparable_as_one_daily_total"] is False
    assert etf["cash_creation_redemption_verified"] is False
    assert etf["direct_xrp_spot_purchase_verified"] is False
    assert len(etf["observations"]) == 2
    assert all(item["raw_bytes_captured"] is False for item in etf["observations"])
    assert all(item["model_eligible"] is False for item in etf["observations"])


def test_cutoff_and_forecast_gate_remain_fail_closed():
    data = load()
    cutoff = data["data_cutoff_utc"]
    assert data["captured_at_utc"] == cutoff
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["directional_forecast_issued"] is False
    assert data["model_admission"]["target"] is None
    assert data["model_admission"]["horizon"] is None
    assert data["model_admission"]["probabilities"] is None
    assert data["preservation"]["paper_trade_executed"] is False
    assert data["preservation"]["real_money_action"] is False
