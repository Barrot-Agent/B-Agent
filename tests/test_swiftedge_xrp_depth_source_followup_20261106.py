from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T022802Z-swiftedge-xrp-depth-source-followup.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_later_provider_page_state_is_timestamped_separately_from_retrieval():
    item = load_artifact()
    source = item["source"]
    assert source["updated_at_utc"] == "2026-11-05T22:53:00Z"
    assert item["capture"]["provider_page_updated_at_utc"] == source["updated_at_utc"]
    assert source["exact_retrieval_timestamp_utc"] is None
    assert source["raw_http_wire_bytes_captured"] is False
    assert item["comparison_to_prior_page_state"]["prior_updated_at_utc"] == "2026-11-05T22:51:00Z"


def test_orderbook_walls_match_the_provider_page_and_prior_state_is_preserved():
    item = load_artifact()
    row = item["observation"]
    prior = item["comparison_to_prior_page_state"]
    assert row["bid_wall_price_usd"] == 1.215
    assert row["bid_wall_size_xrp"] == 3_591_526
    assert row["ask_wall_price_usd"] == 1.221
    assert row["ask_wall_size_xrp"] == 3_128_892
    assert prior["prior_bid_wall_price_usd"] == 1.21
    assert prior["prior_bid_wall_size_xrp"] == 3_676_765
    assert prior["prior_ask_wall_size_xrp"] == 3_081_006


def test_near_price_depth_is_band_specific_not_directional():
    item = load_artifact()["observation"]
    one = item["depth_within_1_percent"]
    two = item["depth_within_2_percent"]
    assert one["asks_usd_rounded"] > one["bids_usd_rounded"]
    assert two["bids_usd_rounded"] > two["asks_usd_rounded"]
    assert one["average_window"] == "one_minute"
    assert two["average_window"] == "one_minute"


def test_provider_explicitly_discloses_cancel_risk_and_estimated_positioning():
    source = load_artifact()["source"]
    assert any("often pulled" in x for x in source["methodology_disclosed"])
    assert any("estimates" in x for x in source["methodology_disclosed"])
    assert len(source["limitations"]) >= 5


def test_followup_remains_research_only_without_a_forecast():
    item = load_artifact()
    assert item["model_eligible"] is False
    assert item["forecast_status"] == "NOT_ISSUED"
    assert item["data_cutoff_utc"] is None
