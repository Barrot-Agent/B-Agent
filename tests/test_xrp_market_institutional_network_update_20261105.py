from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ARTIFACT = Path("research/xrp_intelligence/xrp-market-institutional-network-update-20261105.json")


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_spot_body_hash_and_metrics_are_preserved_but_model_ineligible():
    data = load_artifact()
    spot = data["market_snapshot"]["kraken_xrp_usd"]
    assert hashlib.sha256(spot["raw_response_body_text"].encode()).hexdigest() == spot["raw_response_body_text_sha256"]
    assert spot["values"]["last_trade_usd"] == 1.21721
    assert spot["values"]["spread_bps"] == pytest.approx(0.0821547549)
    assert spot["retrieval_time_utc"] is None
    assert data["capture_time_policy"]["captured_at_utc"] is None
    assert data["model_admission"]["model_eligible"] is False
    assert data["directional_forecast_issued"] is False


def test_derivatives_vintages_keep_venue_scope_and_counterevidence():
    data = load_artifact()["derivatives"]
    latest, prior = data["latest"], data["prior_same_publisher"]
    assert data["provider_page_update_time_utc"] == "2026-11-05T22:35:00Z"
    assert data["display_delay_minutes"] == 15
    assert latest["open_interest_7_exchanges_usd"] == 1_940_000_000
    assert latest["liquidations_24h_5_exchanges_usd_at_least"] == 12_370_000
    assert latest["long_liquidations_usd"] > latest["short_liquidations_usd"]
    assert latest["funding_pct_per_8h"] > 0
    assert latest["long_account_share_pct"] > 80
    assert prior["open_interest_7_exchanges_usd"] > latest["open_interest_7_exchanges_usd"]
    assert data["model_eligible"] is False


def test_etf_universes_and_vintages_are_not_combined():
    data = load_artifact()["etf_flow_reconciliation"]
    rows = {x["source_id"]: x for x in data["observations"]}
    assert rows["XRP_INSIGHTS_ETF_20261104"]["daily_nov4_flow_xrp"] == -64826
    assert rows["XRP_INSIGHTS_ETF_20261104"]["nov2_to_nov4_flow_xrp"] == -259700
    assert "GXRP is excluded" in rows["XRP_INSIGHTS_ETF_20261104"]["exclusion"]
    assert rows["ALPHA_FINANCE_XRP_ETF_20261104"]["nov4_flow_usd"] == 0
    assert rows["ALPHA_FINANCE_XRP_ETF_20261104"]["fund_universe"] == "5 funds"
    assert rows["CRYPTOKEYHOLE_XRP_ETF_20261103_PARTIAL_NOV4"]["fund_universe"] == "4 funds"
    assert "Partial" in rows["CRYPTOKEYHOLE_XRP_ETF_20261103_PARTIAL_NOV4"]["nov4_status"]
    assert data["comparability"]["values_comparable_as_one_daily_total"] is False
    assert data["comparability"]["direct_ap_cash_creation_redemption_verified"] is False


def test_institutional_equity_distribution_custody_and_consortium_edges_are_distinct():
    network = load_artifact()["institutional_network"]
    edges = network["relationship_edges"]
    sbi_circle = next(x for x in edges if x["from"] == "SBI Holdings" and x["to"] == "Circle")
    sbi_ripple = next(x for x in edges if x["from"] == "SBI Holdings" and x["to"] == "Ripple")
    coinbase_ripple = next(x for x in edges if x["from"] == "Coinbase" and x["to"] == "Ripple")
    sbi_open_standard = next(x for x in edges if x["from"] == "SBI Holdings" and x["to"] == "Open Standard")
    assert sbi_circle["amount_usd"] == 25_000_000
    assert sbi_ripple["asset"] == "Ripple corporate equity"
    assert sbi_ripple["not_implied"] == "XRP token holdings"
    assert coinbase_ripple["asset"] == "RLUSD"
    assert sbi_open_standard["relation"] == "consortium participation"
    assert "does not establish a direct Circle-Ripple partnership" in network["circle_ripple_limit"]


def test_jpysc_and_rlusd_capital_is_not_misclassified_as_xrp_demand():
    data = load_artifact()
    events = {x["source_id"]: x for x in data["institutional_network"]["dated_disclosures"]}
    jpysc = events["SBI_JPYSC_JGB_20260907"]
    assert "JPY 10B" in jpysc["relation"]
    assert "JPY 6.9B" in jpysc["lending"]
    assert "not verified loans" in jpysc["lending"]
    assert "Ethereum-chain RLUSD only at launch" in events["SBI_VC_TRADE_RLUSD_JAPAN_20260624"]["launch_limit"]
    assert "not live at launch" in events["RIPPLE_COINBASE_RLUSD_20261028"]["collateral_status"]
    assert "eligible clients" in events["BNY_RIPPLE_XRP_RLUSD_CUSTODY_20261027"]["relation"]
    assert "not a bilateral SBI-Coinbase" in events["SBI_STARTALE_OPEN_STANDARD_20261016"]["uncertainty"]


def test_source_ids_and_retrieval_uncertainty_are_explicit():
    data = load_artifact()
    sources = data["source_registry"]
    ids = [x["source_id"] for x in sources]
    assert len(ids) == len(set(ids))
    assert all(x["retrieval_time_utc"] is None for x in sources)
    assert all(x["url"].startswith("https://") for x in sources)
    assert data["model_admission"]["model_eligible"] is False
    assert data["paper_trade_executed"] is False
    assert data["real_money_action"] is False


def test_etf_timestamp_correction_is_exact_blob_bound_and_preserves_unbound_ancestor():
    import hashlib

    source_path = Path(
        "research/xrp_intelligence/20261105T190803Z-xrp-late-session-spot-derivatives-etf-macro-snapshot.json"
    )
    overlay_path = Path(
        "research/xrp_intelligence/20261105-xrp-late-session-etf-timestamp-correction-preimage-bound.json"
    )
    earlier = Path(
        "research/xrp_intelligence/20261105T191449Z-xrp-late-session-etf-date-only-timestamp-correction.json"
    )
    source_bytes = source_path.read_bytes()
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    git_blob = hashlib.sha1(
        b"blob " + str(len(source_bytes)).encode("ascii") + b"\0" + source_bytes
    ).hexdigest()
    assert overlay["target_artifact_blob_sha"] == git_blob
    assert overlay["target_artifact"] == source_path.as_posix()
    assert overlay["model_eligible"] is False
    assert overlay["forecast_issued"] is False
    assert len(overlay["field_corrections"]) == 4
    assert all(item["model_eligible"] is False for item in overlay["field_corrections"])
    assert earlier.exists()
    earlier_overlay = json.loads(earlier.read_text(encoding="utf-8"))
    assert "target_artifact_blob_sha" not in earlier_overlay


def test_sbic_east_central_west_are_distinct_regional_entities_not_sbi_holdings():
    data = load_artifact()
    identity = data["sbic_identity_disambiguation"]
    entities = {item["region"]: item for item in identity["entities"]}
    assert entities["East"]["legal_name"] == "Tokyo Small and Medium Business Investment & Consultation Co., Ltd."
    assert entities["Central"]["abbreviation"] == "SBIC Central Japan"
    assert entities["West"]["abbreviation"] == "SBIC West Japan"
    assert entities["Central"]["legal_name"].startswith("Nagoya ")
    assert entities["West"]["legal_name"].startswith("Osaka ")
    assert "Osaka Small and Medium Business Investment & Consultation Co., Ltd." in entities["Central"]["sister_companies"]
    assert "Nagoya Small and Medium Business Investment & Consultation Co., Ltd." in entities["West"]["sister_companies"]
    assert "not SBI Holdings" in identity["conclusion"]
    assert "does not establish parentage" in identity["relationship_limit"]
    assert all(item["retrieval_time_utc"] is None for item in data["source_registry"] if item["source_id"].startswith("SBIC_"))
