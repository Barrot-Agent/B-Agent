import json
from pathlib import Path


ARTIFACT = Path(
    "research/xrp_intelligence/"
    "20261105T2135Z-xrp-market-etf-and-occ-charter-reconciliation.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_ticker_keeps_utc_day_and_rolling_24h_fields_separate():
    data = _load()
    spot = data["market_snapshot"]
    assert spot["last_trade_usd"] == 1.22097
    assert spot["utc_day_open_usd"] == 1.3041
    assert spot["volume_xrp"]["rolling_24h"] == 37955216.22697216
    assert spot["volume_xrp"]["utc_day_since_midnight"] == 34405107.02523266
    assert spot["vwap_usd"]["rolling_24h"] == 1.27253343
    assert spot["vwap_usd"]["utc_day_since_midnight"] == 1.26872955
    assert spot["provider_event_timestamp_utc"] is None
    assert round(spot["derived_context"]["last_vs_utc_day_open_pct"], 4) == -6.3745


def test_etf_provider_disagreement_is_not_averaged_or_called_cash_flow():
    data = _load()
    etf = data["etf_flow_reconciliation"]
    rows = {row["source_id"]: row for row in etf["observations"]}
    assert rows["XRP_INSIGHTS_ETF_DATA_20261105"]["net_flow_xrp"] == -194875
    assert rows["CRYPTOKEYHOLE_XRP_ETF_20261105"]["net_flow_xrp"] == -3339
    assert rows["ALPHA_FINANCE_XRP_ETF_20261105"]["net_flow_usd"] == 0
    assert etf["reconciliation"]["values_comparable_as_one_daily_total"] is False
    assert etf["reconciliation"]["cash_creation_redemption_verified"] is False
    assert etf["reconciliation"]["direct_xrp_spot_purchase_verified"] is False
    assert all("issuer-published ETF holdings" == row["independence_group"] for row in data["sources"] if "ETF" in row["id"])


def test_ripple_and_coinbase_occ_charter_statuses_are_not_conflated():
    data = _load()
    comparison = data["regulatory_charter_comparison"]
    ripple = comparison["ripple_national_trust_bank"]
    coinbase = comparison["coinbase_national_trust_company"]
    assert ripple["proposed_charter_number"] == "25364"
    assert ripple["consummated_effective_date"] == "2026-10-26"
    assert "opening" in ripple["operating_status"]
    assert coinbase["proposed_charter_number"] == "25390"
    assert coinbase["conditional_approval_date"] == "2026-04-02"
    assert coinbase["later_effective_action_visible_in_retrieved_cas_record"] is False
    assert "other custody entities" in coinbase["operating_status"]
    assert all("No charter status" not in item for item in comparison["comparison_limits"])


def test_institutional_charter_events_do_not_create_xrp_flow_or_collateral_features():
    data = _load()
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["directional_forecast_issued"] is False
    assert data["model_admission"]["xrp_net_cash_flow_usd"] is None
    assert data["model_admission"]["xrp_custody_balance"] is None
    assert data["model_admission"]["xrp_collateral_balance"] is None
    assert data["regulatory_charter_comparison"]["ripple_national_trust_bank"]["xrp_flow_or_collateral_disclosed"] is False
    assert data["regulatory_charter_comparison"]["coinbase_national_trust_company"]["xrp_flow_or_collateral_disclosed"] is False


def test_source_provenance_is_explicit_and_raw_bytes_are_not_falsely_claimed():
    data = _load()
    assert data["exact_per_source_retrieval_timestamps_utc"] is None
    assert data["sources"]
    ids = [source["id"] for source in data["sources"]]
    assert len(ids) == len(set(ids))
    assert all(source["url"] and source["publisher"] for source in data["sources"])
    assert all(source["raw_bytes_captured"] is False for source in data["sources"])
    assert data["preservation"]["source_disagreements_retained"] is True
    assert data["preservation"]["source_independence_not_overstated"] is True
