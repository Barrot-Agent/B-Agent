import hashlib
import json
import math
from pathlib import Path

ARTIFACT = Path(
    "research/xrp_intelligence/20261107T234225Z-xrpl-depth-exchange-balance-rlusd-agentic-payments.json"
)
CORRECTION = Path(
    "research/xrp_intelligence/20261107T234225Z-sbi-rlusd-source-url-metadata-correction.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_fuelmaps_depth_is_spot_only_and_preserves_bid_share():
    data = load_artifact()
    source = data["order_book_sources"][0]
    assert source["product_scope"].startswith("Spot only")
    assert source["venue_universe"] == [
        "Coinbase", "OKX", "Kraken", "Bitstamp", "Bitfinex", "Gemini"
    ]
    values = source["normalized"]
    bid_share = values["bid_within_1pct_usd"] / (
        values["bid_within_1pct_usd"] + values["ask_within_1pct_usd"]
    ) * 100
    assert math.isclose(bid_share, values["bid_share_within_1pct_pct"], abs_tol=1e-9)
    assert values["bid_share_within_1pct_pct"] == 58.2
    assert values["bid_share_within_5pct_pct"] == 69.4
    assert source["model_feature_eligible"] is False


def test_edge_or_not_mixed_spot_perp_book_is_not_merged_with_fuelmaps():
    data = load_artifact()
    fuelmaps, edge = data["order_book_sources"]
    assert edge["venue_universe"] == ["Binance spot", "OKX XRP-USDT perpetual"]
    assert edge["snapshot_utc"] > fuelmaps["snapshot_utc"]
    bid_share = edge["normalized"]["bid_within_1pct_usd"] / (
        edge["normalized"]["bid_within_1pct_usd"]
        + edge["normalized"]["ask_within_1pct_usd"]
    ) * 100
    assert math.isclose(
        bid_share,
        edge["normalized"]["bid_share_within_1pct_pct"],
        abs_tol=1e-8,
    )
    assert edge["normalized"]["bid_share_within_1pct_pct"] < 51
    assert edge["model_feature_eligible"] is False
    assert "do not average" in data["source_independence"]["order_book"].lower()


def test_exchange_wallet_totals_are_attributed_wallets_not_tradable_float():
    data = load_artifact()
    source = data["exchange_wallet_balance_source"]
    values = source["normalized"]
    assert values["attributed_xrp"] == 22_330_000_000
    assert values["wallet_count"] == 701
    assert values["exchange_count"] == 24
    assert values["same_wallet_change_7d_xrp"] == -150_700_000
    assert values["same_wallet_change_30d_xrp"] == -161_200_000
    assert values["naive_total_change_xrp"] == 350_800_000
    assert values["newly_tracked_wallet_balance_xrp"] == 512_000_000
    assert values["wrapped_insurance_charity_reserves_xrp"] == 487_800_000
    assert "not tradable float" in source["excerpt"].lower()
    assert source["model_feature_eligible"] is False


def test_coinbase_binance_and_sbi_balances_are_wallet_attribution_not_ownership():
    data = load_artifact()
    source = data["exchange_wallet_balance_source"]
    values = source["normalized"]
    assert values["coinbase_attributed_xrp"] == 5_790_000_000
    assert values["coinbase_cb_xrp_reserve_xrp"] == 150_800_000
    assert values["binance_attributed_xrp"] == 2_730_000_000
    assert values["upbit_attributed_xrp"] == 6_440_000_000
    assert values["sbi_vc_trade_attributed_xrp"] == 56_600_000
    assert values["sbi_vc_trade_7d_change_xrp"] == -2_900_000
    assert "not a disclosed customer balance" in source["limitations"][-1].lower()


def test_rlusd_issuer_reserves_and_onchain_network_supply_keep_distinct_scopes():
    data = load_artifact()
    issuer, onchain, product, sbi = data["rlusd_sources"]
    values = issuer["normalized"]
    ratio = values["reserve_funds_usd"] / values["circulating_usd"] * 100
    assert math.isclose(ratio, values["arithmetic_reserve_coverage_pct"], abs_tol=1e-8)
    assert values["arithmetic_reserve_excess_usd"] == 115_100_000
    assert issuer["data_as_of"] == "2026-11-05"
    assert "ends at September 2026" in issuer["excerpt"]
    assert onchain["normalized"]["total_xrpl_ethereum_usd"] == 2_670_000_000
    assert onchain["normalized"]["xrpl_supply_usd"] == 884_300_000
    assert onchain["normalized"]["ethereum_supply_usd"] == 1_790_000_000
    assert product["normalized"]["supported_chain_count"] == 7
    assert sbi["published_date"] == "2026-06-24"
    assert "does not establish XRP settlement" in sbi["excerpt"]


def test_sbi_distribution_url_correction_is_explicit_and_verifiable():
    data = load_artifact()
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    sbi = data["rlusd_sources"][3]
    assert sbi["url"] == correction["corrected"]["url"]
    assert correction["supersedes"]["prior_url"] != correction["corrected"]["url"]
    assert correction["evidence"]["factual_claims_changed"] is False


def test_agentic_payment_counters_are_not_capital_flow_or_xrp_demand():
    data = load_artifact()
    t54, radar, mastercard, xrpl_docs = data["agentic_payments_sources"]
    tv = t54["normalized"]
    rv = radar["normalized"]
    average = tv["all_time_value_settled_usd"] / tv["all_time_transactions"]
    assert math.isclose(
        average,
        tv["average_settled_value_usd_per_transaction"],
        abs_tol=1e-8,
    )
    assert tv["all_time_transactions"] == 15_309_300
    assert rv["all_time_transactions"] == 15_272_937
    assert tv["all_time_transactions"] != rv["all_time_transactions"]
    assert "Unverified" in t54["excerpt"]
    assert rv["settled_xrp"] == 7027
    assert rv["settled_rlusd_usd"] == 57502
    assert mastercard["published_date"] == "2026-06-10"
    assert "program-level co-participation" in mastercard["excerpt"]
    assert "DepositAuth" in xrpl_docs["excerpt"]
    assert "KMS/HSM" in xrpl_docs["excerpt"]


def test_mastercard_participants_do_not_imply_bilateral_xrp_settlement():
    data = load_artifact()
    mastercard = data["agentic_payments_sources"][2]
    participants = set(mastercard["participants"])
    assert {"Coinbase", "OKX", "RippleX", "t54 Labs"}.issubset(participants)
    assert "multi-rail" in mastercard["excerpt"]
    assert "not evidence of a bilateral agreement" in mastercard["excerpt"]


def test_all_preserved_excerpts_match_their_sha256_hashes():
    data = load_artifact()
    sources = (
        data["order_book_sources"]
        + [data["exchange_wallet_balance_source"]]
        + data["rlusd_sources"]
        + data["agentic_payments_sources"]
    )
    for source in sources:
        excerpt = source.get("excerpt", source.get("page_excerpt"))
        digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
        expected = source["excerpt_sha256"]
        assert digest == expected


def test_no_forecast_wallet_or_payment_action_was_issued():
    data = load_artifact()
    assert data["model_admission"]["eligible_as_event_timeline"] is True
    assert all(
        data["model_admission"][key] is False
        for key in (
            "order_book_depth",
            "exchange_wallet_balances",
            "rlusd_supply",
            "agentic_payment_counters",
        )
    )
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast"] is None
    assert data["forecast"]["paper_trade_executed"] is False
    assert data["forecast"]["real_money_action"] is False
    assert data["agentic_payments_sources"][3]["limitations"][-1] == (
        "No transaction was signed or submitted."
    )
