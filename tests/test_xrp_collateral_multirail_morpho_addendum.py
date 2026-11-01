import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = "data/xrp_intelligence/snapshots/20261101T163641Z-xrp-collateral-multirail-morpho-circle-sbi.json"
GRAPH = "data/xrp_intelligence/relationship_graph_addenda/20261101T163641Z-coinbase-circle-sbi-xrp-collateral-multirail.json"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_fxrp_rlusd_market_is_live_but_concentrated_and_not_280m():
    snap = load(SNAPSHOT)["fxrp_rlusd_morpho_market"]
    assert snap["total_market_size_usd"] == 9_350_000
    assert snap["outstanding_loans_usd"] == 8_440_000
    assert snap["current_utilization_pct"] == 90.22
    assert snap["supplier_concentration"][0]["share_pct"] == 99.04
    assert snap["top3_borrower_share_pct"] == 91.0
    assert snap["liquidation_ltv_pct"] == 77
    assert "different scopes and dates" in snap["distinction_from_280m_claim"]
    assert snap["feature_admission"].startswith("DESCRIPTIVE_CANDIDATE_QUARANTINED")


def test_coinbase_usdc_xrp_collateral_is_not_attributed_to_circle_as_lender():
    snap = load(SNAPSHOT)["coinbase_xrp_collateral"]
    assert snap["debt_asset"] == "USDC"
    assert snap["collateral_asset"] == "XRP"
    assert snap["stated_max_loan_usd"] == 100000
    assert snap["reported_max_initial_ltv_pct"] == 49
    assert snap["reported_liquidation_ltv_pct"] == 62.5
    assert "no evidence Circle controls" in snap["circle_role"]


def test_circle_native_usdc_on_xrpl_is_not_native_xrp():
    circle = load(SNAPSHOT)["circle_xrpl_and_arc"]["native_usdc_on_xrpl"]
    assert circle["status"] == "CONFIRMED_BY_CIRCLE"
    assert circle["token_standard"] == "XRPL Fungible Token"
    assert "not native XRP" in circle["distinction"]


def test_circle_arc_and_sbi_are_multi_rail_not_exclusive_ripple_alignment():
    snap = load(SNAPSHOT)
    arc = snap["circle_xrpl_and_arc"]["arc"]
    assert "SBI Group" in arc["founding_validators"]
    assert "Coinbase" in arc["exchange_participants"]
    assert "BitGo" in arc["custody_providers"]
    assert arc["xrp_or_xrpl_named_in_launch_release"] is False
    sbi = snap["sbi_multirail"]
    assert sbi["total_is_xrp_odl_volume"] is False
    assert "Nium" in [x["partner"] for x in sbi["additional_rails"]]
    assert "Fasset" in [x["partner"] for x in sbi["additional_rails"]]


def test_sbi_remit_2_5t_is_not_xrp_corridor_volume():
    sbi = load(SNAPSHOT)["sbi_multirail"]
    assert sbi["sbi_remit_total_cumulative_remittances_jpy_as_of_2026_05_27"] == 2_500_000_000_000
    assert sbi["total_is_xrp_odl_volume"] is False
    assert "volume is undisclosed" in sbi["xrp_odl_status"]


def test_market_snapshot_is_not_admitted_as_predictive_feature_or_forecast():
    snap = load(SNAPSHOT)
    assert snap["market_observation"]["feature_admission"] == "DESCRIPTIVE_ONLY_NOT_ADMITTED_TO_PREDICTIVE_FEATURE_STORE"
    assert snap["model_controls"]["feature_admission"] == "NONE"
    assert snap["model_controls"]["forecast_status"] == "NOT_ISSUED"


def test_graph_preserves_circle_xrpl_link_and_no_direct_circle_native_xrp_claim():
    graph = load(GRAPH)
    edges = graph["edges"]
    assert any(e["from"] == "usdc" and e["to"] == "xrpl" and e["confidence"] == "confirmed" for e in edges)
    assert any(e["from"] == "circle" and e["to"] == "xrp" and e["confidence"] == "not_established" for e in edges)
