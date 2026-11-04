"""Scheduled public XRP market-data capture with content-addressed receipts.

This collector is ingestion-only. It does not issue forecasts, trade signals,
or recommendations. Historical backfills are marked known only at capture
time, so they cannot leak into earlier point-in-time cutoffs.
"""
from __future__ import annotations

import argparse
import hashlib
from email.utils import parsedate_to_datetime
import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .feature_store import FeatureStoreError, HistoricalFeatureStore
from .point_in_time_features import FeatureSnapshotError, build_feature_snapshot

MAX_RESPONSE_BYTES = 10 * 1024 * 1024
ALLOWED_HOSTS = {"api.binance.com", "fapi.binance.com", "api.kraken.com", "api.exchange.coinbase.com"}
ADAPTER_VERSION = "xrp-public-market-v2"
PARSER_VERSION = "xrp-public-market-v2"
MAX_LIVE_AGE_SECONDS = 300
MAX_ORDERBOOK_AGE_SECONDS = 60

ENDPOINTS = (
    ("binance_spot_ticker", "https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT"),
    ("binance_spot_klines", "https://api.binance.com/api/v3/klines?symbol=XRPUSDT&interval=1h&limit=1000"),
    ("binance_perp_premium", "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=XRPUSDT"),
    ("binance_perp_open_interest", "https://fapi.binance.com/fapi/v1/openInterest?symbol=XRPUSDT"),
    ("coinbase_spot_ticker", "https://api.exchange.coinbase.com/products/XRP-USD/ticker"),
    ("coinbase_spot_candles", "https://api.exchange.coinbase.com/products/XRP-USD/candles?granularity=3600"),
    ("coinbase_spot_book", "https://api.exchange.coinbase.com/products/XRP-USD/book?level=2"),
    ("kraken_spot_depth", "https://api.kraken.com/0/public/Depth?pair=XRPUSD&count=100"),
    ("binance_spot_depth", "https://api.binance.com/api/v3/depth?symbol=XRPUSDT&limit=100"),
)


class XRPIngestionError(ValueError):
    """A public market-data response cannot be safely ingested."""


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise XRPIngestionError("capture clock must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _from_ms(value: Any, field: str) -> datetime:
    if isinstance(value, bool):
        raise XRPIngestionError(f"{field} must be an epoch-millisecond timestamp")
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        raise XRPIngestionError(f"{field} must be an epoch-millisecond timestamp") from None
    if number <= 0:
        raise XRPIngestionError(f"{field} must be positive")
    try:
        return datetime.fromtimestamp(number / 1000.0, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        raise XRPIngestionError(f"{field} is outside the supported timestamp range") from None


def _from_seconds(value: Any, field: str) -> datetime:
    if isinstance(value, bool):
        raise XRPIngestionError(f"{field} must be an epoch-second timestamp")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise XRPIngestionError(f"{field} must be an epoch-second timestamp") from None
    if not math.isfinite(number) or number <= 0:
        raise XRPIngestionError(f"{field} must be finite and positive")
    try:
        return datetime.fromtimestamp(number, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        raise XRPIngestionError(f"{field} is outside the supported timestamp range") from None


def _from_iso8601(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise XRPIngestionError(f"{field} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        raise XRPIngestionError(f"{field} must be an ISO-8601 timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise XRPIngestionError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _from_http_date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _number(value: Any, field: str, *, allow_zero: bool = True) -> float:
    if isinstance(value, bool):
        raise XRPIngestionError(f"{field} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise XRPIngestionError(f"{field} must be numeric") from None
    if not math.isfinite(number) or (number < 0 if allow_zero else number <= 0):
        raise XRPIngestionError(f"{field} must be finite and in range")
    return number


def fetch_public_json(source_id: str, url: str) -> dict[str, Any]:
    """Fetch only allowlisted HTTPS public endpoints; no credentials are used."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise XRPIngestionError("source URL is not an allowlisted public HTTPS endpoint")
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Barrot-XRP-Public-Ingestion/1.0",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except Exception:
        raise XRPIngestionError(f"public fetch failed for {source_id}") from None
    if not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise XRPIngestionError(f"response size is invalid for {source_id}")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise XRPIngestionError(f"response is not valid JSON for {source_id}") from None
    return {"raw_bytes": raw, "payload": payload, "http_date": response.headers.get("Date")}


class RawReceiptArchive:
    """Write-once content-addressed raw payloads plus an append-only receipt log."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.raw_root = self.root / "sha256"
        self.raw_root.mkdir(parents=True, exist_ok=True)
        self.receipts_path = self.root / "receipts.jsonl"
        self.receipts: list[dict[str, Any]] = []

    def store(
        self,
        *,
        source_id: str,
        source_uri: str,
        captured_at_utc: str,
        raw_bytes: bytes,
        source_data_as_of_utc: str | None,
        model_eligible: bool,
        raw_only_reason: str = "",
    ) -> dict[str, Any]:
        if not isinstance(raw_bytes, bytes) or not raw_bytes or len(raw_bytes) > MAX_RESPONSE_BYTES:
            raise XRPIngestionError("raw source payload must be non-empty bytes within the size limit")
        digest = hashlib.sha256(raw_bytes).hexdigest()
        path = self.raw_root / f"{digest}.json"
        if path.exists():
            existing = path.read_bytes()
            if hashlib.sha256(existing).hexdigest() != digest or existing != raw_bytes:
                raise XRPIngestionError("content-addressed raw receipt collision or tampering detected")
        else:
            try:
                with path.open("xb") as handle:
                    handle.write(raw_bytes)
                    handle.flush()
                    os.fsync(handle.fileno())
            except FileExistsError:
                existing = path.read_bytes()
                if hashlib.sha256(existing).hexdigest() != digest or existing != raw_bytes:
                    raise XRPIngestionError("content-addressed raw receipt collision or tampering detected")

        receipt = {
            "source_id": source_id,
            "source_uri": source_uri,
            "captured_at_utc": captured_at_utc,
            "source_data_as_of_utc": source_data_as_of_utc,
            "raw_content_sha256": digest,
            "payload_size_bytes": len(raw_bytes),
            "raw_payload_path": str(path.relative_to(self.root.parent)),
            "model_eligible_source": bool(model_eligible),
            "raw_only_reason": raw_only_reason,
        }
        receipt["receipt_id"] = hashlib.sha256(_canonical(receipt).encode("utf-8")).hexdigest()
        with self.receipts_path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical(receipt) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.receipts.append(receipt)
        return receipt


def _feature_record(
    *,
    feature_id: str,
    value: float,
    unit: str,
    event_time_utc: str,
    source_data_as_of_utc: str,
    captured_at_utc: str,
    source_id: str,
    source_uri: str,
    raw_sha256: str,
    independence_group: str,
    venue: str,
    instrument: str,
    currency_pair: str,
    market_type: str,
    aggregation_window: str | None = None,
    model_eligible: bool = True,
    eligibility_reason: str = "",
    quality_status: str = "verified",
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    record = {
        "record_id": f"{feature_id}:{event_time_utc}:{source_id}",
        "feature_id": feature_id,
        "feature_version": 1,
        "asset": "XRP",
        "feature_name": feature_id.rsplit(".", 1)[-1],
        "value": value,
        "unit": unit,
        "event_time_utc": event_time_utc,
        "known_at_utc": captured_at_utc,
        "source_data_as_of_utc": source_data_as_of_utc,
        "ingested_at_utc": captured_at_utc,
        "revision_available_at_utc": captured_at_utc,
        "sources": [
            {
                "source_id": source_id,
                "independence_group": independence_group,
                "source_uri": source_uri,
                "raw_content_sha256": raw_sha256,
            }
        ],
        "quality_status": quality_status,
        "model_eligible": model_eligible,
        "eligibility_reason": "" if model_eligible else (eligibility_reason or "source_not_verified"),
        "revision_status": "original",
        "supersedes_record_id": None,
        "adapter_version": ADAPTER_VERSION,
        "parser_version": PARSER_VERSION,
        "limitations": limitations or [],
        "disconfirming_evidence_ids": [],
        "venue": venue,
        "instrument": instrument,
        "currency_pair": currency_pair,
        "market_type": market_type,
    }
    if aggregation_window:
        record["aggregation_window"] = aggregation_window
    return record


def _live_eligibility(source_time: datetime, captured: datetime, max_age: int) -> tuple[bool, str, str]:
    age = (captured - source_time).total_seconds()
    if age < 0:
        return False, "source_timestamp_in_future", "unverified"
    if age > max_age:
        return False, f"source_timestamp_older_than_{max_age}_seconds", "stale"
    return True, "", "verified"


def _parse_binance_ticker(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    if not isinstance(payload, Mapping) or payload.get("symbol") != "XRPUSDT":
        raise XRPIngestionError("Binance spot ticker symbol or response shape mismatch")
    source_time = _from_ms(payload.get("closeTime"), "Binance ticker closeTime")
    if source_time > captured:
        raise XRPIngestionError("Binance ticker closeTime is later than capture time")
    eligible, reason, quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
    event_s = _iso(source_time)
    captured_s = _iso(captured)
    limitations = ["Single Binance spot venue; USDT quote is not converted to USD."]
    fields = (
        ("lastPrice", "last_price", "USDT/XRP"),
        ("bidPrice", "bid_price", "USDT/XRP"),
        ("askPrice", "ask_price", "USDT/XRP"),
        ("bidQty", "bid_quantity", "XRP"),
        ("askQty", "ask_quantity", "XRP"),
        ("volume", "base_volume_24h", "XRP/24h"),
        ("quoteVolume", "quote_volume_24h", "USDT/24h"),
        ("weightedAvgPrice", "weighted_average_price_24h", "USDT/XRP"),
    )
    records = []
    for field, name, unit in fields:
        value = _number(payload.get(field), f"Binance ticker {field}", allow_zero=name.endswith("quantity") or "volume" in name)
        records.append(
            _feature_record(
                feature_id=f"xrp.spot.binance.{name}",
                value=value,
                unit=unit,
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="binance",
                venue="Binance",
                instrument="XRPUSDT spot",
                currency_pair="XRP/USDT",
                market_type="spot",
                aggregation_window="24h" if "24h" in name else "",
                model_eligible=eligible,
                eligibility_reason=reason,
                quality_status=quality,
                limitations=limitations,
            )
        )
    return records, event_s, eligible, reason


def _parse_binance_klines(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    if not isinstance(payload, list) or not payload:
        raise XRPIngestionError("Binance kline response must be a non-empty array")
    captured_s = _iso(captured)
    records = []
    latest_close = None
    incomplete = 0
    limitations = [
        "Historical candles were first observed at this capture time; they are not known at their historical event times.",
        "Single Binance spot venue; USDT quote is not converted to USD.",
    ]
    metrics = (
        (1, "open_price", "USDT/XRP"),
        (2, "high_price", "USDT/XRP"),
        (3, "low_price", "USDT/XRP"),
        (4, "close_price", "USDT/XRP"),
        (5, "base_volume", "XRP"),
        (7, "quote_volume", "USDT"),
        (8, "trade_count", "trades"),
        (9, "taker_buy_base_volume", "XRP"),
        (10, "taker_buy_quote_volume", "USDT"),
    )
    for row in payload:
        if not isinstance(row, list) or len(row) < 11:
            raise XRPIngestionError("Binance kline row does not match the documented schema")
        open_time = _from_ms(row[0], "Binance kline open time")
        close_time = _from_ms(row[6], "Binance kline close time")
        if close_time > captured:
            incomplete += 1
            continue
        open_s, close_s = _iso(open_time), _iso(close_time)
        latest_close = close_s if latest_close is None or close_s > latest_close else latest_close
        for index, name, unit in metrics:
            value = _number(row[index], f"Binance kline {name}", allow_zero=name not in {"open_price", "high_price", "low_price", "close_price"})
            records.append(
                _feature_record(
                    feature_id=f"xrp.spot.binance.1h.{name}",
                    value=value,
                    unit=unit,
                    event_time_utc=open_s,
                    source_data_as_of_utc=close_s,
                    captured_at_utc=captured_s,
                    source_id=source_id,
                    source_uri=url,
                    raw_sha256=digest,
                    independence_group="binance",
                    venue="Binance",
                    instrument="XRPUSDT spot",
                    currency_pair="XRP/USDT",
                    market_type="spot",
                    aggregation_window="1h",
                    limitations=limitations,
                )
            )
    if not records:
        raise XRPIngestionError("Binance kline response contains no completed candles")
    return records, latest_close, True, f"incomplete_current_candles_skipped:{incomplete}" if incomplete else ""


def _parse_binance_premium(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    if not isinstance(payload, Mapping) or payload.get("symbol") != "XRPUSDT":
        raise XRPIngestionError("Binance perpetual premium response shape mismatch")
    source_time = _from_ms(payload.get("time"), "Binance premium time")
    if source_time > captured:
        raise XRPIngestionError("Binance premium time is later than capture time")
    eligible, reason, quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
    event_s, captured_s = _iso(source_time), _iso(captured)
    fields = (
        ("markPrice", "mark_price", "USDT/XRP", False),
        ("indexPrice", "index_price", "USDT/XRP", False),
        ("lastFundingRate", "funding_rate", "fraction/8h", True),
    )
    records = []
    for field, name, unit, allow_zero in fields:
        value = _number(payload.get(field), f"Binance premium {field}", allow_zero=allow_zero)
        records.append(
            _feature_record(
                feature_id=f"xrp.perpetual.binance.{name}",
                value=value,
                unit=unit,
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="binance",
                venue="Binance",
                instrument="XRPUSDT perpetual",
                currency_pair="XRP/USDT",
                market_type="perpetual",
                aggregation_window="8h" if name == "funding_rate" else "",
                model_eligible=eligible,
                eligibility_reason=reason,
                quality_status=quality,
                limitations=["Single derivatives venue; funding rate is the reported 8-hour rate, not annualized."],
            )
        )
    return records, event_s, eligible, reason


def _parse_binance_open_interest(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    if not isinstance(payload, Mapping) or payload.get("symbol") != "XRPUSDT":
        raise XRPIngestionError("Binance open-interest response shape mismatch")
    source_time = _from_ms(payload.get("time"), "Binance open-interest time")
    if source_time > captured:
        raise XRPIngestionError("Binance open-interest time is later than capture time")
    eligible, reason, quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
    event_s, captured_s = _iso(source_time), _iso(captured)
    value = _number(payload.get("openInterest"), "Binance openInterest", allow_zero=False)
    record = _feature_record(
        feature_id="xrp.perpetual.binance.open_interest_contracts",
        value=value,
        unit="contracts",
        event_time_utc=event_s,
        source_data_as_of_utc=event_s,
        captured_at_utc=captured_s,
        source_id=source_id,
        source_uri=url,
        raw_sha256=digest,
        independence_group="binance",
        venue="Binance",
        instrument="XRPUSDT perpetual",
        currency_pair="XRP/USDT",
        market_type="perpetual",
        model_eligible=eligible,
        eligibility_reason=reason,
        quality_status=quality,
        limitations=["Reported open interest is in contracts; no notional or XRP conversion is inferred."],
    )
    return [record], event_s, eligible, reason


def _parse_coinbase_ticker(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    http_date: str | None = None,
):
    if not isinstance(payload, Mapping):
        raise XRPIngestionError("Coinbase ticker response must be an object")
    trade_time = _from_iso8601(payload.get("time"), "Coinbase ticker trade time")
    if trade_time > captured:
        raise XRPIngestionError("Coinbase ticker trade time is later than capture time")
    server_time = _from_http_date(http_date)
    trade_eligible, trade_reason, trade_quality = _live_eligibility(
        trade_time, captured, MAX_LIVE_AGE_SECONDS
    )
    quote_time = server_time or captured
    quote_eligible, quote_reason, quote_quality = (
        _live_eligibility(quote_time, captured, MAX_LIVE_AGE_SECONDS)
        if server_time is not None
        else (False, "missing_or_invalid_http_date_snapshot_time", "unverified")
    )
    price = _number(payload.get("price"), "Coinbase ticker price", allow_zero=False)
    size = _number(payload.get("size"), "Coinbase ticker size", allow_zero=False)
    bid = _number(payload.get("bid"), "Coinbase ticker bid", allow_zero=False)
    ask = _number(payload.get("ask"), "Coinbase ticker ask", allow_zero=False)
    volume = _number(payload.get("volume"), "Coinbase ticker 24h volume")
    if ask <= bid:
        raise XRPIngestionError("Coinbase ticker bid/ask is crossed or locked")
    trade_s, quote_s, captured_s = _iso(trade_time), _iso(quote_time), _iso(captured)
    mid = (bid + ask) / 2.0
    spread_bps = (ask - bid) / mid * 10000.0
    limitations = [
        "Single Coinbase Exchange XRP/USD spot venue; not consolidated liquidity.",
        "Ticker trade time timestamps the last trade; bid/ask snapshot time uses the HTTP Date response header.",
        "The HTTP Date header is server response time, not an exchange matching-engine sequence timestamp.",
    ]
    records = [
        _feature_record(
            feature_id="xrp.spot.coinbase.last_price",
            value=price,
            unit="USD/XRP",
            event_time_utc=trade_s,
            source_data_as_of_utc=trade_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="coinbase",
            venue="Coinbase",
            instrument="XRP-USD spot",
            currency_pair="XRP/USD",
            market_type="spot",
            model_eligible=trade_eligible,
            eligibility_reason=trade_reason,
            quality_status=trade_quality,
            limitations=limitations,
        ),
        _feature_record(
            feature_id="xrp.spot.coinbase.last_trade_size",
            value=size,
            unit="XRP",
            event_time_utc=trade_s,
            source_data_as_of_utc=trade_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="coinbase",
            venue="Coinbase",
            instrument="XRP-USD spot",
            currency_pair="XRP/USD",
            market_type="spot",
            model_eligible=trade_eligible,
            eligibility_reason=trade_reason,
            quality_status=trade_quality,
            limitations=limitations,
        ),
    ]
    for name, value, unit in (
        ("best_bid", bid, "USD/XRP"),
        ("best_ask", ask, "USD/XRP"),
        ("mid_price", mid, "USD/XRP"),
        ("spread_bps", spread_bps, "bps"),
        ("base_volume_24h", volume, "XRP/24h"),
    ):
        records.append(
            _feature_record(
                feature_id=f"xrp.spot.coinbase.{name}",
                value=value,
                unit=unit,
                event_time_utc=quote_s,
                source_data_as_of_utc=quote_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="coinbase",
                venue="Coinbase",
                instrument="XRP-USD spot",
                currency_pair="XRP/USD",
                market_type="spot",
                aggregation_window="24h" if name == "base_volume_24h" else "",
                model_eligible=quote_eligible,
                eligibility_reason=quote_reason,
                quality_status=quote_quality,
                limitations=limitations,
            )
        )
    source_time = max(trade_time, server_time) if server_time is not None else trade_time
    source_eligible = trade_eligible or quote_eligible
    source_reason = "" if source_eligible else "coinbase_ticker_has_no_fresh_timestamp"
    return records, _iso(source_time), source_eligible, source_reason


def _parse_coinbase_candles(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    if not isinstance(payload, list) or not payload:
        raise XRPIngestionError("Coinbase candle response must be a non-empty array")
    captured_s = _iso(captured)
    records = []
    latest_close = None
    incomplete = 0
    limitations = [
        "Historical Coinbase candles were first observed at this capture time; they are not known at historical event times.",
        "The public Coinbase endpoint returns at most 300 candles per request; pagination is not yet implemented.",
    ]
    metrics = (
        (1, "low_price", "USD/XRP"),
        (2, "high_price", "USD/XRP"),
        (3, "open_price", "USD/XRP"),
        (4, "close_price", "USD/XRP"),
        (5, "base_volume", "XRP"),
    )
    for row in payload:
        if not isinstance(row, list) or len(row) < 6:
            raise XRPIngestionError("Coinbase candle row does not match the documented schema")
        open_time = _from_seconds(row[0], "Coinbase candle open time")
        close_time = open_time + timedelta(seconds=3600)
        if close_time > captured:
            incomplete += 1
            continue
        open_s, close_s = _iso(open_time), _iso(close_time)
        latest_close = close_s if latest_close is None or close_s > latest_close else latest_close
        for index, name, unit in metrics:
            value = _number(
                row[index],
                f"Coinbase candle {name}",
                allow_zero=name == "base_volume",
            )
            records.append(
                _feature_record(
                    feature_id=f"xrp.spot.coinbase.1h.{name}",
                    value=value,
                    unit=unit,
                    event_time_utc=open_s,
                    source_data_as_of_utc=close_s,
                    captured_at_utc=captured_s,
                    source_id=source_id,
                    source_uri=url,
                    raw_sha256=digest,
                    independence_group="coinbase",
                    venue="Coinbase",
                    instrument="XRP-USD spot",
                    currency_pair="XRP/USD",
                    market_type="spot",
                    aggregation_window="1h",
                    limitations=limitations,
                )
            )
    if not records:
        raise XRPIngestionError("Coinbase candle response contains no completed hourly candles")
    reason = f"incomplete_current_candles_skipped:{incomplete}" if incomplete else ""
    return records, latest_close, True, reason


def _raw_only_coinbase_book(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    if not isinstance(payload, Mapping):
        raise XRPIngestionError("Coinbase order-book response must be an object")
    sequence = payload.get("sequence")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence <= 0:
        raise XRPIngestionError("Coinbase order-book sequence is invalid")
    bids, asks = payload.get("bids"), payload.get("asks")
    if not isinstance(bids, list) or not bids or not isinstance(asks, list) or not asks:
        raise XRPIngestionError("Coinbase order book must contain bids and asks")
    for side, rows in (("bid", bids), ("ask", asks)):
        for row in rows:
            if not isinstance(row, list) or len(row) < 2:
                raise XRPIngestionError(f"Coinbase {side} level schema mismatch")
            _number(row[0], f"Coinbase {side} price", allow_zero=False)
            _number(row[1], f"Coinbase {side} quantity", allow_zero=False)
    return [], None, False, "coinbase_book_snapshot_has_no_timestamp_or_websocket_sequence_bridge"


def _parse_kraken_depth(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime, http_date: str | None = None):
    if not isinstance(payload, Mapping) or payload.get("error") not in ([], None):
        raise XRPIngestionError("Kraken depth response contains an API error")
    result = payload.get("result")
    if not isinstance(result, Mapping):
        raise XRPIngestionError("Kraken depth response has no result mapping")
    book = next((value for value in result.values() if isinstance(value, Mapping)), None)
    if not isinstance(book, Mapping):
        raise XRPIngestionError("Kraken depth response has no order book")
    bids_raw, asks_raw = book.get("bids"), book.get("asks")
    if not isinstance(bids_raw, list) or not bids_raw or not isinstance(asks_raw, list) or not asks_raw:
        raise XRPIngestionError("Kraken order book must contain bids and asks")

    def parse_levels(rows: list[Any], side: str):
        levels = []
        for row in rows:
            if not isinstance(row, list) or len(row) < 3:
                raise XRPIngestionError(f"Kraken {side} level schema mismatch")
            price = _number(row[0], f"Kraken {side} price", allow_zero=False)
            quantity = _number(row[1], f"Kraken {side} quantity", allow_zero=False)
            timestamp = _from_seconds(row[2], f"Kraken {side} timestamp")
            levels.append((price, quantity, timestamp))
        return levels

    bids, asks = parse_levels(bids_raw, "bid"), parse_levels(asks_raw, "ask")
    best_bid = max(level[0] for level in bids)
    best_ask = min(level[0] for level in asks)
    if best_ask <= best_bid:
        raise XRPIngestionError("Kraken order book is crossed or locked")
    # Level timestamps describe when each price level last changed, not when this
    # complete REST snapshot was produced. Use the server HTTP Date for snapshot time.
    # Without it, retain the raw receipt but do not admit the depth features.
    source_time = _from_http_date(http_date)
    if source_time is None:
        source_time = captured
        eligible, reason, quality = (
            False,
            "missing_or_invalid_http_date_snapshot_time",
            "unverified",
        )
    else:
        if source_time > captured:
            raise XRPIngestionError("Kraken HTTP Date is later than capture time")
        eligible, reason, quality = _live_eligibility(
            source_time, captured, MAX_ORDERBOOK_AGE_SECONDS
        )
    event_s, captured_s = _iso(source_time), _iso(captured)
    mid = (best_bid + best_ask) / 2.0
    spread_bps = (best_ask - best_bid) / mid * 10000.0
    features = [
        ("best_bid", best_bid, "USD/XRP"),
        ("best_ask", best_ask, "USD/XRP"),
        ("mid_price", mid, "USD/XRP"),
        ("spread_bps", spread_bps, "bps"),
    ]
    for band in (10, 50, 100):
        bid_depth = sum(price * quantity for price, quantity, _ in bids if price >= mid * (1 - band / 10000.0))
        ask_depth = sum(price * quantity for price, quantity, _ in asks if price <= mid * (1 + band / 10000.0))
        total = bid_depth + ask_depth
        imbalance = (bid_depth - ask_depth) / total if total > 0 else 0.0
        features.extend(
            [
                (f"bid_depth_{band}bps", bid_depth, "USD"),
                (f"ask_depth_{band}bps", ask_depth, "USD"),
                (f"depth_imbalance_{band}bps", imbalance, "ratio"),
            ]
        )
    limitations = [
        "Single Kraken spot order-book snapshot; not global or consolidated liquidity.",
        "Snapshot continuity is not established by a sequence bridge; use only as a timestamped observation.",
        "Per-level timestamps are last-update times, not snapshot time; snapshot freshness uses the HTTP Date header.",
    ]
    records = [
        _feature_record(
            feature_id=f"xrp.spot.kraken.orderbook.{name}",
            value=value,
            unit=unit,
            event_time_utc=event_s,
            source_data_as_of_utc=event_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="kraken",
            venue="Kraken",
            instrument="XRP/USD spot",
            currency_pair="XRP/USD",
            market_type="spot",
            model_eligible=eligible,
            eligibility_reason=reason,
            quality_status=quality,
            limitations=limitations,
        )
        for name, value, unit in features
    ]
    return records, event_s, eligible, reason


def _raw_only_binance_depth(payload: Any, **_kwargs):
    if not isinstance(payload, Mapping) or "lastUpdateId" not in payload:
        raise XRPIngestionError("Binance depth response shape mismatch")
    return [], None, False, "sequence_id_present_but_server_timestamp_absent_raw_only"


PARSERS = {
    "binance_spot_ticker": _parse_binance_ticker,
    "binance_spot_klines": _parse_binance_klines,
    "binance_perp_premium": _parse_binance_premium,
    "binance_perp_open_interest": _parse_binance_open_interest,
    "coinbase_spot_ticker": _parse_coinbase_ticker,
    "coinbase_spot_candles": _parse_coinbase_candles,
    "coinbase_spot_book": _raw_only_coinbase_book,
    "kraken_spot_depth": _parse_kraken_depth,
    "binance_spot_depth": _raw_only_binance_depth,
}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(_canonical(value))
        handle.write("\n")


def run_ingestion(
    output_dir: str | Path,
    *,
    fetcher: Callable[[str, str], Mapping[str, Any]] = fetch_public_json,
    now: datetime | None = None,
) -> dict[str, Any]:
    captured = now or datetime.now(timezone.utc)
    captured_s = _iso(captured)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    archive = RawReceiptArchive(output / "raw")
    receipts = []
    records = []
    failures = []
    raw_only = []

    for source_id, url in ENDPOINTS:
        try:
            response = fetcher(source_id, url)
            raw_bytes = response["raw_bytes"]
            payload = response["payload"]
            if not isinstance(raw_bytes, bytes):
                raise XRPIngestionError("fetcher raw_bytes must be bytes")
            digest = hashlib.sha256(raw_bytes).hexdigest()
            parser = PARSERS[source_id]
            parser_kwargs = {
                "source_id": source_id,
                "url": url,
                "digest": digest,
                "captured": captured,
            }
            if source_id in {"coinbase_spot_ticker", "kraken_spot_depth"}:
                parser_kwargs["http_date"] = response.get("http_date")
            parsed_records, source_as_of, source_eligible, reason = parser(
                payload,
                **parser_kwargs,
            )
            receipt = archive.store(
                source_id=source_id,
                source_uri=url,
                captured_at_utc=captured_s,
                raw_bytes=raw_bytes,
                source_data_as_of_utc=source_as_of,
                model_eligible=source_eligible,
                raw_only_reason=reason,
            )
            receipts.append(receipt)
            records.extend(parsed_records)
            if reason and not source_eligible:
                raw_only.append({"source_id": source_id, "reason": reason})
            elif reason and source_id in {"binance_spot_klines", "coinbase_spot_candles"}:
                raw_only.append({"source_id": source_id, "reason": reason})
        except Exception as exc:
            failures.append({"source_id": source_id, "error_type": type(exc).__name__})

    snapshot = None
    store_verification = None
    snapshot_status = "blocked_no_eligible_features"
    try:
        snapshot = build_feature_snapshot(
            records,
            cutoff_utc=captured_s,
            captured_at_utc=captured_s,
            asset_scope=["XRP"],
        )
        database = output / "feature_store.sqlite3"
        store = HistoricalFeatureStore(database, clock=lambda: captured)
        stored = store.append_snapshot(snapshot)
        store_verification = store.verify_snapshot(snapshot["snapshot_id"])
        if not store_verification.get("valid"):
            raise FeatureStoreError("newly appended XRP snapshot failed verification")
        _write_json(output / "snapshot.json", snapshot)
        snapshot_status = "verified"
    except (FeatureSnapshotError, FeatureStoreError, XRPIngestionError) as exc:
        failures.append({"source_id": "feature_snapshot", "error_type": type(exc).__name__})
        stored = None
        _write_json(output / "snapshot_blocked.json", {"status": snapshot_status, "reason": str(exc)})

    _write_json(output / "receipt_manifest.json", receipts)
    _write_json(output / "source_failures.json", failures)
    _write_json(output / "raw_only_sources.json", raw_only)
    summary = {
        "schema_version": 1,
        "artifact_type": "xrp_public_market_ingestion_run",
        "adapter_version": ADAPTER_VERSION,
        "parser_version": PARSER_VERSION,
        "captured_at_utc": captured_s,
        "data_cutoff_utc": captured_s,
        "source_receipt_count": len(receipts),
        "source_failure_count": len(failures),
        "raw_only_source_count": len(raw_only),
        "input_feature_record_count": len(records),
        "snapshot_status": snapshot_status,
        "snapshot_id": snapshot.get("snapshot_id") if snapshot else None,
        "eligible_feature_record_count": snapshot.get("eligible_record_count", 0) if snapshot else 0,
        "excluded_feature_record_count": snapshot.get("excluded_record_count", 0) if snapshot else 0,
        "store_receipt": stored,
        "store_verification": store_verification,
        "forecast_status": "NOT_ISSUED",
        "forecast_model_eligible": False,
        "storage_scope": "one GitHub Actions artifact per run; no cross-run durable store is configured",
        "artifact_retention_days": 90,
        "limitations": [
            "Spot coverage now includes Binance, Coinbase and Kraken; perpetual coverage remains Binance-only in this adapter.",
            "USDT quotes are not converted to USD; open interest remains in contracts.",
            "Binance and Coinbase order-book snapshots remain raw-only because no exchange timestamp/sequence bridge is maintained; Kraken depth requires a fresh HTTP Date header.",
            "Historical Binance and Coinbase candles are known to this collector only at captured_at_utc; they cannot be used at earlier historical cutoffs. Coinbase candle pagination is not yet implemented.",
            "Raw files are content-addressed and hashed, but independent external timestamp anchoring and long-term immutable object storage are not configured.",
            "No exchange wallet flows, ETF flows, institutional collateral, stablecoin supply, custody, payment rails, or regulatory events are inferred by this adapter.",
            "This collector does not issue directional forecasts, trading signals, or recommendations.",
        ],
    }
    _write_json(output / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture public XRP spot, order-book and perpetual-market data.")
    parser.add_argument("--output-dir", default="artifacts/xrp_ingestion")
    args = parser.parse_args()
    summary = run_ingestion(args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
