import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = "data/xrp_intelligence/snapshots/20261101T164842Z-xrpl-usdc-rlusd-circle-coinbase-economics.json"


def load():
    return json.loads((ROOT / PATH).read_text(encoding="utf-8"))


def test_same_indexer_reports_rlusd_supply_materially_above_usdc():
    snap = load()
    tokens = snap["xrpl_tokens"]
    assert tokens["usdc"]["supply"] == 6_020_000
    assert tokens["rlusd"]["supply"] == 712_520_000
    assert tokens["comparisons"]["rlusd_to_usdc_xrpl_supply_multiple"] == 118.36
    assert tokens["comparisons"]["usdc_xrpl_share_of_circle_global_circulation_pct"] == 0.0086
    assert "same-indexer" in tokens["comparisons"]["caveat"].lower()


def test_permissionless_stablecoin_and_xrp_amm_pools_are_not_corporate_partnerships():
    snap = load()
    usdc = snap["xrpl_tokens"]["usdc"]["largest_amm_pools"]
    rlusd = snap["xrpl_tokens"]["rlusd"]["largest_amm_pools"]
    assert usdc[0]["pair"] == "USDC/XRP"
    assert rlusd[0]["pair"] == "RLUSD/XRP"
    assert usdc[1]["pair"] == "USDC/RLUSD"
    assert rlusd[1]["pair"] == "RLUSD/USDC"
    assert usdc[1]["trades_30d"] == 144
    assert "not formal" in " ".join(snap["hypotheses"][2]["counter_evidence"] for _ in [0]).lower() or snap["hypotheses"][2]["classification"] == "CONFIRMED_POOL_EXISTS"


def test_circle_global_redemptions_are_not_attributed_to_xrp():
    circle = load()["circle_global_usdc"]
    assert circle["circulation_usd"] == 70_000_000_000
    assert circle["reserve_assets_usd"] == 71_400_000_000
    assert circle["issuance_redemption"]["days_30"]["net_usd"] == -3_100_000_000
    assert "not evidence of rotation into XRP" in circle["interpretation"]


def test_circle_and_coinbase_financial_dependencies_are_separate_and_period_tagged():
    snap = load()
    circle = snap["circle_q2_2026_sec"]
    coinbase = snap["coinbase_q3_2026_sec"]
    assert circle["reserve_income_share_of_total_revenue_q2_pct"] == 95.2
    assert circle["distribution_costs_to_coinbase_q2_usd"] == 324_600_000
    assert circle["distribution_costs_to_coinbase_h1_usd"] == 655_300_000
    assert coinbase["consumer_spot_volume_q3_yoy_change_pct"] == -59
    assert coinbase["institutional_spot_volume_q3_yoy_change_pct"] == -53
    assert coinbase["net_income_q3_usd"] == 718_697_000
    assert coinbase["gains_on_crypto_assets_held_for_investment_q3_usd"] == 715_022_000
    assert "2026-06-30" == circle["period_end"]
    assert "2026-09-30" == coinbase["period_end"]


def test_no_xrp_forecast_or_predictive_feature_admission():
    snap = load()
    assert snap["data_quality"]["feature_admission"] == "NONE"
    assert snap["model_controls"]["forecast_status"] == "NOT_ISSUED"
