from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKET = ROOT / "research" / "xrp_intelligence" / "20261106T120807Z-xrp-spot-derivatives-etf-vintage-reconciliation.json"
CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261106T120807Z-institutional-network-morpho-key-correction.json"
INSTITUTIONAL = ROOT / "research" / "xrp_intelligence" / "20261106-institutional-xrp-network-cbxrp-sbi-circle-ripple.json"
MACRO = ROOT / "research" / "xrp_intelligence" / "20261106-clarity-act-and-risk-off-xrp-context.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_kraken_rendered_ticker_hash_and_arithmetic_are_reproducible():
    data = read_json(MARKET)
    quote = data["spot"]["kraken_xrp_usd"]
    parsed = json.loads(quote["rendered_response_text"])["result"]["XXRPZUSD"]
    assert hashlib.sha256(quote["rendered_response_text"].encode()).hexdigest() == quote["rendered_response_sha256"]
    bid = float(parsed["b"][0])
    ask = float(parsed["a"][0])
    last = float(parsed["c"][0])
    vwap = float(parsed["p"][1])
    day_open = float(parsed["o"])
    low = float(parsed["l"][1])
    assert math.isclose(quote["parsed_quote"]["spread_bps"], (ask - bid) / ((ask + bid) / 2) * 10000, rel_tol=1e-9)
    assert math.isclose(quote["parsed_quote"]["last_vs_rolling_24h_vwap_pct"], (last / vwap - 1) * 100, rel_tol=1e-9)
    assert math.isclose(quote["parsed_quote"]["last_vs_utc_day_open_pct"], (last / day_open - 1) * 100, rel_tol=1e-9)
    assert math.isclose(quote["parsed_quote"]["last_above_rolling_24h_low_pct"], (last / low - 1) * 100, rel_tol=1e-9)
    assert quote["provider_event_timestamp_utc"] is None
    assert quote["raw_http_wire_bytes_captured"] is False
    assert quote["model_eligible"] is False


def test_tradradar_seven_venue_oi_reconciles_and_keeps_measurement_limits():
    data = read_json(MARKET)["derivatives"]["tradradar_xrp_perpetuals"]
    assert sum(data["exchange_open_interest_usd"].values()) == data["exchange_sum_open_interest_usd"]
    assert abs(data["exchange_sum_open_interest_usd"] - data["open_interest_usd"]) <= 1_000_000
    assert data["displayed_delay_minutes"] == 15
    assert data["exact_underlying_observation_timestamp_utc"] is None
    assert data["long_liquidations_lower_bound_usd"] > data["short_liquidations_lower_bound_usd"]
    assert "not notional" in data["methodology_limits"][2]


def test_etf_universes_and_settlement_vintages_are_not_averaged():
    data = read_json(MARKET)["etf_flows"]
    xi = data["xrp_insights"]
    ck = data["cryptokeyhole"]
    assert xi["data_as_of"] == "2026-11-05"
    assert xi["net_holdings_change_xrp"] == -149_487
    assert xi["total_xrp_holdings"] == 1_196_450_700
    assert "Six US spot" in xi["universe"]
    assert ck["november_5_status"] == "partial_3_of_4"
    assert ck["november_5_partial_flow_xrp"] == -3_339
    assert "Four US spot" in ck["universe"]
    assert xi["independence_group"] != ck["independence_group"]
    assert "not a direct AP cash" in xi["flow_method"]
    assert "not a completed four-fund day" in ck["limitations"][0]


def test_aggregator_internal_inconsistencies_are_quarantined():
    data = read_json(MARKET)["etf_flows"]
    assert data["non_comparable_universe"]["displayed_total_xrp"] == 1_414_952_215
    assert "NCIQ" in data["non_comparable_universe"]["methodology_conflict"]
    assert data["other_quality_flags"][0]["treatment"].startswith("Excluded")
    assert data["other_quality_flags"][1]["treatment"].startswith("Excluded")
    assert data["non_comparable_universe"]["treatment"].startswith("Excluded")


def test_macro_close_sources_have_post_close_vintages_and_distinct_lineage():
    data = read_json(MACRO)
    sources = {x["id"]: x for x in data["source_registry"]}
    ap = sources["ap_postclose_market_close"]
    herald = sources["herald_postclose_market_close"]
    reuters = sources["reuters_nasdaq_close"]
    assert ap["published_at"] == "2026-11-05T21:22:00Z"
    assert herald["published_at"] == "2026-11-05T21:45:58Z"
    assert ap["independence_group"] != herald["independence_group"]
    assert "pre-open context" in " ".join(reuters["supports"])
    assert reuters["published_at"] == "2026-11-05T10:54:00Z"


def test_morpho_key_correction_is_preimage_bound_and_not_claimed_applied():
    target = INSTITUTIONAL.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(target)).encode() + bytes([0]) + target).hexdigest()
    correction = read_json(CORRECTION)
    original = json.loads(target.decode("utf-8"))
    item = correction["corrections"][0]
    assert git_blob == correction["target_artifact"]["git_blob_sha"]
    assert correction["target_artifact"]["git_blob_sha"] == "303453dd9f5d11bce742dbe61e0f7cb4b18dcdd3"
    assert "morpo_market_snapshot_exact_time" in original["quality_and_limits"]
    assert "morpho_market_snapshot_exact_time" not in original["quality_and_limits"]
    assert item["from_key"] == "morpo_market_snapshot_exact_time"
    assert item["to_key"] == "morpho_market_snapshot_exact_time"
    assert correction["original_artifact_modified"] is False
    assert correction["application_status"] == "RECORD_ONLY_NOT_APPLIED"
    assert correction["automatic_consumer_status"] == "NOT_IMPLEMENTED"


def test_market_snapshot_remains_model_ineligible_and_forecast_is_not_issued():
    data = read_json(MARKET)
    assert data["quality_and_limits"]["point_in_time_feature_eligible"] is False
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["action_status"]["paper_trade_executed"] is False
    assert data["action_status"]["real_money_action"] is False
