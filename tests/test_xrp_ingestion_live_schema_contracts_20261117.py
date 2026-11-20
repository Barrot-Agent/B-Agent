from __future__ import annotations

from datetime import datetime, timezone

import pytest

import barrot_agent.evolution.xrp_public_ingestion as ingestion


CAPTURED = datetime(2026, 11, 17, 23, 13, 33, tzinfo=timezone.utc)
CSV_COLUMNS = [
    "date", "ticker", "issuer", "xrp_holdings", "xrp_flow", "flow_usd",
    "flow_status", "aum_usd", "close_price_usd", "volume_shares",
    "volume_usd", "row_status",
]


def _xrp_insights_metadata(row_count: int) -> dict:
    return {
        "dataset": "XRP ETF Daily Holdings & Flows by Fund",
        "publisher": "XRP Insights",
        "generated_at": "2026-11-17T22:19:28.980Z",
        "data_as_of": "2026-11-16",
        "latest_row_date": "2026-11-16",
        "provisional_row_date": None,
        "coverage": {"rows": row_count},
        "funds": [{"ticker": "XRP", "issuer": "Bitwise"}],
        "columns": [{"name": name} for name in CSV_COLUMNS],
        "citation": "XRP Insights (xrp-insights.com), XRP ETF holdings & flows dataset",
        "license": {
            "name": "Free to use and cite with attribution; commercial redistribution requires written permission",
            "url": "https://xrp-insights.com/terms",
        },
    }


def test_xrp_insights_json_accepts_publisher_nested_fund_and_column_registries():
    source_id = "xrp_etf_flows_aggregator"
    payload = {"metadata": _xrp_insights_metadata(1), "data": []}
    records, source_as_of, eligible, reason = ingestion.PARSERS[source_id](
        payload,
        source_id=source_id,
        url=dict(ingestion.ENDPOINTS)[source_id],
        digest="a" * 64,
        captured=CAPTURED,
    )
    assert records == []
    assert source_as_of is None
    assert eligible is False
    assert "raw_only" in reason


def test_xrp_insights_csv_accepts_nested_metadata_and_blank_unavailable_price_volume_fields():
    source_id = "xrp_etf_flows_csv"
    metadata_payload = {"metadata": _xrp_insights_metadata(3)}
    csv_text = (
        ",".join(CSV_COLUMNS) + "\n"
        "2025-12-01,XRP,Bitwise,1000,,,initial,1000,,,,settled\n"
        "2025-12-02,XRP,Bitwise,1000,0,0,computed,1000,,,,settled\n"
        "2026-11-16,XRP,Bitwise,1000,0,0,computed,1000,1.00,10,10,settled\n"
    )
    records, source_as_of, eligible, reason = ingestion.PARSERS[source_id](
        {"csv_text": csv_text},
        source_id=source_id,
        url=dict(ingestion.ENDPOINTS)[source_id],
        digest="b" * 64,
        captured=CAPTURED,
        metadata_payload=metadata_payload,
    )
    assert len(records) == 1
    assert records[0]["latest_date_direct_spot_flow_xrp"] == 0
    assert records[0]["source_attribution"] == metadata_payload["metadata"]["citation"]
    assert records[0]["license_name"] == metadata_payload["metadata"]["license"]["name"]
    assert source_as_of is None
    assert eligible is False
    assert "hash_only_receipt" in records[0]["license_compliance"]
    assert "research_only_aggregate" in reason


def test_xrpr_issuer_parser_accepts_current_coinshares_physical_xrp_holding_label():
    source_id = "xrp_etf_xrpr_issuer_page"
    payload = {
        "html_text": (
            "<title>XRPR Price & NAV Today | REX-Osprey XRP ETF</title>"
            "<div>REX-Osprey</div><div>As of 11/16/2026</div>"
            "<div>CoinShares Physical XRP</div>"
        )
    }
    records, source_as_of, eligible, reason = ingestion.PARSERS[source_id](
        payload,
        source_id=source_id,
        url=dict(ingestion.ENDPOINTS)[source_id],
        digest="c" * 64,
        captured=CAPTURED,
    )
    assert records == []
    assert source_as_of is None
    assert eligible is False
    assert "raw_only" in reason


def test_bitwise_issuer_uses_canonical_non_redirecting_official_url():
    source_id = "xrp_etf_bitwise_issuer_page"
    assert dict(ingestion.ENDPOINTS)[source_id] == (
        "https://www.bitwiseetfs.com/single-asset/xrp"
    )
    assert "www.bitwiseetfs.com" in ingestion.ALLOWED_HOSTS
    assert "bitxrpetf.com" not in ingestion.ALLOWED_HOSTS


def test_morpho_liquidity_accepts_documented_response_without_identity_echo():
    source_id = "morpho_cbxrp_market_liquidity"
    payload = {
        "data": {
            "market_liquidity": "1000000",
            "reallocatable_liquidity": "200000",
            "borrow_amount_to_target_utilization": "1200000",
            "last_indexed_block": "40000000",
        }
    }
    records, source_as_of, eligible, reason = ingestion.PARSERS[source_id](
        payload,
        source_id=source_id,
        url=dict(ingestion.ENDPOINTS)[source_id],
        digest="d" * 64,
        captured=CAPTURED,
    )
    assert records == []
    assert source_as_of is None
    assert eligible is False
    assert "raw_only" in reason


def test_morpho_liquidity_rejects_a_different_market_path():
    source_id = "morpho_cbxrp_market_liquidity"
    payload = {
        "data": {
            "market_liquidity": "1000000",
            "reallocatable_liquidity": "200000",
            "borrow_amount_to_target_utilization": "1200000",
            "last_indexed_block": "40000000",
        }
    }
    wrong_url = (
        "https://api.morpho.org/v0/blue/markets/8453:0x"
        + "0" * 64
        + "/liquidity"
    )
    with pytest.raises(ingestion.XRPIngestionError, match="endpoint URL"):
        ingestion.PARSERS[source_id](
            payload,
            source_id=source_id,
            url=wrong_url,
            digest="e" * 64,
            captured=CAPTURED,
        )


def test_source_processing_failure_records_sanitized_parser_detail():
    failure = ingestion._source_failure_record(
        "xrp_etf_flows_aggregator",
        "https://xrp-insights.com/data/xrp-etf-flows.json",
        CAPTURED.isoformat(),
        ingestion.XRPIngestionError("  XRP Insights   metadata identity mismatch  "),
    )
    assert failure["error_category"] == "source_processing_error"
    assert failure["failure_detail"] == "XRP Insights metadata identity mismatch"


def test_provider_http_failure_uses_provider_reason_not_parser_detail():
    failure = ingestion._source_failure_record(
        "bybit_spot_ticker",
        "https://api.bybit.com/v5/market/tickers?category=spot&symbol=XRPUSDT",
        CAPTURED.isoformat(),
        ingestion.XRPSourceHTTPError("bybit_spot_ticker", 403, "Forbidden"),
    )
    assert failure["http_status_code"] == 403
    assert failure["provider_reason"] == "Forbidden"
    assert "failure_detail" not in failure



def test_xrp_insights_csv_rejects_partial_price_volume_fields():
    source_id = "xrp_etf_flows_csv"
    metadata_payload = {"metadata": _xrp_insights_metadata(1)}
    csv_text = (
        ",".join(CSV_COLUMNS) + "\n"
        "2026-11-16,XRP,Bitwise,1000,0,0,computed,1000,1.00,,10,settled\n"
    )
    with pytest.raises(ingestion.XRPIngestionError, match="all present or all blank"):
        ingestion.PARSERS[source_id](
            {"csv_text": csv_text},
            source_id=source_id,
            url=dict(ingestion.ENDPOINTS)[source_id],
            digest="f" * 64,
            captured=CAPTURED,
            metadata_payload=metadata_payload,
        )
