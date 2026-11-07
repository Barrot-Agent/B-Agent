import hashlib
import json
from pathlib import Path

ARTIFACT = Path(
    "research/xrp_intelligence/20261107T110558Z-xrp-market-structure-exchange-wallet-etf-derivatives-macro-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_complete_api_response_hashes_are_exact():
    artifact = load_artifact()
    sources = {source["source_id"]: source for source in artifact["source_registry"]}
    for source_id in ("kraken_xrp_usd_ticker", "okx_xrp_usdt_ticker"):
        source = sources[source_id]
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_text_sha256"]


def test_rendered_excerpt_hashes_are_exact():
    artifact = load_artifact()
    for source in artifact["source_registry"]:
        for excerpt in source.get("excerpts", []):
            assert hashlib.sha256(excerpt["text"].encode("utf-8")).hexdigest() == excerpt["sha256"]


def test_spot_quotes_are_not_promoted_to_synchronized_arbitrage():
    artifact = load_artifact()
    spot = artifact["market_reconciliation"]["spot"]
    assert spot["kraken_xrp_usd"]["provider_event_timestamp_utc"] is None
    assert spot["okx_xrp_usdt"]["age_seconds_at_capture"] > 300
    assert spot["cross_venue_arbitrage_signal"] is False
    assert spot["depth_capture_status"] == "NOT_CAPTURED"


def test_kraken_today_open_is_not_mislabeled_as_rolling_24h_open():
    artifact = load_artifact()
    semantics = artifact["market_reconciliation"]["spot"]["kraken_field_semantics"]
    assert semantics["rest_o_field"] == "utc_day_open"
    assert "v[1]" in semantics["rolling_24h_fields"]
    assert "o" not in semantics["rolling_24h_fields"]


def test_exchange_wallet_balances_are_not_tradable_float():
    artifact = load_artifact()
    wallets = artifact["market_reconciliation"]["exchange_wallets"]
    assert wallets["tradable_float_estimate"] is False
    assert wallets["same_wallet_change_7d_xrp"] == -150700000
    assert wallets["naive_total_change_xrp"] == 350800000
    assert wallets["newly_tracked_wallet_balance_xrp"] == 512000000
    assert wallets["wrapped_insurance_charity_reserves_xrp"] == 487800000


def test_sbi_vc_trade_wallets_are_not_sbi_holdings_corporate_treasury():
    artifact = load_artifact()
    wallets = artifact["market_reconciliation"]["exchange_wallets"]
    sbi = next(row for row in wallets["selected_exchange_balances"] if row["exchange"] == "SBI VC Trade")
    assert sbi["xrp"] == 56600000
    assert "not an SBI Holdings corporate treasury balance" in sbi["notes"]


def test_derivatives_aggregator_disagreement_is_preserved_not_averaged():
    artifact = load_artifact()
    derivatives = artifact["market_reconciliation"]["derivatives"]
    assert derivatives["tradradar"]["open_interest_usd"] == 1900000000
    assert derivatives["alpha_finance"]["open_interest_usd"] == 2760000000
    assert derivatives["do_not_average"] is True
    assert derivatives["open_interest_difference_usd"] == 860000000


def test_etf_partial_day_and_future_file_date_are_quarantined():
    artifact = load_artifact()
    etf = artifact["market_reconciliation"]["etf_flows"]
    assert etf["alpha_finance"]["nov6_net_flow_usd"] == 0
    assert etf["cryptokeyhole"]["nov6_partial_flow_xrp"] == -752048
    assert etf["cryptokeyhole"]["nov6_coverage"] == "3/4"
    assert etf["cryptokeyhole"]["future_dated_latest_issuer_file"] == "2026-11-09"
    assert etf["reconciliation"]["provider_disagreement"] is True
    assert etf["reconciliation"]["resolution"] == "Unresolved. The CryptoKeyhole future-dated 9 Nov file metadata is quarantined; its 6 Nov row remains partial. No averaging or directional flow inference."


def test_macro_observation_is_context_only():
    artifact = load_artifact()
    macro = artifact["market_reconciliation"]["macro"]
    assert macro["reuters_us_money_market_weekly_net_inflow_usd"] == 117970000000
    assert "not an XRP-specific catalyst" in macro["context"]


def test_no_directional_or_shadow_forecast_is_issued():
    artifact = load_artifact()
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert artifact["forecast"]["shadow_forecast"] is None
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False


def test_only_event_timeline_admission_is_allowed():
    artifact = load_artifact()
    admission = artifact["model_admission"]
    assert admission["eligible_spot_features"] == []
    assert admission["eligible_exchange_wallet_features"] == []
    assert admission["eligible_derivatives_features"] == []
    assert admission["eligible_etf_flow_features"] == []
    assert admission["eligible_macro_features"] == []
    assert admission["event_timeline_only"] is True


def test_xrp_insights_etf_settled_and_provisional_dates_are_separate():
    artifact = load_artifact()
    etf = artifact["market_reconciliation"]["etf_flows"]["xrp_insights"]
    assert etf["data_as_of"] == "2026-11-05"
    assert etf["nov6_row_status"] == "PROVISIONAL"
    assert etf["latest_settled_day_net_flow_xrp"] == 110214
    assert etf["nov2_to_nov5_net_flow_xrp"] == -149500
    assert etf["gxrp_flow_status"] == "EXCLUDED_DUE_CAPTURE_GAP"


def test_november_escrow_gross_release_is_separated_from_net_locked_supply():
    artifact = load_artifact()
    escrow = artifact["market_reconciliation"]["ripple_escrow"]
    nov = escrow["november_2026_release"]
    assert nov["gross_escrow_finish_xrp"] == 1_000_000_000
    assert nov["re_escrowed_xrp"] == 700_000_000
    assert nov["net_reduction_in_locked_supply_xrp"] == 300_000_000
    assert sum(x["amount_xrp"] for x in nov["escrow_finish_transactions"]) == 1_000_000_000
    assert sum(x["amount_xrp"] for x in nov["escrow_create_transactions"]) == 700_000_000
    assert "not proven sold" in escrow["interpretation"]
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
