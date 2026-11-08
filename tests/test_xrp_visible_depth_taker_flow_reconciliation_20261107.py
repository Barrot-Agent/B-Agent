import hashlib
import json
from pathlib import Path

ARTIFACT = Path(
    "research/xrp_intelligence/20261107T091900Z-xrp-visible-depth-taker-flow-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_edge_or_not_depth_is_labeled_as_mixed_spot_and_perpetual():
    artifact = load_artifact()
    edge = next(x for x in artifact["sources"] if x["source_id"].startswith("edge_or_not"))
    assert edge["instrument_coverage"] == ["Binance XRP spot", "OKX XRP-USDT perpetual"]
    assert edge["method"]["sampling"] == "Full visible order book sampled each minute"
    assert edge["method"]["aggregation"] == "15-minute averages"
    assert edge["metrics"]["visible_bids_within_1pct_usd_millions"] == 9.8
    assert edge["metrics"]["visible_asks_within_1pct_usd_millions"] == 10.4


def test_visible_depth_arithmetic_is_reconciled():
    artifact = load_artifact()
    derived = artifact["derived_reconciliation"]
    assert round(derived["edge_visible_bid_ask_ratio"], 6) == round(9.8 / 10.4, 6)
    assert round(derived["edge_visible_depth_imbalance"], 6) == round((9.8 - 10.4) / 20.2, 6)
    assert round(derived["edge_visible_bid_share_pct"], 4) == round(9.8 / 20.2 * 100, 4)


def test_swiftedge_flow_and_wall_are_separate_secondary_observations():
    artifact = load_artifact()
    swift = next(x for x in artifact["sources"] if x["source_id"].startswith("swiftedge"))
    metrics = swift["metrics"]
    assert metrics["net_taker_flow_pct_of_volume"] == -17.1
    assert metrics["large_order_net_usd_millions"] == -10.0
    assert metrics["funding_pct_per_8h"] == 0.01
    assert metrics["open_interest_change_pct_24h"] == -1.5
    assert metrics["bid_wall"]["size_usd_millions"] == 5.7
    assert metrics["ask_wall"]["size_usd_millions"] == 4.1


def test_page_timestamps_are_not_misrepresented_as_exchange_event_times():
    artifact = load_artifact()
    for source in artifact["sources"][:2]:
        assert "page_updated_at_utc" in source
        assert "provider_event_timestamp_utc" not in source
    assert "Page update times differ by 13 minutes" in artifact["derived_reconciliation"]["interpretation"]
    assert "not an arbitrage spread" in artifact["derived_reconciliation"]["interpretation"]


def test_etf_flow_keeps_its_five_fund_universe():
    artifact = load_artifact()
    alpha = next(x for x in artifact["sources"] if x["source_id"].startswith("alpha_finance"))
    assert alpha["metrics"]["fund_count"] == 5
    assert alpha["metrics"]["nov6_net_flow_usd"] == 0
    assert alpha["metrics"]["last_30_sessions_net_flow_usd"] == 45_900_000
    assert "does not publish fund AUM or holdings" in alpha["normalized_excerpt"]


def test_normalized_excerpt_hashes_are_exact():
    artifact = load_artifact()
    for source in artifact["sources"]:
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]


def test_model_admission_and_forecast_remain_fail_closed():
    artifact = load_artifact()
    assert artifact["model_admission"]["eligible_as_price_feature"] is False
    assert artifact["model_admission"]["eligible_as_depth_feature"] is False
    assert artifact["model_admission"]["eligible_as_event_timeline"] is True
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert artifact["forecast"]["shadow_forecast"] is None
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False


def test_orderbook_signal_is_explicitly_unvalidated():
    artifact = load_artifact()
    edge = next(x for x in artifact["sources"] if x["source_id"].startswith("edge_or_not"))
    assert any("signal has not been tested" in item for item in edge["limitations"])
