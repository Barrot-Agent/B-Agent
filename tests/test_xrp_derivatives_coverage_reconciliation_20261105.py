import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261105T1702Z-xrp-derivatives-coverage-reconciliation.json"
)


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_spot_spread_and_return_arithmetic_are_reconciled():
    spot = load()["market_snapshot"]["spot"]["kraken_xrpusd"]
    midpoint = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    spread_bps = (spot["best_ask_usd"] - spot["best_bid_usd"]) / midpoint * 10_000
    vwap_return = (spot["last_usd"] / spot["vwap_24h_usd"] - 1) * 100
    day_open_return = (spot["last_usd"] / spot["utc_day_open_usd"] - 1) * 100

    assert spot["midpoint_usd"] == midpoint
    assert abs(spot["spread_bps"] - spread_bps) < 1e-12
    assert abs(spot["last_vs_vwap_pct"] - vwap_return) < 1e-12
    assert abs(spot["last_vs_utc_day_open_pct"] - day_open_return) < 1e-12
    assert spot["provider_event_time_utc"] is None
    assert spot["retrieval_time_utc"] is None
    assert spot["model_eligible"] is False


def test_open_interest_aggregates_are_kept_in_separate_coverage_universes():
    data = load()["market_snapshot"]["derivatives"]
    coverage = data["coverage_reconciliation"]["observed_aggregate_open_interest_usd"]

    assert data["kodexius"]["contract_count"] == 7
    assert data["kodexius"]["venue_count"] == 5
    assert data["loris"]["venue_count"] == 40
    assert data["bitcoinleverage_coinalyze"]["venue_count"] == 2
    assert coverage["bitcoinleverage_two_venues"] == 737_350_000
    assert coverage["kodexius_seven_contracts_five_venues"] == 862_500_000
    assert coverage["optimistfi_thirty_six_venues_at_0656z"] == 1_700_000_000
    assert coverage["loris_forty_venues_at_1651z"] == 2_220_000_000
    assert data["coverage_reconciliation"]["aggregation"] == "not_averaged"


def test_binance_overlap_is_close_but_bybit_open_interest_remains_unresolved():
    reconciliation = load()["market_snapshot"]["derivatives"]["coverage_reconciliation"]
    binance = reconciliation["overlapping_binance_contract_comparison"]
    bybit = reconciliation["unresolved_bybit_comparison"]

    assert binance["kodexius_xrpusdt_usd"] == 440_550_000
    assert binance["bitcoinleverage_binance_usd"] == 439_870_000
    assert binance["kodexius_vs_bitcoinleverage_difference_pct"] < 0.2
    assert bybit["kodexius_exchange_total_usd"] == 152_400_000
    assert bybit["bitcoinleverage_exchange_total_usd"] == 297_480_000
    assert bybit["loris_exchange_total_usd"] == 340_000_000
    assert bybit["bitcoinleverage_to_kodexius_ratio"] > 1.9
    assert bybit["loris_to_kodexius_ratio"] > 2.2


def test_loris_bybit_price_outlier_is_quarantined_not_used_as_reference():
    loris = load()["market_snapshot"]["derivatives"]["loris"]
    prices = loris["page_internal_price_observations_usd"]
    expected = (prices["Bybit"] / prices["Binance"] - 1) * 100

    assert abs(loris["bybit_vs_binance_price_premium_pct"] - expected) < 1e-12
    assert expected > 4.9
    assert loris["bybit_price_outlier_status"] == "QUARANTINED_PENDING_SYNCHRONIZED_CONTRACT_VALIDATION"
    assert loris["page_internal_change_disagreement_status"] == "UNRESOLVED"


def test_funding_account_positioning_taker_flow_and_liquidations_keep_distinct_units():
    data = load()["market_snapshot"]["derivatives"]["bitcoinleverage_coinalyze"]
    assert data["funding_pct_per_8h"]["Binance"] > 0
    assert data["long_account_pct"]["Bybit"] > 78
    assert data["long_short_account_ratio"]["Bybit"] > 3.7
    assert 49 < data["taker_buy_share_pct"]["Binance"] < 52
    assert 48 < data["taker_buy_share_pct"]["Bybit"] < 51
    assert data["liquidations_24h_usd"]["Binance"]["longs"] > data["liquidations_24h_usd"]["Binance"]["shorts"]
    assert data["liquidations_24h_usd"]["Binance"]["coverage_hours"] == "23/24"
    assert data["liquidations_24h_usd"]["Bybit"]["coverage_hours"] == "20/24"
    assert "account" in load()["interpretation"]["observations"][3].lower()


def test_older_optimist_snapshot_is_not_misrepresented_as_current():
    optimist = load()["market_snapshot"]["derivatives"]["optimistfi"]
    assert optimist["updated_at_utc"] == "2026-11-05T06:56:00Z"
    assert optimist["stale_at_later_1651z_cutoff"] is True
    assert optimist["model_eligible"] is False


def test_all_rendered_sources_remain_model_ineligible_and_no_forecast_is_issued():
    data = load()
    assert all(source["model_eligible"] is False for source in data["source_registry"])
    assert all(source["raw_source_sha256"] is None for source in data["source_registry"])
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["admission"]["directional_forecast_issued"] is False
    assert data["admission"]["paper_trade_executed"] is False
