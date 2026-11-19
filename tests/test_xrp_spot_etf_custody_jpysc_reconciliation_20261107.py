import hashlib
import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T130152Z-xrp-spot-etf-custody-jpysc-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_exchange_receipt_hashes_are_exact():
    data = load_artifact()
    for source in data["spot_market"]["sources"]:
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_kraken_missing_provider_timestamp_is_not_called_fresh():
    data = load_artifact()
    kraken = data["spot_market"]["sources"][0]
    assert kraken["provider_event_timestamp_utc"] is None
    assert kraken["freshness"] == "UNKNOWN_PROVIDER_EVENT_TIME"


def test_okx_timestamp_fails_300_second_live_threshold():
    data = load_artifact()
    okx = data["spot_market"]["sources"][1]
    assert okx["age_at_capture_seconds"] > 300
    assert okx["freshness"] == "STALE_GT_300_SECONDS"


def test_level_one_spreads_recompute():
    data = load_artifact()
    kraken, okx = data["spot_market"]["sources"]
    k = kraken["normalized"]
    o = okx["normalized"]
    k_spread = (k["best_ask_usd"] - k["best_bid_usd"]) / (
        (k["best_ask_usd"] + k["best_bid_usd"]) / 2
    ) * 10000
    o_spread = (o["best_ask_usdt"] - o["best_bid_usdt"]) / (
        (o["best_ask_usdt"] + o["best_bid_usdt"]) / 2
    ) * 10000
    assert math.isclose(k_spread, k["level1_spread_bps"], rel_tol=0, abs_tol=1e-10)
    assert math.isclose(o_spread, o["level1_spread_bps"], rel_tol=0, abs_tol=1e-10)


def test_cross_venue_difference_is_not_an_arbitrage_feature():
    data = load_artifact()
    cross = data["spot_market"]["cross_venue"]
    assert cross["currencies"] == "USD versus USDT"
    assert not cross["fx_or_stablecoin_basis_normalized"]
    assert not cross["event_times_synchronized"]
    assert data["spot_market"]["model_admission"] == "EXCLUDED"


def test_partial_etf_holdings_sum_is_exact_and_not_a_total():
    data = load_artifact()["etf_issuer_snapshots"]
    funds = {x["ticker"]: x for x in data["funds"]}
    expected = (
        funds["XRP"]["xrp_in_trust"]
        + funds["XRPZ"]["xrp_in_fund"]
        + funds["GXRP"]["xrp_in_fund"]
    )
    assert math.isclose(expected, data["partial_known_xrp_holdings_sum"], abs_tol=1e-6)
    assert data["partial_sum_status"] == "INCOMPLETE_AND_NON_SYNCHRONIZED_NOT_TOTAL_MARKET_HOLDINGS"


def test_missing_etf_flow_is_not_zero():
    data = load_artifact()["etf_issuer_snapshots"]
    assert data["daily_dollar_flows"] == "NOT_VERIFIED_FROM_ISSUER_PAGES"
    assert data["flow_disagreement"]["treatment"] == "MISSING_OR_NOT_UPDATED_NOT_CONFIRMED_ZERO_FLOW"


def test_future_dated_canary_snapshot_is_excluded():
    data = load_artifact()["etf_issuer_snapshots"]
    canary = next(x for x in data["funds"] if x["ticker"] == "XRPC")
    assert canary["as_of_date"] is None
    assert canary["xrp_holdings_quantity"] is None
    assert "future-dated values were excluded" in canary["exclusion"].lower()


def test_jpysc_handled_balance_includes_lending_and_is_not_xrp_demand():
    data = load_artifact()["jpysc_sbi"]
    assert "on-chain balance plus lending balance" in data["handled_balance_definition"]
    assert data["reported_lending_balance_jpy"] == ">10000000000"
    assert data["reported_handled_balance_jpy"] == ">30000000000"
    assert "future step" in data["public_chain_status"]
    assert "not an XRP flow" in data["interpretation"]


def test_bny_custody_is_separated_from_conditional_future_work():
    data = load_artifact()
    bny = next(x for x in data["institutional_relationships"] if x["relationship"] == "BNY <-> Ripple")
    assert any("supports XRP and RLUSD" in x for x in bny["verified_roles"])
    assert any("subject to final BNY and regulatory approvals" in x for x in bny["planned_or_conditional"])
    assert "does not prove XRP balances" in bny["interpretation"]


def test_no_forecast_is_issued():
    data = load_artifact()
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["model_admission"]["admitted"] is False
