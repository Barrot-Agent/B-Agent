from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "data/xrp_intelligence/snapshots").glob("*-xrpl-rlusd-supply-and-payment-quality-reconciliation.json"))


def load():
    assert FILES, "XRPL RLUSD supply/payment-quality snapshot missing"
    return json.loads(FILES[-1].read_text(encoding="utf-8"))


def test_current_xrpl_rlusd_supply_is_corroborated_but_global_split_is_unknown():
    d = load()
    obs = d["current_supply_observations"]
    dashboard = next(x for x in obs if x["provider"] == "XRPL Dashboard")
    llama = next(x for x in obs if x["provider"] == "DefiLlama XRPL chain stablecoins")
    assert 700000000 <= dashboard["rlusd_outstanding_xrpl"] <= 720000000
    assert 700000000 <= llama["rlusd_market_cap_usd"] <= 720000000
    assert "not traced" in d["supply_assessment"]["unresolved"]


def test_rlusd_gross_payment_volume_is_not_called_net_external_capital():
    p = load()["payment_quality_observation"]
    assert p["reported_total_payment_count"] == 7820000
    assert p["sub_1_rlusd_payment_share_pct"] == 99.6
    assert p["gross_value_of_payments_at_least_1_rlusd_usd"] == 7330000000
    assert any("not net external capital" in item for item in p["limitations"])


def test_cross_river_is_company_announced_but_usage_metrics_remain_unknown():
    d = load()["institutional_payment_rail"]
    assert d["status"] == "Company-announced integration with limited-state availability"
    assert any("No customer count" in item for item in d["unknowns"])


def test_xrp_auto_bridge_flow_is_gross_transient_usage_not_net_xrp_demand():
    d = load()["xrp_bridge_usage"]
    assert d["reported_bridge_trades"] == 11009
    assert d["reported_xrp_in_swaps"] == 246000
    assert any("not net XRP acquired or held" in item for item in d["limitations"])
    assert load()["prediction_status"] == "NOT_ISSUED"

def test_cross_chain_migration_is_supported_but_does_not_reconcile_full_supply_change():
    d = load()
    claim = d["supply_assessment"]["cross_chain_migration_claim"]
    assert "do not reconcile the full" in claim
    assert any("coindaro.com" in source for source in d["supply_assessment"]["sources"])
    assert any("tokenpost.com" in source for source in d["supply_assessment"]["sources"])


def test_ai_agent_transaction_count_is_separated_from_settled_value():
    d = load()["ai_agent_payment_case"]
    assert d["reported_all_time_transactions"] == 4491820
    assert d["reported_xrp_settled"] == 5836.71
    assert d["reported_rlusd_settled"] == 4125.29
    assert d["approximate_usd_value_at_article_price"] == 11830
    assert any("not equivalent to economic value" in item for item in d["limitations"])
