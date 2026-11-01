from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "data/xrp_intelligence/research_ledger_addenda").glob("*-coinbase-circle-q3-2026-financial-position-and-metric-reconciliation.json"))


def load():
    assert FILES, "Coinbase/Circle Q3 financial reconciliation artifact missing"
    return json.loads(FILES[-1].read_text(encoding="utf-8"))


def test_coinbase_spot_weakness_and_stablecoin_rate_sensitivity_are_separate():
    d = load()["coinbase_q3_2026"]
    assert d["drivers"]["consumer_crypto_spot_volume_yoy_pct"] == -59
    assert d["drivers"]["institutional_crypto_spot_volume_yoy_pct"] == -53
    assert d["metrics_usd_millions"]["stablecoin_revenue_yoy_pct"] == -5
    assert d["drivers"]["lower_average_interest_rate_impact_on_q3_stablecoin_revenue_usd_millions"] == -52.8


def test_circle_and_coinbase_usdc_balance_metrics_are_not_comparable():
    d = load()["metric_reconciliation"]
    assert "not directly comparable" in d["conclusion"]
    assert "non-custodial" in d["circle_usdc_on_platform_definition"]
    assert "full or partial keys" in d["coinbase_usdc_aop_definition"]


def test_coinbase_reported_net_income_is_not_equated_with_adjusted_ebitda():
    d = load()["coinbase_q3_2026"]["metrics_usd_millions"]
    assert d["net_income"] == 718.697
    assert d["adjusted_ebitda"] == 332.868
    assert d["crypto_asset_investment_gains_excluded_from_adjusted_ebitda"] == 715.022


def test_circle_distribution_costs_and_coinbase_renewal_are_distinct_evidence():
    d = load()
    assert d["circle_q2_2026"]["distribution_costs_to_coinbase_q2_usd_millions"] == 324.6
    assert d["coinbase_q3_2026"]["drivers"]["circle_arrangement"] == "Renewed on the same terms."
    assert d["prediction_status"] == "NOT_ISSUED"
