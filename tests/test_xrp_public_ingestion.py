from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

import pytest
from io import BytesIO
from urllib.error import HTTPError

import barrot_agent.evolution.xrp_public_ingestion as xrp_ingestion
from barrot_agent.evolution.feature_store import HistoricalFeatureStore
from barrot_agent.evolution.xrp_public_ingestion import (
    RawReceiptArchive,
    _normalize_walk_forward_horizons,
    _walk_forward_report,
    _coinbase_candle_backfill_ranges,
    XRPIngestionError,
    XRPSourceHTTPError,
    _source_failure_record,
    fetch_public_json,
    fetch_public_csv,
    fetch_public_html,
    fetch_public_rpc,
    _open_public_request,
    _default_public_fetcher,
    run_ingestion,
    ALLOWED_HOSTS,
    BITBANK_SOURCE_IDS,
    ENDPOINTS,
    SCHEDULED_ENDPOINTS,
    WEEKLY_ENDPOINTS,
    _weekly_endpoints_for_capture,
    PARSERS,
    XRPL_NODE_SOURCES,
    _reconcile_xrpl_node_records,
    _bitbank_transactions_research_summary,
)


def _iso_ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def _fake_fetcher(captured: datetime):
    captured_ms = _iso_ms(captured)

    def fetcher(source_id: str, url: str):
        http_date = format_datetime(captured - timedelta(seconds=5), usegmt=True)
        if source_id == "binance_spot_ticker":
            payload = {
                "symbol": "XRPUSDT",
                "closeTime": captured_ms - 1000,
                "lastPrice": "1.29",
                "bidPrice": "1.2899",
                "askPrice": "1.2901",
                "bidQty": "1000",
                "askQty": "900",
                "volume": "1000000",
                "quoteVolume": "1290000",
                "weightedAvgPrice": "1.28",
            }
        elif source_id == "binance_spot_klines":
            payload = [
                [captured_ms - 7200000, "1.20", "1.30", "1.19", "1.27", "1000", captured_ms - 3600001, "1270", 25, "500", "635", "0"],
                [captured_ms, "1.29", "1.31", "1.28", "1.30", "100", captured_ms + 3599999, "130", 5, "50", "65", "0"],
            ]
        elif source_id == "binance_perp_premium":
            payload = {
                "symbol": "XRPUSDT",
                "time": captured_ms - 2000,
                "markPrice": "1.291",
                "indexPrice": "1.290",
                "lastFundingRate": "0.0001",
                "nextFundingTime": captured_ms + 8 * 3600000,
            }
        elif source_id == "binance_perp_open_interest":
            payload = {"symbol": "XRPUSDT", "time": captured_ms - 3000, "openInterest": "2500000"}
        elif source_id == "binance_perp_funding_history":
            payload = [
                {"symbol": "XRPUSDT", "fundingRate": "-0.0002", "fundingTime": captured_ms - 9 * 3600000, "markPrice": "1.280"},
                {"symbol": "XRPUSDT", "fundingRate": "0.0001", "fundingTime": captured_ms - 3600000, "markPrice": "1.290"},
            ]
        elif source_id == "binance_perp_open_interest_history":
            payload = [
                {"symbol": "XRPUSDT", "sumOpenInterest": "2500000", "sumOpenInterestValue": "3225000", "timestamp": captured_ms - 7200000},
                {"symbol": "XRPUSDT", "sumOpenInterest": "2510000", "sumOpenInterestValue": "3247900", "timestamp": captured_ms - 3600000},
            ]
        elif source_id == "binance_perp_global_long_short_ratio":
            payload = [
                {"symbol": "XRPUSDT", "longShortRatio": "1.25", "longAccount": "0.5556", "shortAccount": "0.4444", "timestamp": captured_ms - 7200000},
                {"symbol": "XRPUSDT", "longShortRatio": "1.20", "longAccount": "0.5455", "shortAccount": "0.4545", "timestamp": captured_ms - 3600000},
            ]
        elif source_id == "coinbase_spot_ticker":
            payload = {
                "trade_id": 123456,
                "price": "1.2900",
                "size": "125",
                "time": (captured - timedelta(seconds=6)).isoformat().replace("+00:00", "Z"),
                "bid": "1.2899",
                "ask": "1.2901",
                "volume": "500000",
            }
        elif source_id == "coinbase_spot_candles":
            captured_seconds = int(captured.timestamp())
            payload = [
                [captured_seconds - 7200, "1.20", "1.30", "1.21", "1.27", "1000"],
                [captured_seconds - 3600, "1.25", "1.31", "1.27", "1.30", "1200"],
                [captured_seconds, "1.29", "1.31", "1.30", "1.30", "100"],
            ]
        elif source_id == "coinbase_spot_book":
            payload = {
                "sequence": 123456,
                "bids": [["1.289", "1000", 3]],
                "asks": [["1.291", "1200", 2]],
            }
        elif source_id == "kraken_spot_ticker":
            payload = {
                "error": [],
                "result": {
                    "XXRPZUSD": {
                        "a": ["1.291", "100", "100"],
                        "b": ["1.289", "200", "200"],
                        "c": ["1.290", "12.5"],
                        "v": ["100000", "200000"],
                        "p": ["1.28", "1.27"],
                        "t": [1000, 2000],
                        "l": ["1.20", "1.19"],
                        "h": ["1.30", "1.31"],
                        "o": "1.25",
                    }
                },
            }
        elif source_id == "kraken_spot_depth":
            ts = captured.timestamp() - 1800
            payload = {
                "error": [],
                "result": {
                    "XXRPZUSD": {
                        "bids": [["1.289", "1000", str(ts)], ["1.288", "2000", str(ts)]],
                        "asks": [["1.291", "1200", str(ts)], ["1.292", "1800", str(ts)]],
                    }
                },
            }
        elif source_id == "okx_spot_ticker":
            payload = {
                "code": "0",
                "msg": "",
                "data": [{
                    "instId": "XRP-USDT",
                    "last": "1.2900",
                    "lastSz": "125",
                    "askPx": "1.2901",
                    "askSz": "900",
                    "bidPx": "1.2899",
                    "bidSz": "1000",
                    "open24h": "1.28",
                    "high24h": "1.31",
                    "low24h": "1.27",
                    "volCcy24h": "1290000",
                    "vol24h": "1000000",
                    "ts": str(captured_ms - 1000),
                }],
            }
        elif source_id == "okx_spot_depth":
            payload = {
                "code": "0",
                "msg": "",
                "data": [{
                    "asks": [["1.291", "1200", "0", "2"], ["1.292", "1800", "0", "3"]],
                    "bids": [["1.289", "1000", "0", "3"], ["1.288", "2000", "0", "2"]],
                    "ts": str(captured_ms - 2000),
                    "seqId": "123456",
                    "checksum": 123456,
                }],
            }
        elif source_id == "bybit_spot_ticker":
            payload = {
                "retCode": 0,
                "retMsg": "OK",
                "result": {
                    "category": "spot",
                    "list": [{
                        "symbol": "XRPUSDT",
                        "lastPrice": "1.2900",
                        "bid1Price": "1.2899",
                        "bid1Size": "1000",
                        "ask1Price": "1.2901",
                        "ask1Size": "900",
                        "prevPrice24h": "1.2800",
                        "highPrice24h": "1.3100",
                        "lowPrice24h": "1.2700",
                        "turnover24h": "1290000",
                        "volume24h": "1000000",
                    }],
                },
                "time": captured_ms - 1000,
            }
        elif source_id == "bybit_spot_depth":
            payload = {
                "retCode": 0,
                "retMsg": "OK",
                "result": {
                    "s": "XRPUSDT",
                    "a": [["1.291", "1200"], ["1.292", "1800"]],
                    "b": [["1.289", "1000"], ["1.288", "2000"]],
                    "ts": captured_ms - 1500,
                    "u": 123456,
                    "seq": 987654,
                    "cts": captured_ms - 2000,
                },
                "time": captured_ms - 1000,
            }
        elif source_id == "bybit_linear_ticker":
            payload = {
                "retCode": 0,
                "retMsg": "OK",
                "result": {
                    "category": "linear",
                    "list": [{
                        "symbol": "XRPUSDT",
                        "lastPrice": "1.290",
                        "markPrice": "1.291",
                        "indexPrice": "1.290",
                        "prevPrice24h": "1.280",
                        "price24hPcnt": "0.0078",
                        "highPrice24h": "1.310",
                        "lowPrice24h": "1.270",
                        "openInterest": "2500000",
                        "singleOpenInterest": "1250000",
                        "openInterestValue": "3225000",
                        "singleOpenInterestValue": "1612500",
                        "volume24h": "1000000",
                        "turnover24h": "1290000",
                        "fundingRate": "0.0001",
                        "nextFundingTime": captured_ms + 8 * 3600000,
                        "fundingIntervalHour": "8",
                        "bid1Price": "1.2899",
                        "ask1Price": "1.2901",
                        "bid1Size": "1000",
                        "ask1Size": "900",
                    }],
                },
                "time": captured_ms - 2000,
            }
        elif source_id == "bybit_linear_open_interest":
            payload = {
                "retCode": 0,
                "retMsg": "OK",
                "result": {
                    "category": "linear",
                    "symbol": "XRPUSDT",
                    "list": [
                        {"openInterest": "2510000", "singleOpenInterest": "1255000", "timestamp": captured_ms - 3600000},
                        {"openInterest": "2500000", "singleOpenInterest": "1250000", "timestamp": captured_ms - 7200000},
                    ],
                    "nextPageCursor": "next-page",
                },
                "time": captured_ms - 1000,
            }
        elif source_id == "bybit_linear_funding_history":
            payload = {
                "retCode": 0,
                "retMsg": "OK",
                "result": {
                    "category": "linear",
                    "list": [
                        {"symbol": "XRPUSDT", "fundingRate": "0.0001", "fundingRateTimestamp": captured_ms - 3600000},
                        {"symbol": "XRPUSDT", "fundingRate": "-0.0002", "fundingRateTimestamp": captured_ms - 6 * 3600000},
                    ],
                },
                "time": captured_ms - 1000,
            }
        elif source_id == "bitbank_spot_circuit_break":
            payload = {
                "success": 1,
                "data": {
                    "mode": "NONE",
                    "estimated_itayose_price": None,
                    "estimated_itayose_amount": None,
                    "fee_type": "NORMAL",
                    "timestamp": captured_ms - 500,
                },
            }
        elif source_id == "bitbank_spot_transactions":
            payload = {
                "success": 1,
                "data": {
                    "transactions": [
                        {"transaction_id": 101, "side": "buy", "price": "180.15", "amount": "100", "executed_at": captured_ms - 4000},
                        {"transaction_id": 102, "side": "sell", "price": "180.10", "amount": "60", "executed_at": captured_ms - 3000},
                    ]
                },
            }
        elif source_id == "bitbank_spot_ticker":
            payload = {
                "success": 1,
                "data": {
                    "sell": "180.2",
                    "buy": "180.1",
                    "high": "185.0",
                    "low": "175.0",
                    "open": "182.0",
                    "last": "180.15",
                    "vol": "250000",
                    "timestamp": captured_ms - 1000,
                },
            }
        elif source_id == "bitbank_spot_depth":
            payload = {
                "success": 1,
                "data": {
                    "asks": [["180.2", "1000"], ["180.3", "1500"]],
                    "bids": [["180.1", "900"], ["180.0", "1100"]],
                    "asks_over": "0",
                    "bids_under": "0",
                    "asks_under": "0",
                    "bids_over": "0",
                    "ask_market": "0",
                    "bid_market": "0",
                    "timestamp": captured_ms - 2000,
                    "sequenceId": "123456",
                },
            }
        elif source_id == "binance_spot_depth":
            payload = {
                "lastUpdateId": 123456,
                "bids": [["1.289", "1000"]],
                "asks": [["1.291", "1200"]],
            }
        elif source_id == "xrp_exchange_balances_json":
            payload = {
                "dataset": "XRP Exchange Balances (attributed exchange wallets)",
                "publisher": "XRP Insights",
                "url": "https://xrp-insights.com/exchange-balances",
                "license": "Free to cite with attribution to xrp-insights.com",
                "citation": "XRP Insights, xrp-insights.com/exchange-balances",
                "definition": "XRP held in XRP Ledger wallets publicly attributed to tracked exchanges (hot, deposit and cold wallets). Not an estimate of tradable float.",
                "methodology": "Balances: rippled account_info on the validated ledger for every tracked wallet, daily at ~08:00 UTC. Attribution: XRPSCAN public labels only (XRPSCAN balances are never used).",
            }
        elif source_id in XRPL_NODE_SOURCES:
            payload = {
                "result": {
                    "info": {
                        "server_state": "full",
                        "validated_ledger": {
                            "age": 5,
                            "base_fee_xrp": 0.00001,
                            "hash": "A" * 64,
                            "reserve_base_xrp": 1,
                            "reserve_inc_xrp": 0.2,
                            "seq": 108123456,
                        },
                    }
                },
                "status": "success",
                "type": "response",
            }
        elif source_id == "xrp_etf_flows_aggregator":
            payload = {
                "metadata": {
                    "dataset": "XRP ETF Daily Holdings & Flows by Fund",
                    "publisher": "XRP Insights",
                    "generated_at": captured.isoformat().replace("+00:00", "Z"),
                    "data_as_of": "2026-11-03",
                    "latest_row_date": "2026-11-03",
                    "provisional_row_date": None,
                    "coverage": {"rows": 3},
                },
                "license": {
                    "name": "Free to use and cite with attribution; commercial redistribution requires written permission",
                    "url": "https://xrp-insights.com/terms",
                },
                "citation": "XRP Insights (xrp-insights.com), XRP ETF holdings & flows dataset",
                "funds": [
                    {"ticker": "XRP", "issuer": "Bitwise"},
                    {"ticker": "BITW", "issuer": "Bitwise"},
                    {"ticker": "XRPC", "issuer": "Canary Capital"},
                ],
                "columns": [
                    {"name": "date"}, {"name": "ticker"}, {"name": "issuer"},
                    {"name": "xrp_holdings"}, {"name": "xrp_flow"}, {"name": "flow_usd"},
                    {"name": "flow_status"}, {"name": "aum_usd"}, {"name": "close_price_usd"},
                    {"name": "volume_shares"}, {"name": "volume_usd"}, {"name": "row_status"},
                ],
            }
        elif source_id == "xrp_etf_flows_csv":
            csv_text = (
                "date,ticker,issuer,xrp_holdings,xrp_flow,flow_usd,flow_status,aum_usd,"
                "close_price_usd,volume_shares,volume_usd,row_status\n"
                "2026-11-03,XRP,Bitwise,1000,-10,-12.9,computed,1290,1.29,100,129,settled\n"
                "2026-11-03,BITW,Bitwise,200,5,6.45,computed,258,1.29,50,64.5,settled\n"
                "2026-11-03,XRPC,Canary Capital,100,,,initial,129,1.29,10,12.9,settled\n"
            )
            return {
                "raw_bytes": csv_text.encode("utf-8"),
                "payload": {"csv_text": csv_text},
                "http_date": http_date,
            }
        elif source_id in {
            "xrp_etf_xrpr_issuer_page",
            "xrp_etf_bitwise_issuer_page",
            "xrp_etf_grayscale_gxrp_issuer_page",
            "xrp_etf_franklin_xrpz_issuer_page",
            "xrp_etf_canary_xrpc_issuer_page",
            "xrp_etf_21shares_toxr_issuer_page",
            "ripple_rlusd_transparency_dashboard",
            "xrpldashboard_rlusd_cross_chain_supply",
            "circle_usdc_transparency_dashboard",
            "cftc_tff_financial_futures",
        }:
            html_by_source = {
                "xrp_etf_xrpr_issuer_page": "<html><title>REX-Osprey XRP ETF XRPR</title><p>As of 11/03/2026</p><table><tr><td>CoinShares XRP ETP</td></tr></table></html>",
                "xrp_etf_bitwise_issuer_page": "<html><title>Bitwise XRP ETF</title><p>Data as of 11/03/2026</p><td>XRP in Trust</td><td>Digital Asset Custodian</td></html>",
                "xrp_etf_grayscale_gxrp_issuer_page": "<html><title>Grayscale XRP Trust ETF</title><p>As of 11/04/2026</p><td>TOTAL XRP IN FUND</td><td>DIGITAL ASSET CUSTODIAN</td></html>",
                "xrp_etf_franklin_xrpz_issuer_page": "<html><title>Franklin XRP ETF XRPZ</title><p>XRP in Fund</p><p>As of 09/04/2026</p></html>",
                "xrp_etf_canary_xrpc_issuer_page": "<html><title>Canary XRP ETF XRPC</title><h2>Holdings</h2><p>As of 10/19/2026</p></html>",
                "xrp_etf_21shares_toxr_issuer_page": "<html><title>21shares XRP ETF TOXR</title><h2>Holdings</h2><p>Value as of September 17, 2026</p></html>",
                "ripple_rlusd_transparency_dashboard": "<html><title>Ripple USD Transparency</title><h1>Ripple USD (RLUSD)</h1><h2>Total Circulating RLUSD</h2><p>RLUSD Reserve Funds</p><p>As of 11/05/2026</p></html>",
                "xrpldashboard_rlusd_cross_chain_supply": "<html><title>RLUSD cross-chain supply</title><h1>RLUSD</h1><p>Ethereum</p><p>XRP Ledger</p><p>Snapshot</p></html>",
                "circle_usdc_transparency_dashboard": "<html><title>Transparency and stability</title><h1>USDC</h1><p>EURC</p><p>Reserves</p><p>As of Nov 05, 2026</p></html>",
                "cftc_tff_financial_futures": """<html><title>CFTC Traders in Financial Futures</title><pre>
Traders in Financial Futures - Futures Only Positions as of November 3, 2026
XRP - CHICAGO MERCANTILE EXCHANGE (Contracts of 50,000 XRP)
CFTC Code #176740 Open Interest is 7,216
Positions
4,228 4,431 17 868 802 21 1,976 1,696 22 0 0 0 84 227
Changes from: October 27, 2026 Total Change is: -845
163 -210 0 -53 36 20 -410 -258 -501 0 0 0 -64 68
NANO XRP - COINBASE DERIVATIVES, LLC (500 XRP x $2.00 = $1000)
CFTC Code #176LM1 Open Interest is 32,505
Positions
0 0 0 0 0 0 29,317 31,625 120 2,693 601 0 375 159
Changes from: October 27, 2026 Total Change is: -32,864
0 0 0 0 0 0 -26,142 -28,053 -4,911 -1,607 28 0 -204 72
NANO XRP PERP STYLE - COINBASE DERIVATIVES, LLC (500 XRP x $2.00 = $1000)
CFTC Code #176LM3 Open Interest is 38,392
Positions
0 0 0 0 0 0 1,780 29,554 0 28,858 2,853 0 7,754 5,985
Changes from: October 27, 2026 Total Change is: -465
0 0 0 0 0 0 82 -1,313 0 -1,217 753 0 670 95
</pre></html>""",
            }
            html_text = html_by_source[source_id]
            return {
                "raw_bytes": html_text.encode("utf-8"),
                "payload": {"html_text": html_text},
                "http_date": "Fri, 06 Nov 2026 20:30:00 GMT",
            }
        else:
            raise AssertionError(source_id)
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        response = {"raw_bytes": raw, "payload": payload}
        if source_id in {"coinbase_spot_ticker", "kraken_spot_ticker", "kraken_spot_depth", "xrp_exchange_balances_json"} or source_id in XRPL_NODE_SOURCES or source_id in BITBANK_SOURCE_IDS:
            response["http_date"] = http_date
        return response

    return fetcher


def test_raw_receipt_archive_is_content_addressed_and_write_once(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    raw = b'{"x":1}'
    first = archive.store(
        source_id="test",
        source_uri="https://api.binance.com/test",
        captured_at_utc="2026-11-04T12:00:00.000000Z",
        raw_bytes=raw,
        source_data_as_of_utc="2026-11-04T11:59:59.000000Z",
        model_eligible=True,
        source_http_date="Thu, 05 Nov 2026 12:00:00 GMT",
    )
    path = tmp_path / first["raw_payload_path"]
    assert path.read_bytes() == raw
    assert first["raw_content_sha256"] == hashlib.sha256(raw).hexdigest()
    assert first["source_http_date"] == "Thu, 05 Nov 2026 12:00:00 GMT"
    assert len(first["receipt_id"]) == 64

    second = archive.store(
        source_id="test",
        source_uri="https://api.binance.com/test",
        captured_at_utc="2026-11-04T12:00:00.000000Z",
        raw_bytes=raw,
        source_data_as_of_utc="2026-11-04T11:59:59.000000Z",
        model_eligible=True,
        source_http_date="Thu, 05 Nov 2026 12:00:01 GMT",
    )
    assert second["raw_content_sha256"] == first["raw_content_sha256"]
    assert second["receipt_id"] != first["receipt_id"]
    assert second["source_http_date"] == "Thu, 05 Nov 2026 12:00:01 GMT"
    assert len(archive.receipts_path.read_text(encoding="utf-8").splitlines()) == 2

    path.write_bytes(b'{"x":2}')
    with pytest.raises(XRPIngestionError, match="tampering"):
        archive.store(
            source_id="test",
            source_uri="https://api.binance.com/test",
            captured_at_utc="2026-11-04T12:00:02.000000Z",
            raw_bytes=raw,
            source_data_as_of_utc="2026-11-04T11:59:59.000000Z",
            model_eligible=True,
        )


def test_fetcher_rejects_non_allowlisted_hosts_without_network():
    with pytest.raises(XRPIngestionError, match="allowlisted"):
        fetch_public_json("bad", "https://example.com/public.json")
    with pytest.raises(XRPIngestionError, match="allowlisted"):
        fetch_public_json("bad", "http://api.binance.com/api/v3/ticker/24hr")


def test_public_ingestion_builds_verified_point_in_time_snapshot_and_preserves_backfill_receipt(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    summary = run_ingestion(tmp_path / "run", fetcher=_fake_fetcher(captured), now=captured)

    assert summary["snapshot_status"] == "verified", (
        summary,
        (tmp_path / "run" / "snapshot_blocked.json").read_text(encoding="utf-8")
        if (tmp_path / "run" / "snapshot_blocked.json").exists()
        else None,
        (tmp_path / "run" / "source_failures.json").read_text(encoding="utf-8"),
    )
    assert summary["forecast_status"] == "NOT_ISSUED"
    assert summary["forecast_model_eligible"] is False
    walk_forward = json.loads((tmp_path / "run" / "walk_forward.json").read_text(encoding="utf-8"))
    assert any(
        "rolling temporal temperature scaling" in item.lower()
        and "independent shadow evaluation" in item.lower()
        for item in walk_forward["limitations"]
    )
    assert any(
        "rolling temporal temperature scaling" in item.lower()
        and "trained predictive model" in item.lower()
        and "independent shadow evaluation" in item.lower()
        for item in summary["limitations"]
    )
    assert summary["coinbase_backfill"]["status"] == "NOT_REQUESTED"
    assert summary["coinbase_backfill"]["pages_requested"] == 0
    assert summary["source_receipt_count"] == len(SCHEDULED_ENDPOINTS) + len(_weekly_endpoints_for_capture(captured)), (
        summary,
        (tmp_path / "run" / "source_failures.json").read_text(encoding="utf-8"),
    )
    assert summary["source_failure_count"] == 0
    assert summary["eligible_feature_record_count"] > 0
    assert summary["store_verification"]["valid"] is True
    assert summary["feature_store_backup_retention_days"] == 90
    assert summary["feature_store_backup_frequency"] == "daily_plus_manual_dispatch"
    assert summary["feature_store_checkpoint_retention_days"] == 7
    assert summary["feature_store_checkpoint_frequency"] == "every_ingestion_run"
    assert summary["feature_store_restore_strategy"] == "exact_cache_key_then_latest_per_run_checkpoint_then_daily_archive"
    assert summary["feature_store_restore_search_max_pages"] == 30
    assert summary["xrpl_node_reconciliation"]["status"] == "NOT_COLLECTED_PROVIDER_TERMS_POLICY"
    assert summary["xrpl_node_reconciliation"]["model_admission_allowed"] is False
    assert summary["collection_policy"]["noncommercial_xrpl_nodes_included"] is False
    assert summary["weekly_source_policy"]["captured_source_ids"] == []
    assert summary["weekly_source_policy"]["skipped_source_ids"] == ["cftc_tff_financial_futures"]
    assert set(summary["collection_policy"]["excluded_noncommercial_xrpl_node_source_ids"]) == set(XRPL_NODE_SOURCES)

    snapshot = json.loads((tmp_path / "run" / "snapshot.json").read_text(encoding="utf-8"))
    historical = next(
        item for item in snapshot["records"]
        if item["feature_id"] == "xrp.spot.binance.1h.close_price"
    )
    assert historical["event_time_utc"] < historical["known_at_utc"]
    assert historical["known_at_utc"] == "2026-11-04T12:30:00.000000Z"
    assert "first observed at this capture time" in historical["limitations"][0]

    assert summary["adapter_version"] == "xrp-public-market-v3.20"
    assert summary["parser_version"] == "xrp-public-market-v3.19"
    assert any(item["feature_id"] == "xrp.spot.coinbase.last_price" for item in snapshot["records"])
    coinbase_closes = [
        item for item in snapshot["records"]
        if item["feature_id"] == "xrp.spot.coinbase.1h.close_price"
    ]
    assert len(coinbase_closes) == 2
    assert all(item["event_time_utc"] < item["known_at_utc"] for item in coinbase_closes)
    assert any(item["feature_id"] == "xrp.spot.kraken.orderbook.mid_price" for item in snapshot["records"])
    assert any(item["feature_id"] == "xrp.spot.okx.last_price" and item["unit"] == "USDT/XRP" for item in snapshot["records"])
    assert any(item["feature_id"] == "xrp.spot.okx.orderbook.mid_price" and item["model_eligible"] is True for item in snapshot["records"])
    assert any(item["feature_id"] == "xrp.spot.bybit.last_price" and item["model_eligible"] is True for item in snapshot["records"])
    assert any(item["feature_id"] == "xrp.spot.bybit.orderbook.mid_price" and item["model_eligible"] is True for item in snapshot["records"])
    assert not any(item["feature_id"].startswith("xrp.network.xrpl.") for item in snapshot["records"])
    historical_derivatives = [
        item for item in snapshot["records"]
        if item["feature_id"].startswith("xrp.perpetual.binance.1h.")
        or item["feature_id"] == "xrp.perpetual.binance.funding_rate"
    ]
    assert historical_derivatives
    assert all(item["known_at_utc"] == "2026-11-04T12:30:00.000000Z" for item in historical_derivatives)
    assert all(item["event_time_utc"] < item["known_at_utc"] for item in historical_derivatives)
    assert any(item["feature_id"] == "xrp.perpetual.binance.1h.open_interest_value" and item["unit"] == "USDT" for item in historical_derivatives)
    assert any(item["feature_id"] == "xrp.perpetual.binance.1h.global_long_short_account_ratio" for item in historical_derivatives)
    assert any(item["feature_id"] == "xrp.perpetual.binance.funding_rate" and item["value"] < 0 for item in historical_derivatives)

    raw_only = json.loads((tmp_path / "run" / "raw_only_sources.json").read_text(encoding="utf-8"))
    assert any(item["source_id"] == "binance_spot_depth" for item in raw_only)
    assert any(item["source_id"] == "coinbase_spot_book" for item in raw_only)
    assert not any(item["source_id"] == "okx_spot_depth" for item in raw_only)
    assert any(item["source_id"] == "xrp_etf_flows_aggregator" for item in raw_only)
    assert any(item["source_id"] == "xrp_exchange_balances_json" for item in raw_only)
    assert any(item["source_id"] == "xrp_etf_flows_csv" for item in raw_only)
    assert any(item["source_id"] == "xrp_etf_xrpr_issuer_page" for item in raw_only)
    assert any(item["source_id"] == "xrp_etf_bitwise_issuer_page" for item in raw_only)
    assert any(item["source_id"] == "xrp_etf_grayscale_gxrp_issuer_page" for item in raw_only)
    assert any(item["source_id"] == "xrp_etf_franklin_xrpz_issuer_page" for item in raw_only)
    assert any(item["source_id"] == "xrp_etf_canary_xrpc_issuer_page" for item in raw_only)
    assert any(item["source_id"] == "xrp_etf_21shares_toxr_issuer_page" for item in raw_only)
    assert any(item["source_id"] == "ripple_rlusd_transparency_dashboard" for item in raw_only)
    assert any(item["source_id"] == "xrpldashboard_rlusd_cross_chain_supply" for item in raw_only)
    assert any(item["source_id"] == "circle_usdc_transparency_dashboard" for item in raw_only)
    receipts = json.loads((tmp_path / "run" / "receipt_manifest.json").read_text(encoding="utf-8"))
    manifest = {item["source_id"]: item for item in receipts}
    # The default/scheduled collector must not request non-commercial public-node endpoints.
    assert not set(XRPL_NODE_SOURCES).intersection(manifest)
    assert manifest["xrp_etf_flows_aggregator"]["model_eligible_source"] is False
    assert manifest["xrp_etf_flows_aggregator"]["source_data_as_of_utc"] is None
    assert manifest["xrp_exchange_balances_json"]["model_eligible_source"] is False
    assert manifest["xrp_exchange_balances_json"]["source_data_as_of_utc"] is None

    for source_id in (
        "ripple_rlusd_transparency_dashboard",
        "xrpldashboard_rlusd_cross_chain_supply",
        "circle_usdc_transparency_dashboard",
    ):
        assert manifest[source_id]["model_eligible_source"] is False
        assert manifest[source_id]["source_data_as_of_utc"] is None
    assert manifest["xrp_exchange_balances_json"]["raw_bytes_retained"] is False
    assert manifest["xrp_exchange_balances_json"]["raw_payload_path"] is None
    for source_id in ("xrp_etf_franklin_xrpz_issuer_page", "xrp_etf_canary_xrpc_issuer_page", "xrp_etf_21shares_toxr_issuer_page"):
        assert manifest[source_id]["model_eligible_source"] is False
        assert manifest[source_id]["source_data_as_of_utc"] is None
        assert len(manifest[source_id]["raw_content_sha256"]) == 64
        assert manifest[source_id]["raw_bytes_retained"] is False
        assert manifest[source_id]["raw_payload_path"] is None
        assert "redistribution" in manifest[source_id]["raw_retention_reason"]
    assert "attribution" in manifest["xrp_exchange_balances_json"]["raw_retention_reason"]
    assert manifest["xrp_etf_flows_csv"]["model_eligible_source"] is False
    assert manifest["xrp_etf_flows_csv"]["source_data_as_of_utc"] is None
    assert len(manifest["xrp_etf_flows_csv"]["raw_content_sha256"]) == 64
    assert manifest["xrp_etf_flows_csv"]["raw_bytes_retained"] is False
    assert manifest["xrp_etf_flows_csv"]["raw_payload_path"] is None
    assert "commercial redistribution" in manifest["xrp_etf_flows_csv"]["raw_retention_reason"]
    research_only = json.loads((tmp_path / "run" / "research_only_observations.json").read_text(encoding="utf-8"))
    assert research_only["model_eligible"] is False
    assert research_only["observation_count"] == 2
    bitbank = next(
        item for item in research_only["observations"]
        if item["source_id"] == "bitbank_spot_transactions"
    )
    assert bitbank["observation_type"] == "bitbank_latest_60_trade_sample"
    assert bitbank["trade_count"] == 2
    assert bitbank["net_taker_flow_xrp"] == 40.0
    assert bitbank["model_eligible"] is False
    assert len(bitbank["raw_content_sha256"]) == 64
    assert bitbank["receipt_id"] == manifest["bitbank_spot_transactions"]["receipt_id"]
    aggregate = next(
        item for item in research_only["observations"]
        if item["source_id"] == "xrp_etf_flows_csv"
    )
    assert aggregate["data_as_of"] == "2026-11-03"
    assert aggregate["latest_date_direct_spot_holdings_xrp"] == 1100
    assert aggregate["latest_date_direct_spot_flow_xrp"] == -10
    assert aggregate["latest_date_index_sleeve_holdings_xrp"] == 200
    assert aggregate["latest_date_index_sleeve_flow_xrp"] == 5
    assert aggregate["model_eligible"] is False
    assert aggregate["raw_bytes_retained"] is False
    assert len(aggregate["raw_content_sha256"]) == 64
    assert aggregate["receipt_id"] == manifest["xrp_etf_flows_csv"]["receipt_id"]
    assert not any("etf" in item["feature_id"] for item in snapshot["records"])
    assert manifest["xrp_etf_xrpr_issuer_page"]["model_eligible_source"] is False
    assert manifest["xrp_etf_xrpr_issuer_page"]["source_data_as_of_utc"] is None
    for source_id in ("xrp_etf_bitwise_issuer_page", "xrp_etf_grayscale_gxrp_issuer_page"):
        assert manifest[source_id]["model_eligible_source"] is False
        assert manifest[source_id]["source_data_as_of_utc"] is None
    for source_id in ("binance_perp_funding_history", "binance_perp_open_interest_history", "binance_perp_global_long_short_ratio"):
        assert manifest[source_id]["model_eligible_source"] is True
        assert len(manifest[source_id]["raw_content_sha256"]) == 64
    assert all(len(item["raw_content_sha256"]) == 64 for item in receipts)
    assert (tmp_path / "run" / "feature_store.sqlite3").exists()


def test_stale_live_sources_are_excluded_but_historical_backfill_remains_known_at_capture(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    stale = captured - timedelta(minutes=20)
    fetcher = _fake_fetcher(captured)

    def stale_fetcher(source_id: str, url: str):
        response = fetcher(source_id, url)
        if source_id == "binance_spot_ticker":
            payload = dict(response["payload"], closeTime=_iso_ms(stale))
            raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            return {"raw_bytes": raw, "payload": payload}
        return response

    summary = run_ingestion(tmp_path / "stale-run", fetcher=stale_fetcher, now=captured)
    snapshot = json.loads((tmp_path / "stale-run" / "snapshot.json").read_text(encoding="utf-8"))
    assert summary["snapshot_status"] == "verified"
    assert any(
        "quality_stale" in item["reasons"]
        for item in snapshot["excluded_records"]
    )
    assert all(
        record["known_at_utc"] == "2026-11-04T12:30:00.000000Z"
        for record in snapshot["records"]
    )


def test_kraken_level_timestamps_do_not_define_rest_snapshot_freshness(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    summary = run_ingestion(tmp_path / "old-levels", fetcher=_fake_fetcher(captured), now=captured)
    snapshot = json.loads((tmp_path / "old-levels" / "snapshot.json").read_text(encoding="utf-8"))
    kraken = next(
        item for item in snapshot["records"]
        if item["feature_id"] == "xrp.spot.kraken.orderbook.mid_price"
    )
    assert kraken["model_eligible"] is True
    assert summary["snapshot_status"] == "verified"


def test_kraken_depth_without_server_date_is_raw_only(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)

    def no_date(source_id: str, url: str):
        response = fetcher(source_id, url)
        if source_id == "kraken_spot_depth":
            response.pop("http_date", None)
        return response

    summary = run_ingestion(tmp_path / "no-date", fetcher=no_date, now=captured)
    snapshot = json.loads((tmp_path / "no-date" / "snapshot.json").read_text(encoding="utf-8"))
    raw_only = json.loads((tmp_path / "no-date" / "raw_only_sources.json").read_text(encoding="utf-8"))
    assert summary["snapshot_status"] == "verified"
    assert any(item["source_id"] == "kraken_spot_depth" for item in raw_only)
    assert not any(item["feature_id"].startswith("xrp.spot.kraken.orderbook.") for item in snapshot["records"])


def test_kraken_ticker_snapshot_uses_http_date_not_last_trade_event(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    summary = run_ingestion(tmp_path / "kraken-ticker", fetcher=_fake_fetcher(captured), now=captured)
    snapshot = json.loads((tmp_path / "kraken-ticker" / "snapshot.json").read_text(encoding="utf-8"))
    price = next(
        item for item in snapshot["records"]
        if item["feature_id"] == "xrp.spot.kraken.last_trade_price_snapshot"
    )
    spread = next(
        item for item in snapshot["records"]
        if item["feature_id"] == "xrp.spot.kraken.spread_bps"
    )
    assert price["value"] == pytest.approx(1.29)
    assert price["event_time_utc"] == "2026-11-04T12:29:55.000000Z"
    assert price["source_data_as_of_utc"] == price["event_time_utc"]
    assert price["model_eligible"] is True
    assert any("does not expose an individual last-trade timestamp" in item for item in price["limitations"])
    assert spread["value"] == pytest.approx((1.291 - 1.289) / 1.290 * 10000)
    assert summary["snapshot_status"] == "verified"


def test_kraken_ticker_without_http_date_is_raw_only(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)

    def no_date(source_id: str, url: str):
        response = fetcher(source_id, url)
        if source_id == "kraken_spot_ticker":
            response.pop("http_date", None)
        return response

    summary = run_ingestion(tmp_path / "kraken-ticker-no-date", fetcher=no_date, now=captured)
    snapshot = json.loads((tmp_path / "kraken-ticker-no-date" / "snapshot.json").read_text(encoding="utf-8"))
    raw_only = json.loads((tmp_path / "kraken-ticker-no-date" / "raw_only_sources.json").read_text(encoding="utf-8"))
    assert summary["snapshot_status"] == "verified"
    assert any(item["source_id"] == "kraken_spot_ticker" for item in raw_only)
    assert not any(item["feature_id"].startswith("xrp.spot.kraken.") and item["feature_id"].endswith("_snapshot") for item in snapshot["records"])


def test_kraken_ticker_locked_book_is_preserved_as_raw_only_failure(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)

    def locked_book(source_id: str, url: str):
        response = fetcher(source_id, url)
        if source_id == "kraken_spot_ticker":
            payload = response["payload"]
            payload["result"]["XXRPZUSD"]["a"][0] = "1.289"
            response["raw_bytes"] = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return response

    summary = run_ingestion(tmp_path / "kraken-ticker-locked", fetcher=locked_book, now=captured)
    raw_only = json.loads((tmp_path / "kraken-ticker-locked" / "raw_only_sources.json").read_text(encoding="utf-8"))
    assert summary["snapshot_status"] == "verified"
    assert any(
        item["source_id"] == "kraken_spot_ticker"
        and item["reason"] == "source_processing_failure:XRPIngestionError"
        for item in raw_only
    )


def test_kraken_ticker_is_in_scheduled_source_registry():
    endpoint_map = dict(ENDPOINTS)
    assert endpoint_map["kraken_spot_ticker"] == "https://api.kraken.com/0/public/Ticker?pair=XRPUSD"
    assert PARSERS["kraken_spot_ticker"] is not None
    assert any(source_id == "kraken_spot_ticker" for source_id, _ in SCHEDULED_ENDPOINTS)


def test_okx_spot_sources_are_timestamped_and_in_scheduled_registry():
    endpoint_map = dict(ENDPOINTS)
    assert endpoint_map["okx_spot_ticker"] == "https://us.okx.com/api/v5/market/ticker?instId=XRP-USDT"
    assert endpoint_map["okx_spot_depth"] == "https://us.okx.com/api/v5/market/books?instId=XRP-USDT&sz=100"
    assert "us.okx.com" in ALLOWED_HOSTS
    assert PARSERS["okx_spot_ticker"] is not None
    assert PARSERS["okx_spot_depth"] is not None
    assert {"okx_spot_ticker", "okx_spot_depth"}.issubset(
        {source_id for source_id, _url in SCHEDULED_ENDPOINTS}
    )


def test_okx_orderbook_uses_provider_timestamp_and_rejects_stale_or_crossed_books():
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    source_id = "okx_spot_depth"
    url = dict(ENDPOINTS)[source_id]
    response = _fake_fetcher(captured)(source_id, url)
    parser = PARSERS[source_id]
    digest = hashlib.sha256(response["raw_bytes"]).hexdigest()

    records, event_time, eligible, reason = parser(
        response["payload"],
        source_id=source_id,
        url=url,
        digest=digest,
        captured=captured,
    )
    assert eligible is True
    assert reason == ""
    assert event_time == "2026-11-04T12:29:58.000000Z"
    by_feature = {item["feature_id"]: item for item in records}
    assert by_feature["xrp.spot.okx.orderbook.best_bid"]["value"] == pytest.approx(1.289)
    assert by_feature["xrp.spot.okx.orderbook.best_ask"]["value"] == pytest.approx(1.291)
    assert by_feature["xrp.spot.okx.orderbook.mid_price"]["value"] == pytest.approx(1.29)
    assert by_feature["xrp.spot.okx.orderbook.bid_depth_10bps"]["unit"] == "USDT"
    assert by_feature["xrp.spot.okx.orderbook.mid_price"]["sources"][0]["independence_group"] == "okx"

    stale_payload = json.loads(json.dumps(response["payload"]))
    stale_payload["data"][0]["ts"] = str(_iso_ms(captured - timedelta(seconds=61)))
    stale_raw = json.dumps(stale_payload, separators=(",", ":")).encode("utf-8")
    stale_records, _stale_event, stale_eligible, stale_reason = parser(
        stale_payload,
        source_id=source_id,
        url=url,
        digest=hashlib.sha256(stale_raw).hexdigest(),
        captured=captured,
    )
    assert stale_eligible is False
    assert stale_reason == "source_timestamp_older_than_60_seconds"
    assert all(item["model_eligible"] is False and item["quality_status"] == "stale" for item in stale_records)

    crossed_payload = json.loads(json.dumps(response["payload"]))
    crossed_payload["data"][0]["asks"][0][0] = "1.289"
    with pytest.raises(XRPIngestionError, match="crossed or locked"):
        parser(
            crossed_payload,
            source_id=source_id,
            url=url,
            digest=digest,
            captured=captured,
        )


def test_scheduled_ingestion_workflow_persists_history_without_repository_writes():
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "xrp-public-ingestion.yml").read_text(encoding="utf-8")
    assert "cron: '3 * * * *'" in workflow
    assert "cron: '15 0 * * *'" in workflow
    assert "actions: read" in workflow
    assert "contents: read" in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/cache/restore@v4" in workflow
    assert "actions/cache/save@v4" in workflow
    assert "if: steps.feature_cache.outputs.cache-hit == 'true'" in workflow
    assert "if: steps.feature_cache.outputs.cache-hit != 'true'" in workflow
    assert "cache-matched-key" not in workflow
    fallback = workflow.split("Restore latest trusted feature-store artifact when exact cache key is unavailable", 1)[1].split("      - name:", 1)[0]
    cleanup = "rm -f artifacts/xrp_ingestion/feature_store.sqlite3"
    assert cleanup in fallback
    assert fallback.index(cleanup) < fallback.index('while [[ "$page"')
    assert workflow.index("Upload immutable raw-source receipts") < workflow.index("Upload per-run point-in-time feature-store checkpoint") < workflow.index("Save cumulative feature-store cache after successful artifact publication")
    assert workflow.index("Upload daily point-in-time feature-store backup and walk-forward report") < workflow.index("Save cumulative feature-store cache after successful artifact publication")
    assert workflow.count("actions/cache/save@v4") == 1
    cache_save_step = workflow.split(
        "      - name: Save cumulative feature-store cache after successful artifact publication", 1
    )[1].split("\n      - name:", 1)[0]
    assert "continue-on-error: true" in cache_save_step
    assert "actions/workflows/xrp-public-ingestion.yml/runs?branch=main&status=completed&per_page=100" in workflow
    assert "per_page=100&page=${page}" in workflow
    assert 'while [[ "$page" -le 30 && "$restored" != "1" ]]' in workflow
    assert "page_run_count=\"$(jq '.workflow_runs | length' <<< \"$run_page\")\"" in workflow
    assert '[[ "$page_run_count" -gt 0 ]] || break' in workflow
    assert 'if [[ -n "$run_ids" ]]; then' in workflow
    assert "page=$((page+1))" in workflow
    assert "select(.conclusion == \"success\"" in workflow
    assert '.head_branch == "main"' in workflow
    assert ".head_repository.full_name == env.GITHUB_REPOSITORY" in workflow
    assert '(.event == "schedule" or .event == "workflow_dispatch")' in workflow
    assert 'gh run download "$previous_run_id" --name "xrp-public-feature-store-${previous_run_id}"' in workflow
    assert 'gh run download "$previous_run_id" --name "xrp-public-feature-${previous_run_id}"' in workflow
    assert 'trusted_ingestion_workflow_run:${previous_run_id}:per_run_checkpoint' in workflow
    assert 'trusted_ingestion_workflow_run:${previous_run_id}:daily_archive' in workflow
    assert "actions/artifacts?per_page=100" not in workflow
    assert "gh api --paginate" not in workflow
    assert "RUNNER_TEMP/xrp-feature-restore-" in workflow
    assert "github.event.schedule == '15 0 * * *'" in workflow
    assert "xrp-public-raw-${{ github.run_id }}" in workflow
    assert "xrp-public-feature-store-${{ github.run_id }}" in workflow
    assert "xrp-public-feature-${{ github.run_id }}" in workflow
    assert "retention-days: 7" in workflow
    assert "python -m barrot_agent.evolution.research_timestamp_audit" in workflow
    assert workflow.index("Apply XRP research timestamp corrections in memory") < workflow.index("Capture public XRP market sources")
    assert "xrp-research-correction-audit-${{ github.run_id }}" in workflow
    assert "${{ runner.temp }}/xrp-research-correction-audit.json" in workflow
    assert "if-no-files-found: error" in workflow
    assert "actions: write" not in workflow
    assert workflow.count("retention-days: 90") == 3
    assert workflow.count("retention-days: 7") == 1
    assert "retention-days: 1" not in workflow
    assert "if: github.ref == 'refs/heads/main'" in workflow
    assert "secrets." not in workflow
    assert "contents: write" not in workflow
    assert "git push" not in workflow
    assert "deploy" not in workflow.lower()
    assert "--include-noncommercial-xrpl-nodes" not in workflow




def test_feature_store_recovery_contract_docs_match_workflow_policy():
    root = Path(__file__).resolve().parents[1]
    feature_contract = (root / "research" / "xrp_intelligence" / "feature-store-contract.md").read_text(encoding="utf-8")
    forecast_contract = (root / "research" / "xrp_intelligence" / "forecast-ledger-contract.md").read_text(encoding="utf-8")

    for contract in (feature_contract, forecast_contract):
        assert "exact cache" in contract.lower()
        assert "7-day retention" in contract
        assert "90-day retention" in contract
        assert "30 pages of 100" in contract
    assert "deletes any restore-key file" in feature_contract.lower()
    assert "external WORM" in feature_contract
    assert "no scheduled main-branch run is verified" in forecast_contract
    assert "daily 00:15 UTC schedule and manual dispatch evaluate" in forecast_contract
    assert "block-bootstrap adjustment" in forecast_contract


def test_walk_forward_overall_status_is_partial_until_every_venue_is_scored(tmp_path, monkeypatch):
    store = HistoricalFeatureStore(tmp_path / "features.sqlite3")
    statuses = {"binance": "SCORED", "coinbase": "INSUFFICIENT_HISTORY"}

    def fake_evaluator(records, **kwargs):
        status = statuses[kwargs["venue"]]
        return {
            "status": status,
            "forecast_count": 4 if status == "SCORED" else 0,
            "forecasts": [],
            "live_forecast_issued": False,
        }

    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion.evaluate_chronological_walk_forward",
        fake_evaluator,
    )
    report, history = _walk_forward_report(
        store,
        evaluation_as_of_utc="2026-11-05T02:00:00Z",
    )

    assert history == []
    assert report["evaluations"]["binance_xrpusdt_1h"]["status"] == "SCORED"
    assert report["evaluations"]["coinbase_xrpusd_1h"]["status"] == "INSUFFICIENT_HISTORY"
    assert report["all_venues_scored"] is False
    assert report["overall_status"] == "PARTIAL_OR_BLOCKED"
    assert report["live_forecast_issued"] is False
    assert report["paper_trade_executed"] is False


def test_walk_forward_overall_status_is_scored_only_when_all_venues_are_scored(tmp_path, monkeypatch):
    store = HistoricalFeatureStore(tmp_path / "features.sqlite3")

    def fake_evaluator(records, **kwargs):
        return {
            "status": "SCORED",
            "forecast_count": 4,
            "forecasts": [],
            "live_forecast_issued": False,
        }

    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion.evaluate_chronological_walk_forward",
        fake_evaluator,
    )
    report, _ = _walk_forward_report(
        store,
        evaluation_as_of_utc="2026-11-05T02:00:00Z",
    )

    assert report["all_venues_scored"] is True
    assert report["overall_status"] == "SCORED"
    assert report["live_forecast_issued"] is False
    assert report["paper_trade_executed"] is False


def test_walk_forward_horizon_parser_accepts_only_unique_supported_labels():
    assert _normalize_walk_forward_horizons("1h,4h,24h,7d,30d") == (
        "1h",
        "4h",
        "24h",
        "7d",
        "30d",
    )
    assert _normalize_walk_forward_horizons(("30d", "1h")) == ("30d", "1h")
    with pytest.raises(XRPIngestionError, match="duplicate walk-forward horizon"):
        _normalize_walk_forward_horizons("1h,1h")
    with pytest.raises(XRPIngestionError, match="unsupported walk-forward horizon"):
        _normalize_walk_forward_horizons("1h,2h")
    with pytest.raises(XRPIngestionError, match="at least one supported horizon"):
        _normalize_walk_forward_horizons("")


def test_walk_forward_report_evaluates_daily_horizon_matrix_with_horizon_sized_embargo(tmp_path, monkeypatch):
    store = HistoricalFeatureStore(tmp_path / "features.sqlite3")
    calls = []

    def fake_evaluator(records, **kwargs):
        calls.append(kwargs)
        return {
            "status": "SCORED",
            "forecast_count": 1,
            "forecasts": [],
            "live_forecast_issued": False,
            "paper_trade_executed": False,
        }

    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion.evaluate_chronological_walk_forward",
        fake_evaluator,
    )
    report, history = _walk_forward_report(
        store,
        evaluation_as_of_utc="2026-11-08T13:00:00Z",
        horizons=("1h", "4h", "24h", "7d", "30d"),
    )

    assert history == []
    assert len(calls) == 10
    assert report["evaluation_count"] == 10
    assert report["requested_horizons"] == ["1h", "4h", "24h", "7d", "30d"]
    assert set(report["requested_horizons_seconds"]) == {3600, 14400, 86400, 604800, 2592000}
    assert all(call["embargo_seconds"] == call["horizon_seconds"] for call in calls)
    assert report["all_venue_horizon_pairs_scored"] is True
    assert report["all_horizons_scored"] is True
    assert report["all_venues_scored"] is True
    assert report["overall_status"] == "SCORED"
    assert report["forecast_count"] == 10
    assert report["evaluations"]["binance_xrpusdt_30d"]["horizon_label"] == "30d"
    assert report["model_eligible"] is False
    assert "target windows overlap" in report["oos_dependence_policy"]
    assert report["live_forecast_issued"] is False
    assert report["paper_trade_executed"] is False


def test_xrp_insights_etf_aggregator_is_captured_raw_only_and_never_promoted_to_features():
    captured = datetime(2026, 11, 5, 2, 30, tzinfo=timezone.utc)
    payload = _fake_fetcher(captured)("xrp_etf_flows_aggregator", dict(ENDPOINTS)["xrp_etf_flows_aggregator"])["payload"]
    parser = PARSERS["xrp_etf_flows_aggregator"]
    records, source_as_of, eligible, reason = parser(
        payload,
        source_id="xrp_etf_flows_aggregator",
        url=dict(ENDPOINTS)["xrp_etf_flows_aggregator"],
        digest="a" * 64,
        captured=captured,
    )
    assert "xrp-insights.com" in ALLOWED_HOSTS
    assert ("xrp_etf_flows_aggregator", "https://xrp-insights.com/data/xrp-etf-flows.json") in ENDPOINTS
    assert records == []
    assert source_as_of is None
    assert eligible is False
    assert "raw_only" in reason
    assert "primary_receipts" in reason

    invalid = dict(payload)
    invalid["metadata"] = dict(payload["metadata"], publisher="unverified-copy")
    with pytest.raises(XRPIngestionError, match="identity mismatch"):
        parser(
            invalid,
            source_id="xrp_etf_flows_aggregator",
            url=dict(ENDPOINTS)["xrp_etf_flows_aggregator"],
            digest="b" * 64,
            captured=captured,
        )


def test_xrp_exchange_balance_dataset_is_registered_hash_only_and_raw_only():
    captured = datetime(2026, 11, 5, 9, 0, tzinfo=timezone.utc)
    source_id = "xrp_exchange_balances_json"
    url = dict(ENDPOINTS)[source_id]
    payload = _fake_fetcher(captured)(source_id, url)["payload"]
    parser = PARSERS[source_id]
    records, source_as_of, eligible, reason = parser(
        payload,
        source_id=source_id,
        url=url,
        digest="c" * 64,
        captured=captured,
    )

    assert url == "https://xrp-insights.com/exchange-balances/data.json"
    assert source_id in dict(SCHEDULED_ENDPOINTS)
    assert "xrp-insights.com" in ALLOWED_HOSTS
    assert records == []
    assert source_as_of is None
    assert eligible is False
    assert "raw_only" in reason
    assert "same_wallet" in reason

    invalid = dict(payload, publisher="unverified-copy")
    with pytest.raises(XRPIngestionError, match="publisher identity mismatch"):
        parser(
            invalid,
            source_id=source_id,
            url=url,
            digest="d" * 64,
            captured=captured,
        )


def test_public_fetch_rejects_redirects_outside_the_https_allowlist(monkeypatch):
    class RedirectedResponse:
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def geturl(self):
            return "https://untrusted.example/redirected.json"

        def read(self, _limit):
            raise AssertionError("body must not be read after an untrusted redirect")

    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion._open_public_request",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(XRPIngestionError("public fetch redirects are disabled")),
    )
    with pytest.raises(XRPIngestionError, match="redirects are disabled"):
        fetch_public_json(
            "xrp_etf_flows_aggregator",
            "https://xrp-insights.com/data/xrp-etf-flows.json",
        )


def test_xrpr_primary_issuer_page_is_registered_and_retained_raw_only():
    captured = datetime(2026, 11, 5, 2, 30, tzinfo=timezone.utc)
    url = dict(ENDPOINTS)["xrp_etf_xrpr_issuer_page"]
    payload = _fake_fetcher(captured)("xrp_etf_xrpr_issuer_page", url)["payload"]
    records, source_as_of, eligible, reason = PARSERS["xrp_etf_xrpr_issuer_page"](
        payload,
        source_id="xrp_etf_xrpr_issuer_page",
        url=url,
        digest="c" * 64,
        captured=captured,
    )
    assert "www.rexshares.com" in ALLOWED_HOSTS
    assert url == "https://www.rexshares.com/xrpr/"
    assert records == []
    assert source_as_of is None
    assert eligible is False
    assert "raw_only" in reason


@pytest.mark.parametrize(
    ("source_id", "host", "url"),
    [
        ("xrp_etf_bitwise_issuer_page", "bitxrpetf.com", "https://bitxrpetf.com/"),
        ("xrp_etf_grayscale_gxrp_issuer_page", "etfs.grayscale.com", "https://etfs.grayscale.com/gxrp"),
        ("xrp_etf_franklin_xrpz_issuer_page", "www.franklintempleton.com", "https://www.franklintempleton.com/investments/options/exchange-traded-funds/products/47318/SINGLCLASS/franklin-xrp-etf/XRPZ"),
        ("xrp_etf_canary_xrpc_issuer_page", "canaryetfs.com", "https://canaryetfs.com/xrpc/"),
        ("xrp_etf_21shares_toxr_issuer_page", "www.21shares.com", "https://www.21shares.com/en-us/products-us/toxr"),
    ],
)
def test_primary_issuer_pages_are_registered_without_feature_promotion(source_id, host, url):
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    payload = _fake_fetcher(captured)(source_id, url)["payload"]
    records, source_as_of, eligible, reason = PARSERS[source_id](
        payload, source_id=source_id, url=url, digest="d" * 64, captured=captured
    )
    assert host in ALLOWED_HOSTS
    assert dict(ENDPOINTS)[source_id] == url
    assert records == []
    assert source_as_of is None
    assert eligible is False
    hash_only_sources = {
        "xrp_etf_franklin_xrpz_issuer_page",
        "xrp_etf_canary_xrpc_issuer_page",
        "xrp_etf_21shares_toxr_issuer_page",
    }
    expected_reason = "hash_only" if source_id in hash_only_sources else "raw_only"
    assert expected_reason in reason



@pytest.mark.parametrize(
    ("source_id", "host", "url"),
    [
        (
            "ripple_rlusd_transparency_dashboard",
            "ripple.com",
            "https://ripple.com/products/stablecoin/transparency/",
        ),
        (
            "xrpldashboard_rlusd_cross_chain_supply",
            "xrpldashboard.com",
            "https://xrpldashboard.com/rlusd",
        ),
        (
            "circle_usdc_transparency_dashboard",
            "www.circle.com",
            "https://www.circle.com/transparency",
        ),
    ],
)
def test_stablecoin_transparency_pages_are_registered_and_retained_raw_only(source_id, host, url):
    captured = datetime(2026, 11, 8, 11, 0, tzinfo=timezone.utc)
    payload = _fake_fetcher(captured)(source_id, url)["payload"]
    records, source_as_of, eligible, reason = PARSERS[source_id](
        payload, source_id=source_id, url=url, digest="e" * 64, captured=captured
    )
    assert host in ALLOWED_HOSTS
    assert dict(ENDPOINTS)[source_id] == url
    assert source_id in dict(SCHEDULED_ENDPOINTS)
    assert len(ENDPOINTS) == 39
    assert len(SCHEDULED_ENDPOINTS) == 36
    assert records == []
    assert source_as_of is None
    assert eligible is False
    assert "raw_only" in reason


@pytest.mark.parametrize(
    "source_id",
    [
        "ripple_rlusd_transparency_dashboard",
        "xrpldashboard_rlusd_cross_chain_supply",
        "circle_usdc_transparency_dashboard",
    ],
)
def test_stablecoin_transparency_pages_reject_wrong_publisher_markup(source_id):
    captured = datetime(2026, 11, 8, 11, 0, tzinfo=timezone.utc)
    with pytest.raises(XRPIngestionError):
        PARSERS[source_id](
            {"html_text": "<html><title>unrelated page</title></html>"},
            source_id=source_id,
            url=dict(ENDPOINTS)[source_id],
            digest="f" * 64,
            captured=captured,
        )


@pytest.mark.parametrize(
    "source_id",
    [
        "ripple_rlusd_transparency_dashboard",
        "xrpldashboard_rlusd_cross_chain_supply",
        "circle_usdc_transparency_dashboard",
    ],
)
def test_default_public_fetcher_routes_stablecoin_transparency_pages_to_html(monkeypatch, source_id):
    calls = []
    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion.fetch_public_html",
        lambda sid, url: calls.append(("html", sid, url)) or {"kind": "html"},
    )
    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion.fetch_public_json",
        lambda sid, url: calls.append(("json", sid, url)) or {"kind": "json"},
    )
    url = dict(ENDPOINTS)[source_id]
    assert _default_public_fetcher(source_id, url) == {"kind": "html"}
    assert calls == [("html", source_id, url)]


@pytest.mark.parametrize(
    "source_id",
    ["xrp_etf_xrpr_issuer_page", "xrp_etf_bitwise_issuer_page", "xrp_etf_grayscale_gxrp_issuer_page"],
)
def test_default_public_fetcher_routes_primary_issuer_pages_to_html(monkeypatch, source_id):
    calls = []
    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion.fetch_public_html",
        lambda sid, url: calls.append(("html", sid, url)) or {"kind": "html"},
    )
    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion.fetch_public_json",
        lambda sid, url: calls.append(("json", sid, url)) or {"kind": "json"},
    )
    url = dict(ENDPOINTS)[source_id]
    assert _default_public_fetcher(source_id, url) == {"kind": "html"}
    assert calls == [("html", source_id, url)]


def test_public_html_fetch_captures_allowlisted_issuer_bytes(monkeypatch):
    class HtmlResponse:
        headers = {
            "Content-Type": "text/html; charset=utf-8",
            "Date": "Wed, 05 Nov 2026 02:30:00 GMT",
        }

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def geturl(self):
            return "https://www.rexshares.com/xrpr/"

        def read(self, _limit):
            return b"<html>REX-Osprey XRPR CoinShares XRP ETP As of</html>"

    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion._open_public_request",
        lambda request, timeout: HtmlResponse(),
    )
    result = fetch_public_html("xrp_etf_xrpr_issuer_page", dict(ENDPOINTS)["xrp_etf_xrpr_issuer_page"])
    assert result["raw_bytes"].startswith(b"<html>")
    assert "CoinShares XRP ETP" in result["payload"]["html_text"]
    assert result["http_date"] == "Wed, 05 Nov 2026 02:30:00 GMT"


def test_public_html_fetch_rejects_untrusted_redirect(monkeypatch):
    class RedirectedHtmlResponse:
        headers = {"Content-Type": "text/html"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def geturl(self):
            return "https://untrusted.example/redirected.html"

        def read(self, _limit):
            raise AssertionError("body must not be read after an untrusted redirect")

    monkeypatch.setattr(
        "barrot_agent.evolution.xrp_public_ingestion._open_public_request",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(XRPIngestionError("public fetch redirects are disabled")),
    )
    with pytest.raises(XRPIngestionError, match="redirects are disabled"):
        fetch_public_html("xrp_etf_xrpr_issuer_page", dict(ENDPOINTS)["xrp_etf_xrpr_issuer_page"])


def test_binance_funding_history_preserves_signed_event_rates_and_capture_vintage():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    source_id, url = "binance_perp_funding_history", dict(ENDPOINTS)["binance_perp_funding_history"]
    payload = _fake_fetcher(captured)(source_id, url)["payload"]
    records, source_as_of, eligible, reason = PARSERS[source_id](
        payload, source_id=source_id, url=url, digest="a" * 64, captured=captured
    )
    funding = [item for item in records if item["feature_id"] == "xrp.perpetual.binance.funding_rate"]
    assert [item["value"] for item in funding] == [-0.0002, 0.0001]
    assert source_as_of == funding[-1]["event_time_utc"]
    assert eligible is True and reason == ""
    assert all(item["known_at_utc"] == "2026-11-05T04:00:00.000000Z" for item in funding)
    assert all(item["event_time_utc"] < item["known_at_utc"] for item in funding)
    assert all(item["unit"] == "fraction_per_settlement" for item in funding)
    assert all("not assumed fixed" in item["limitations"][1] for item in funding)

    invalid = [dict(payload[0]), dict(payload[1], fundingTime=payload[0]["fundingTime"])]
    with pytest.raises(XRPIngestionError, match="duplicate"):
        PARSERS[source_id](
            invalid, source_id=source_id, url=url, digest="b" * 64, captured=captured
        )


def test_binance_open_interest_history_keeps_contracts_and_quote_value_separate():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    source_id, url = "binance_perp_open_interest_history", dict(ENDPOINTS)["binance_perp_open_interest_history"]
    payload = _fake_fetcher(captured)(source_id, url)["payload"]
    records, source_as_of, eligible, reason = PARSERS[source_id](
        payload, source_id=source_id, url=url, digest="c" * 64, captured=captured
    )
    contracts = [item for item in records if item["feature_id"].endswith("open_interest_contracts")]
    values = [item for item in records if item["feature_id"].endswith("open_interest_value")]
    assert [item["value"] for item in contracts] == [2500000.0, 2510000.0]
    assert [item["value"] for item in values] == [3225000.0, 3247900.0]
    assert all(item["unit"] == "contracts" for item in contracts)
    assert all(item["unit"] == "USDT" for item in values)
    assert source_as_of == contracts[-1]["event_time_utc"]
    assert eligible is True and reason == ""
    assert all(item["known_at_utc"] == "2026-11-05T04:00:00.000000Z" for item in records)
    assert "no-trade periods may be omitted" in records[0]["limitations"][0]


def test_binance_global_long_short_ratio_is_account_based_and_validated():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    source_id, url = "binance_perp_global_long_short_ratio", dict(ENDPOINTS)["binance_perp_global_long_short_ratio"]
    payload = _fake_fetcher(captured)(source_id, url)["payload"]
    records, source_as_of, eligible, reason = PARSERS[source_id](
        payload, source_id=source_id, url=url, digest="d" * 64, captured=captured
    )
    ratios = [item for item in records if item["feature_id"].endswith("global_long_short_account_ratio")]
    assert [item["value"] for item in ratios] == [1.25, 1.20]
    assert all("account-count ratios" in item["limitations"][0] for item in ratios)
    assert source_as_of == ratios[-1]["event_time_utc"]
    assert eligible is True and reason == ""

    inconsistent = [dict(payload[0], longShortRatio="3.0")]
    retained, _, source_eligible, source_reason = PARSERS[source_id](
        inconsistent, source_id=source_id, url=url, digest="e" * 64, captured=captured
    )
    reported_ratio = next(item for item in retained if item["feature_id"].endswith("global_long_short_account_ratio"))
    account_fractions = [
        item for item in retained
        if item["feature_id"].endswith(("global_long_account_fraction", "global_short_account_fraction"))
    ]
    assert source_eligible is True and source_reason == ""
    assert reported_ratio["value"] == 3.0
    assert reported_ratio["model_eligible"] is False
    assert reported_ratio["eligibility_reason"] == "reported_ratio_conflicts_with_account_fractions"
    assert all(item["model_eligible"] is True for item in account_fractions)


def test_historical_derivatives_reject_future_event_timestamps():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    source_id, url = "binance_perp_funding_history", dict(ENDPOINTS)["binance_perp_funding_history"]
    payload = [{
        "symbol": "XRPUSDT",
        "fundingRate": "0.0001",
        "fundingTime": _iso_ms(captured + timedelta(seconds=1)),
        "markPrice": "1.29",
    }]
    with pytest.raises(XRPIngestionError, match="later than capture"):
        PARSERS[source_id](
            payload, source_id=source_id, url=url, digest="f" * 64, captured=captured
        )


def test_xrpl_server_info_uses_validated_ledger_and_http_date():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    source_id, url = "xrpl_inftf_server_info", dict(ENDPOINTS)["xrpl_inftf_server_info"]
    response = _fake_fetcher(captured)(source_id, url)
    records, source_as_of, eligible, reason = PARSERS[source_id](
        response["payload"],
        source_id=source_id,
        url=url,
        digest="a" * 64,
        captured=captured,
        http_date=response["http_date"],
    )
    assert eligible is False
    assert reason == "xrpl_node_state_is_integrity_only_not_an_economic_feature"
    assert source_as_of == "2026-11-05T03:59:55.000000Z"
    assert all(item["model_eligible"] is False for item in records)
    values = {item["feature_id"]: item for item in records}
    assert values["xrp.network.xrpl.validated_ledger_index"]["value"] == 108123456.0
    assert values["xrp.network.xrpl.base_fee_xrp"]["value"] == 0.00001
    assert values["xrp.network.xrpl.reserve_base_xrp"]["value"] == 1.0
    assert values["xrp.network.xrpl.reserve_increment_xrp"]["value"] == 0.2
    assert all(item["sources"][0]["independence_group"] == "xrpl_public_ledger" for item in records)
    assert all(
        any("not independent economic evidence" in limitation for limitation in item["limitations"])
        for item in records
    )


def test_xrpl_server_info_without_http_date_remains_raw_only():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    source_id, url = "xrpl_inftf_server_info", dict(ENDPOINTS)["xrpl_inftf_server_info"]
    payload = _fake_fetcher(captured)(source_id, url)["payload"]
    records, source_as_of, eligible, reason = PARSERS[source_id](
        payload,
        source_id=source_id,
        url=url,
        digest="b" * 64,
        captured=captured,
        http_date=None,
    )
    assert records == []
    assert source_as_of is None
    assert eligible is False
    assert reason == "missing_or_invalid_http_date_for_xrpl_server_info"


def test_xrpl_node_reconciliation_requires_exact_two_operator_ledger_match():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)
    payloads = {}
    records = []
    for source_id, url in ENDPOINTS:
        if source_id not in XRPL_NODE_SOURCES:
            continue
        response = fetcher(source_id, url)
        payloads[source_id] = response["payload"]
        parsed, _, _, _ = PARSERS[source_id](
            response["payload"],
            source_id=source_id,
            url=url,
            digest=("c" if source_id == "xrpl_inftf_server_info" else "d") * 64,
            captured=captured,
            http_date=response["http_date"],
        )
        records.extend(parsed)

    agreed = _reconcile_xrpl_node_records(records, payloads)
    assert agreed["status"] == "AGREED"
    assert agreed["integrity_check_only"] is True
    assert agreed["model_admission_allowed"] is False
    assert agreed["observed_source_count"] == 2
    assert all(item["model_eligible"] is False for item in records)

    payloads["xrpl_honeycluster_server_info"] = json.loads(
        json.dumps(payloads["xrpl_honeycluster_server_info"])
    )
    payloads["xrpl_honeycluster_server_info"]["result"]["info"]["validated_ledger"]["seq"] += 1
    blocked = _reconcile_xrpl_node_records(records, payloads)
    assert blocked["status"] == "DISAGREEMENT"
    assert blocked["model_admission_allowed"] is False
    assert all(item["model_eligible"] is False for item in records)
    assert all(
        item["eligibility_reason"] == "xrpl_public_nodes_report_different_validated_ledgers"
        for item in records
    )


def test_xrpl_node_reconciliation_fails_closed_without_two_operators():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    source_id, url = "xrpl_inftf_server_info", dict(ENDPOINTS)["xrpl_inftf_server_info"]
    response = _fake_fetcher(captured)(source_id, url)
    records, _, _, _ = PARSERS[source_id](
        response["payload"],
        source_id=source_id,
        url=url,
        digest="e" * 64,
        captured=captured,
        http_date=response["http_date"],
    )
    result = _reconcile_xrpl_node_records(records, {source_id: response["payload"]})
    assert result["status"] == "INSUFFICIENT_NODE_CONFIRMATION"
    assert result["model_admission_allowed"] is False
    assert all(item["model_eligible"] is False for item in records)


def test_xrpl_rpc_fetch_is_fixed_read_only_and_redirect_bound(monkeypatch):
    import barrot_agent.evolution.xrp_public_ingestion as ingestion

    source_id, url = "xrpl_inftf_server_info", dict(ENDPOINTS)["xrpl_inftf_server_info"]
    response_payload = {
        "result": {"info": {"validated_ledger": {"seq": 1, "hash": "A" * 64}}},
        "status": "success",
    }
    raw = json.dumps(response_payload).encode("utf-8")
    seen = {}

    class FakeResponse:
        headers = {"Date": "Thu, 05 Nov 2026 04:00:00 GMT"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def geturl(self):
            return url

        def read(self, _limit):
            return raw

    def fake_urlopen(request, timeout):
        seen["method"] = request.get_method()
        seen["url"] = request.full_url
        seen["body"] = json.loads(request.data.decode("utf-8"))
        seen["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(ingestion, "_open_public_request", fake_urlopen)
    result = fetch_public_rpc(source_id, url)
    assert seen["method"] == "POST"
    assert seen["url"] == url
    assert seen["timeout"] == 15
    assert seen["body"] == {"method": "server_info", "params": [{"api_version": 2}]}
    assert result["payload"]["status"] == "success"

    class RedirectResponse(FakeResponse):
        def geturl(self):
            return "https://example.invalid/"

    monkeypatch.setattr(ingestion, "_open_public_request", lambda *_args, **_kwargs: RedirectResponse())
    with pytest.raises(XRPIngestionError, match="redirected outside"):
        fetch_public_rpc(source_id, url)

    with pytest.raises(XRPIngestionError, match="not registered"):
        fetch_public_rpc("xrpl_submit", url)


def test_xrpl_server_info_with_stale_validated_ledger_is_not_model_eligible():
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    source_id, url = "xrpl_inftf_server_info", dict(ENDPOINTS)["xrpl_inftf_server_info"]
    response = _fake_fetcher(captured)(source_id, url)
    response["payload"]["result"]["info"]["validated_ledger"]["age"] = 301
    records, source_as_of, eligible, reason = PARSERS[source_id](
        response["payload"],
        source_id=source_id,
        url=url,
        digest="f" * 64,
        captured=captured,
        http_date=response["http_date"],
    )
    assert source_as_of == "2026-11-05T03:59:55.000000Z"
    assert eligible is False
    assert reason == "validated_ledger_age_exceeds_300_seconds"
    assert records and all(item["model_eligible"] is False for item in records)
    assert all(item["quality_status"] == "stale" for item in records)


def test_public_request_rejects_redirect_before_target_receives_request():
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.request import Request

    target_hits = []

    class TargetHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            target_hits.append(self.path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"unexpected target request")

        def log_message(self, *_args):
            pass

    target_server = ThreadingHTTPServer(("127.0.0.1", 0), TargetHandler)
    target_thread = threading.Thread(target=target_server.serve_forever, daemon=True)
    target_thread.start()
    target_url = f"http://127.0.0.1:{target_server.server_address[1]}/target"

    class RedirectHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", target_url)
            self.end_headers()

        def log_message(self, *_args):
            pass

    redirect_server = ThreadingHTTPServer(("127.0.0.1", 0), RedirectHandler)
    redirect_thread = threading.Thread(target=redirect_server.serve_forever, daemon=True)
    redirect_thread.start()
    redirect_url = f"http://127.0.0.1:{redirect_server.server_address[1]}/redirect"

    try:
        with pytest.raises(XRPIngestionError, match="redirects are disabled"):
            _open_public_request(Request(redirect_url), timeout=5)
        assert target_hits == []
    finally:
        redirect_server.shutdown()
        target_server.shutdown()
        redirect_server.server_close()
        target_server.server_close()
        redirect_thread.join(timeout=5)
        target_thread.join(timeout=5)

def test_parser_failure_preserves_exact_raw_bytes_as_ineligible_receipt(tmp_path, monkeypatch):
    import barrot_agent.evolution.xrp_public_ingestion as ingestion

    source_id, url = ingestion.ENDPOINTS[0]
    captured = datetime(2026, 11, 5, 7, 30, tzinfo=timezone.utc)
    raw_bytes = b'{"unexpected":"schema"}'

    def reject_payload(_payload, **_kwargs):
        raise XRPIngestionError("fixture parser rejection")

    monkeypatch.setattr(ingestion, "ENDPOINTS", ((source_id, url),))
    monkeypatch.setattr(ingestion, "SCHEDULED_ENDPOINTS", ((source_id, url),))
    monkeypatch.setattr(ingestion, "PARSERS", {source_id: reject_payload})

    summary = ingestion.run_ingestion(
        tmp_path / "run",
        fetcher=lambda *_args: {
            "raw_bytes": raw_bytes,
            "payload": {"unexpected": "schema"},
            "http_date": None,
        },
        now=captured,
    )

    receipts = json.loads((tmp_path / "run" / "receipt_manifest.json").read_text(encoding="utf-8"))
    failures = json.loads((tmp_path / "run" / "source_failures.json").read_text(encoding="utf-8"))
    raw_only = json.loads((tmp_path / "run" / "raw_only_sources.json").read_text(encoding="utf-8"))

    assert summary["source_receipt_count"] == 1
    assert summary["source_failure_count"] == 1
    assert summary["raw_only_source_count"] == 1
    assert summary["snapshot_status"] == "no_new_eligible_features"
    assert len(receipts) == 1
    receipt = receipts[0]
    assert receipt["source_id"] == source_id
    assert receipt["raw_content_sha256"] == hashlib.sha256(raw_bytes).hexdigest()
    assert receipt["source_data_as_of_utc"] is None
    assert receipt["model_eligible_source"] is False
    assert receipt["raw_only_reason"] == "source_processing_failure:XRPIngestionError"
    assert (tmp_path / "run" / receipt["raw_payload_path"]).read_bytes() == raw_bytes
    assert failures[0]["raw_receipt_id"] == receipt["receipt_id"]
    assert failures[0]["raw_content_sha256"] == receipt["raw_content_sha256"]
    assert raw_only[0]["receipt_id"] == receipt["receipt_id"]



def test_xrp_insights_csv_is_schema_validated_and_kept_research_only():
    captured = datetime(2026, 11, 5, 2, 30, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)
    metadata = fetcher("xrp_etf_flows_aggregator", dict(ENDPOINTS)["xrp_etf_flows_aggregator"])["payload"]
    response = fetcher("xrp_etf_flows_csv", dict(ENDPOINTS)["xrp_etf_flows_csv"])
    records, source_as_of, eligible, reason = PARSERS["xrp_etf_flows_csv"](
        response["payload"],
        source_id="xrp_etf_flows_csv",
        url=dict(ENDPOINTS)["xrp_etf_flows_csv"],
        digest=hashlib.sha256(response["raw_bytes"]).hexdigest(),
        captured=captured,
        metadata_payload=metadata,
    )
    assert len(records) == 1
    assert source_as_of is None
    assert eligible is False
    assert "hash_only_receipt" in reason
    summary = records[0]
    assert summary["data_as_of"] == "2026-11-03"
    assert summary["latest_date_direct_spot_holdings_xrp"] == 1100
    assert summary["latest_date_direct_spot_flow_xrp"] == -10
    assert summary["latest_date_index_sleeve_holdings_xrp"] == 200
    assert summary["latest_date_index_sleeve_flow_xrp"] == 5
    assert summary["research_eligible"] is True
    assert summary["model_eligible"] is False
    assert "commercial redistribution" in summary["license_name"]


def test_xrp_insights_csv_rejects_header_or_row_count_mismatch():
    captured = datetime(2026, 11, 5, 2, 30, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)
    metadata = fetcher("xrp_etf_flows_aggregator", dict(ENDPOINTS)["xrp_etf_flows_aggregator"])["payload"]
    response = fetcher("xrp_etf_flows_csv", dict(ENDPOINTS)["xrp_etf_flows_csv"])
    parser = PARSERS["xrp_etf_flows_csv"]
    bad_header = {"csv_text": response["payload"]["csv_text"].replace("date,ticker", "day,ticker", 1)}
    with pytest.raises(XRPIngestionError, match="header"):
        parser(
            bad_header,
            source_id="xrp_etf_flows_csv",
            url=dict(ENDPOINTS)["xrp_etf_flows_csv"],
            digest="a" * 64,
            captured=captured,
            metadata_payload=metadata,
        )
    bad_metadata = json.loads(json.dumps(metadata))
    bad_metadata["metadata"]["coverage"]["rows"] = 4
    with pytest.raises(XRPIngestionError, match="row count"):
        parser(
            response["payload"],
            source_id="xrp_etf_flows_csv",
            url=dict(ENDPOINTS)["xrp_etf_flows_csv"],
            digest="b" * 64,
            captured=captured,
            metadata_payload=bad_metadata,
        )


def test_xrp_insights_csv_rejects_future_duplicate_and_invalid_flow_rows():
    captured = datetime(2026, 11, 5, 2, 30, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)
    metadata = fetcher("xrp_etf_flows_aggregator", dict(ENDPOINTS)["xrp_etf_flows_aggregator"])["payload"]
    response = fetcher("xrp_etf_flows_csv", dict(ENDPOINTS)["xrp_etf_flows_csv"])
    parser = PARSERS["xrp_etf_flows_csv"]
    text = response["payload"]["csv_text"]
    future = {"csv_text": text.replace("2026-11-03,BITW", "2026-11-06,BITW", 1)}
    with pytest.raises(XRPIngestionError, match="after capture"):
        parser(future, source_id="xrp_etf_flows_csv", url=dict(ENDPOINTS)["xrp_etf_flows_csv"], digest="c" * 64, captured=captured, metadata_payload=metadata)
    duplicate = {"csv_text": text.replace("2026-11-03,BITW,Bitwise", "2026-11-03,XRP,Bitwise", 1)}
    with pytest.raises(XRPIngestionError, match="duplicate"):
        parser(duplicate, source_id="xrp_etf_flows_csv", url=dict(ENDPOINTS)["xrp_etf_flows_csv"], digest="d" * 64, captured=captured, metadata_payload=metadata)
    invalid_flow = {"csv_text": text.replace("2026-11-03,XRP,Bitwise,1000,-10,-12.9,computed", "2026-11-03,XRP,Bitwise,1000,,-12.9,computed", 1)}
    with pytest.raises(XRPIngestionError, match="computed flow is blank"):
        parser(invalid_flow, source_id="xrp_etf_flows_csv", url=dict(ENDPOINTS)["xrp_etf_flows_csv"], digest="e" * 64, captured=captured, metadata_payload=metadata)


def test_fetch_public_csv_preserves_exact_bytes_and_requires_csv_content_type(monkeypatch):
    raw = b"date,ticker\\n2026-11-03,XRP\\n"

    class Response:
        def __init__(self, content_type):
            self.headers = {"Content-Type": content_type, "Date": "Thu, 05 Nov 2026 02:30:00 GMT"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def geturl(self):
            return "https://xrp-insights.com/data/xrp-etf-flows.csv"

        def read(self, _limit):
            return raw

    monkeypatch.setattr("barrot_agent.evolution.xrp_public_ingestion._open_public_request", lambda *_args, **_kwargs: Response("text/csv; charset=utf-8"))
    result = fetch_public_csv("xrp_etf_flows_csv", "https://xrp-insights.com/data/xrp-etf-flows.csv")
    assert result["raw_bytes"] == raw
    assert result["payload"]["csv_text"] == raw.decode("utf-8")
    assert result["http_date"] == "Thu, 05 Nov 2026 02:30:00 GMT"

    monkeypatch.setattr("barrot_agent.evolution.xrp_public_ingestion._open_public_request", lambda *_args, **_kwargs: Response("application/json"))
    with pytest.raises(XRPIngestionError, match="not CSV"):
        fetch_public_csv("xrp_etf_flows_csv", "https://xrp-insights.com/data/xrp-etf-flows.csv")


def test_raw_receipt_archive_can_record_digest_without_retaining_restricted_payload(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    raw = b"restricted-public-csv"
    receipt = archive.store(
        source_id="restricted_csv",
        source_uri="https://xrp-insights.com/data/xrp-etf-flows.csv",
        captured_at_utc="2026-11-05T12:30:00.000000Z",
        raw_bytes=raw,
        source_data_as_of_utc=None,
        model_eligible=False,
        raw_only_reason="publisher_terms_require_hash_only_capture",
        retain_raw_bytes=False,
        raw_retention_reason="commercial redistribution requires written permission",
    )
    assert receipt["raw_content_sha256"] == hashlib.sha256(raw).hexdigest()
    assert receipt["raw_bytes_retained"] is False
    assert receipt["raw_payload_path"] is None
    assert "written permission" in receipt["raw_retention_reason"]
    assert not list((tmp_path / "raw" / "sha256").glob("*"))
    assert len(receipt["receipt_id"]) == 64



def test_scheduled_endpoint_set_excludes_noncommercial_xrpl_nodes():
    scheduled_ids = {source_id for source_id, _url in SCHEDULED_ENDPOINTS}
    assert not scheduled_ids.intersection(XRPL_NODE_SOURCES)
    assert len(SCHEDULED_ENDPOINTS) == len(ENDPOINTS) - len(XRPL_NODE_SOURCES) - len(WEEKLY_ENDPOINTS)


def test_explicit_noncommercial_xrpl_research_capture_is_never_model_eligible(tmp_path):
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    summary = run_ingestion(
        tmp_path / "noncommercial-research",
        fetcher=_fake_fetcher(captured),
        now=captured,
        include_noncommercial_xrpl_nodes=True,
    )

    assert summary["source_receipt_count"] == len(SCHEDULED_ENDPOINTS) + len(XRPL_NODE_SOURCES) + len(_weekly_endpoints_for_capture(captured))
    assert summary["xrpl_node_reconciliation"]["status"] == "AGREED"
    assert summary["xrpl_node_reconciliation"]["integrity_check_only"] is True
    assert summary["xrpl_node_reconciliation"]["model_admission_allowed"] is False
    assert summary["collection_policy"]["noncommercial_xrpl_nodes_included"] is True

    receipts = json.loads((tmp_path / "noncommercial-research" / "receipt_manifest.json").read_text(encoding="utf-8"))
    node_receipts = [item for item in receipts if item["source_id"] in XRPL_NODE_SOURCES]
    assert len(node_receipts) == 2
    expected_http_date = format_datetime(captured - timedelta(seconds=5), usegmt=True)
    assert all(item["source_http_date"] == expected_http_date for item in node_receipts)
    assert all(item["model_eligible_source"] is False for item in node_receipts)

    snapshot = json.loads((tmp_path / "noncommercial-research" / "snapshot.json").read_text(encoding="utf-8"))
    assert not any(item["feature_id"].startswith("xrp.network.xrpl.") for item in snapshot["records"])


def test_coinbase_backfill_ranges_are_contiguous_and_bounded():
    oldest_open = datetime(2026, 11, 7, 2, 0, tzinfo=timezone.utc)
    ranges = _coinbase_candle_backfill_ranges(oldest_open, 365)

    assert len(ranges) == 30
    assert ranges[0][0] == oldest_open - timedelta(days=365)
    assert ranges[-1][1] == oldest_open
    assert all(start < end for start, end in ranges)
    assert all(end - start <= timedelta(hours=300) for start, end in ranges)
    assert all(ranges[index][1] == ranges[index + 1][0] for index in range(len(ranges) - 1))

    for invalid_days in (0, -1, 366, True, 1.5):
        with pytest.raises(XRPIngestionError):
            _coinbase_candle_backfill_ranges(oldest_open, invalid_days)
    with pytest.raises(XRPIngestionError, match="align"):
        _coinbase_candle_backfill_ranges(oldest_open.replace(minute=1), 1)


def test_coinbase_manual_backfill_preserves_each_page_and_filters_boundary_overlap(tmp_path, monkeypatch):
    from urllib.parse import parse_qs, urlsplit

    captured = datetime(2026, 11, 7, 2, 0, tzinfo=timezone.utc)
    base_fetcher = _fake_fetcher(captured)
    page_payloads = {}

    monkeypatch.setattr("barrot_agent.evolution.xrp_public_ingestion.time.sleep", lambda *_args: None)

    def fetcher(source_id, url):
        if source_id == "coinbase_spot_candles" and "start=" in url:
            query = parse_qs(urlsplit(url).query)
            page_start = datetime.fromisoformat(query["start"][0].replace("Z", "+00:00"))
            page_end = datetime.fromisoformat(query["end"][0].replace("Z", "+00:00"))
            rows = [
                [int((page_start - timedelta(hours=1)).timestamp()), "1.00", "1.20", "1.10", "1.15", "10"],
                [int(page_start.timestamp()), "1.01", "1.21", "1.11", "1.16", "11"],
                [int(page_end.timestamp()), "1.02", "1.22", "1.12", "1.17", "12"],
            ]
            raw = json.dumps(rows, separators=(",", ":")).encode("utf-8")
            page_payloads[url] = raw
            return {"raw_bytes": raw, "payload": rows, "http_date": None}
        return base_fetcher(source_id, url)

    summary = run_ingestion(
        tmp_path / "coinbase-backfill",
        fetcher=fetcher,
        now=captured,
        coinbase_backfill_days=15,
    )

    backfill = summary["coinbase_backfill"]
    assert backfill["status"] == "COMPLETED"
    assert backfill["requested_days_before_oldest_latest_page_candle"] == 15
    assert backfill["pages_requested"] == 2
    assert backfill["pages_completed"] == 2
    assert backfill["pages_failed"] == 0
    assert backfill["empty_pages"] == 0
    assert backfill["candles_ingested"] == 2
    assert summary["source_receipt_count"] == len(SCHEDULED_ENDPOINTS) + len(_weekly_endpoints_for_capture(captured)) + 2

    receipts = json.loads((tmp_path / "coinbase-backfill" / "receipt_manifest.json").read_text(encoding="utf-8"))
    page_receipts = sorted(
        (item for item in receipts if item["source_id"].startswith("coinbase_spot_candles_backfill_page_")),
        key=lambda item: item["source_id"],
    )
    assert len(page_receipts) == 2
    for receipt in page_receipts:
        assert receipt["raw_content_sha256"] == hashlib.sha256(page_payloads[receipt["source_uri"]]).hexdigest()
        assert receipt["raw_bytes_retained"] is True
        assert receipt["model_eligible_source"] is True

    page_ranges = []
    for receipt in page_receipts:
        query = parse_qs(urlsplit(receipt["source_uri"]).query)
        page_ranges.append((
            datetime.fromisoformat(query["start"][0].replace("Z", "+00:00")),
            datetime.fromisoformat(query["end"][0].replace("Z", "+00:00")),
        ))
    assert page_ranges[0][1] == page_ranges[1][0]

    snapshot = json.loads((tmp_path / "coinbase-backfill" / "snapshot.json").read_text(encoding="utf-8"))
    coinbase_closes = [
        item for item in snapshot["records"]
        if item["feature_id"] == "xrp.spot.coinbase.1h.close_price"
    ]
    event_times = [item["event_time_utc"] for item in coinbase_closes]
    source_ids = {
        source["source_id"]
        for item in coinbase_closes
        for source in item["sources"]
    }
    assert "coinbase_spot_candles" in source_ids
    assert {
        "coinbase_spot_candles_backfill_page_001",
        "coinbase_spot_candles_backfill_page_002",
    }.issubset(source_ids)
    receipt_hashes = {item["source_id"]: item["raw_content_sha256"] for item in page_receipts}
    for item in coinbase_closes:
        for source in item["sources"]:
            if source["source_id"].startswith("coinbase_spot_candles_backfill_page_"):
                assert source["raw_content_sha256"] == receipt_hashes[source["source_id"]]
    assert len(event_times) == 4
    assert len(set(event_times)) == 4
    assert all(item["known_at_utc"] == "2026-11-07T02:00:00.000000Z" for item in coinbase_closes)
    assert all(item["event_time_utc"] < item["known_at_utc"] for item in coinbase_closes)


def test_coinbase_manual_backfill_records_empty_no_tick_pages_without_fabricating_candles(tmp_path, monkeypatch):
    captured = datetime(2026, 11, 7, 2, 0, tzinfo=timezone.utc)
    base_fetcher = _fake_fetcher(captured)
    monkeypatch.setattr("barrot_agent.evolution.xrp_public_ingestion.time.sleep", lambda *_args: None)

    def fetcher(source_id, url):
        if source_id == "coinbase_spot_candles" and "start=" in url:
            return {"raw_bytes": b"[]", "payload": [], "http_date": None}
        return base_fetcher(source_id, url)

    summary = run_ingestion(
        tmp_path / "coinbase-empty-backfill",
        fetcher=fetcher,
        now=captured,
        coinbase_backfill_days=1,
    )

    backfill = summary["coinbase_backfill"]
    assert backfill["status"] == "COMPLETED"
    assert backfill["pages_requested"] == 1
    assert backfill["pages_completed"] == 1
    assert backfill["pages_failed"] == 0
    assert backfill["empty_pages"] == 1
    assert backfill["candles_ingested"] == 0

    raw_only = json.loads((tmp_path / "coinbase-empty-backfill" / "raw_only_sources.json").read_text(encoding="utf-8"))
    assert any(
        item["source_id"] == "coinbase_spot_candles_backfill_page_001"
        and "no_in_range_completed_candles" in item["reason"]
        for item in raw_only
    )
    failures = json.loads((tmp_path / "coinbase-empty-backfill" / "source_failures.json").read_text(encoding="utf-8"))
    assert not any(item["source_id"] == "coinbase_spot_candles_backfill_page_001" for item in failures)


@pytest.mark.parametrize("days", [True, -1, 366, 1.5, "2"])
def test_coinbase_backfill_input_rejects_unbounded_or_non_integer_values(tmp_path, days):
    captured = datetime(2026, 11, 7, 2, 30, tzinfo=timezone.utc)
    with pytest.raises(XRPIngestionError):
        run_ingestion(
            tmp_path / "invalid-coinbase-backfill",
            fetcher=_fake_fetcher(captured),
            now=captured,
            coinbase_backfill_days=days,
        )


def test_coinbase_historical_backfill_is_manual_only_and_does_not_expand_permissions():
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "xrp-public-ingestion.yml"
    ).read_text(encoding="utf-8")

    assert "coinbase_backfill_days:" in workflow
    assert "type: number" in workflow
    assert "default: 0" in workflow
    assert "maximum 365 days" in workflow
    assert "--coinbase-backfill-days" in workflow
    assert "--walk-forward-horizons" in workflow
    assert "WALK_FORWARD_HORIZONS" in workflow
    assert "'1h,4h,24h,7d,30d'" in workflow
    assert "github.event.schedule == '15 0 * * *'" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "actions: write" not in workflow
    assert "secrets." not in workflow
    assert "cron: '3 * * * *'" in workflow
    assert "cron: '15 0 * * *'" in workflow


def test_bitbank_xrp_jpy_public_sources_are_allowlisted_and_scheduled():
    endpoint_map = dict(ENDPOINTS)
    assert endpoint_map["bitbank_spot_circuit_break"] == "https://public.bitbank.cc/xrp_jpy/circuit_break_info"
    assert endpoint_map["bitbank_spot_transactions"] == "https://public.bitbank.cc/xrp_jpy/transactions"
    assert endpoint_map["bitbank_spot_ticker"] == "https://public.bitbank.cc/xrp_jpy/ticker"
    assert endpoint_map["bitbank_spot_depth"] == "https://public.bitbank.cc/xrp_jpy/depth"
    assert "public.bitbank.cc" in ALLOWED_HOSTS
    assert BITBANK_SOURCE_IDS == {
        "bitbank_spot_circuit_break",
        "bitbank_spot_transactions",
        "bitbank_spot_ticker",
        "bitbank_spot_depth",
    }
    assert BITBANK_SOURCE_IDS.issubset({source_id for source_id, _url in SCHEDULED_ENDPOINTS})
    assert BITBANK_SOURCE_IDS.issubset(PARSERS)


def test_bitbank_ticker_uses_jpy_and_requires_synchronized_continuous_quotes():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)
    circuit = fetcher("bitbank_spot_circuit_break", dict(ENDPOINTS)["bitbank_spot_circuit_break"])
    response = fetcher("bitbank_spot_ticker", dict(ENDPOINTS)["bitbank_spot_ticker"])
    records, source_as_of, eligible, reason = PARSERS["bitbank_spot_ticker"](
        response["payload"],
        source_id="bitbank_spot_ticker",
        url=dict(ENDPOINTS)["bitbank_spot_ticker"],
        digest=hashlib.sha256(response["raw_bytes"]).hexdigest(),
        captured=captured,
        circuit_break_info=circuit["payload"],
    )
    by_id = {item["feature_id"]: item for item in records}
    assert eligible is True
    assert reason == ""
    assert source_as_of is not None
    assert by_id["xrp.spot.bitbank.best_bid"]["unit"] == "JPY/XRP"
    assert by_id["xrp.spot.bitbank.best_bid"]["model_eligible"] is True
    assert by_id["xrp.spot.bitbank.mid_price"]["model_eligible"] is True
    assert by_id["xrp.spot.bitbank.base_volume_24h"]["unit"] == "XRP/24h"
    assert by_id["xrp.spot.bitbank.last_price_snapshot"]["model_eligible"] is False
    assert by_id["xrp.spot.bitbank.last_price_snapshot"]["eligibility_reason"] == "ticker_snapshot_not_trade_event"


def test_bitbank_ticker_circuit_break_mode_quarantines_quotes_without_losing_volume():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)
    circuit = fetcher("bitbank_spot_circuit_break", dict(ENDPOINTS)["bitbank_spot_circuit_break"])["payload"]
    circuit["data"]["mode"] = "CIRCUIT_BREAK"
    circuit["data"]["estimated_itayose_price"] = "180.15"
    ticker = fetcher("bitbank_spot_ticker", dict(ENDPOINTS)["bitbank_spot_ticker"])["payload"]
    ticker["data"]["sell"] = "180.1"
    ticker["data"]["buy"] = "180.2"
    records, _source_as_of, eligible, _reason = PARSERS["bitbank_spot_ticker"](
        ticker,
        source_id="bitbank_spot_ticker",
        url=dict(ENDPOINTS)["bitbank_spot_ticker"],
        digest="a" * 64,
        captured=captured,
        circuit_break_info=circuit,
    )
    by_id = {item["feature_id"]: item for item in records}
    assert eligible is True
    assert by_id["xrp.spot.bitbank.best_bid"]["model_eligible"] is False
    assert "not_continuous" in by_id["xrp.spot.bitbank.best_bid"]["eligibility_reason"]
    assert by_id["xrp.spot.bitbank.base_volume_24h"]["model_eligible"] is True


def test_bitbank_depth_requires_fresh_circuit_state_and_rejects_crossed_normal_book():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)
    circuit = fetcher("bitbank_spot_circuit_break", dict(ENDPOINTS)["bitbank_spot_circuit_break"])["payload"]
    depth = fetcher("bitbank_spot_depth", dict(ENDPOINTS)["bitbank_spot_depth"])["payload"]
    records, _source_as_of, eligible, reason = PARSERS["bitbank_spot_depth"](
        depth,
        source_id="bitbank_spot_depth",
        url=dict(ENDPOINTS)["bitbank_spot_depth"],
        digest="b" * 64,
        captured=captured,
        circuit_break_info=circuit,
    )
    by_id = {item["feature_id"]: item for item in records}
    assert eligible is True
    assert reason == ""
    assert by_id["xrp.spot.bitbank.orderbook.mid_price"]["model_eligible"] is True
    assert by_id["xrp.spot.bitbank.orderbook.bid_depth_10bps"]["unit"] == "JPY"
    crossed = json.loads(json.dumps(depth))
    crossed["data"]["bids"] = [["180.3", "1000"]]
    crossed["data"]["asks"] = [["180.2", "1000"]]
    with pytest.raises(XRPIngestionError, match="crossed or locked"):
        PARSERS["bitbank_spot_depth"](
            crossed,
            source_id="bitbank_spot_depth",
            url=dict(ENDPOINTS)["bitbank_spot_depth"],
            digest="c" * 64,
            captured=captured,
            circuit_break_info=circuit,
        )


def test_bitbank_depth_circuit_break_snapshot_is_retained_but_not_model_eligible():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    fetcher = _fake_fetcher(captured)
    circuit = fetcher("bitbank_spot_circuit_break", dict(ENDPOINTS)["bitbank_spot_circuit_break"])["payload"]
    circuit["data"]["mode"] = "CIRCUIT_BREAK"
    circuit["data"]["estimated_itayose_price"] = "180.15"
    depth = fetcher("bitbank_spot_depth", dict(ENDPOINTS)["bitbank_spot_depth"])["payload"]
    depth["data"]["bids"] = [["180.3", "1000"]]
    depth["data"]["asks"] = [["180.2", "1000"]]
    records, _source_as_of, eligible, _reason = PARSERS["bitbank_spot_depth"](
        depth,
        source_id="bitbank_spot_depth",
        url=dict(ENDPOINTS)["bitbank_spot_depth"],
        digest="d" * 64,
        captured=captured,
        circuit_break_info=circuit,
    )
    assert eligible is True
    assert records
    assert all(item["model_eligible"] is False for item in records)
    assert all("not_continuous" in item["eligibility_reason"] for item in records)


def test_bitbank_circuit_break_context_is_raw_only_and_validates_mode():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    response = _fake_fetcher(captured)("bitbank_spot_circuit_break", dict(ENDPOINTS)["bitbank_spot_circuit_break"])
    records, source_as_of, eligible, reason = PARSERS["bitbank_spot_circuit_break"](
        response["payload"],
        source_id="bitbank_spot_circuit_break",
        url=dict(ENDPOINTS)["bitbank_spot_circuit_break"],
        digest=hashlib.sha256(response["raw_bytes"]).hexdigest(),
        captured=captured,
    )
    assert records == []
    assert source_as_of is not None
    assert eligible is False
    assert reason == "market_state_context_only_not_numeric_feature"
    invalid = json.loads(json.dumps(response["payload"]))
    invalid["data"]["mode"] = "UNKNOWN"
    with pytest.raises(XRPIngestionError, match="mode is unknown"):
        PARSERS["bitbank_spot_circuit_break"](
            invalid,
            source_id="bitbank_spot_circuit_break",
            url=dict(ENDPOINTS)["bitbank_spot_circuit_break"],
            digest="e" * 64,
            captured=captured,
        )


def test_bitbank_transactions_create_point_in_time_taker_events_and_research_summary():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    response = _fake_fetcher(captured)("bitbank_spot_transactions", dict(ENDPOINTS)["bitbank_spot_transactions"])
    records, source_as_of, eligible, reason = PARSERS["bitbank_spot_transactions"](
        response["payload"],
        source_id="bitbank_spot_transactions",
        url=dict(ENDPOINTS)["bitbank_spot_transactions"],
        digest=hashlib.sha256(response["raw_bytes"]).hexdigest(),
        captured=captured,
    )
    assert eligible is False
    assert reason == "latest_60_trade_sample_incomplete_coverage"
    assert source_as_of is not None
    assert len(records) == 12
    assert len({item["record_id"] for item in records}) == 12
    assert all(item["model_eligible"] is False for item in records)
    assert all(item["quality_status"] == "unverified" for item in records)
    assert all(item["known_at_utc"] > item["event_time_utc"] for item in records)
    signed_amounts = [item["value"] for item in records if item["feature_id"] == "xrp.spot.bitbank.trade.signed_amount"]
    assert signed_amounts == [100.0, -60.0]
    summary = _bitbank_transactions_research_summary(response["payload"])
    assert summary["window_kind"] == "latest_60_trades_variable_duration"
    assert summary["net_taker_flow_xrp"] == 40.0
    assert summary["net_taker_flow_jpy"] == 7209.0
    assert summary["model_eligible"] is False


def test_bitbank_transactions_reject_duplicate_ids_and_future_execution_times():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    response = _fake_fetcher(captured)("bitbank_spot_transactions", dict(ENDPOINTS)["bitbank_spot_transactions"])
    parser = PARSERS["bitbank_spot_transactions"]
    duplicate = json.loads(json.dumps(response["payload"]))
    duplicate["data"]["transactions"][1]["transaction_id"] = 101
    with pytest.raises(XRPIngestionError, match="positive and unique"):
        parser(duplicate, source_id="bitbank_spot_transactions", url=dict(ENDPOINTS)["bitbank_spot_transactions"], digest="f" * 64, captured=captured)
    future = json.loads(json.dumps(response["payload"]))
    future["data"]["transactions"][0]["executed_at"] = _iso_ms(captured + timedelta(seconds=1))
    with pytest.raises(XRPIngestionError, match="later than capture"):
        parser(future, source_id="bitbank_spot_transactions", url=dict(ENDPOINTS)["bitbank_spot_transactions"], digest="1" * 64, captured=captured)


def test_bitbank_sources_integrate_into_full_ingestion_and_research_only_flow_summary(tmp_path):
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    summary = run_ingestion(tmp_path / "bitbank-run", fetcher=_fake_fetcher(captured), now=captured)
    snapshot = json.loads((tmp_path / "bitbank-run" / "snapshot.json").read_text(encoding="utf-8"))
    research = json.loads((tmp_path / "bitbank-run" / "research_only_observations.json").read_text(encoding="utf-8"))
    raw_only = json.loads((tmp_path / "bitbank-run" / "raw_only_sources.json").read_text(encoding="utf-8"))
    bitbank = [item for item in snapshot["records"] if item.get("venue") == "Bitbank"]
    assert summary["snapshot_status"] == "verified"
    assert summary["source_receipt_count"] == len(SCHEDULED_ENDPOINTS) + len(_weekly_endpoints_for_capture(captured))
    assert summary["source_failure_count"] == 0
    assert any(item["feature_id"] == "xrp.spot.bitbank.orderbook.mid_price" for item in bitbank)
    trade_summary = next(item for item in research["observations"] if item["observation_type"] == "bitbank_latest_60_trade_sample")
    assert trade_summary["net_taker_flow_xrp"] == 40.0
    assert trade_summary["model_eligible"] is False
    assert any(item["source_id"] == "bitbank_spot_circuit_break" for item in raw_only)
    assert any(item["source_id"] == "bitbank_spot_transactions" for item in raw_only)



def test_bybit_spot_sources_are_allowlisted_and_scheduled():
    endpoint_map = dict(ENDPOINTS)
    assert endpoint_map["bybit_spot_ticker"] == "https://api.bybit.com/v5/market/tickers?category=spot&symbol=XRPUSDT"
    assert endpoint_map["bybit_spot_depth"] == "https://api.bybit.com/v5/market/orderbook?category=spot&symbol=XRPUSDT&limit=100"
    assert "api.bybit.com" in ALLOWED_HOSTS
    assert {"bybit_spot_ticker", "bybit_spot_depth"}.issubset(PARSERS)
    assert {"bybit_spot_ticker", "bybit_spot_depth"}.issubset(
        {source_id for source_id, _url in SCHEDULED_ENDPOINTS}
    )


def test_bybit_ticker_uses_response_time_and_rejects_stale_or_crossed_quotes():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    source_id = "bybit_spot_ticker"
    url = dict(ENDPOINTS)[source_id]
    response = _fake_fetcher(captured)(source_id, url)
    parser = PARSERS[source_id]
    digest = hashlib.sha256(response["raw_bytes"]).hexdigest()
    records, event_time, eligible, reason = parser(
        response["payload"], source_id=source_id, url=url, digest=digest, captured=captured
    )
    assert event_time == (captured - timedelta(seconds=1)).isoformat(timespec="microseconds").replace("+00:00", "Z")
    assert eligible is True
    assert reason == ""
    assert any(item["feature_id"] == "xrp.spot.bybit.last_price" for item in records)
    assert all(item["unit"] == "USDT/XRP" for item in records if item["feature_id"].endswith(("last_price", "best_bid", "best_ask")))

    stale = json.loads(json.dumps(response["payload"]))
    stale["time"] = _iso_ms(captured - timedelta(seconds=301))
    _stale_records, _stale_time, stale_eligible, stale_reason = parser(
        stale, source_id=source_id, url=url, digest=digest, captured=captured
    )
    assert stale_eligible is False
    assert "older_than_300_seconds" in stale_reason

    crossed = json.loads(json.dumps(response["payload"]))
    crossed["result"]["list"][0]["ask1Price"] = "1.2898"
    with pytest.raises(XRPIngestionError, match="crossed or locked"):
        parser(crossed, source_id=source_id, url=url, digest=digest, captured=captured)


def test_bybit_orderbook_uses_matching_engine_cts_and_computes_depth():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    source_id = "bybit_spot_depth"
    url = dict(ENDPOINTS)[source_id]
    response = _fake_fetcher(captured)(source_id, url)
    parser = PARSERS[source_id]
    digest = hashlib.sha256(response["raw_bytes"]).hexdigest()
    records, event_time, eligible, reason = parser(
        response["payload"], source_id=source_id, url=url, digest=digest, captured=captured
    )
    assert event_time == (captured - timedelta(seconds=2)).isoformat(timespec="microseconds").replace("+00:00", "Z")
    assert event_time != (captured - timedelta(milliseconds=1500)).isoformat(timespec="microseconds").replace("+00:00", "Z")
    assert eligible is True
    assert reason == ""
    by_feature = {item["feature_id"]: item for item in records}
    assert by_feature["xrp.spot.bybit.orderbook.mid_price"]["value"] == pytest.approx(1.290)
    assert by_feature["xrp.spot.bybit.orderbook.bid_depth_10bps"]["value"] == pytest.approx(1289.0)
    assert by_feature["xrp.spot.bybit.orderbook.ask_depth_10bps"]["value"] == pytest.approx(1549.2)
    assert by_feature["xrp.spot.bybit.orderbook.depth_imbalance_10bps"]["model_eligible"] is True
    assert any("Retail Price Improvement (RPI) orders are excluded" in item for item in by_feature["xrp.spot.bybit.orderbook.mid_price"]["limitations"])


def test_bybit_orderbook_fails_closed_on_missing_matching_engine_time_or_crossed_levels():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    source_id = "bybit_spot_depth"
    url = dict(ENDPOINTS)[source_id]
    response = _fake_fetcher(captured)(source_id, url)
    parser = PARSERS[source_id]
    missing_cts = json.loads(json.dumps(response["payload"]))
    del missing_cts["result"]["cts"]
    with pytest.raises(XRPIngestionError, match="matching-engine timestamp"):
        parser(missing_cts, source_id=source_id, url=url, digest="a" * 64, captured=captured)

    crossed = json.loads(json.dumps(response["payload"]))
    crossed["result"]["a"][0][0] = "1.288"
    with pytest.raises(XRPIngestionError, match="crossed or locked"):
        parser(crossed, source_id=source_id, url=url, digest="b" * 64, captured=captured)




def test_bybit_linear_sources_are_allowlisted_and_scheduled():
    endpoint_map = dict(ENDPOINTS)
    expected = {
        "bybit_linear_ticker": "https://api.bybit.com/v5/market/tickers?category=linear&symbol=XRPUSDT",
        "bybit_linear_open_interest": "https://api.bybit.com/v5/market/open-interest?category=linear&symbol=XRPUSDT&intervalTime=1h&limit=200",
        "bybit_linear_funding_history": "https://api.bybit.com/v5/market/funding/history?category=linear&symbol=XRPUSDT&limit=200",
    }
    assert all(endpoint_map[source_id] == url for source_id, url in expected.items())
    assert set(expected).issubset(xrp_ingestion.BYBIT_SOURCE_IDS)
    assert set(expected).issubset(PARSERS)
    assert set(expected).issubset({source_id for source_id, _url in SCHEDULED_ENDPOINTS})


def test_bybit_linear_ticker_preserves_open_interest_conventions_and_funding_interval():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    source_id = "bybit_linear_ticker"
    url = dict(ENDPOINTS)[source_id]
    response = _fake_fetcher(captured)(source_id, url)
    parser = PARSERS[source_id]
    digest = hashlib.sha256(response["raw_bytes"]).hexdigest()
    records, event_time, eligible, reason = parser(
        response["payload"], source_id=source_id, url=url, digest=digest, captured=captured
    )
    assert event_time == (captured - timedelta(seconds=2)).isoformat(timespec="microseconds").replace("+00:00", "Z")
    assert eligible is True
    assert reason == ""
    by_feature = {item["feature_id"]: item for item in records}
    assert by_feature["xrp.perpetual.bybit.open_interest_xrp_both_sides"]["value"] == 2_500_000
    assert "both sides" in by_feature["xrp.perpetual.bybit.open_interest_xrp_both_sides"]["unit"]
    assert by_feature["xrp.perpetual.bybit.open_interest_xrp_single_side"]["value"] == 1_250_000
    assert by_feature["xrp.perpetual.bybit.open_interest_value_usdt_both_sides"]["value"] == 3_225_000
    assert by_feature["xrp.perpetual.bybit.open_interest_value_usdt_single_side"]["value"] == 1_612_500
    assert by_feature["xrp.perpetual.bybit.current_funding_rate"]["value"] == pytest.approx(0.0001)
    assert by_feature["xrp.perpetual.bybit.current_funding_rate"]["unit"] == "fraction_per_funding_interval"
    assert by_feature["xrp.perpetual.bybit.current_funding_rate"]["model_eligible"] is True
    assert by_feature["xrp.perpetual.bybit.funding_interval_hours"]["value"] == 8
    assert any("USDT is not converted to USD" in item for item in by_feature["xrp.perpetual.bybit.last_price"]["limitations"])

    stale = json.loads(json.dumps(response["payload"]))
    stale["time"] = _iso_ms(captured - timedelta(seconds=301))
    _stale_records, _stale_time, stale_eligible, stale_reason = parser(
        stale, source_id=source_id, url=url, digest=digest, captured=captured
    )
    assert stale_eligible is False
    assert "older_than_300_seconds" in stale_reason

    crossed = json.loads(json.dumps(response["payload"]))
    crossed["result"]["list"][0]["ask1Price"] = crossed["result"]["list"][0]["bid1Price"]
    with pytest.raises(XRPIngestionError, match="crossed or locked"):
        parser(crossed, source_id=source_id, url=url, digest=digest, captured=captured)

    missing_interval = json.loads(json.dumps(response["payload"]))
    del missing_interval["result"]["list"][0]["fundingIntervalHour"]
    partial, _partial_time, partial_eligible, _partial_reason = parser(
        missing_interval, source_id=source_id, url=url, digest=digest, captured=captured
    )
    partial_features = {item["feature_id"]: item for item in partial}
    assert partial_eligible is True
    assert partial_features["xrp.perpetual.bybit.last_price"]["model_eligible"] is True
    assert partial_features["xrp.perpetual.bybit.current_funding_rate"]["model_eligible"] is False
    assert partial_features["xrp.perpetual.bybit.current_funding_rate"]["eligibility_reason"] == "funding_interval_missing"


def test_bybit_linear_open_interest_history_preserves_both_sides_and_point_in_time_availability():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    source_id = "bybit_linear_open_interest"
    url = dict(ENDPOINTS)[source_id]
    response = _fake_fetcher(captured)(source_id, url)
    parser = PARSERS[source_id]
    digest = hashlib.sha256(response["raw_bytes"]).hexdigest()
    records, latest_time, eligible, reason = parser(
        response["payload"], source_id=source_id, url=url, digest=digest, captured=captured
    )
    assert eligible is True
    assert reason == ""
    assert latest_time == (captured - timedelta(hours=1)).isoformat(timespec="microseconds").replace("+00:00", "Z")
    both_sides = [item for item in records if item["feature_id"] == "xrp.perpetual.bybit.1h.open_interest_xrp_both_sides"]
    single_side = [item for item in records if item["feature_id"] == "xrp.perpetual.bybit.1h.open_interest_xrp_single_side"]
    assert [item["value"] for item in both_sides] == [2_500_000, 2_510_000]
    assert [item["value"] for item in single_side] == [1_250_000, 1_255_000]
    assert both_sides[0]["event_time_utc"] < both_sides[1]["event_time_utc"]
    assert single_side[0]["event_time_utc"] < single_side[1]["event_time_utc"]
    assert all(item["known_at_utc"] == captured.isoformat(timespec="microseconds").replace("+00:00", "Z") for item in records)
    assert all(item["model_eligible"] is True for item in records)
    assert any("nextPageCursor" in item for item in records[0]["limitations"])

    missing_single = json.loads(json.dumps(response["payload"]))
    del missing_single["result"]["list"][0]["singleOpenInterest"]
    partial, _partial_time, partial_eligible, _partial_reason = parser(
        missing_single, source_id=source_id, url=url, digest=digest, captured=captured
    )
    assert partial_eligible is True
    assert len([item for item in partial if item["feature_id"] == "xrp.perpetual.bybit.1h.open_interest_xrp_both_sides"]) == 2
    assert len([item for item in partial if item["feature_id"] == "xrp.perpetual.bybit.1h.open_interest_xrp_single_side"]) == 1
    assert any("no single-side value is inferred" in item for item in partial[0]["limitations"])

    duplicate = json.loads(json.dumps(response["payload"]))
    duplicate["result"]["list"][1]["timestamp"] = duplicate["result"]["list"][0]["timestamp"]
    with pytest.raises(XRPIngestionError, match="duplicate event timestamp"):
        parser(duplicate, source_id=source_id, url=url, digest=digest, captured=captured)

    future = json.loads(json.dumps(response["payload"]))
    future["result"]["list"][0]["timestamp"] = _iso_ms(captured + timedelta(seconds=1))
    with pytest.raises(XRPIngestionError, match="later than capture time"):
        parser(future, source_id=source_id, url=url, digest=digest, captured=captured)

    mixed = json.loads(json.dumps(response["payload"]))
    mixed["result"]["list"].append({
        "openInterest": "2505000",
        "singleOpenInterest": "1252500",
        "timestamp": _iso_ms(captured - timedelta(minutes=90)),
    })
    with pytest.raises(XRPIngestionError, match="not strictly monotonic"):
        parser(mixed, source_id=source_id, url=url, digest=digest, captured=captured)


def test_bybit_linear_funding_history_uses_actual_settlement_times_without_assuming_eight_hours():
    captured = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    source_id = "bybit_linear_funding_history"
    url = dict(ENDPOINTS)[source_id]
    response = _fake_fetcher(captured)(source_id, url)
    parser = PARSERS[source_id]
    digest = hashlib.sha256(response["raw_bytes"]).hexdigest()
    records, latest_time, eligible, reason = parser(
        response["payload"], source_id=source_id, url=url, digest=digest, captured=captured
    )
    assert eligible is True
    assert reason == ""
    assert latest_time == (captured - timedelta(hours=1)).isoformat(timespec="microseconds").replace("+00:00", "Z")
    assert [item["value"] for item in records] == pytest.approx([-0.0002, 0.0001])
    assert records[0]["event_time_utc"] == (captured - timedelta(hours=6)).isoformat(timespec="microseconds").replace("+00:00", "Z")
    assert records[1]["event_time_utc"] == (captured - timedelta(hours=1)).isoformat(timespec="microseconds").replace("+00:00", "Z")
    assert records[0]["unit"] == "fraction_per_settlement"
    assert records[0]["aggregation_window"] == "funding_event"
    first = datetime.fromisoformat(records[0]["event_time_utc"].replace("Z", "+00:00"))
    second = datetime.fromisoformat(records[1]["event_time_utc"].replace("Z", "+00:00"))
    assert (second - first).total_seconds() == 5 * 3600
    assert any("not assumed to be eight hours" in item for item in records[0]["limitations"])
    assert all(item["known_at_utc"] == captured.isoformat(timespec="microseconds").replace("+00:00", "Z") for item in records)

    duplicate = json.loads(json.dumps(response["payload"]))
    duplicate["result"]["list"][1]["fundingRateTimestamp"] = duplicate["result"]["list"][0]["fundingRateTimestamp"]
    with pytest.raises(XRPIngestionError, match="duplicate event timestamp"):
        parser(duplicate, source_id=source_id, url=url, digest=digest, captured=captured)

    future = json.loads(json.dumps(response["payload"]))
    future["result"]["list"][0]["fundingRateTimestamp"] = _iso_ms(captured + timedelta(seconds=1))
    with pytest.raises(XRPIngestionError, match="later than capture time"):
        parser(future, source_id=source_id, url=url, digest=digest, captured=captured)


def test_bybit_linear_403_is_recorded_as_provider_access_failure():
    failure = _source_failure_record(
        "bybit_linear_ticker",
        "https://api.bybit.com/v5/market/tickers?category=linear&symbol=XRPUSDT",
        "2026-11-07T14:00:00Z",
        XRPSourceHTTPError("bybit_linear_ticker", 403, "Forbidden"),
    )
    assert failure["http_status_code"] == 403
    assert failure["error_category"] == "provider_http_forbidden"
    assert failure["model_eligible"] is False
    assert failure["retryable"] is False
    assert failure["provider_access_documentation_url"] == "https://bybit-exchange.github.io/docs/v5/guide"


def test_public_json_fetch_preserves_http_status_and_reason(monkeypatch):
    url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=XRPUSDT"

    def forbidden(*_args, **_kwargs):
        raise HTTPError(url, 403, "Forbidden", {}, BytesIO(b""))

    monkeypatch.setattr(xrp_ingestion, "_open_public_request", forbidden)
    with pytest.raises(XRPSourceHTTPError) as error:
        fetch_public_json("bybit_spot_ticker", url)
    assert error.value.status_code == 403
    assert error.value.source_id == "bybit_spot_ticker"
    assert error.value.reason == "Forbidden"


def test_bybit_403_failure_is_recorded_as_access_forbidden_not_empty_data():
    failure = _source_failure_record(
        "bybit_spot_ticker",
        "https://api.bybit.com/v5/market/tickers?category=spot&symbol=XRPUSDT",
        "2026-11-07T14:00:00Z",
        XRPSourceHTTPError("bybit_spot_ticker", 403, "Forbidden"),
    )
    assert failure["http_status_code"] == 403
    assert failure["error_category"] == "provider_http_forbidden"
    assert failure["model_eligible"] is False
    assert failure["retryable"] is False
    assert "runner region is unverified" in failure["access_restriction_hint"]
    assert failure["provider_access_documentation_url"] == "https://bybit-exchange.github.io/docs/v5/guide"


def test_http_429_failure_is_classified_as_provider_rate_limited():
    failure = _source_failure_record(
        "binance_spot_ticker",
        "https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT",
        "2026-11-07T14:00:00Z",
        XRPSourceHTTPError("binance_spot_ticker", 429, "Too Many Requests"),
    )
    assert failure["http_status_code"] == 429
    assert failure["error_category"] == "provider_rate_limited"
    assert failure["retryable"] is True
    assert failure["model_eligible"] is False


def test_ingestion_records_bybit_403_with_source_url_and_capture_time(tmp_path):
    captured = datetime(2026, 11, 7, 14, 0, tzinfo=timezone.utc)
    base_fetcher = _fake_fetcher(captured)

    def fetcher(source_id: str, url: str):
        if source_id == "bybit_spot_ticker":
            raise XRPSourceHTTPError(source_id, 403, "Forbidden")
        return base_fetcher(source_id, url)

    summary = run_ingestion(tmp_path, fetcher=fetcher, now=captured)
    failures = json.loads((tmp_path / "source_failures.json").read_text(encoding="utf-8"))
    bybit_failure = next(item for item in failures if item["source_id"] == "bybit_spot_ticker")
    receipts = json.loads((tmp_path / "receipt_manifest.json").read_text(encoding="utf-8"))

    assert summary["source_failure_count"] == 1
    assert bybit_failure["source_uri"] == "https://api.bybit.com/v5/market/tickers?category=spot&symbol=XRPUSDT"
    assert bybit_failure["captured_at_utc"] == "2026-11-07T14:00:00.000000Z"
    assert bybit_failure["http_status_code"] == 403
    assert bybit_failure["error_category"] == "provider_http_forbidden"
    assert bybit_failure["model_eligible"] is False
    assert not any(item["source_id"] == "bybit_spot_ticker" for item in receipts)


def test_weekly_cftc_endpoint_is_selected_only_after_scheduled_publication(monkeypatch):
    saturday_daily_run = datetime(2026, 11, 7, 0, 15, tzinfo=timezone.utc)
    saturday_hourly_run = datetime(2026, 11, 7, 0, 3, tzinfo=timezone.utc)
    friday_hourly_run = datetime(2026, 11, 6, 21, 3, tzinfo=timezone.utc)
    saturday_late_run = datetime(2026, 11, 7, 2, 15, tzinfo=timezone.utc)
    delayed_monday_run = datetime(2026, 11, 16, 21, 3, tzinfo=timezone.utc)
    unlisted_monday_run = datetime(2026, 11, 9, 21, 3, tzinfo=timezone.utc)

    assert len(WEEKLY_ENDPOINTS) == 1
    assert WEEKLY_ENDPOINTS[0][0] == "cftc_tff_financial_futures"
    assert _weekly_endpoints_for_capture(saturday_daily_run) == WEEKLY_ENDPOINTS
    assert _weekly_endpoints_for_capture(saturday_hourly_run) == ()
    assert _weekly_endpoints_for_capture(friday_hourly_run) == ()
    assert _weekly_endpoints_for_capture(saturday_late_run) == ()
    assert _weekly_endpoints_for_capture(delayed_monday_run) == WEEKLY_ENDPOINTS
    assert _weekly_endpoints_for_capture(unlisted_monday_run) == ()

    monkeypatch.setattr(xrp_ingestion, "CFTC_SEMIWEEKLY_EFFECTIVE_DATE", "2026-12-01")
    wednesday_after_effective = datetime(2026, 12, 2, 21, 3, tzinfo=timezone.utc)
    friday_after_effective = datetime(2026, 12, 4, 21, 3, tzinfo=timezone.utc)
    monday_after_effective = datetime(2026, 12, 7, 21, 3, tzinfo=timezone.utc)
    assert _weekly_endpoints_for_capture(wednesday_after_effective) == WEEKLY_ENDPOINTS
    assert _weekly_endpoints_for_capture(friday_after_effective) == WEEKLY_ENDPOINTS
    assert _weekly_endpoints_for_capture(monday_after_effective) == ()

def test_weekly_cftc_tff_capture_is_receipted_and_research_only_on_saturday_daily_run(tmp_path):
    captured = datetime(2026, 11, 7, 0, 15, tzinfo=timezone.utc)
    summary = run_ingestion(tmp_path / "weekly", fetcher=_fake_fetcher(captured), now=captured)

    assert summary["source_receipt_count"] == len(SCHEDULED_ENDPOINTS) + 1
    assert summary["source_failure_count"] == 0
    assert summary["weekly_source_policy"]["captured_source_ids"] == [
        "cftc_tff_financial_futures"
    ]
    assert summary["weekly_source_policy"]["parsed_source_ids"] == [
        "cftc_tff_financial_futures"
    ]
    assert summary["weekly_source_policy"]["raw_only_source_ids"] == []

    raw_only = json.loads(
        (tmp_path / "weekly" / "raw_only_sources.json").read_text(encoding="utf-8")
    )
    assert not any(item["source_id"] == "cftc_tff_financial_futures" for item in raw_only)

    research_only = json.loads(
        (tmp_path / "weekly" / "research_only_observations.json").read_text(encoding="utf-8")
    )
    cftc_observation = next(
        item for item in research_only
        if item["source_id"] == "cftc_tff_financial_futures"
    )
    assert cftc_observation["observation_type"] == "cftc_tff_xrp_futures_only_position_features"
    assert cftc_observation["source_data_as_of_utc"] == "2026-11-03T00:00:00.000000Z"
    assert cftc_observation["timestamp_precision"] == "date_only"
    assert cftc_observation["model_eligible"] is False
    assert cftc_observation["feature_count"] == 21
    features = {item["feature_id"]: item for item in cftc_observation["features"]}
    assert features["xrp.derivatives.cftc.tff.cme_xrp.open_interest_contracts"]["value"] == 7216
    assert features["xrp.derivatives.cftc.tff.coinbase_nano_xrp.open_interest_contracts"]["value"] == 32505
    assert features["xrp.derivatives.cftc.tff.coinbase_nano_xrp.open_interest_change_contracts"]["value"] == -32864
    assert features["xrp.derivatives.cftc.tff.coinbase_nano_xrp_perp_style.open_interest_contracts"]["value"] == 38392
    assert features["xrp.derivatives.cftc.tff.coinbase_nano_xrp.leveraged_funds_net_contracts"]["value"] == -2308
    assert features["xrp.derivatives.cftc.tff.coinbase_nano_xrp_perp_style.other_reportables_net_contracts"]["value"] == 26005

    receipt_manifest = json.loads(
        (tmp_path / "weekly" / "receipt_manifest.json").read_text(encoding="utf-8")
    )
    cftc_receipt = next(
        item for item in receipt_manifest
        if item["source_id"] == "cftc_tff_financial_futures"
    )
    assert cftc_receipt["model_eligible_source"] is False
    assert cftc_receipt["source_data_as_of_utc"] == "2026-11-03T00:00:00.000000Z"
    assert cftc_receipt["source_http_date"] == "Fri, 06 Nov 2026 20:30:00 GMT"
    assert cftc_receipt["raw_bytes_retained"] is True
    assert len(cftc_receipt["raw_content_sha256"]) == 64

    snapshot = json.loads(
        (tmp_path / "weekly" / "snapshot.json").read_text(encoding="utf-8")
    )
    assert not any(
        source["source_id"] == "cftc_tff_financial_futures"
        for record in snapshot["records"]
        for source in record["sources"]
    )
    assert summary["forecast_status"] == "NOT_ISSUED"