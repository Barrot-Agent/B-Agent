import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data/xrp_intelligence/sources/sbi_visa_crypto_card_current_terms_20261031.json").read_text(encoding="utf-8"))
SNAPSHOT = json.loads((ROOT / "data/xrp_intelligence/snapshots/202610311440Z-sbi-visa-crypto-card-current-campaign.json").read_text(encoding="utf-8"))
GRAPH = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/202610311440Z-sbi-visa-card-current-campaign-graph.json").read_text(encoding="utf-8"))
DECISION = json.loads((ROOT / "data/xrp_intelligence/architecture_decisions/202610311440Z-sbi-card-current-terms-actual-capital.json").read_text(encoding="utf-8"))


def test_current_campaign_window_and_delivery_are_timestamped():
    campaign = SNAPSHOT["current_campaign"]
    assert campaign["application_start"] == "2026-09-01"
    assert campaign["application_end"] == "2026-10-31"
    assert campaign["card_issue_deadline"] == "2026-11-30"
    assert campaign["eligible_spend_end"] == "2026-12-05"
    assert campaign["reward_delivery_target"] == "2027-02-28"
    assert campaign["status_at_capture"] == "APPLICATION_WINDOW_OPEN_AT_CAPTURE"


def test_base_monthly_rewards_are_separate_from_campaign_rewards():
    base = SNAPSHOT["current_base_rewards"]
    assert base["standard"]["yen_spend_per_point"] == 200
    assert base["gold"]["yen_spend_per_point"] == 200
    assert base["standard"]["point_value_jpy"] == 1
    assert base["gold"]["point_value_jpy"] == 2
    assert base["crypto_conversion"] == "AUTOMATIC_BY_MONTH_END"
    assert base["xrp_precision"] == "TRUNCATE_TO_7_DECIMAL_PLACES"


def test_reward_price_reference_is_not_an_execution_record():
    base = SNAPSHOT["current_base_rewards"]
    assert "displayed sales price" in base["conversion_price_reference"]
    actual = SNAPSHOT["actual_capital"]
    assert actual["xrp_spot_purchase_units"] == "UNKNOWN"
    assert actual["xrp_otc_purchase_units"] == "UNKNOWN"
    assert actual["net_external_xrp_capital"] == "UNKNOWN"


def test_campaign_caps_and_multiple_card_priority_are_bounded():
    campaign = SNAPSHOT["current_campaign"]
    assert campaign["joining_reward_jpy_equivalent"] == 500
    assert campaign["standard"]["maximum_jpy_equivalent"] == 2000
    assert campaign["gold"]["maximum_jpy_equivalent"] == 4000
    assert campaign["combined_usage_reward_max_if_both_card_types_jpy_equivalent"] == 6000
    assert campaign["campaign_asset_priority_when_multiple_cards"] == ["GOLD_BEFORE_STANDARD", "BTC_BEFORE_ETH_BEFORE_XRP"]


def test_current_campaign_xrp_feature_is_not_admitted_as_price_signal():
    assert SNAPSHOT["feature_admission"]["xrp_distribution_event_timeline"] == "ADMITTED"
    assert SNAPSHOT["feature_admission"]["xrp_actual_capital_feature"] == "BLOCKED_PENDING_REWARD_CREDIT_AND_INVENTORY_SOURCE_DATA"
    assert SNAPSHOT["feature_admission"]["xrp_directional_price_feature"] == "NOT_ADMITTED"
    assert SNAPSHOT["feature_admission"]["forecast_status"] == "NOT_ISSUED"
    assert DECISION["forecast_status"] == "NOT_ISSUED"


def test_source_and_graph_provenance_resolve():
    source_ids = {item["source_id"] for item in SOURCE["sources"]}
    node_ids = {node["id"] for node in GRAPH["nodes"]}
    for edge in GRAPH["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert set(edge["source_ids"]).issubset(source_ids)
