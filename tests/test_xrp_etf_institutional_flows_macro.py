import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "xrp_intelligence"


def _load(relative):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_xrp_etf_daily_flow_keeps_pending_funds_separate_from_zero():
    snapshot = _load("snapshots/20261031T181303Z-xrp-etf-institutional-flows-and-macro.json")
    flows = snapshot["xrp_etf_flows"]
    assert flows["latest_daily_net_flow_usd"] == 200000
    assert flows["latest_daily_status"] == "PARTIAL_3_OF_5_FUNDS"
    assert set(flows["pending_funds"]) == {"XRPZ", "GXRP"}
    assert flows["two_day_inflow_streak_usd"] == 8700000
    assert flows["reported_xrp_holdings"] == 1142785690
    assert snapshot["prediction"]["forecast_status"] == "NOT_ISSUED"


def test_xrp_13f_data_is_lagged_and_not_direct_xrp_beneficial_ownership():
    snapshot = _load("snapshots/20261031T181303Z-xrp-etf-institutional-flows-and-macro.json")
    holders = snapshot["institutional_13f"]
    assert holders["as_of_date"] == "2026-06-30"
    assert holders["institution_count"] == 127
    assert holders["reported_value_usd"] == 179000000
    assert "direct XRP beneficial ownership" in " ".join(holders["limitations"])


def test_fomc_policy_context_retains_hawkish_dissent_without_price_claim():
    snapshot = _load("snapshots/20261031T181303Z-xrp-etf-institutional-flows-and-macro.json")
    macro = snapshot["macro_context"]
    assert macro["vote"] == "10-2"
    assert macro["target_range_low_pct"] == 3.75
    assert macro["target_range_high_pct"] == 4.0
    assert len(macro["dissenters"]) == 2
    assert snapshot["prediction"]["directional_features_admitted"] == []


def test_etf_and_macro_source_references_resolve():
    snapshot = _load("snapshots/20261031T181303Z-xrp-etf-institutional-flows-and-macro.json")
    graph = _load("relationship_graph_addenda/20261031T181303Z-xrp-etf-institutional-holders-macro.json")
    bundle = _load("sources/20261031T181303Z-xrp-etf-and-macro-source-bundle.json")
    source_ids = {item["source_id"] for item in bundle["sources"]}
    assert set(snapshot["source_ids"]) <= source_ids
    assert set(graph["source_ids"]) <= source_ids
