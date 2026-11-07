import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T210512Z-xrp-etf-flow-provider-scope-disagreement.json"
)


def _artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_etf_flow_disagreement_artifact_is_well_formed_and_time_bounded():
    record = _artifact()
    assert record["schema_version"] == "1.0"
    assert record["revision"] == 2
    assert record["record_type"] == "xrp_etf_flow_provider_scope_disagreement"
    assert record["mission_id"] == "xrp_intelligence_prediction_engine"
    captured = datetime.fromisoformat(record["captured_at_utc"].replace("Z", "+00:00"))
    assert captured.tzinfo is not None
    assert captured.utcoffset() == timezone.utc.utcoffset(captured)
    assert record["data_as_of_utc"].startswith("2026-11-06")


def test_rendered_excerpt_receipts_recompute_and_respect_quote_limit():
    record = _artifact()
    contract = record["source_capture_contract"]
    assert contract["raw_wire_bytes_captured"] is False
    assert contract["maximum_direct_quote_words_per_source"] == 25
    sources = record["sources"]
    assert len({source["source_id"] for source in sources}) == len(sources)
    for source in sources:
        assert source["url"].startswith("https://")
        assert source["retrieved_at_utc"] == record["captured_at_utc"]
        digest = source["excerpt_sha256"]
        if digest is None:
            assert source["excerpt"] is None
            assert source["source_id"] == "THE_XRP_INVESTOR_UNPARSED_DASHBOARD"
            continue
        assert re.fullmatch(r"[0-9a-f]{64}", digest)
        assert len(source["excerpt"].split()) <= 25
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == digest


def test_alpha_five_fund_zero_flow_is_not_a_universal_market_total():
    record = _artifact()
    alpha = next(s for s in record["sources"] if s["source_id"] == "ALPHA_FINANCE_XRP_ETF_DASHBOARD")
    claims = alpha["claims"]
    assert claims["fund_count"] == 5
    assert claims["nov6_net_flow_usd"] == 0
    assert set(claims["tickers"]) == {"XRP", "XRPZ", "XRPC", "GXRP", "TOXR"}
    assert "does not publish fund-level aum or holdings" in alpha["source_summary"].lower()
    assert "upstream flow source" in alpha["source_summary"].lower()


def test_cryptokeyhole_nov6_is_partial_and_xrpc_outflow_is_preserved():
    record = _artifact()
    source = next(s for s in record["sources"] if s["source_id"] == "CRYPTOKEYHOLE_XRP_ETF_FLOWS")
    claims = source["claims"]
    assert claims["nov6_status"] == "PARTIAL"
    assert claims["reporting_funds"] == 3
    assert claims["expected_daily_funds"] == 4
    assert claims["nov6_partial_net_flow_xrp"] == -752048
    assert claims["fund_flows_xrp"] == {"XRP": 0, "XRPC": -752048, "TOXR": 0, "XRPZ": None}
    assert claims["nov5_complete_net_flow_xrp"] == -3339


def test_cryptokeyhole_future_dated_issuer_label_is_quarantined():
    record = _artifact()
    source = next(s for s in record["sources"] if s["source_id"] == "CRYPTOKEYHOLE_XRP_ETF_FLOWS")
    assert "9 Nov 2026" in source["source_summary"]
    assert "future-date anomaly" in source["source_summary"].lower()
    assert any("future-dated" in item for item in source["limitations"])


def test_xrp_insights_aggregate_scope_and_vintage_are_explicit():
    record = _artifact()
    source = next(s for s in record["sources"] if s["source_id"] == "XRP_INSIGHTS_XRP_ETF_DATASET")
    claims = source["claims"]
    assert source["publisher_generated_at_utc"] == "2026-11-07T18:25:50.922Z"
    assert source["publisher_data_as_of"] == "2026-11-06"
    assert claims["nov6_net_flow_xrp"] == -663043
    assert claims["nov2_to_nov6_net_flow_xrp"] == -812529
    assert claims["total_holdings_xrp"] == 1195787657
    assert claims["tracked_universe"] == ["XRPC", "XRP", "XRPR", "XRPZ", "GXRP", "TOXR", "BITW"]


def test_xrp_insights_known_flow_exclusions_and_non_pure_spot_components_are_retained():
    record = _artifact()
    source = next(s for s in record["sources"] if s["source_id"] == "XRP_INSIGHTS_XRP_ETF_DATASET")
    summary = source["source_summary"].lower()
    assert "withholds gxrp flows" in summary
    assert "xrpr with partly indirect etp exposure" in summary
    assert "bitw whose xrp sleeve can change through index rebalancing" in summary
    assert "reconstructed historical rows" in summary


def test_aggregators_share_issuer_source_class_but_have_distinct_processing_lineage():
    record = _artifact()
    crypto = next(s for s in record["sources"] if s["source_id"] == "CRYPTOKEYHOLE_XRP_ETF_FLOWS")
    insights = next(s for s in record["sources"] if s["source_id"] == "XRP_INSIGHTS_XRP_ETF_DATASET")
    alpha = next(s for s in record["sources"] if s["source_id"] == "ALPHA_FINANCE_XRP_ETF_DASHBOARD")
    assert crypto["source_independence_group"] == "issuer_reported_holdings_aggregator_a"
    assert insights["source_independence_group"] == "issuer_reported_holdings_aggregator_b"
    assert crypto["upstream_lineage"] != insights["upstream_lineage"]
    assert "underlying issuers overlap" in crypto["upstream_lineage"].lower()
    assert "underlying issuers overlap" in insights["upstream_lineage"].lower()
    assert alpha["source_independence_group"] == "alpha_finance_upstream_undisclosed"


def test_provider_scope_reconciliation_does_not_average_or_select_a_winner():
    record = _artifact()
    scope = record["source_scope_reconciliation"]
    assert scope["no_comparable_universe_established"] is True
    assert "partial" in scope["cryptokeyhole"].lower()
    assert "five tickers" in scope["alpha_finance"].lower()
    assert "six spot etfs plus bitw" in scope["xrp_insights"].lower()
    assert "No. Public aggregators report materially different" in record["conclusion"]


def test_etf_flow_evidence_is_excluded_from_forecast_features_and_no_forecast_is_issued():
    record = _artifact()
    admission = record["admission"]
    assert admission["model_eligible"] is False
    assert admission["status"] == "EXCLUDED_UNRESOLVED_SCOPE_TIMESTAMP_AND_SOURCE_LINEAGE"
    assert "Directional model feature" in admission["prohibited_use"]
    assert record["forecast_status"] == "NOT_ISSUED"
    assert record["trade_status"] == "NO_TRADE"
