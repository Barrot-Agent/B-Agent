from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

import pytest

from barrot_agent.evolution.feature_store import HistoricalFeatureStore
from barrot_agent.evolution.xrp_public_ingestion import (
    RawReceiptArchive,
    _walk_forward_report,
    _coinbase_candle_backfill_ranges,
    XRPIngestionError,
    fetch_public_json,
    fetch_public_csv,
    fetch_public_html,
    fetch_public_rpc,
    _open_public_request,
    _default_public_fetcher,
    run_ingestion,
    ALLOWED_HOSTS,
    ENDPOINTS,
    SCHEDULED_ENDPOINTS,
    PARSERS,
    XRPL_NODE_SOURCES,
    _reconcile_xrpl_node_records,
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
        }:
            html_by_source = {
                "xrp_etf_xrpr_issuer_page": "<html><title>REX-Osprey XRP ETF XRPR</title><p>As of 11/03/2026</p><table><tr><td>CoinShares XRP ETP</td></tr></table></html>",
                "xrp_etf_bitwise_issuer_page": "<html><title>Bitwise XRP ETF</title><p>Data as of 11/03/2026</p><td>XRP in Trust</td><td>Digital Asset Custodian</td></html>",
                "xrp_etf_grayscale_gxrp_issuer_page": "<html><title>Grayscale XRP Trust ETF</title><p>As of 11/04/2026</p><td>TOTAL XRP IN FUND</td><td>DIGITAL ASSET CUSTODIAN</td></html>",
            }
            html_text = html_by_source[source_id]
            return {
                "raw_bytes": html_text.encode("utf-8"),
                "payload": {"html_text": html_text},
                "http_date": "Thu, 05 Nov 2026 04:00:00 GMT",
            }
        else:
            raise AssertionError(source_id)
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        response = {"raw_bytes": raw, "payload": payload}
        if source_id in {"coinbase_spot_ticker", "kraken_spot_ticker", "kraken_spot_depth", "xrp_exchange_balances_json"} or source_id in XRPL_NODE_SOURCES:
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
    assert summary["coinbase_backfill"]["status"] == "NOT_REQUESTED"
    assert summary["coinbase_backfill"]["pages_requested"] == 0
    assert summary["source_receipt_count"] == len(ENDPOINTS) - len(XRPL_NODE_SOURCES), (
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
    assert set(summary["collection_policy"]["excluded_noncommercial_xrpl_node_source_ids"]) == set(XRPL_NODE_SOURCES)

    snapshot = json.loads((tmp_path / "run" / "snapshot.json").read_text(encoding="utf-8"))
    historical = next(
        item for item in snapshot["records"]
        if item["feature_id"] == "xrp.spot.binance.1h.close_price"
    )
    assert historical["event_time_utc"] < historical["known_at_utc"]
    assert historical["known_at_utc"] == "2026-11-04T12:30:00.000000Z"
    assert "first observed at this capture time" in historical["limitations"][0]

    assert summary["adapter_version"] == "xrp-public-market-v3.11"
    assert summary["parser_version"] == "xrp-public-market-v3.10"
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
    receipts = json.loads((tmp_path / "run" / "receipt_manifest.json").read_text(encoding="utf-8"))
    manifest = {item["source_id"]: item for item in receipts}
    # The default/scheduled collector must not request non-commercial public-node endpoints.
    assert not set(XRPL_NODE_SOURCES).intersection(manifest)
    assert manifest["xrp_etf_flows_aggregator"]["model_eligible_source"] is False
    assert manifest["xrp_etf_flows_aggregator"]["source_data_as_of_utc"] is None
    assert manifest["xrp_exchange_balances_json"]["model_eligible_source"] is False
    assert manifest["xrp_exchange_balances_json"]["source_data_as_of_utc"] is None
    assert manifest["xrp_exchange_balances_json"]["raw_bytes_retained"] is False
    assert manifest["xrp_exchange_balances_json"]["raw_payload_path"] is None
    assert "attribution" in manifest["xrp_exchange_balances_json"]["raw_retention_reason"]
    assert manifest["xrp_etf_flows_csv"]["model_eligible_source"] is False
    assert manifest["xrp_etf_flows_csv"]["source_data_as_of_utc"] is None
    assert len(manifest["xrp_etf_flows_csv"]["raw_content_sha256"]) == 64
    assert manifest["xrp_etf_flows_csv"]["raw_bytes_retained"] is False
    assert manifest["xrp_etf_flows_csv"]["raw_payload_path"] is None
    assert "commercial redistribution" in manifest["xrp_etf_flows_csv"]["raw_retention_reason"]
    research_only = json.loads((tmp_path / "run" / "research_only_observations.json").read_text(encoding="utf-8"))
    assert research_only["model_eligible"] is False
    assert research_only["observation_count"] == 1
    aggregate = research_only["observations"][0]
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
    assert workflow.index("Upload immutable raw-source receipts") < workflow.index("Upload per-run point-in-time feature-store checkpoint") < workflow.index("Save cumulative feature-store cache after successful artifact publication")
    assert workflow.index("Upload daily point-in-time feature-store backup and walk-forward report") < workflow.index("Save cumulative feature-store cache after successful artifact publication")
    assert workflow.count("actions/cache/save@v4") == 1
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
    assert "external WORM" in feature_contract
    assert "no scheduled main-branch run is verified" in forecast_contract


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
    ],
)
def test_additional_primary_issuer_pages_are_registered_and_retained_raw_only(source_id, host, url):
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
    assert "raw_only" in reason


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
    assert len(SCHEDULED_ENDPOINTS) == len(ENDPOINTS) - len(XRPL_NODE_SOURCES)


def test_explicit_noncommercial_xrpl_research_capture_is_never_model_eligible(tmp_path):
    captured = datetime(2026, 11, 5, 4, 0, tzinfo=timezone.utc)
    summary = run_ingestion(
        tmp_path / "noncommercial-research",
        fetcher=_fake_fetcher(captured),
        now=captured,
        include_noncommercial_xrpl_nodes=True,
    )

    assert summary["source_receipt_count"] == len(ENDPOINTS)
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


def test_coinbase_manual_backfill_preserves_each_page_and_filters_boundary_overlap(tmp_path, monkeypatch):
    from urllib.parse import parse_qs, urlsplit

    captured = datetime(2026, 11, 7, 2, 30, tzinfo=timezone.utc)
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
    assert summary["source_receipt_count"] == len(ENDPOINTS) - len(XRPL_NODE_SOURCES) + 2

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
    assert len(event_times) == 4
    assert len(set(event_times)) == 4
    assert all(item["known_at_utc"] == "2026-11-07T02:30:00.000000Z" for item in coinbase_closes)
    assert all(item["event_time_utc"] < item["known_at_utc"] for item in coinbase_closes)


def test_coinbase_manual_backfill_records_empty_no_tick_pages_without_fabricating_candles(tmp_path, monkeypatch):
    captured = datetime(2026, 11, 7, 2, 30, tzinfo=timezone.utc)
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
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "actions: write" not in workflow
    assert "secrets." not in workflow
    assert "cron: '3 * * * *'" in workflow
    assert "cron: '15 0 * * *'" in workflow
