import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data/xrp_intelligence/sources/sbi_visa_crypto_card_and_ripple_rails_20261031.json").read_text(encoding="utf-8"))
SNAPSHOT = json.loads((ROOT / "data/xrp_intelligence/snapshots/20261031T1438Z-sbi-xrp-retail-rewards-and-rlusd-rails.json").read_text(encoding="utf-8"))
GRAPH = json.loads((ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261031T1438Z-sbi-visa-xrp-rewards-and-rlusd-graph.json").read_text(encoding="utf-8"))
DECISION = json.loads((ROOT / "data/xrp_intelligence/architecture_decisions/20261031T1438Z-sbi-xrp-distribution-vs-actual-capital.json").read_text(encoding="utf-8"))


def test_sbi_card_selects_one_crypto_and_converts_monthly():
    card = SNAPSHOT["sbi_visa_crypto_card"]
    assert card["crypto_selection"] == ["BTC", "ETH", "XRP"]
    assert card["selection_rule"] == "ONE_CRYPTO_ASSET_PER_CARD"
    assert card["conversion"] == "AUTOMATIC_MONTHLY_POINTS_TO_SELECTED_CRYPTO"
    assert card["required_account"] == "SBI VC Trade VCTRADE service account"


def test_expired_campaign_is_not_presented_as_current_rate():
    campaign = SNAPSHOT["sbi_visa_crypto_card"]["launch_campaign"]
    assert campaign["application_window_end"] == "2026-05-31"
    assert campaign["spending_window_end"] == "2026-08-05"
    assert campaign["status_at_capture"] == "EXPIRED"
    assert campaign["standard_max_reward_percent"] == 2.5
    assert campaign["gold_max_reward_percent"] == 10.0


def test_actual_xrp_reward_flow_and_sourcing_remain_unknown():
    actual = SNAPSHOT["sbi_visa_crypto_card"]["actual_capital"]
    assert actual["xrp_selected_card_share"] == "UNKNOWN"
    assert actual["monthly_xrp_reward_units"] == "UNKNOWN"
    assert actual["xrp_source"] == "UNKNOWN"
    assert actual["spot_purchase_quantity"] == "UNKNOWN"
    assert actual["otc_purchase_quantity"] == "UNKNOWN"
    assert SNAPSHOT["feature_admission"]["xrp_actual_capital_feature"] == "BLOCKED_PENDING_REDEMPTION_AND_SOURCING_DATA"


def test_sbi_visa_mou_is_exploratory_not_an_xrp_agreement():
    mou = SNAPSHOT["sbi_visa_digital_finance_mou"]
    assert mou["status"] == "EXPLORATORY_BASIC_AGREEMENT"
    assert "XRP" not in mou["scope"]
    assert mou["completed_xrp_or_stablecoin_product"] == "NOT_ESTABLISHED"


def test_sbi_vc_trade_rlusd_listing_is_separate_from_native_xrp():
    listing = SNAPSHOT["sbi_vc_trade_rlusd"]
    assert listing["parties"] == ["SBI VC Trade", "Ripple"]
    assert listing["product"] == "RLUSD"
    assert listing["native_xrp_demand"] == "NOT_ESTABLISHED_BY_LISTING_ALONE"


def test_sbi_deposit_voucher_does_not_equal_redeemed_xrp():
    voucher = SNAPSHOT["sbi_shinsei_deposit_xrp_voucher"]
    assert voucher["minimum_eligible_deposit_jpy"] == 300000
    assert voucher["maximum_voucher_value_jpy"] == 20000
    assert voucher["redemptions_completed"] == "UNKNOWN"
    assert voucher["xrp_units_credited"] == "UNKNOWN"


def test_sbi_graph_edges_resolve_to_source_and_entity_ids():
    node_ids = {node["id"] for node in GRAPH["nodes"]}
    source_ids = {item["source_id"] for item in SOURCE["sources"]}
    edge_ids = [edge["id"] for edge in GRAPH["edges"]]
    assert len(edge_ids) == len(set(edge_ids))
    for edge in GRAPH["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert set(edge["source_ids"]).issubset(source_ids)
        assert edge["evidence_class"]


def test_sbi_prediction_and_actual_capital_are_not_issued():
    assert SNAPSHOT["feature_admission"]["xrp_directional_price_feature"] == "NOT_ADMITTED"
    assert SNAPSHOT["feature_admission"]["xrp_actual_capital_feature"] == "BLOCKED_PENDING_REDEMPTION_AND_SOURCING_DATA"
    assert SNAPSHOT["feature_admission"]["forecast_status"] == "NOT_ISSUED"
    assert DECISION["forecast_status"] == "NOT_ISSUED"
