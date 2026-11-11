"""Scheduled public XRP market-data capture with content-addressed receipts.

This collector is ingestion-only. It does not issue forecasts, trade signals,
or recommendations. Historical backfills are marked known only at capture
time, so they cannot leak into earlier point-in-time cutoffs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
from email.utils import parsedate_to_datetime
import json
import math
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .feature_store import FeatureStoreError, HistoricalFeatureStore
from .point_in_time_features import FeatureSnapshotError, build_feature_snapshot
from .walk_forward import WalkForwardEvaluationError, evaluate_chronological_walk_forward
from .feature_drift import DRIFT_REPORT_RETENTION_DAYS, MONITOR_VERSION as DRIFT_MONITOR_VERSION, monitor_feature_drift
from .cftc_tff import parse_cftc_contract_status, parse_cftc_tff_report

MAX_RESPONSE_BYTES = 10 * 1024 * 1024
ALLOWED_HOSTS = {"api.binance.com", "api.bybit.com", "us.okx.com", "fapi.binance.com", "api.kraken.com", "api.exchange.coinbase.com", "public.bitbank.cc", "xrp-insights.com", "www.rexshares.com", "bitxrpetf.com", "etfs.grayscale.com", "www.franklintempleton.com", "canaryetfs.com", "www.21shares.com", "xrplcluster.com", "honeycluster.io", "ripple.com", "xrpldashboard.com", "www.circle.com", "circle.com", "www.cftc.gov", "api.morpho.org", "www.coinbase.com", "www.sbivc.co.jp"}
ADAPTER_VERSION = "xrp-public-market-v3.24"
PARSER_VERSION = "xrp-public-market-v3.23"
MAX_LIVE_AGE_SECONDS = 300
MAX_ORDERBOOK_AGE_SECONDS = 60
HTTP_PROVENANCE_HEADER_NAMES = frozenset({
    "age", "cache-control", "content-type", "content-encoding",
    "etag", "expires", "last-modified", "cf-cache-status", "x-cache",
})
LIVE_HTTP_CACHE_AGE_LIMITS = {
    "binance_spot_ticker": MAX_LIVE_AGE_SECONDS,
    "coinbase_spot_ticker": MAX_LIVE_AGE_SECONDS,
    "kraken_spot_ticker": MAX_LIVE_AGE_SECONDS,
    "bitbank_spot_ticker": MAX_LIVE_AGE_SECONDS,
    "okx_spot_ticker": MAX_LIVE_AGE_SECONDS,
    "bybit_spot_ticker": MAX_LIVE_AGE_SECONDS,
    "binance_perp_premium": MAX_LIVE_AGE_SECONDS,
    "binance_perp_open_interest": MAX_LIVE_AGE_SECONDS,
    "bybit_linear_ticker": MAX_LIVE_AGE_SECONDS,
    "bybit_linear_open_interest": MAX_LIVE_AGE_SECONDS,
    "coinbase_spot_book": MAX_ORDERBOOK_AGE_SECONDS,
    "kraken_spot_depth": MAX_ORDERBOOK_AGE_SECONDS,
    "bitbank_spot_depth": MAX_ORDERBOOK_AGE_SECONDS,
    "okx_spot_depth": MAX_ORDERBOOK_AGE_SECONDS,
    "bybit_spot_depth": MAX_ORDERBOOK_AGE_SECONDS,
    "morpho_cbxrp_market_parameters": 3_600,
    "morpho_cbxrp_market_state": 300,
    "morpho_cbxrp_market_liquidity": 300,
    "morpho_cbxrp_market_state_history": 3_600,
    "morpho_cbxrp_oracle_state": 300,
    "coinbase_cbxrp_proof_of_reserves": 3_600,
}
COINBASE_CANDLE_GRANULARITY_SECONDS = 3600
COINBASE_CANDLES_PER_REQUEST = 300
MAX_COINBASE_BACKFILL_DAYS = 365
MAX_COINBASE_BACKFILL_PAGES = 30
COINBASE_BACKFILL_PAGE_DELAY_SECONDS = 0.5

MORPHO_CBXRP_CHAIN_ID = 8453
MORPHO_CBXRP_MARKET_ID = "0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109"
MORPHO_CBXRP_MARKET_SELECTOR = f"{MORPHO_CBXRP_CHAIN_ID}:{MORPHO_CBXRP_MARKET_ID}"
MORPHO_CBXRP_LOAN_TOKEN_ADDRESS = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
MORPHO_CBXRP_COLLATERAL_TOKEN_ADDRESS = "0xcb585250f852c6c6bf90434ab21a00f02833a4af"
MORPHO_CBXRP_ORACLE_ADDRESS = "0x031b2efc8d70042ac8d9f5c793c4149ec4b60fde"

WALK_FORWARD_HORIZON_SECONDS = {
    "1h": 3_600,
    "4h": 14_400,
    "24h": 86_400,
    "7d": 604_800,
    "30d": 2_592_000,
}
DEFAULT_WALK_FORWARD_HORIZONS = ("1h",)
FULL_WALK_FORWARD_HORIZONS = tuple(WALK_FORWARD_HORIZON_SECONDS)
WALK_FORWARD_REPORT_VERSION = "xrp-walk-forward-matrix-v1"

ENDPOINTS = (
    ("binance_spot_ticker", "https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT"),
    ("binance_spot_klines", "https://api.binance.com/api/v3/klines?symbol=XRPUSDT&interval=1h&limit=1000"),
    ("binance_perp_premium", "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=XRPUSDT"),
    ("binance_perp_open_interest", "https://fapi.binance.com/fapi/v1/openInterest?symbol=XRPUSDT"),
    ("binance_perp_funding_history", "https://fapi.binance.com/fapi/v1/fundingRate?symbol=XRPUSDT&limit=1000"),
    ("binance_perp_open_interest_history", "https://fapi.binance.com/futures/data/openInterestHist?symbol=XRPUSDT&period=1h&limit=500"),
    ("binance_perp_global_long_short_ratio", "https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=XRPUSDT&period=1h&limit=500"),
    ("coinbase_spot_ticker", "https://api.exchange.coinbase.com/products/XRP-USD/ticker"),
    ("kraken_spot_ticker", "https://api.kraken.com/0/public/Ticker?pair=XRPUSD"),
    ("bitbank_spot_circuit_break", "https://public.bitbank.cc/xrp_jpy/circuit_break_info"),
    ("bitbank_spot_transactions", "https://public.bitbank.cc/xrp_jpy/transactions"),
    ("bitbank_spot_ticker", "https://public.bitbank.cc/xrp_jpy/ticker"),
    ("bitbank_spot_depth", "https://public.bitbank.cc/xrp_jpy/depth"),
    ("okx_spot_ticker", "https://us.okx.com/api/v5/market/ticker?instId=XRP-USDT"),
    ("okx_spot_depth", "https://us.okx.com/api/v5/market/books?instId=XRP-USDT&sz=100"),
    ("bybit_spot_ticker", "https://api.bybit.com/v5/market/tickers?category=spot&symbol=XRPUSDT"),
    ("bybit_spot_depth", "https://api.bybit.com/v5/market/orderbook?category=spot&symbol=XRPUSDT&limit=100"),
    ("bybit_linear_ticker", "https://api.bybit.com/v5/market/tickers?category=linear&symbol=XRPUSDT"),
    ("bybit_linear_open_interest", "https://api.bybit.com/v5/market/open-interest?category=linear&symbol=XRPUSDT&intervalTime=1h&limit=200"),
    ("bybit_linear_funding_history", "https://api.bybit.com/v5/market/funding/history?category=linear&symbol=XRPUSDT&limit=200"),
    ("coinbase_spot_candles", "https://api.exchange.coinbase.com/products/XRP-USD/candles?granularity=3600"),
    ("coinbase_spot_book", "https://api.exchange.coinbase.com/products/XRP-USD/book?level=2"),
    ("kraken_spot_depth", "https://api.kraken.com/0/public/Depth?pair=XRPUSD&count=100"),
    ("binance_spot_depth", "https://api.binance.com/api/v3/depth?symbol=XRPUSDT&limit=100"),
    ("xrp_etf_flows_aggregator", "https://xrp-insights.com/data/xrp-etf-flows.json"),
    ("xrp_exchange_balances_json", "https://xrp-insights.com/exchange-balances/data.json"),
    ("xrp_etf_flows_csv", "https://xrp-insights.com/data/xrp-etf-flows.csv"),
    ("xrp_etf_xrpr_issuer_page", "https://www.rexshares.com/xrpr/"),
    ("xrp_etf_bitwise_issuer_page", "https://bitxrpetf.com/"),
    ("xrp_etf_grayscale_gxrp_issuer_page", "https://etfs.grayscale.com/gxrp"),
    ("xrp_etf_franklin_xrpz_issuer_page", "https://www.franklintempleton.com/investments/options/exchange-traded-funds/products/47318/SINGLCLASS/franklin-xrp-etf/XRPZ"),
    ("xrp_etf_canary_xrpc_issuer_page", "https://canaryetfs.com/xrpc/"),
    ("xrp_etf_21shares_toxr_issuer_page", "https://www.21shares.com/en-us/products-us/toxr"),
    ("ripple_rlusd_transparency_dashboard", "https://ripple.com/products/stablecoin/transparency/"),
    ("xrpldashboard_rlusd_cross_chain_supply", "https://xrpldashboard.com/rlusd"),
    ("circle_usdc_transparency_dashboard", "https://www.circle.com/transparency"),
    ("sbi_vc_trade_lending_page", "https://www.sbivc.co.jp/services/lending"),
    ("morpho_cbxrp_market_parameters", "https://api.morpho.org/v0/blue/markets/8453:0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109"),
    ("morpho_cbxrp_market_state", "https://api.morpho.org/v0/blue/markets/8453:0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109/state"),
    ("morpho_cbxrp_market_liquidity", "https://api.morpho.org/v0/blue/markets/8453:0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109/liquidity"),
    ("morpho_cbxrp_market_state_history", "https://api.morpho.org/v0/blue/markets/8453:0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109/state/history?lookback=thirty_days"),
    ("morpho_cbxrp_oracle_state", "https://api.morpho.org/v0/oracles/8453:0x031b2efc8d70042ac8d9f5c793c4149ec4b60fde/state"),
    ("coinbase_cbxrp_proof_of_reserves", "https://www.coinbase.com/en-gb/cbxrp/proof-of-reserves"),
    ("cftc_contract_status_index", "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm"),
    ("cftc_tff_financial_futures", "https://www.cftc.gov/dea/futures/financial_lf.htm"),
    ("xrpl_inftf_server_info", "https://xrplcluster.com/"),
    ("xrpl_honeycluster_server_info", "https://honeycluster.io/"),
)


DIGEST_ONLY_RAW_SOURCE_REASONS = {
    "xrp_etf_flows_csv": (
        "Publisher terms allow use and citation with attribution but require written permission "
        "for commercial redistribution; full CSV bytes are not retained in public artifacts."
    ),
    "xrp_exchange_balances_json": (
        "Publisher permits citation with attribution but does not expressly grant redistribution "
        "of the raw exchange-balance JSON; retain its SHA-256 receipt only."
    ),
    "xrp_etf_franklin_xrpz_issuer_page": (
        "Public issuer page is cited for research; raw HTML redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "xrp_etf_canary_xrpc_issuer_page": (
        "Public issuer page is cited for research; raw HTML redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "xrp_etf_21shares_toxr_issuer_page": (
        "Public issuer page is cited for research; raw HTML redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "morpho_cbxrp_market_parameters": (
        "Public Morpho API response is used for research; raw-response redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "morpho_cbxrp_market_state": (
        "Public Morpho API response is used for research; raw-response redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "morpho_cbxrp_market_liquidity": (
        "Public Morpho API response is used for research; raw-response redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "morpho_cbxrp_market_state_history": (
        "Public Morpho API response is used for research; raw-response redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "morpho_cbxrp_oracle_state": (
        "Public Morpho API response is used for research; raw-response redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "coinbase_cbxrp_proof_of_reserves": (
        "Public issuer page is cited for research; raw HTML redistribution terms have not been reviewed, "
        "so retain the SHA-256 receipt only until permission is established."
    ),
    "sbi_vc_trade_lending_page": (
        "SBI VC Trade's public lending terms are captured for source-change detection; raw HTML redistribution "
        "rights have not been reviewed, so retain only the SHA-256 receipt and do not publish the page bytes."
    ),
}

BITBANK_SOURCE_IDS = frozenset({
    "bitbank_spot_circuit_break",
    "bitbank_spot_transactions",
    "bitbank_spot_ticker",
    "bitbank_spot_depth",
})
BITBANK_CIRCUIT_MODES = frozenset({"NONE", "CIRCUIT_BREAK", "FULL_RANGE_CIRCUIT_BREAK", "RESUMPTION", "LISTING"})

XRPL_NODE_SOURCES = {
    "xrpl_inftf_server_info": {
        "url": "https://xrplcluster.com/",
        "host": "xrplcluster.com",
        "operator": "InFTF",
    },
    "xrpl_honeycluster_server_info": {
        "url": "https://honeycluster.io/",
        "host": "honeycluster.io",
        "operator": "Honeycluster",
    },
}

# The official XRPL public-server directory classifies these free endpoints as
# non-commercial. Keep them available for explicitly requested one-off research,
# but never include them in the default/scheduled collection set.
NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS = frozenset(XRPL_NODE_SOURCES)
WEEKLY_ENDPOINTS = (
    ("cftc_contract_status_index", "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm"),
    ("cftc_tff_financial_futures", "https://www.cftc.gov/dea/futures/financial_lf.htm"),
)
WEEKLY_SOURCE_IDS = frozenset(source_id for source_id, _url in WEEKLY_ENDPOINTS)
# CFTC currently lists these delayed 2026 release dates. Its announced semiweekly plan has no confirmed effective date yet.
CFTC_DELAYED_RELEASE_DATES_2026 = frozenset({"2026-11-16", "2026-11-30", "2026-12-28"})
CFTC_SEMIWEEKLY_EFFECTIVE_DATE: str | None = None
SCHEDULED_ENDPOINTS = tuple(
    (source_id, url)
    for source_id, url in ENDPOINTS
    if source_id not in NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS
    and source_id not in WEEKLY_SOURCE_IDS
)


def _weekly_endpoints_for_capture(captured: datetime) -> tuple[tuple[str, str], ...]:
    """Select CFTC TFF after scheduled publication, including listed holiday delays."""
    if captured.tzinfo is None:
        return ()
    utc = captured.astimezone(timezone.utc)
    if CFTC_SEMIWEEKLY_EFFECTIVE_DATE is not None:
        if (
            utc.strftime("%Y-%m-%d") >= CFTC_SEMIWEEKLY_EFFECTIVE_DATE
            and utc.weekday() in {2, 4}
            and utc.hour == 21
            and utc.minute >= 3
        ):
            return WEEKLY_ENDPOINTS
        return ()
    if utc.weekday() == 5 and utc.hour in {0, 1} and utc.minute >= 10:
        return WEEKLY_ENDPOINTS
    if (
        utc.strftime("%Y-%m-%d") in CFTC_DELAYED_RELEASE_DATES_2026
        and utc.weekday() == 0
        and utc.hour == 21
        and utc.minute >= 3
    ):
        return WEEKLY_ENDPOINTS
    return ()

class XRPIngestionError(ValueError):
    """A public market-data response cannot be safely ingested."""


class XRPSourceHTTPError(XRPIngestionError):
    """An HTTP response failure with a preserved provider status code."""

    def __init__(self, source_id: str, status_code: int, reason: str = "") -> None:
        self.source_id = source_id
        self.status_code = int(status_code)
        self.reason = str(reason)[:160]
        super().__init__(f"public fetch failed for {source_id} (HTTP {self.status_code})")


BYBIT_SOURCE_IDS = frozenset({"bybit_spot_ticker", "bybit_spot_depth", "bybit_linear_ticker", "bybit_linear_open_interest", "bybit_linear_funding_history"})
BYBIT_ACCESS_DOCUMENTATION_URL = "https://bybit-exchange.github.io/docs/v5/guide"


def _public_fetch_error(source_id: str, exc: Exception) -> XRPIngestionError:
    status_code = getattr(exc, "code", None)
    if not isinstance(status_code, int):
        status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int) and 400 <= status_code <= 599:
        return XRPSourceHTTPError(source_id, status_code, str(getattr(exc, "reason", "")))
    return XRPIngestionError(f"public fetch failed for {source_id}")


def _source_failure_record(
    source_id: str,
    source_uri: str,
    captured_at_utc: str,
    exc: Exception,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "source_id": source_id,
        "source_uri": source_uri,
        "captured_at_utc": captured_at_utc,
        "error_type": type(exc).__name__,
        "error_category": "source_processing_error",
        "model_eligible": False,
        "retryable": False,
    }
    if isinstance(exc, XRPSourceHTTPError):
        status = exc.status_code
        record["http_status_code"] = status
        record["provider_reason"] = exc.reason
        if status == 403:
            record["error_category"] = "provider_http_forbidden"
        elif status == 429:
            record["error_category"] = "provider_rate_limited"
            record["retryable"] = True
        elif status in (408, 504):
            record["error_category"] = "provider_timeout"
            record["retryable"] = True
        elif status >= 500:
            record["error_category"] = "provider_server_error"
            record["retryable"] = True
        elif 400 <= status < 500:
            record["error_category"] = "provider_client_error"
        else:
            record["error_category"] = "provider_http_error"
        if source_id in BYBIT_SOURCE_IDS and status == 403:
            record["provider_access_documentation_url"] = BYBIT_ACCESS_DOCUMENTATION_URL
            record["access_restriction_hint"] = (
                "Bybit documentation states that U.S. and Mainland China IP addresses are restricted "
                "and may receive HTTP 403. The runner region is unverified; do not proxy or bypass "
                "the restriction. Keep this source unavailable until lawful regional access is verified."
            )
    else:
        record["retryable"] = not isinstance(exc, XRPIngestionError)
    return record


class _RejectPublicRedirectHandler(HTTPRedirectHandler):
    """Reject redirects before urllib sends a request to the redirect target."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise XRPIngestionError("public fetch redirects are disabled")


def _open_public_request(request: Request, *, timeout: int = 15):
    """Open a request with redirects disabled at the transport layer."""
    return build_opener(_RejectPublicRedirectHandler()).open(request, timeout=timeout)


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


def _capture_http_headers(headers: Any) -> dict[str, str]:
    """Retain only bounded, non-sensitive HTTP cache/validator metadata."""
    if headers is None or not hasattr(headers, "items"):
        return {}
    captured: dict[str, str] = {}
    try:
        items = headers.items()
    except Exception:
        return {}
    for raw_name, raw_value in items:
        name = str(raw_name).strip().lower()
        if name not in HTTP_PROVENANCE_HEADER_NAMES:
            continue
        value = str(raw_value).strip()
        if not value or len(value) > 512 or any(ord(character) < 32 or ord(character) == 127 for character in value):
            continue
        captured[name] = value
    return dict(sorted(captured.items()))


def _http_cache_age_exclusion_reason(source_id: str, headers: Mapping[str, Any] | None) -> str:
    """Fail closed when a live snapshot is served from an over-age or malformed cache."""
    maximum_age = LIVE_HTTP_CACHE_AGE_LIMITS.get(source_id)
    if maximum_age is None:
        return ""
    age = _capture_http_headers(headers).get("age")
    if age is None:
        return ""
    if not re.fullmatch(r"[0-9]{1,10}", age):
        return "invalid_http_cache_age_header"
    if int(age) > maximum_age:
        return f"http_cache_age_exceeds_{maximum_age}_seconds"
    return ""


def _apply_http_cache_age_gate(
    source_id: str,
    headers: Mapping[str, Any] | None,
    records: list[dict[str, Any]],
) -> str:
    """Mark parsed live features ineligible when their HTTP cache age exceeds policy."""
    reason = _http_cache_age_exclusion_reason(source_id, headers)
    if not reason:
        return ""
    quality = "stale" if reason.startswith("http_cache_age_exceeds_") else "unverified"
    for record in records:
        record["model_eligible"] = False
        record["eligibility_reason"] = reason
        record["quality_status"] = quality
    return reason


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


def _signed_number(value: Any, field: str) -> float:
    """Parse a finite signed market value such as a negative funding rate."""
    if isinstance(value, bool):
        raise XRPIngestionError(f"{field} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise XRPIngestionError(f"{field} must be numeric") from None
    if not math.isfinite(number):
        raise XRPIngestionError(f"{field} must be finite")
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
        with _open_public_request(request, timeout=15) as response:
            final_url = urlsplit(response.geturl())
            if final_url.scheme != "https" or final_url.hostname not in ALLOWED_HOSTS:
                raise XRPIngestionError("public fetch redirected outside allowlisted HTTPS hosts")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            http_date = response.headers.get("Date")
            http_headers = _capture_http_headers(response.headers)
    except XRPIngestionError:
        raise
    except Exception as exc:
        raise _public_fetch_error(source_id, exc) from None
    if not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise XRPIngestionError(f"response size is invalid for {source_id}")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise XRPIngestionError(f"response is not valid JSON for {source_id}") from None
    return {"raw_bytes": raw, "payload": payload, "http_date": http_date, "http_headers": http_headers}


def fetch_public_csv(source_id: str, url: str) -> dict[str, Any]:
    """Capture an allowlisted public CSV response without credentials or redirects."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise XRPIngestionError("source URL is not an allowlisted public HTTPS endpoint")
    request = Request(
        url,
        headers={
            "Accept": "text/csv",
            "User-Agent": "Barrot-XRP-Public-Ingestion/1.0",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with _open_public_request(request, timeout=15) as response:
            final_url = urlsplit(response.geturl())
            if final_url.scheme != "https" or final_url.hostname not in ALLOWED_HOSTS:
                raise XRPIngestionError("public fetch redirected outside allowlisted HTTPS hosts")
            content_type = response.headers.get("Content-Type", "").lower()
            if not content_type.startswith("text/csv"):
                raise XRPIngestionError(f"response is not CSV for {source_id}")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            http_date = response.headers.get("Date")
            http_headers = _capture_http_headers(response.headers)
    except XRPIngestionError:
        raise
    except Exception as exc:
        raise _public_fetch_error(source_id, exc) from None
    if not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise XRPIngestionError(f"response size is invalid for {source_id}")
    try:
        csv_text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise XRPIngestionError(f"response is not valid UTF-8 CSV for {source_id}") from None
    if not csv_text.strip():
        raise XRPIngestionError(f"CSV response is empty for {source_id}")
    return {"raw_bytes": raw, "payload": {"csv_text": csv_text}, "http_date": http_date, "http_headers": http_headers}



def fetch_public_html(source_id: str, url: str) -> dict[str, Any]:
    """Capture allowlisted public HTML as bytes; no credentials are used."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise XRPIngestionError("source URL is not an allowlisted public HTTPS endpoint")
    request = Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": "Barrot-XRP-Public-Ingestion/1.0",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with _open_public_request(request, timeout=15) as response:
            final_url = urlsplit(response.geturl())
            if final_url.scheme != "https" or final_url.hostname not in ALLOWED_HOSTS:
                raise XRPIngestionError("public fetch redirected outside allowlisted HTTPS hosts")
            content_type = response.headers.get("Content-Type", "").lower()
            if not content_type.startswith(("text/html", "application/xhtml+xml")):
                raise XRPIngestionError(f"response is not HTML for {source_id}")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            http_date = response.headers.get("Date")
            http_headers = _capture_http_headers(response.headers)
    except XRPIngestionError:
        raise
    except Exception as exc:
        raise _public_fetch_error(source_id, exc) from None
    if not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise XRPIngestionError(f"response size is invalid for {source_id}")
    try:
        html_text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise XRPIngestionError(f"response is not valid UTF-8 HTML for {source_id}") from None
    return {"raw_bytes": raw, "payload": {"html_text": html_text}, "http_date": http_date, "http_headers": http_headers}


def fetch_public_rpc(source_id: str, url: str) -> dict[str, Any]:
    """Fetch only the fixed, read-only XRPL server_info method from a registered public node."""
    config = XRPL_NODE_SOURCES.get(source_id)
    if config is None or url != config["url"]:
        raise XRPIngestionError("XRPL RPC source is not registered")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != config["host"] or parsed.hostname not in ALLOWED_HOSTS:
        raise XRPIngestionError("XRPL RPC URL is not an allowlisted public HTTPS endpoint")

    body = _canonical({"method": "server_info", "params": [{"api_version": 2}]}).encode("utf-8")
    request = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Barrot-XRP-Public-Ingestion/1.0",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with _open_public_request(request, timeout=15) as response:
            final_url = urlsplit(response.geturl())
            if final_url.scheme != "https" or final_url.hostname != config["host"]:
                raise XRPIngestionError("XRPL RPC redirected outside its registered operator host")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            http_date = response.headers.get("Date")
            http_headers = _capture_http_headers(response.headers)
    except XRPIngestionError:
        raise
    except Exception:
        raise XRPIngestionError(f"public XRPL RPC fetch failed for {source_id}") from None
    if not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise XRPIngestionError(f"XRPL RPC response size is invalid for {source_id}")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise XRPIngestionError(f"XRPL RPC response is not valid JSON for {source_id}") from None
    if (
        not isinstance(payload, Mapping)
        or not isinstance(payload.get("result"), Mapping)
        or payload.get("error")
        or payload.get("status") not in (None, "success")
    ):
        raise XRPIngestionError(f"XRPL RPC response is not a successful server_info result for {source_id}")
    return {"raw_bytes": raw, "payload": payload, "http_date": http_date, "http_headers": http_headers}


class RawReceiptArchive:
    """Write-once raw payloads with canonical receipts and a verifiable per-run hash chain."""

    _CHAIN_ZERO = "0" * 64

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.raw_root = self.root / "sha256"
        self.raw_root.mkdir(parents=True, exist_ok=True)
        self.receipts_path = self.root / "receipts.jsonl"
        self.chain_path = self.root / "receipt_chain.jsonl"
        self.receipts: list[dict[str, Any]] = []
        self._chain_head = self._CHAIN_ZERO
        self._chain_count = 0
        self._legacy_chain_bootstrap = False

        if self.chain_path.exists() and not self.receipts_path.exists():
            raise XRPIngestionError("receipt chain exists without its canonical receipt log")
        if self.receipts_path.exists():
            existing = self._read_receipts()
            if self.chain_path.exists():
                verification = self.verify()
            elif existing:
                # Preserve valid pre-chain archives. Their current bytes are
                # verified before a chain is added; the bootstrap itself is
                # explicitly recorded and is not represented as a prior anchor.
                self._legacy_chain_bootstrap = True
                for receipt in existing:
                    self._verify_receipt(receipt)
                    self._append_chain_record(receipt)
                verification = self.verify()
            else:
                verification = self.verify()
            self.receipts = existing
            self._chain_head = verification["chain_head_sha256"]
            self._chain_count = verification["receipt_count"]

    def _read_receipts(self) -> list[dict[str, Any]]:
        if not self.receipts_path.exists():
            return []
        content = self.receipts_path.read_text(encoding="utf-8")
        if not content:
            return []
        receipts = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            if not line.strip():
                raise XRPIngestionError(f"receipt log contains an empty line at {line_number}")
            try:
                receipt = json.loads(line)
            except json.JSONDecodeError as exc:
                raise XRPIngestionError(f"receipt log contains invalid JSON at line {line_number}") from exc
            if not isinstance(receipt, dict):
                raise XRPIngestionError(f"receipt log line {line_number} must be an object")
            receipts.append(receipt)
        return receipts

    def _verify_receipt(self, receipt: Mapping[str, Any]) -> bool:
        required = {
            "source_id",
            "source_uri",
            "captured_at_utc",
            "source_data_as_of_utc",
            "source_http_date",
            "raw_content_sha256",
            "payload_size_bytes",
            "raw_payload_path",
            "raw_bytes_retained",
            "raw_retention_reason",
            "model_eligible_source",
            "raw_only_reason",
            "receipt_id",
        }
        required_v2 = required | {"source_http_headers"}
        if set(receipt) not in (required, required_v2):
            raise XRPIngestionError("raw receipt does not match the canonical receipt schema")
        for field in ("source_id", "source_uri", "captured_at_utc"):
            if not isinstance(receipt.get(field), str) or not receipt[field].strip():
                raise XRPIngestionError(f"raw receipt {field} must be a non-empty string")
        if receipt.get("source_data_as_of_utc") is not None and not isinstance(receipt.get("source_data_as_of_utc"), str):
            raise XRPIngestionError("raw receipt source_data_as_of_utc must be a string or None")
        if receipt.get("source_http_date") is not None and not isinstance(receipt.get("source_http_date"), str):
            raise XRPIngestionError("raw receipt source_http_date must be a string or None")
        source_http_headers = receipt.get("source_http_headers", {})
        if not isinstance(source_http_headers, Mapping):
            raise XRPIngestionError("raw receipt source_http_headers must be an object")
        for name, value in source_http_headers.items():
            if (
                name not in HTTP_PROVENANCE_HEADER_NAMES
                or not isinstance(value, str)
                or not value
                or len(value) > 512
                or any(ord(character) < 32 or ord(character) == 127 for character in value)
            ):
                raise XRPIngestionError("raw receipt contains invalid or unapproved HTTP provenance headers")
        if not isinstance(receipt.get("raw_retention_reason"), str) or not isinstance(receipt.get("raw_only_reason"), str):
            raise XRPIngestionError("raw receipt retention and raw-only reasons must be strings")
        if not isinstance(receipt.get("raw_bytes_retained"), bool) or not isinstance(receipt.get("model_eligible_source"), bool):
            raise XRPIngestionError("raw receipt retention and eligibility flags must be boolean")
        digest = receipt.get("raw_content_sha256")
        receipt_id = receipt.get("receipt_id")
        if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise XRPIngestionError("raw receipt content digest must be lowercase SHA-256 hex")
        if not isinstance(receipt_id, str) or len(receipt_id) != 64 or any(ch not in "0123456789abcdef" for ch in receipt_id):
            raise XRPIngestionError("raw receipt ID must be lowercase SHA-256 hex")
        size = receipt.get("payload_size_bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise XRPIngestionError("raw receipt payload size must be a positive integer")
        canonical_payload = {key: value for key, value in receipt.items() if key != "receipt_id"}
        expected_id = hashlib.sha256(_canonical(canonical_payload).encode("utf-8")).hexdigest()
        if receipt_id != expected_id:
            raise XRPIngestionError("raw receipt ID does not match canonical receipt metadata")

        if receipt["raw_bytes_retained"]:
            raw_path_value = receipt.get("raw_payload_path")
            if not isinstance(raw_path_value, str) or not raw_path_value.strip() or "\\" in raw_path_value:
                raise XRPIngestionError("retained raw receipt path is invalid")
            relative = Path(raw_path_value)
            if relative.is_absolute() or ".." in relative.parts or relative.parts[-2:] != ("sha256", f"{digest}.json"):
                raise XRPIngestionError("retained raw receipt path is not bound to its SHA-256 digest")
            payload_path = self.root.parent / relative
            if payload_path.is_symlink():
                raise XRPIngestionError("retained raw receipt path cannot be a symbolic link")
            resolved_path = payload_path.resolve()
            if not resolved_path.is_relative_to(self.raw_root.resolve()):
                raise XRPIngestionError("retained raw receipt resolves outside the raw archive")
            try:
                raw_bytes = payload_path.read_bytes()
            except OSError as exc:
                raise XRPIngestionError("retained raw receipt payload is missing or unreadable") from exc
            if len(raw_bytes) != size or hashlib.sha256(raw_bytes).hexdigest() != digest:
                raise XRPIngestionError("retained raw receipt bytes do not match canonical size and SHA-256")
            if receipt["raw_retention_reason"]:
                raise XRPIngestionError("retained raw receipts cannot declare a retention exception")
            if receipt.get("source_data_as_of_utc") is None and receipt["model_eligible_source"]:
                raise XRPIngestionError("model-eligible raw receipts require a source data as-of timestamp")
            return True

        if receipt.get("raw_payload_path") is not None or not receipt["raw_retention_reason"].strip():
            raise XRPIngestionError("digest-only receipts need no payload path and a retention reason")
        return False

    def _append_chain_record(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        payload = {
            "sequence": self._chain_count + 1,
            "receipt_id": receipt["receipt_id"],
            "previous_chain_sha256": self._chain_head,
        }
        chain_hash = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
        record = {**payload, "chain_sha256": chain_hash}
        with self.chain_path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._chain_head = chain_hash
        self._chain_count += 1
        return record

    def verify(self) -> dict[str, Any]:
        """Verify receipt IDs, retained payload bytes and every per-run chain link."""
        receipts = self._read_receipts()
        chain_text = self.chain_path.read_text(encoding="utf-8") if self.chain_path.exists() else ""
        chain_lines = chain_text.splitlines() if chain_text else []
        if len(receipts) != len(chain_lines):
            raise XRPIngestionError("receipt log and receipt-chain entry counts do not match")

        previous = self._CHAIN_ZERO
        retained_count = 0
        digest_only_count = 0
        for index, (receipt, line) in enumerate(zip(receipts, chain_lines), start=1):
            retained = self._verify_receipt(receipt)
            retained_count += int(retained)
            digest_only_count += int(not retained)
            try:
                chain_record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise XRPIngestionError(f"receipt chain contains invalid JSON at entry {index}") from exc
            required_chain_fields = {"sequence", "receipt_id", "previous_chain_sha256", "chain_sha256"}
            if not isinstance(chain_record, dict) or set(chain_record) != required_chain_fields:
                raise XRPIngestionError(f"receipt chain entry {index} has an invalid schema")
            if isinstance(chain_record.get("sequence"), bool) or chain_record.get("sequence") != index:
                raise XRPIngestionError(f"receipt chain sequence is invalid at entry {index}")
            if chain_record.get("receipt_id") != receipt.get("receipt_id"):
                raise XRPIngestionError(f"receipt chain identity mismatch at entry {index}")
            if chain_record.get("previous_chain_sha256") != previous:
                raise XRPIngestionError(f"receipt chain predecessor mismatch at entry {index}")
            chain_payload = {key: value for key, value in chain_record.items() if key != "chain_sha256"}
            expected_chain_hash = hashlib.sha256(_canonical(chain_payload).encode("utf-8")).hexdigest()
            if chain_record.get("chain_sha256") != expected_chain_hash:
                raise XRPIngestionError(f"receipt chain hash mismatch at entry {index}")
            previous = expected_chain_hash

        receipt_bytes = self.receipts_path.read_bytes() if self.receipts_path.exists() else b""
        chain_bytes = self.chain_path.read_bytes() if self.chain_path.exists() else b""
        return {
            "verified": True,
            "receipt_count": len(receipts),
            "retained_raw_payload_count": retained_count,
            "digest_only_receipt_count": digest_only_count,
            "chain_head_sha256": previous,
            "receipt_log_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
            "chain_log_sha256": hashlib.sha256(chain_bytes).hexdigest(),
        }

    def write_manifest(self, path: str | Path) -> dict[str, Any]:
        """Write a run-level verification manifest with GitHub workflow identity when available."""
        verification = self.verify()
        github_context = {
            "repository": os.getenv("GITHUB_REPOSITORY") or None,
            "run_id": os.getenv("GITHUB_RUN_ID") or None,
            "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT") or None,
            "sha": os.getenv("GITHUB_SHA") or None,
            "workflow_ref": os.getenv("GITHUB_WORKFLOW_REF") or None,
            "event_name": os.getenv("GITHUB_EVENT_NAME") or None,
        }
        manifest = {
            "schema_version": "barrot.xrp.raw-receipt-chain.v1",
            "verification_status": "PASS",
            **verification,
            "legacy_chain_bootstrap": self._legacy_chain_bootstrap,
            "github_actions_context": github_context,
            "github_run_context_available": bool(github_context["run_id"] and github_context["sha"]),
            "per_source_independent_timestamp_anchor": False,
            "limitations": [
                "The hash chain is tamper-evident only relative to its final head; an immutable external anchor is still required to prove the artifact was not wholly rewritten.",
                "GitHub run identity binds the artifact to a repository commit and workflow run, but does not independently timestamp each provider observation.",
                "Per-run raw artifacts remain subject to the configured GitHub Actions retention period.",
            ],
        }
        _write_json(path, manifest)
        return manifest

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
        source_http_date: str | None = None,
        source_http_headers: Mapping[str, Any] | None = None,
        retain_raw_bytes: bool = True,
        raw_retention_reason: str = "",
    ) -> dict[str, Any]:
        if not isinstance(raw_bytes, bytes) or not raw_bytes or len(raw_bytes) > MAX_RESPONSE_BYTES:
            raise XRPIngestionError("raw source payload must be non-empty bytes within the size limit")
        if not isinstance(retain_raw_bytes, bool):
            raise XRPIngestionError("retain_raw_bytes must be a boolean")
        if not retain_raw_bytes and (
            not isinstance(raw_retention_reason, str) or not raw_retention_reason.strip()
        ):
            raise XRPIngestionError("digest-only receipts require a raw retention reason")
        if source_http_date is not None and (
            not isinstance(source_http_date, str)
            or len(source_http_date) > 128
            or any(ord(character) < 32 for character in source_http_date)
        ):
            raise XRPIngestionError("source HTTP Date header must be a bounded printable string or None")
        normalized_http_headers: dict[str, str] = {}
        if source_http_headers is not None:
            if not isinstance(source_http_headers, Mapping):
                raise XRPIngestionError("source_http_headers must be a mapping or None")
            for raw_name, raw_value in source_http_headers.items():
                if not isinstance(raw_name, str):
                    raise XRPIngestionError("source HTTP provenance header names must be strings")
                name = raw_name.strip().lower()
                if name not in HTTP_PROVENANCE_HEADER_NAMES:
                    raise XRPIngestionError("source HTTP provenance header is not allowlisted")
                if not isinstance(raw_value, str):
                    raise XRPIngestionError("source HTTP provenance header values must be strings")
                value = raw_value.strip()
                if not value:
                    continue
                if len(value) > 512 or any(ord(character) < 32 or ord(character) == 127 for character in value):
                    raise XRPIngestionError("source HTTP provenance header value is not bounded printable text")
                normalized_http_headers[name] = value
        normalized_http_headers = dict(sorted(normalized_http_headers.items()))
        digest = hashlib.sha256(raw_bytes).hexdigest()
        raw_payload_path = None
        if retain_raw_bytes:
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
            raw_payload_path = str(path.relative_to(self.root.parent))

        receipt = {
            "source_id": source_id,
            "source_uri": source_uri,
            "captured_at_utc": captured_at_utc,
            "source_data_as_of_utc": source_data_as_of_utc,
            "source_http_date": source_http_date,
            "source_http_headers": normalized_http_headers,
            "raw_content_sha256": digest,
            "payload_size_bytes": len(raw_bytes),
            "raw_payload_path": raw_payload_path,
            "raw_bytes_retained": retain_raw_bytes,
            "raw_retention_reason": raw_retention_reason,
            "model_eligible_source": bool(model_eligible),
            "raw_only_reason": raw_only_reason,
        }
        receipt["receipt_id"] = hashlib.sha256(_canonical(receipt).encode("utf-8")).hexdigest()
        self._verify_receipt(receipt)
        with self.receipts_path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical(receipt) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._append_chain_record(receipt)
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


def _parse_binance_funding_history(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    """Capture Binance USD-M funding settlements with their actual event times."""
    if not isinstance(payload, list) or not payload:
        raise XRPIngestionError("Binance funding history must be a non-empty array")
    captured_s = _iso(captured)
    records = []
    seen = set()
    previous_time = None
    latest_time = None
    limitations = [
        "Single Binance USD-M XRPUSDT perpetual contract.",
        "Funding is a signed fraction per actual settlement event; settlement intervals are not assumed fixed or annualized.",
        "Historical rows are first known to this collector at captured_at_utc and cannot be used at earlier point-in-time origins.",
    ]
    for row in payload:
        if not isinstance(row, Mapping) or row.get("symbol") != "XRPUSDT":
            raise XRPIngestionError("Binance funding history symbol or row shape mismatch")
        event_time = _from_ms(row.get("fundingTime"), "Binance fundingTime")
        if event_time > captured:
            raise XRPIngestionError("Binance fundingTime is later than capture time")
        event_s = _iso(event_time)
        if event_s in seen:
            raise XRPIngestionError("Binance funding history contains a duplicate settlement timestamp")
        if previous_time is not None and event_time < previous_time:
            raise XRPIngestionError("Binance funding history is not in ascending event-time order")
        seen.add(event_s)
        previous_time = event_time
        latest_time = event_time if latest_time is None or event_time > latest_time else latest_time
        rate = _signed_number(row.get("fundingRate"), "Binance fundingRate")
        records.append(
            _feature_record(
                feature_id="xrp.perpetual.binance.funding_rate",
                value=rate,
                unit="fraction_per_settlement",
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="binance",
                venue="Binance",
                instrument="XRPUSDT USD-M perpetual",
                currency_pair="XRP/USDT",
                market_type="perpetual",
                aggregation_window="funding_event",
                model_eligible=True,
                quality_status="verified",
                limitations=limitations,
            )
        )
        mark_price = row.get("markPrice")
        if mark_price not in (None, ""):
            records.append(
                _feature_record(
                    feature_id="xrp.perpetual.binance.funding_mark_price",
                    value=_number(mark_price, "Binance funding markPrice", allow_zero=False),
                    unit="USDT/XRP",
                    event_time_utc=event_s,
                    source_data_as_of_utc=event_s,
                    captured_at_utc=captured_s,
                    source_id=source_id,
                    source_uri=url,
                    raw_sha256=digest,
                    independence_group="binance",
                    venue="Binance",
                    instrument="XRPUSDT USD-M perpetual",
                    currency_pair="XRP/USDT",
                    market_type="perpetual",
                    aggregation_window="funding_event",
                    model_eligible=True,
                    quality_status="verified",
                    limitations=limitations,
                )
            )
    if not records or latest_time is None:
        raise XRPIngestionError("Binance funding history contains no usable settlements")
    return records, _iso(latest_time), True, ""


def _parse_binance_open_interest_history(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    """Capture Binance's one-hour open-interest history without inventing gaps."""
    if not isinstance(payload, list) or not payload:
        raise XRPIngestionError("Binance open-interest history must be a non-empty array")
    captured_s = _iso(captured)
    records = []
    seen = set()
    previous_time = None
    latest_time = None
    limitations = [
        "Single Binance USD-M XRPUSDT perpetual contract; endpoint history is limited to the latest 30 days and no-trade periods may be omitted.",
        "Historical rows are first known to this collector at captured_at_utc and cannot be used at earlier point-in-time origins.",
        "Open-interest contracts and Binance-reported USDT value are retained separately; no USD conversion or cross-venue aggregation is inferred.",
    ]
    for row in payload:
        if not isinstance(row, Mapping) or row.get("symbol") != "XRPUSDT":
            raise XRPIngestionError("Binance open-interest history symbol or row shape mismatch")
        event_time = _from_ms(row.get("timestamp"), "Binance open-interest history timestamp")
        if event_time > captured:
            raise XRPIngestionError("Binance open-interest history timestamp is later than capture time")
        event_s = _iso(event_time)
        if event_s in seen:
            raise XRPIngestionError("Binance open-interest history contains a duplicate timestamp")
        if previous_time is not None and event_time < previous_time:
            raise XRPIngestionError("Binance open-interest history is not in ascending event-time order")
        seen.add(event_s)
        previous_time = event_time
        latest_time = event_time if latest_time is None or event_time > latest_time else latest_time
        metrics = (
            ("sumOpenInterest", "xrp.perpetual.binance.1h.open_interest_contracts", "contracts"),
            ("sumOpenInterestValue", "xrp.perpetual.binance.1h.open_interest_value", "USDT"),
        )
        for field, feature_id, unit in metrics:
            records.append(
                _feature_record(
                    feature_id=feature_id,
                    value=_number(row.get(field), f"Binance open-interest history {field}", allow_zero=False),
                    unit=unit,
                    event_time_utc=event_s,
                    source_data_as_of_utc=event_s,
                    captured_at_utc=captured_s,
                    source_id=source_id,
                    source_uri=url,
                    raw_sha256=digest,
                    independence_group="binance",
                    venue="Binance",
                    instrument="XRPUSDT USD-M perpetual",
                    currency_pair="XRP/USDT",
                    market_type="perpetual",
                    aggregation_window="1h",
                    model_eligible=True,
                    quality_status="verified",
                    limitations=limitations,
                )
            )
    if not records or latest_time is None:
        raise XRPIngestionError("Binance open-interest history contains no usable observations")
    return records, _iso(latest_time), True, ""


def _parse_binance_global_long_short_ratio(payload: Any, *, source_id: str, url: str, digest: str, captured: datetime):
    """Capture global account ratios without treating account counts as notional."""
    if not isinstance(payload, list) or not payload:
        raise XRPIngestionError("Binance global long/short history must be a non-empty array")
    captured_s = _iso(captured)
    records = []
    seen = set()
    previous_time = None
    latest_time = None
    limitations = [
        "Global long/short values are account-count ratios and fractions, not position size, notional exposure or trader capital.",
        "Single Binance USD-M XRPUSDT perpetual contract; endpoint history is limited to the latest 30 days and no-trade periods may be omitted.",
        "Historical rows are first known to this collector at captured_at_utc and cannot be used at earlier point-in-time origins.",
    ]
    for row in payload:
        if not isinstance(row, Mapping) or row.get("symbol") != "XRPUSDT":
            raise XRPIngestionError("Binance global long/short history symbol or row shape mismatch")
        event_time = _from_ms(row.get("timestamp"), "Binance global long/short timestamp")
        if event_time > captured:
            raise XRPIngestionError("Binance global long/short timestamp is later than capture time")
        event_s = _iso(event_time)
        if event_s in seen:
            raise XRPIngestionError("Binance global long/short history contains a duplicate timestamp")
        if previous_time is not None and event_time < previous_time:
            raise XRPIngestionError("Binance global long/short history is not in ascending event-time order")
        seen.add(event_s)
        previous_time = event_time
        latest_time = event_time if latest_time is None or event_time > latest_time else latest_time
        ratio = _number(row.get("longShortRatio"), "Binance longShortRatio", allow_zero=False)
        long_fraction = _number(row.get("longAccount"), "Binance longAccount", allow_zero=False)
        short_fraction = _number(row.get("shortAccount"), "Binance shortAccount", allow_zero=False)
        if long_fraction > 1 or short_fraction > 1 or abs((long_fraction + short_fraction) - 1.0) > 0.02:
            raise XRPIngestionError("Binance long/short account fractions must sum to one")
        implied_ratio = long_fraction / short_fraction
        ratio_consistent = math.isclose(ratio, implied_ratio, rel_tol=0.05, abs_tol=0.02)
        limitations_with_reconciliation = limitations + [
            "The exchange-reported ratio is preserved as reported; if it conflicts with the accompanying account fractions, only the ratio feature is excluded and the fractions remain separate. No corrected ratio is inferred."
        ]
        metrics = (
            (
                "xrp.perpetual.binance.1h.global_long_short_account_ratio",
                ratio,
                "ratio",
                ratio_consistent,
                "" if ratio_consistent else "reported_ratio_conflicts_with_account_fractions",
                "verified" if ratio_consistent else "unverified",
            ),
            ("xrp.perpetual.binance.1h.global_long_account_fraction", long_fraction, "fraction_of_accounts", True, "", "verified"),
            ("xrp.perpetual.binance.1h.global_short_account_fraction", short_fraction, "fraction_of_accounts", True, "", "verified"),
        )
        for feature_id, value, unit, feature_eligible, eligibility_reason, quality_status in metrics:
            records.append(
                _feature_record(
                    feature_id=feature_id,
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
                    instrument="XRPUSDT USD-M perpetual",
                    currency_pair="XRP/USDT",
                    market_type="perpetual",
                    aggregation_window="1h",
                    model_eligible=feature_eligible,
                    eligibility_reason=eligibility_reason,
                    quality_status=quality_status,
                    limitations=limitations_with_reconciliation,
                )
            )
    if not records or latest_time is None:
        raise XRPIngestionError("Binance global long/short history contains no usable observations")
    return records, _iso(latest_time), True, ""


def _parse_xrpl_server_info(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    http_date: str | None = None,
):
    """Parse one node's validated-ledger status; cross-node agreement is checked separately."""
    config = XRPL_NODE_SOURCES.get(source_id)
    if config is None:
        raise XRPIngestionError("XRPL server-info source is not registered")
    if not isinstance(payload, Mapping) or not isinstance(payload.get("result"), Mapping):
        raise XRPIngestionError("XRPL server_info response shape mismatch")
    info = payload["result"].get("info")
    if not isinstance(info, Mapping):
        raise XRPIngestionError("XRPL server_info response has no info object")
    validated = info.get("validated_ledger")
    if not isinstance(validated, Mapping):
        return [], None, False, "validated_ledger_missing_from_public_node"

    sequence = validated.get("seq")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence <= 0:
        raise XRPIngestionError("XRPL validated ledger sequence is invalid")
    ledger_hash = validated.get("hash")
    if not isinstance(ledger_hash, str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", ledger_hash):
        raise XRPIngestionError("XRPL validated ledger hash is invalid")

    age = _number(validated.get("age"), "XRPL validated ledger age")
    base_fee = _number(validated.get("base_fee_xrp"), "XRPL base fee", allow_zero=False)
    reserve_base = _number(validated.get("reserve_base_xrp"), "XRPL base reserve", allow_zero=False)
    reserve_increment = _number(validated.get("reserve_inc_xrp"), "XRPL owner reserve increment", allow_zero=False)
    server_date = _from_http_date(http_date)
    if server_date is None:
        return [], None, False, "missing_or_invalid_http_date_for_xrpl_server_info"
    if server_date > captured + timedelta(seconds=60):
        raise XRPIngestionError("XRPL server HTTP Date is later than the capture clock")
    source_time = server_date
    if source_time > captured + timedelta(seconds=60):
        raise XRPIngestionError("XRPL server response time is later than the capture clock")
    fresh, freshness_reason, quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
    if age > MAX_LIVE_AGE_SECONDS:
        eligible, reason, quality = False, "validated_ledger_age_exceeds_300_seconds", "stale"
    elif not fresh:
        eligible, reason = False, freshness_reason
    else:
        # Network server_info is an integrity/operations observation, not an
        # economic XRP feature. Agreement between nodes cannot make it model data.
        eligible, reason = False, "xrpl_node_state_is_integrity_only_not_an_economic_feature"
    event_s, captured_s = _iso(source_time), _iso(captured)
    limitations = [
        f"Public non-commercial XRPL node operated by {config['operator']}; source_id preserves operator identity.",
        "HTTP Date timestamps the server-info response to whole seconds; validated_ledger_age_seconds separately reports ledger lag. This is not the exact ledger close time and server/proxy clock skew may remain.",
        "Validated-ledger index, fee and reserve metrics are network state, not exchange volume, payment volume, XRP collateral or circulating supply.",
        "The two node operators report the same public ledger; their agreement is a node-integrity check, not independent economic evidence.",
    ]
    fields = (
        ("validated_ledger_index", float(sequence), "ledger_index"),
        ("validated_ledger_age_seconds", age, "seconds"),
        ("base_fee_xrp", base_fee, "XRP"),
        ("reserve_base_xrp", reserve_base, "XRP"),
        ("reserve_increment_xrp", reserve_increment, "XRP"),
    )
    records = [
        _feature_record(
            feature_id=f"xrp.network.xrpl.{name}",
            value=value,
            unit=unit,
            event_time_utc=event_s,
            source_data_as_of_utc=event_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="xrpl_public_ledger",
            venue="XRPL",
            instrument="XRPL mainnet validated server state",
            currency_pair="XRP/network",
            market_type="network",
            model_eligible=eligible,
            eligibility_reason=reason,
            quality_status=quality,
            limitations=limitations,
        )
        for name, value, unit in fields
    ]
    return records, event_s, eligible, reason


def _reconcile_xrpl_node_records(
    records: list[dict[str, Any]],
    payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Require two registered operators to report the same validated ledger before admission."""
    observations: dict[str, dict[str, Any]] = {}
    for source_id, config in XRPL_NODE_SOURCES.items():
        payload = payloads.get(source_id)
        if not isinstance(payload, Mapping):
            continue
        result = payload.get("result")
        info = result.get("info") if isinstance(result, Mapping) else None
        validated = info.get("validated_ledger") if isinstance(info, Mapping) else None
        if not isinstance(validated, Mapping):
            continue
        sequence = validated.get("seq")
        ledger_hash = validated.get("hash")
        if (
            isinstance(sequence, bool)
            or not isinstance(sequence, int)
            or sequence <= 0
            or not isinstance(ledger_hash, str)
            or not re.fullmatch(r"[0-9A-Fa-f]{64}", ledger_hash)
        ):
            continue
        observations[source_id] = {
            "operator": config["operator"],
            "ledger_index": sequence,
            "ledger_hash": ledger_hash.upper(),
        }

    identities = {(item["ledger_index"], item["ledger_hash"]) for item in observations.values()}
    if len(observations) == len(XRPL_NODE_SOURCES) and len(identities) == 1:
        status = "AGREED"
        reason = ""
    elif len(observations) == len(XRPL_NODE_SOURCES):
        status = "DISAGREEMENT"
        reason = "xrpl_public_nodes_report_different_validated_ledgers"
    else:
        status = "INSUFFICIENT_NODE_CONFIRMATION"
        reason = "xrpl_public_node_independent_confirmation_missing"

    node_records = []
    for record in records:
        source_ids = {
            source.get("source_id")
            for source in record.get("sources", [])
            if isinstance(source, Mapping)
        }
        if source_ids.intersection(XRPL_NODE_SOURCES):
            node_records.append(record)
            if status != "AGREED":
                record["model_eligible"] = False
                record["eligibility_reason"] = reason
                record["quality_status"] = "unverified"

    return {
        "status": status,
        "reason": reason,
        "required_source_count": len(XRPL_NODE_SOURCES),
        "observed_source_count": len(observations),
        "observed_source_ids": sorted(observations),
        "observations": observations,
        "integrity_check_only": True,
        "model_admission_allowed": False,
        "model_admission_reason": "xrpl_node_agreement_is_not_independent_economic_corroboration_or_a_model_feature",
    }


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


def _parse_coinbase_candles(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    page_start_utc: str | None = None,
    page_end_utc: str | None = None,
):
    if not isinstance(payload, list):
        raise XRPIngestionError("Coinbase candle response must be an array")
    if (page_start_utc is None) != (page_end_utc is None):
        raise XRPIngestionError("Coinbase backfill page requires both start and end boundaries")
    page_start = _from_iso8601(page_start_utc, "Coinbase backfill page start") if page_start_utc is not None else None
    page_end = _from_iso8601(page_end_utc, "Coinbase backfill page end") if page_end_utc is not None else None
    if page_start is not None and page_end is not None and page_start >= page_end:
        raise XRPIngestionError("Coinbase backfill page start must precede its end")
    if not payload and page_start is None:
        raise XRPIngestionError("Coinbase candle response must be a non-empty array")

    captured_s = _iso(captured)
    records = []
    latest_close = None
    incomplete = 0
    seen_open_times = set()
    in_range_rows = []
    limitations = [
        "Historical Coinbase candles were first observed at this capture time; they are not known at historical event times.",
        "The public Coinbase endpoint returns at most 300 candles per request; extended history is acquired only by an explicit manual backfill.",
        "Coinbase omits intervals with no ticks; missing hours are not synthesized as zero-volume candles.",
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
        if page_start is not None and int(open_time.timestamp()) % COINBASE_CANDLE_GRANULARITY_SECONDS != 0:
            raise XRPIngestionError("Coinbase backfill candle open time is not aligned to its hourly granularity")
        if page_start is not None and page_end is not None and (open_time < page_start or open_time >= page_end):
            continue
        if open_time in seen_open_times:
            raise XRPIngestionError("Coinbase candle response contains a duplicate timestamp")
        seen_open_times.add(open_time)
        in_range_rows.append((open_time, row))

    for open_time, row in sorted(in_range_rows, key=lambda item: item[0]):
        close_time = open_time + timedelta(seconds=COINBASE_CANDLE_GRANULARITY_SECONDS)
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
        if page_start is not None:
            return [], None, False, "coinbase_backfill_page_has_no_in_range_completed_candles"
        raise XRPIngestionError("Coinbase candle response contains no completed hourly candles")
    reason = f"incomplete_current_candles_skipped:{incomplete}" if incomplete else ""
    return records, latest_close, True, reason


def _coinbase_candle_backfill_ranges(oldest_open: datetime, days: int) -> list[tuple[datetime, datetime]]:
    """Build contiguous, non-overlapping Coinbase hourly windows of at most 300 candles."""
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= MAX_COINBASE_BACKFILL_DAYS:
        raise XRPIngestionError(f"Coinbase backfill days must be an integer from 1 to {MAX_COINBASE_BACKFILL_DAYS}")
    if not isinstance(oldest_open, datetime) or oldest_open.tzinfo is None or oldest_open.utcoffset() is None:
        raise XRPIngestionError("Coinbase backfill boundary must be timezone-aware")
    end = oldest_open.astimezone(timezone.utc)
    if end.minute or end.second or end.microsecond:
        raise XRPIngestionError("Coinbase backfill boundary must align to the hourly candle granularity")
    start = end - timedelta(days=days)
    ranges = []
    cursor = start
    page_width = timedelta(hours=COINBASE_CANDLES_PER_REQUEST)
    while cursor < end:
        page_end = min(cursor + page_width, end)
        ranges.append((cursor, page_end))
        cursor = page_end
    if not ranges or len(ranges) > MAX_COINBASE_BACKFILL_PAGES:
        raise XRPIngestionError("Coinbase backfill page count exceeds its bounded limit")
    return ranges


def _coinbase_candle_page_url(start: datetime, end: datetime) -> str:
    base_url = dict(ENDPOINTS)["coinbase_spot_candles"]
    parts = urlsplit(base_url)
    query = urlencode(
        {
            "granularity": str(COINBASE_CANDLE_GRANULARITY_SECONDS),
            "start": _iso(start),
            "end": _iso(end),
        }
    )
    return f"{parts.scheme}://{parts.netloc}{parts.path}?{query}"

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




def _bitbank_data(payload: Any, source_name: str) -> Mapping[str, Any]:
    if (
        not isinstance(payload, Mapping)
        or payload.get("success") != 1
        or not isinstance(payload.get("data"), Mapping)
    ):
        raise XRPIngestionError(f"Bitbank {source_name} response shape or success code mismatch")
    return payload["data"]


def _bitbank_circuit_context(
    payload: Any,
    captured: datetime,
) -> tuple[str | None, datetime | None, bool, str]:
    if not isinstance(payload, Mapping):
        return None, None, False, "missing_bitbank_circuit_break_state"
    try:
        data = _bitbank_data(payload, "circuit-break context")
        mode = data.get("mode")
        if mode not in BITBANK_CIRCUIT_MODES:
            raise XRPIngestionError("Bitbank circuit-break mode is unknown")
        source_time = _from_ms(data.get("timestamp"), "Bitbank circuit-break timestamp")
        if source_time > captured:
            raise XRPIngestionError("Bitbank circuit-break timestamp is later than capture time")
        estimated = data.get("estimated_itayose_price")
        if estimated is not None:
            _number(estimated, "Bitbank estimated itayose price", allow_zero=False)
        if mode == "NONE" and estimated is not None:
            raise XRPIngestionError("Bitbank NONE circuit mode cannot carry an estimated itayose price")
        eligible, reason, _quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
        return mode, source_time, eligible, reason
    except XRPIngestionError:
        return None, None, False, "missing_or_invalid_bitbank_circuit_break_state"


def _parse_bitbank_circuit_break(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    http_date: str | None = None,
):
    data = _bitbank_data(payload, "circuit-break info")
    mode = data.get("mode")
    if mode not in BITBANK_CIRCUIT_MODES:
        raise XRPIngestionError("Bitbank circuit-break mode is unknown")
    source_time = _from_ms(data.get("timestamp"), "Bitbank circuit-break timestamp")
    if source_time > captured:
        raise XRPIngestionError("Bitbank circuit-break timestamp is later than capture time")
    estimated = data.get("estimated_itayose_price")
    if estimated is not None:
        _number(estimated, "Bitbank estimated itayose price", allow_zero=False)
    if mode == "NONE" and estimated is not None:
        raise XRPIngestionError("Bitbank NONE circuit mode cannot carry an estimated itayose price")
    return [], _iso(source_time), False, "market_state_context_only_not_numeric_feature"


def _parse_bitbank_ticker(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    circuit_break_info: Any = None,
    http_date: str | None = None,
):
    data = _bitbank_data(payload, "XRP/JPY ticker")
    source_time = _from_ms(data.get("timestamp"), "Bitbank ticker timestamp")
    if source_time > captured:
        raise XRPIngestionError("Bitbank ticker timestamp is later than capture time")
    fresh, stale_reason, stale_quality = _live_eligibility(
        source_time, captured, MAX_LIVE_AGE_SECONDS
    )
    mode, mode_time, mode_fresh, mode_reason = _bitbank_circuit_context(
        circuit_break_info, captured
    )
    mode_synchronized = (
        mode_time is not None
        and abs((source_time - mode_time).total_seconds()) <= 60
    )
    continuous = mode == "NONE" and mode_fresh and mode_synchronized
    bid = _number(data.get("buy"), "Bitbank ticker best bid", allow_zero=False)
    ask = _number(data.get("sell"), "Bitbank ticker best ask", allow_zero=False)
    quote_valid = ask > bid
    quote_eligible = fresh and continuous and quote_valid
    if not fresh:
        quote_reason = stale_reason
    elif not mode_synchronized or not mode_fresh or mode is None:
        quote_reason = "bitbank_circuit_break_state_missing_stale_or_unsynchronized"
    elif mode != "NONE":
        quote_reason = f"bitbank_market_mode_{mode.lower()}_not_continuous"
    elif not quote_valid:
        quote_reason = "bitbank_ticker_quote_crossed_or_locked"
    else:
        quote_reason = ""
    event_s, captured_s = _iso(source_time), _iso(captured)
    mid = (bid + ask) / 2.0
    spread_bps = (ask - bid) / mid * 10000.0
    limitations = [
        "Single Bitbank XRP/JPY spot venue; JPY is not converted to USD or USDT.",
        "Bitbank ticker timestamp is the ticker update time, not an individual last-trade execution timestamp.",
        "Bitbank documents that sell may be less than or equal to buy outside continuous trading mode; quote features require a synchronized NONE circuit-break state and a positive spread.",
        "24-hour ticker aggregates are not consolidated exchange flows.",
    ]
    last_price = _number(data.get("last"), "Bitbank ticker last price", allow_zero=False)
    volume = _number(data.get("vol"), "Bitbank ticker 24h volume", allow_zero=True)
    high = _number(data.get("high"), "Bitbank ticker 24h high", allow_zero=False)
    low = _number(data.get("low"), "Bitbank ticker 24h low", allow_zero=False)
    open_price = _number(data.get("open"), "Bitbank ticker 24h open", allow_zero=False)
    metrics = [
        ("last_price_snapshot", last_price, "JPY/XRP", False, "ticker_snapshot_not_trade_event"),
        ("base_volume_24h", volume, "XRP/24h", fresh, stale_reason),
        ("high_24h", high, "JPY/XRP", fresh, stale_reason),
        ("low_24h", low, "JPY/XRP", fresh, stale_reason),
        ("open_24h", open_price, "JPY/XRP", fresh, stale_reason),
        ("best_bid", bid, "JPY/XRP", quote_eligible, quote_reason),
        ("best_ask", ask, "JPY/XRP", quote_eligible, quote_reason),
        ("mid_price", mid, "JPY/XRP", quote_eligible, quote_reason),
        ("spread_bps", spread_bps, "bps", quote_eligible, quote_reason),
    ]
    records = []
    for name, value, unit, eligible, reason in metrics:
        quality = "verified" if eligible else ("stale" if not fresh else "unverified")
        records.append(
            _feature_record(
                feature_id=f"xrp.spot.bitbank.{name}",
                value=value,
                unit=unit,
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="bitbank",
                venue="Bitbank",
                instrument="XRP/JPY spot",
                currency_pair="XRP/JPY",
                market_type="spot",
                aggregation_window="24h" if name.endswith("_24h") else "",
                model_eligible=eligible,
                eligibility_reason=reason,
                quality_status=quality,
                limitations=limitations,
            )
        )
    # The last field is the latest executed price, but the ticker's timestamp is
    # only a ticker-update time. Keep it visible as a snapshot and fail it closed
    # as a trade-event feature until a trade-time source is used.
    return records, event_s, fresh, stale_reason


def _parse_bitbank_depth(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    circuit_break_info: Any = None,
    http_date: str | None = None,
):
    data = _bitbank_data(payload, "XRP/JPY order book")
    source_time = _from_ms(data.get("timestamp"), "Bitbank order-book timestamp")
    if source_time > captured:
        raise XRPIngestionError("Bitbank order-book timestamp is later than capture time")
    fresh, stale_reason, _quality = _live_eligibility(
        source_time, captured, MAX_ORDERBOOK_AGE_SECONDS
    )
    mode, mode_time, mode_fresh, mode_reason = _bitbank_circuit_context(
        circuit_break_info, captured
    )
    mode_synchronized = (
        mode_time is not None
        and abs((source_time - mode_time).total_seconds()) <= 60
    )
    continuous = mode == "NONE" and mode_fresh and mode_synchronized
    bids_raw, asks_raw = data.get("bids"), data.get("asks")
    if (
        not isinstance(bids_raw, list)
        or not bids_raw
        or len(bids_raw) > 400
        or not isinstance(asks_raw, list)
        or not asks_raw
        or len(asks_raw) > 400
    ):
        raise XRPIngestionError("Bitbank order book must contain 1–400 bids and asks")
    def parse_levels(rows: list[Any], side: str) -> list[tuple[float, float]]:
        levels = []
        for row in rows:
            if not isinstance(row, list) or len(row) < 2:
                raise XRPIngestionError(f"Bitbank {side} level schema mismatch")
            price = _number(row[0], f"Bitbank {side} price", allow_zero=False)
            quantity = _number(row[1], f"Bitbank {side} quantity", allow_zero=False)
            levels.append((price, quantity))
        return levels
    bids, asks = parse_levels(bids_raw, "bid"), parse_levels(asks_raw, "ask")
    best_bid = max(price for price, _quantity in bids)
    best_ask = min(price for price, _quantity in asks)
    book_valid = best_ask > best_bid
    if mode == "NONE" and not book_valid:
        raise XRPIngestionError("Bitbank continuous order book is crossed or locked")
    eligible = fresh and continuous and book_valid
    if not fresh:
        reason = stale_reason
    elif not mode_synchronized or not mode_fresh or mode is None:
        reason = "bitbank_circuit_break_state_missing_stale_or_unsynchronized"
    elif mode != "NONE":
        reason = f"bitbank_market_mode_{mode.lower()}_not_continuous"
    elif not book_valid:
        reason = "bitbank_order_book_crossed_or_locked"
    else:
        reason = ""
    mid = (best_bid + best_ask) / 2.0
    spread_bps = (best_ask - best_bid) / mid * 10000.0
    features = [
        ("best_bid", best_bid, "JPY/XRP"),
        ("best_ask", best_ask, "JPY/XRP"),
        ("mid_price", mid, "JPY/XRP"),
        ("spread_bps", spread_bps, "bps"),
    ]
    for band in (10, 50, 100):
        bid_depth = sum(
            price * quantity for price, quantity in bids
            if price >= mid * (1 - band / 10000.0)
        )
        ask_depth = sum(
            price * quantity for price, quantity in asks
            if price <= mid * (1 + band / 10000.0)
        )
        total = bid_depth + ask_depth
        imbalance = (bid_depth - ask_depth) / total if total > 0 else 0.0
        features.extend([
            (f"bid_depth_{band}bps", bid_depth, "JPY"),
            (f"ask_depth_{band}bps", ask_depth, "JPY"),
            (f"depth_imbalance_{band}bps", imbalance, "ratio"),
        ])
    limitations = [
        "Single Bitbank XRP/JPY spot order-book snapshot; not global or consolidated liquidity.",
        "Depth is denominated in JPY and is not converted to USD or USDT.",
        "Bitbank documents that circuit-break books may be centered on an estimated auction price and may cross; depth is admitted only in synchronized NONE mode.",
        "Sequence IDs are retained in the raw receipt but no sequence bridge or continuity claim is made.",
        "asks_over, bids_under, asks_under, bids_over, ask_market and bid_market are retained in raw data but not included in the depth sums.",
    ]
    event_s, captured_s = _iso(source_time), _iso(captured)
    records = [
        _feature_record(
            feature_id=f"xrp.spot.bitbank.orderbook.{name}",
            value=value,
            unit=unit,
            event_time_utc=event_s,
            source_data_as_of_utc=event_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="bitbank",
            venue="Bitbank",
            instrument="XRP/JPY spot",
            currency_pair="XRP/JPY",
            market_type="spot",
            model_eligible=eligible,
            eligibility_reason=reason,
            quality_status="verified" if eligible else ("stale" if not fresh else "unverified"),
            limitations=limitations,
        )
        for name, value, unit in features
    ]
    # Preserve the provider sequence id in the raw receipt; it is not treated as
    # a complete sequence bridge because Bitbank says it is not always consecutive.
    return records, event_s, fresh, stale_reason


def _parse_bitbank_transactions(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    http_date: str | None = None,
):
    data = _bitbank_data(payload, "XRP/JPY transactions")
    rows = data.get("transactions")
    if not isinstance(rows, list) or len(rows) > 60:
        raise XRPIngestionError("Bitbank latest-transactions response must contain at most 60 rows")
    if not rows:
        return [], None, False, "no_recent_transactions_raw_only"
    parsed = []
    seen_ids = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise XRPIngestionError("Bitbank transaction row must be an object")
        transaction_id = row.get("transaction_id")
        if isinstance(transaction_id, bool):
            raise XRPIngestionError("Bitbank transaction id must be a positive integer")
        try:
            transaction_id = int(transaction_id)
        except (TypeError, ValueError, OverflowError):
            raise XRPIngestionError("Bitbank transaction id must be a positive integer") from None
        if transaction_id <= 0 or transaction_id in seen_ids:
            raise XRPIngestionError("Bitbank transaction ids must be positive and unique")
        seen_ids.add(transaction_id)
        side = row.get("side")
        if side not in {"buy", "sell"}:
            raise XRPIngestionError("Bitbank transaction taker side must be buy or sell")
        price = _number(row.get("price"), "Bitbank transaction price", allow_zero=False)
        amount = _number(row.get("amount"), "Bitbank transaction amount", allow_zero=False)
        executed = _from_ms(row.get("executed_at"), "Bitbank transaction executed_at")
        if executed > captured:
            raise XRPIngestionError("Bitbank transaction executed_at is later than capture time")
        parsed.append((transaction_id, side, price, amount, executed))
    parsed.sort(key=lambda item: (item[4], item[0]))
    captured_s = _iso(captured)
    limitations = [
        "Bitbank public endpoint returns only the latest 60 transactions when no date is supplied.",
        "Snapshots overlap; transaction ids are appended to record ids so repeated trades can be deduplicated.",
        "The latest-60 sample is not a fixed-duration or complete 24-hour exchange-flow measure.",
        "Trade events are known to this collector only at captured_at_utc; they are never backdated into earlier point-in-time cutoffs.",
        "Taker side is the exchange-reported transaction side; buy is positive and sell is negative for signed-flow features.",
    ]
    records = []
    for transaction_id, side, price, amount, executed in parsed:
        event_s = _iso(executed)
        signed_amount = amount if side == "buy" else -amount
        notional = price * amount
        signed_notional = notional if side == "buy" else -notional
        features = [
            ("price", price, "JPY/XRP"),
            ("amount", amount, "XRP"),
            ("signed_amount", signed_amount, "XRP"),
            ("notional", notional, "JPY"),
            ("signed_notional", signed_notional, "JPY"),
            ("side_is_buy", 1.0 if side == "buy" else 0.0, "ratio"),
        ]
        for name, value, unit in features:
            record = _feature_record(
                feature_id=f"xrp.spot.bitbank.trade.{name}",
                value=value,
                unit=unit,
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="bitbank",
                venue="Bitbank",
                instrument=f"XRP/JPY spot trade {transaction_id}",
                currency_pair="XRP/JPY",
                market_type="spot",
                model_eligible=False,
                eligibility_reason="latest_60_trade_sample_incomplete_coverage",
                quality_status="unverified",
                limitations=limitations,
            )
            record["record_id"] = f"{record['record_id']}:{transaction_id}"
            record["transaction_id"] = transaction_id
            record["taker_side"] = side
            records.append(record)
    return (
        records,
        _iso(max(item[4] for item in parsed)),
        False,
        "latest_60_trade_sample_incomplete_coverage",
    )


def _bitbank_transactions_research_summary(payload: Any) -> dict[str, Any] | None:
    data = _bitbank_data(payload, "XRP/JPY transactions summary")
    rows = data.get("transactions")
    if not isinstance(rows, list) or not rows:
        return None
    parsed = []
    for row in rows:
        side = row["side"]
        price = float(row["price"])
        amount = float(row["amount"])
        executed = _from_ms(row["executed_at"], "Bitbank transaction executed_at")
        parsed.append((side, price, amount, executed))
    earliest = min(item[3] for item in parsed)
    latest = max(item[3] for item in parsed)
    buy_amount = sum(item[2] for item in parsed if item[0] == "buy")
    sell_amount = sum(item[2] for item in parsed if item[0] == "sell")
    buy_notional = sum(item[1] * item[2] for item in parsed if item[0] == "buy")
    sell_notional = sum(item[1] * item[2] for item in parsed if item[0] == "sell")
    return {
        "observation_type": "bitbank_latest_60_trade_sample",
        "currency_pair": "XRP/JPY",
        "window_kind": "latest_60_trades_variable_duration",
        "trade_count": len(parsed),
        "first_trade_at_utc": _iso(earliest),
        "last_trade_at_utc": _iso(latest),
        "sample_window_seconds": (latest - earliest).total_seconds(),
        "buy_taker_volume_xrp": round(buy_amount, 12),
        "sell_taker_volume_xrp": round(sell_amount, 12),
        "net_taker_flow_xrp": round(buy_amount - sell_amount, 12),
        "buy_taker_notional_jpy": round(buy_notional, 8),
        "sell_taker_notional_jpy": round(sell_notional, 8),
        "net_taker_flow_jpy": round(buy_notional - sell_notional, 8),
        "model_eligible": False,
        "reason": "Variable latest-60-trade window; not a fixed-duration or complete 24-hour flow metric.",
    }



def _parse_kraken_ticker(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    http_date: str | None = None,
):
    """Parse Kraken ticker values as a server-timestamped snapshot, not trade events."""
    if not isinstance(payload, Mapping) or payload.get("error") not in ([], None):
        raise XRPIngestionError("Kraken ticker response contains an API error")
    result = payload.get("result")
    if not isinstance(result, Mapping):
        raise XRPIngestionError("Kraken ticker response has no result mapping")
    ticker = next((value for value in result.values() if isinstance(value, Mapping)), None)
    if not isinstance(ticker, Mapping):
        raise XRPIngestionError("Kraken ticker response has no pair data")

    def pair(key: str, field: str) -> list[Any]:
        value = ticker.get(key)
        if not isinstance(value, list) or len(value) < 2:
            raise XRPIngestionError(f"Kraken ticker {field} array schema mismatch")
        return value

    ask_row = pair("a", "ask")
    bid_row = pair("b", "bid")
    last_row = pair("c", "last trade")
    volume_row = pair("v", "volume")
    vwap_row = pair("p", "VWAP")
    trade_count_row = pair("t", "trade count")
    low_row = pair("l", "low")
    high_row = pair("h", "high")

    ask = _number(ask_row[0], "Kraken ticker best ask", allow_zero=False)
    bid = _number(bid_row[0], "Kraken ticker best bid", allow_zero=False)
    last = _number(last_row[0], "Kraken ticker last trade price", allow_zero=False)
    last_size = _number(last_row[1], "Kraken ticker last trade size", allow_zero=False)
    if ask <= bid:
        raise XRPIngestionError("Kraken ticker bid/ask is crossed or locked")

    # Kraken's ticker payload does not include a last-trade event timestamp.
    # The HTTP Date header timestamps the returned snapshot only.
    source_time = _from_http_date(http_date)
    if source_time is None:
        return [], None, False, "missing_or_invalid_http_date_snapshot_time"
    if source_time > captured:
        raise XRPIngestionError("Kraken HTTP Date is later than capture time")
    eligible, reason, quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
    event_s, captured_s = _iso(source_time), _iso(captured)
    mid = (bid + ask) / 2.0
    spread_bps = (ask - bid) / mid * 10000.0
    limitations = [
        "Single Kraken XRP/USD spot venue; not consolidated liquidity.",
        "Kraken ticker does not expose an individual last-trade timestamp; HTTP Date timestamps the returned snapshot, not the matching-engine trade event.",
        "The HTTP Date header is server response time, not an exchange matching-engine sequence timestamp.",
        "24-hour and UTC-day aggregates are distinct windows and must not be substituted for one another.",
    ]
    metrics = (
        ("last_trade_price_snapshot", last, "USD/XRP", ""),
        ("last_trade_size", last_size, "XRP", ""),
        ("best_bid", bid, "USD/XRP", ""),
        ("best_ask", ask, "USD/XRP", ""),
        ("mid_price", mid, "USD/XRP", ""),
        ("spread_bps", spread_bps, "bps", ""),
        ("base_volume_24h", _number(volume_row[1], "Kraken ticker 24h volume", allow_zero=True), "XRP", "24h"),
        ("vwap_24h", _number(vwap_row[1], "Kraken ticker 24h VWAP", allow_zero=False), "USD/XRP", "24h"),
        ("high_24h", _number(high_row[1], "Kraken ticker 24h high", allow_zero=False), "USD/XRP", "24h"),
        ("low_24h", _number(low_row[1], "Kraken ticker 24h low", allow_zero=False), "USD/XRP", "24h"),
        ("utc_day_open", _number(ticker.get("o"), "Kraken ticker UTC-day open", allow_zero=False), "USD/XRP", "utc_day"),
        ("base_volume_utc_day", _number(volume_row[0], "Kraken ticker UTC-day volume", allow_zero=True), "XRP", "utc_day"),
        ("vwap_utc_day", _number(vwap_row[0], "Kraken ticker UTC-day VWAP", allow_zero=False), "USD/XRP", "utc_day"),
        ("trade_count_24h", _number(trade_count_row[1], "Kraken ticker 24h trade count", allow_zero=True), "trades", "24h"),
    )
    records = [
        _feature_record(
            feature_id=f"xrp.spot.kraken.{name}",
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
            instrument="XRPUSD spot",
            currency_pair="XRP/USD",
            market_type="spot",
            aggregation_window=window,
            model_eligible=eligible,
            eligibility_reason=reason,
            quality_status=quality,
            limitations=limitations,
        )
        for name, value, unit, window in metrics
    ]
    return records, event_s, eligible, reason


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


def _okx_market_row(
    payload: Any,
    source_name: str,
    *,
    require_instrument: bool = True,
) -> Mapping[str, Any]:
    if (
        not isinstance(payload, Mapping)
        or payload.get("code") != "0"
        or payload.get("msg") not in ("", None)
    ):
        raise XRPIngestionError(f"OKX {source_name} response contains an API error")
    data = payload.get("data")
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], Mapping):
        raise XRPIngestionError(f"OKX {source_name} response must contain exactly one data row")
    row = data[0]
    instrument = row.get("instId")
    if instrument is not None and instrument != "XRP-USDT":
        raise XRPIngestionError(f"OKX {source_name} instrument mismatch")
    if require_instrument and instrument != "XRP-USDT":
        raise XRPIngestionError(f"OKX {source_name} response does not identify XRP-USDT")
    return row


def _parse_okx_ticker(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
):
    """Parse an OKX XRP-USDT ticker using the provider's snapshot-generation timestamp."""
    row = _okx_market_row(payload, "spot ticker")
    source_time = _from_ms(row.get("ts"), "OKX ticker ts")
    if source_time > captured:
        raise XRPIngestionError("OKX ticker timestamp is later than capture time")
    eligible, reason, quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
    event_s, captured_s = _iso(source_time), _iso(captured)

    bid = _number(row.get("bidPx"), "OKX ticker best bid", allow_zero=False)
    ask = _number(row.get("askPx"), "OKX ticker best ask", allow_zero=False)
    if ask <= bid:
        raise XRPIngestionError("OKX ticker bid/ask is crossed or locked")

    fields = (
        ("last", "last_price", "USDT/XRP", False),
        ("bidPx", "bid_price", "USDT/XRP", False),
        ("askPx", "ask_price", "USDT/XRP", False),
        ("bidSz", "bid_quantity", "XRP", True),
        ("askSz", "ask_quantity", "XRP", True),
        ("vol24h", "base_volume_24h", "XRP/24h", True),
        ("volCcy24h", "quote_volume_24h", "USDT/24h", True),
        ("open24h", "open_24h", "USDT/XRP", False),
        ("high24h", "high_24h", "USDT/XRP", False),
        ("low24h", "low_24h", "USDT/XRP", False),
    )
    limitations = [
        "Single OKX XRP-USDT spot venue; USDT is not converted to USD.",
        "The OKX ts field timestamps ticker snapshot generation, not the individual last-trade event.",
    ]
    records = [
        _feature_record(
            feature_id=f"xrp.spot.okx.{name}",
            value=_number(row.get(field), f"OKX ticker {field}", allow_zero=allow_zero),
            unit=unit,
            event_time_utc=event_s,
            source_data_as_of_utc=event_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="okx",
            venue="OKX",
            instrument="XRP-USDT spot",
            currency_pair="XRP/USDT",
            market_type="spot",
            aggregation_window="24h" if name.endswith("_24h") else "",
            model_eligible=eligible,
            eligibility_reason=reason,
            quality_status=quality,
            limitations=limitations,
        )
        for field, name, unit, allow_zero in fields
    ]
    return records, event_s, eligible, reason


def _parse_okx_depth(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
):
    """Parse a timestamped OKX order-book snapshot without claiming sequence continuity."""
    row = _okx_market_row(payload, "spot order book", require_instrument=False)
    source_time = _from_ms(row.get("ts"), "OKX order-book ts")
    if source_time > captured:
        raise XRPIngestionError("OKX order-book timestamp is later than capture time")
    eligible, reason, quality = _live_eligibility(
        source_time, captured, MAX_ORDERBOOK_AGE_SECONDS
    )
    bids_raw, asks_raw = row.get("bids"), row.get("asks")
    if not isinstance(bids_raw, list) or not bids_raw or not isinstance(asks_raw, list) or not asks_raw:
        raise XRPIngestionError("OKX order book must contain non-empty bids and asks")

    def parse_levels(level_rows: list[Any], side: str) -> list[tuple[float, float]]:
        levels = []
        for level in level_rows:
            if not isinstance(level, list) or len(level) < 2:
                raise XRPIngestionError(f"OKX {side} level schema mismatch")
            price = _number(level[0], f"OKX {side} price", allow_zero=False)
            quantity = _number(level[1], f"OKX {side} quantity", allow_zero=False)
            levels.append((price, quantity))
        return levels

    bids = parse_levels(bids_raw, "bid")
    asks = parse_levels(asks_raw, "ask")
    best_bid = max(price for price, _quantity in bids)
    best_ask = min(price for price, _quantity in asks)
    if best_ask <= best_bid:
        raise XRPIngestionError("OKX order book is crossed or locked")

    event_s, captured_s = _iso(source_time), _iso(captured)
    mid = (best_bid + best_ask) / 2.0
    spread_bps = (best_ask - best_bid) / mid * 10000.0
    features = [
        ("best_bid", best_bid, "USDT/XRP"),
        ("best_ask", best_ask, "USDT/XRP"),
        ("mid_price", mid, "USDT/XRP"),
        ("spread_bps", spread_bps, "bps"),
    ]
    for band in (10, 50, 100):
        bid_depth = sum(
            price * quantity
            for price, quantity in bids
            if price >= mid * (1 - band / 10000.0)
        )
        ask_depth = sum(
            price * quantity
            for price, quantity in asks
            if price <= mid * (1 + band / 10000.0)
        )
        total = bid_depth + ask_depth
        imbalance = (bid_depth - ask_depth) / total if total > 0 else 0.0
        features.extend(
            [
                (f"bid_depth_{band}bps", bid_depth, "USDT"),
                (f"ask_depth_{band}bps", ask_depth, "USDT"),
                (f"depth_imbalance_{band}bps", imbalance, "ratio"),
            ]
        )

    limitations = [
        "Single OKX XRP-USDT spot order-book snapshot; not global or consolidated liquidity.",
        "USDT quote depth is not converted to USD.",
        "The exchange-provided ts timestamps the REST snapshot; seqId is retained in the raw receipt but no sequence bridge is maintained.",
    ]
    records = [
        _feature_record(
            feature_id=f"xrp.spot.okx.orderbook.{name}",
            value=value,
            unit=unit,
            event_time_utc=event_s,
            source_data_as_of_utc=event_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="okx",
            venue="OKX",
            instrument="XRP-USDT spot",
            currency_pair="XRP/USDT",
            market_type="spot",
            model_eligible=eligible,
            eligibility_reason=reason,
            quality_status=quality,
            limitations=limitations,
        )
        for name, value, unit in features
    ]
    return records, event_s, eligible, reason



def _bybit_result(payload: Any, source_name: str) -> Mapping[str, Any]:
    """Validate the unauthenticated Bybit V5 public-market response envelope."""
    if not isinstance(payload, Mapping):
        raise XRPIngestionError(f"Bybit {source_name} response must be an object")
    ret_code = payload.get("retCode")
    if isinstance(ret_code, bool) or ret_code not in (0, "0") or payload.get("retMsg") not in ("OK", "", None):
        raise XRPIngestionError(f"Bybit {source_name} response contains an API error")
    result = payload.get("result")
    if not isinstance(result, Mapping):
        raise XRPIngestionError(f"Bybit {source_name} response has no result object")
    return result


def _parse_bybit_ticker(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
):
    """Parse Bybit XRPUSDT spot ticker; top-level time is response time, not trade time."""
    result = _bybit_result(payload, "spot ticker")
    if result.get("category") != "spot":
        raise XRPIngestionError("Bybit ticker category is not spot")
    rows = result.get("list")
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], Mapping):
        raise XRPIngestionError("Bybit spot ticker must contain exactly one row")
    row = rows[0]
    if row.get("symbol") != "XRPUSDT":
        raise XRPIngestionError("Bybit spot ticker symbol mismatch")

    source_time = _from_ms(payload.get("time"), "Bybit ticker response time")
    if source_time > captured:
        raise XRPIngestionError("Bybit ticker response time is later than capture time")
    eligible, reason, quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
    event_s, captured_s = _iso(source_time), _iso(captured)

    bid = _number(row.get("bid1Price"), "Bybit ticker best bid", allow_zero=False)
    ask = _number(row.get("ask1Price"), "Bybit ticker best ask", allow_zero=False)
    if ask <= bid:
        raise XRPIngestionError("Bybit ticker bid/ask is crossed or locked")

    fields = (
        ("lastPrice", "last_price", "USDT/XRP", False, ""),
        ("bid1Price", "best_bid", "USDT/XRP", False, ""),
        ("ask1Price", "best_ask", "USDT/XRP", False, ""),
        ("bid1Size", "best_bid_size", "XRP", True, ""),
        ("ask1Size", "best_ask_size", "XRP", True, ""),
        ("volume24h", "base_volume_24h", "XRP/24h", True, "24h"),
        ("turnover24h", "quote_volume_24h", "USDT/24h", True, "24h"),
        ("prevPrice24h", "previous_price_24h", "USDT/XRP", False, "24h"),
        ("highPrice24h", "high_24h", "USDT/XRP", False, "24h"),
        ("lowPrice24h", "low_24h", "USDT/XRP", False, "24h"),
    )
    limitations = [
        "Single Bybit XRP-USDT spot venue; USDT is not converted to USD.",
        "The top-level Bybit time field timestamps the REST response, not the individual last-trade event.",
    ]
    records = [
        _feature_record(
            feature_id=f"xrp.spot.bybit.{name}",
            value=_number(row.get(field), f"Bybit ticker {field}", allow_zero=allow_zero),
            unit=unit,
            event_time_utc=event_s,
            source_data_as_of_utc=event_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="bybit",
            venue="Bybit",
            instrument="XRPUSDT spot",
            currency_pair="XRP/USDT",
            market_type="spot",
            aggregation_window=window,
            model_eligible=eligible,
            eligibility_reason=reason,
            quality_status=quality,
            limitations=limitations,
        )
        for field, name, unit, allow_zero, window in fields
    ]
    return records, event_s, eligible, reason


def _parse_bybit_depth(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
):
    """Parse a Bybit REST order-book snapshot using cts, the matching-engine timestamp."""
    row = _bybit_result(payload, "spot order book")
    if row.get("s") != "XRPUSDT":
        raise XRPIngestionError("Bybit spot order-book symbol mismatch")
    snapshot_time = _from_ms(row.get("ts"), "Bybit order-book system timestamp")
    source_time = _from_ms(row.get("cts"), "Bybit order-book matching-engine timestamp")
    if snapshot_time > captured or source_time > captured:
        raise XRPIngestionError("Bybit order-book timestamp is later than capture time")
    eligible, reason, quality = _live_eligibility(source_time, captured, MAX_ORDERBOOK_AGE_SECONDS)

    bids_raw, asks_raw = row.get("b"), row.get("a")
    if not isinstance(bids_raw, list) or not bids_raw or not isinstance(asks_raw, list) or not asks_raw:
        raise XRPIngestionError("Bybit order book must contain non-empty bids and asks")

    def parse_levels(level_rows: list[Any], side: str) -> list[tuple[float, float]]:
        levels = []
        for level in level_rows:
            if not isinstance(level, list) or len(level) < 2:
                raise XRPIngestionError(f"Bybit {side} level schema mismatch")
            price = _number(level[0], f"Bybit {side} price", allow_zero=False)
            quantity = _number(level[1], f"Bybit {side} quantity", allow_zero=False)
            levels.append((price, quantity))
        return levels

    bids = parse_levels(bids_raw, "bid")
    asks = parse_levels(asks_raw, "ask")
    if any(bids[i][0] < bids[i + 1][0] for i in range(len(bids) - 1)):
        raise XRPIngestionError("Bybit bid levels are not sorted in descending price order")
    if any(asks[i][0] > asks[i + 1][0] for i in range(len(asks) - 1)):
        raise XRPIngestionError("Bybit ask levels are not sorted in ascending price order")

    best_bid = bids[0][0]
    best_ask = asks[0][0]
    if best_ask <= best_bid:
        raise XRPIngestionError("Bybit order book is crossed or locked")

    event_s, captured_s = _iso(source_time), _iso(captured)
    mid = (best_bid + best_ask) / 2.0
    spread_bps = (best_ask - best_bid) / mid * 10000.0
    features = [
        ("best_bid", best_bid, "USDT/XRP"),
        ("best_ask", best_ask, "USDT/XRP"),
        ("mid_price", mid, "USDT/XRP"),
        ("spread_bps", spread_bps, "bps"),
    ]
    for band in (10, 50, 100):
        bid_depth = sum(
            price * quantity
            for price, quantity in bids
            if price >= mid * (1 - band / 10000.0)
        )
        ask_depth = sum(
            price * quantity
            for price, quantity in asks
            if price <= mid * (1 + band / 10000.0)
        )
        total = bid_depth + ask_depth
        imbalance = (bid_depth - ask_depth) / total if total > 0 else 0.0
        features.extend(
            [
                (f"bid_depth_{band}bps", bid_depth, "USDT"),
                (f"ask_depth_{band}bps", ask_depth, "USDT"),
                (f"depth_imbalance_{band}bps", imbalance, "ratio"),
            ]
        )

    limitations = [
        "Single Bybit XRP-USDT REST order-book snapshot; no WebSocket sequence continuity is maintained.",
        "Bybit documents that Retail Price Improvement (RPI) orders are excluded from the REST order-book response.",
        "USDT quote depth is not converted to USD; displayed depth is not a fill or slippage guarantee.",
        "The cts field is the matching-engine timestamp; ts is the system-generated snapshot timestamp.",
    ]
    records = [
        _feature_record(
            feature_id=f"xrp.spot.bybit.orderbook.{name}",
            value=value,
            unit=unit,
            event_time_utc=event_s,
            source_data_as_of_utc=event_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="bybit",
            venue="Bybit",
            instrument="XRPUSDT spot",
            currency_pair="XRP/USDT",
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


def _raw_only_xrp_insights_etf_flows(payload: Any, *, captured: datetime, **_kwargs):
    """Validate the aggregator envelope but retain its rows as raw-only evidence."""
    if not isinstance(payload, Mapping):
        raise XRPIngestionError("XRP Insights ETF response must be an object")
    metadata = payload.get("metadata")
    if (
        not isinstance(metadata, Mapping)
        or metadata.get("dataset") != "XRP ETF Daily Holdings & Flows by Fund"
        or metadata.get("publisher") != "XRP Insights"
    ):
        raise XRPIngestionError("XRP Insights ETF metadata identity mismatch")
    generated_at = _from_iso8601(metadata.get("generated_at"), "XRP Insights generated_at")
    if generated_at > captured + timedelta(seconds=60):
        raise XRPIngestionError("XRP Insights generated_at is later than the capture clock")
    data_as_of = metadata.get("data_as_of")
    if not isinstance(data_as_of, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data_as_of):
        raise XRPIngestionError("XRP Insights data_as_of must be a date-only value")
    try:
        datetime.strptime(data_as_of, "%Y-%m-%d")
    except ValueError:
        raise XRPIngestionError("XRP Insights data_as_of is not a valid calendar date") from None
    coverage = metadata.get("coverage")
    if not isinstance(coverage, Mapping):
        raise XRPIngestionError("XRP Insights coverage metadata is missing")
    row_count = coverage.get("rows")
    if isinstance(row_count, bool) or not isinstance(row_count, int) or row_count <= 0:
        raise XRPIngestionError("XRP Insights row count must be a positive integer")
    funds, columns = payload.get("funds"), payload.get("columns")
    if not isinstance(funds, list) or not funds or not isinstance(columns, list) or not columns:
        raise XRPIngestionError("XRP Insights fund and column registries are required")
    if not any(isinstance(item, Mapping) and item.get("ticker") == "XRP" for item in funds):
        raise XRPIngestionError("XRP Insights fund registry does not contain the spot XRP fund")
    if not any(isinstance(item, Mapping) and item.get("name") == "xrp_flow" for item in columns):
        raise XRPIngestionError("XRP Insights column registry does not define xrp_flow")
    return (
        [],
        None,
        False,
        "third_party_issuer_holdings_aggregator_retained_raw_only_until_fund_row_vintages_and_primary_receipts_are_verified",
    )



def _raw_only_xrp_exchange_balances(payload: Any, *, captured: datetime, **_kwargs):
    """Validate XRP Insights exchange-wallet dataset identity without promoting its totals."""
    if not isinstance(payload, Mapping):
        raise XRPIngestionError("XRP Insights exchange-balance response must be an object")
    expected = {
        "dataset": "XRP Exchange Balances (attributed exchange wallets)",
        "publisher": "XRP Insights",
        "url": "https://xrp-insights.com/exchange-balances",
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            raise XRPIngestionError(f"XRP Insights exchange-balance {field} identity mismatch")
    definition = payload.get("definition")
    if not isinstance(definition, str) or "Not an estimate of tradable float" not in definition:
        raise XRPIngestionError("XRP Insights exchange-balance definition is missing its tradable-float limitation")
    methodology = payload.get("methodology")
    if (
        not isinstance(methodology, str)
        or "rippled account_info" not in methodology
        or "XRPSCAN public labels" not in methodology
    ):
        raise XRPIngestionError("XRP Insights exchange-balance methodology identity mismatch")
    license_text = payload.get("license")
    if not isinstance(license_text, str) or "cite with attribution" not in license_text.lower():
        raise XRPIngestionError("XRP Insights exchange-balance citation terms are missing")
    return (
        [],
        None,
        False,
        "xrp_insights_exchange_wallet_attribution_retained_hash_only_raw_only_until_daily_snapshot_and_same_wallet_schema_are_validated",
    )


def _raw_only_xrp_insights_etf_csv(
    payload: Any,
    *,
    captured: datetime,
    metadata_payload: Any = None,
    **_kwargs,
):
    """Validate the licensed CSV in memory and emit one attributed, hash-linked aggregate."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("csv_text"), str):
        raise XRPIngestionError("XRP Insights ETF CSV response must contain csv_text")
    if not isinstance(metadata_payload, Mapping):
        raise XRPIngestionError("XRP Insights CSV metadata envelope is unavailable")
    _raw_only_xrp_insights_etf_flows(metadata_payload, captured=captured)
    metadata = metadata_payload["metadata"]
    expected_columns = [
        item.get("name") for item in metadata_payload.get("columns", [])
        if isinstance(item, Mapping)
    ]
    if "flow_usd" not in expected_columns:
        raise XRPIngestionError("XRP Insights CSV metadata is missing flow_usd")
    try:
        reader = csv.DictReader(io.StringIO(payload["csv_text"], newline=""))
        if reader.fieldnames != expected_columns:
            raise XRPIngestionError("XRP Insights CSV header does not match its metadata column registry")
        rows = list(reader)
    except csv.Error:
        raise XRPIngestionError("XRP Insights CSV could not be parsed") from None
    coverage = metadata.get("coverage", {})
    if len(rows) != coverage.get("rows"):
        raise XRPIngestionError("XRP Insights CSV row count does not match metadata coverage")
    if not rows or len(rows) > 10000:
        raise XRPIngestionError("XRP Insights CSV row count is outside the supported range")

    fund_registry = {
        item["ticker"]: item["issuer"]
        for item in metadata_payload.get("funds", [])
        if isinstance(item, Mapping)
        and isinstance(item.get("ticker"), str)
        and isinstance(item.get("issuer"), str)
    }
    if not fund_registry:
        raise XRPIngestionError("XRP Insights CSV fund registry is empty")

    direct_spot_tickers = {"XRPC", "XRP", "XRPZ", "TOXR", "GXRP"}
    valid_flow_statuses = {"computed", "initial", "excluded"}
    valid_row_statuses = {"settled", "provisional", "reconstructed"}
    seen = set()
    normalized_rows = []
    row_dates = []
    settled_dates = []
    provisional_dates = []
    flow_status_counts = {status: 0 for status in valid_flow_statuses}
    row_status_counts = {status: 0 for status in valid_row_statuses}
    capture_date = captured.astimezone(timezone.utc).date()

    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise XRPIngestionError("XRP Insights CSV contains an incomplete or over-wide row")
        date_text = row.get("date", "")
        try:
            row_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise XRPIngestionError("XRP Insights CSV row date is invalid") from None
        if row_date > capture_date:
            raise XRPIngestionError("XRP Insights CSV contains a row dated after capture time")
        ticker = row.get("ticker", "")
        if ticker not in fund_registry or row.get("issuer") != fund_registry[ticker]:
            raise XRPIngestionError("XRP Insights CSV ticker/issuer does not match the fund registry")
        identity = (date_text, ticker)
        if identity in seen:
            raise XRPIngestionError("XRP Insights CSV contains a duplicate date/ticker row")
        seen.add(identity)

        flow_status = row.get("flow_status", "")
        row_status = row.get("row_status", "")
        if flow_status not in valid_flow_statuses or row_status not in valid_row_statuses:
            raise XRPIngestionError("XRP Insights CSV contains an unknown flow or row status")
        flow_status_counts[flow_status] += 1
        row_status_counts[row_status] += 1

        holdings = _number(row.get("xrp_holdings"), "XRP Insights xrp_holdings")
        aum_usd = _number(row.get("aum_usd"), "XRP Insights aum_usd")
        close_price_usd = _number(row.get("close_price_usd"), "XRP Insights close_price_usd", allow_zero=False)
        volume_usd = _number(row.get("volume_usd"), "XRP Insights volume_usd")
        shares_text = row.get("volume_shares", "").strip()
        try:
            volume_shares = int(shares_text)
        except (TypeError, ValueError, OverflowError):
            raise XRPIngestionError("XRP Insights volume_shares must be a non-negative integer") from None
        if volume_shares < 0 or str(volume_shares) != shares_text:
            raise XRPIngestionError("XRP Insights volume_shares must be a non-negative integer")
        expected_volume_usd = volume_shares * close_price_usd
        if abs(volume_usd - expected_volume_usd) > max(0.02, expected_volume_usd * 1e-6):
            raise XRPIngestionError("XRP Insights volume_usd does not reconcile to shares times close")

        flow_text = row.get("xrp_flow", "").strip()
        flow_usd_text = row.get("flow_usd", "").strip()
        if flow_status == "computed":
            if not flow_text or not flow_usd_text:
                raise XRPIngestionError("XRP Insights computed flow is blank")
            xrp_flow = _signed_number(flow_text, "XRP Insights xrp_flow")
            flow_usd = _signed_number(flow_usd_text, "XRP Insights flow_usd")
            if xrp_flow and flow_usd and (xrp_flow < 0) != (flow_usd < 0):
                raise XRPIngestionError("XRP Insights XRP and USD flow signs disagree")
        else:
            if flow_text or flow_usd_text:
                raise XRPIngestionError("XRP Insights non-computed flow must be blank")
            xrp_flow = None
            flow_usd = None

        if ticker == "BITW":
            fund_class = "multi_asset_index_sleeve"
        elif ticker == "XRPR":
            fund_class = "mixed_direct_and_indirect_etp_exposure"
        else:
            fund_class = "spot_xrp_fund"

        normalized_rows.append(
            {
                "date": date_text,
                "ticker": ticker,
                "fund_class": fund_class,
                "xrp_holdings": holdings,
                "xrp_flow": xrp_flow,
                "flow_usd": flow_usd,
                "flow_status": flow_status,
                "row_status": row_status,
            }
        )
        row_dates.append(row_date)
        if row_status == "settled":
            settled_dates.append(row_date)
        elif row_status == "provisional":
            provisional_dates.append(row_date)

    if not settled_dates or max(settled_dates).isoformat() != metadata.get("data_as_of"):
        raise XRPIngestionError("XRP Insights data_as_of does not match the latest settled CSV row")
    if max(row_dates).isoformat() != metadata.get("latest_row_date"):
        raise XRPIngestionError("XRP Insights latest_row_date does not match the CSV rows")
    expected_provisional = max(provisional_dates).isoformat() if provisional_dates else None
    if metadata.get("provisional_row_date") != expected_provisional:
        raise XRPIngestionError("XRP Insights provisional_row_date does not match the CSV rows")

    latest_date = metadata["data_as_of"]
    latest_rows = [
        row for row in normalized_rows
        if row["date"] == latest_date and row["row_status"] == "settled"
    ]
    if not latest_rows:
        raise XRPIngestionError("XRP Insights latest settled date has no settled fund rows")

    direct_rows = [row for row in latest_rows if row["ticker"] in direct_spot_tickers]
    direct_flow_rows = [row for row in direct_rows if row["flow_status"] == "computed"]
    index_rows = [row for row in latest_rows if row["ticker"] == "BITW"]
    index_flow_rows = [row for row in index_rows if row["flow_status"] == "computed"]
    mixed_rows = [row for row in latest_rows if row["ticker"] == "XRPR"]
    mixed_flow_rows = [row for row in mixed_rows if row["flow_status"] == "computed"]

    def _sum(rows_to_sum, field):
        return round(sum(row[field] or 0.0 for row in rows_to_sum), 8)

    license_info = metadata_payload.get("license", {})
    summary = {
        "data_as_of": latest_date,
        "latest_row_date": metadata.get("latest_row_date"),
        "provisional_row_date": metadata.get("provisional_row_date"),
        "row_count": len(rows),
        "fund_count": len(fund_registry),
        "latest_date_fund_row_count": len(latest_rows),
        "latest_date_direct_spot_holdings_xrp": _sum(direct_rows, "xrp_holdings"),
        "latest_date_direct_spot_flow_xrp": _sum(direct_flow_rows, "xrp_flow"),
        "latest_date_direct_spot_flow_usd": _sum(direct_flow_rows, "flow_usd"),
        "latest_date_direct_spot_flow_fund_count": len(direct_flow_rows),
        "latest_date_direct_spot_excluded_flow_fund_count": sum(
            1 for row in direct_rows if row["flow_status"] == "excluded"
        ),
        "latest_date_index_sleeve_holdings_xrp": _sum(index_rows, "xrp_holdings"),
        "latest_date_index_sleeve_flow_xrp": _sum(index_flow_rows, "xrp_flow"),
        "latest_date_index_sleeve_flow_usd": _sum(index_flow_rows, "flow_usd"),
        "latest_date_mixed_indirect_holdings_xrp": _sum(mixed_rows, "xrp_holdings"),
        "latest_date_mixed_indirect_flow_xrp": _sum(mixed_flow_rows, "xrp_flow"),
        "latest_date_mixed_indirect_flow_usd": _sum(mixed_flow_rows, "flow_usd"),
        "flow_status_counts": flow_status_counts,
        "row_status_counts": row_status_counts,
        "reconstructed_row_count": row_status_counts["reconstructed"],
        "flow_method": "holdings_delta_not_issuer_ap_cash_flow",
        "source_attribution": metadata_payload.get("citation", "XRP Insights (xrp-insights.com)"),
        "license_name": license_info.get("name"),
        "license_url": license_info.get("url"),
        "license_compliance": "hash_only_receipt; no full CSV payload or row-level dataset is persisted to public artifacts",
        "research_eligible": True,
        "research_eligibility_reason": "attributed aggregate only; holdings delta is not issuer AP cash flow and primary issuer reconciliation remains required",
        "model_eligible": False,
    }
    reason = (
        "research_only_aggregate;hash_only_receipt_due_to_publisher_terms;"
        "no_full_csv_or_row_level_dataset_persisted;primary_issuer_ap_cash_flow_reconciliation_pending"
    )
    return [summary], None, False, reason


def _raw_only_xrpr_issuer_page(payload: Any, *, captured: datetime, **_kwargs):
    """Validate REX issuer-page identity while retaining the original HTML raw-only."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("XRPR issuer page response must contain HTML text")
    html_text = payload["html_text"]
    required_markers = ("XRPR", "REX-Osprey", "CoinShares XRP ETP", "As of")
    if any(marker not in html_text for marker in required_markers):
        raise XRPIngestionError("XRPR issuer page identity or holdings-table markers are missing")
    return (
        [],
        None,
        False,
        "primary_issuer_html_retained_raw_only_until_holdings_parser_and_source_vintage_are_verified",
    )


def _raw_only_bitwise_xrp_etf_page(payload: Any, *, captured: datetime, **_kwargs):
    """Validate Bitwise's official XRP ETF page while retaining exact HTML bytes raw-only."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("Bitwise XRP ETF page response must contain HTML text")
    html_text = payload["html_text"]
    normalized = html_text.casefold()
    required_markers = ("bitwise xrp etf", "xrp in trust", "digital asset custodian", "data as of")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("Bitwise issuer-page identity or holdings markers are missing")
    return (
        [],
        None,
        False,
        "primary_issuer_html_retained_raw_only_until_holdings_parser_and_source_vintage_are_verified",
    )


def _raw_only_grayscale_gxrp_issuer_page(payload: Any, *, captured: datetime, **_kwargs):
    """Validate Grayscale's official GXRP page while retaining exact HTML bytes raw-only."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("Grayscale GXRP page response must contain HTML text")
    html_text = payload["html_text"]
    normalized = html_text.casefold()
    required_markers = ("grayscale xrp trust etf", "total xrp in fund", "digital asset custodian", "as of")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("Grayscale GXRP issuer-page identity or holdings markers are missing")
    return (
        [],
        None,
        False,
        "primary_issuer_html_retained_raw_only_until_holdings_parser_and_source_vintage_are_verified",
    )



def _raw_only_franklin_xrpz_issuer_page(payload: Any, *, captured: datetime, **_kwargs):
    """Validate Franklin XRPZ issuer-page identity; retain only a digest receipt."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("Franklin XRPZ issuer page response must contain HTML text")
    normalized = payload["html_text"].casefold()
    required_markers = ("franklin xrp etf", "xrpz", "xrp in fund", "as of")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("Franklin XRPZ issuer-page identity or holdings markers are missing")
    return (
        [],
        None,
        False,
        "primary_issuer_html_hash_only_until_holdings_parser_source_vintage_and_redistribution_terms_are_verified",
    )


def _raw_only_canary_xrpc_issuer_page(payload: Any, *, captured: datetime, **_kwargs):
    """Validate Canary XRPC issuer-page identity; retain only a digest receipt."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("Canary XRPC issuer page response must contain HTML text")
    normalized = payload["html_text"].casefold()
    required_markers = ("canary xrp etf", "xrpc", "holdings", "as of")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("Canary XRPC issuer-page identity or holdings markers are missing")
    return (
        [],
        None,
        False,
        "primary_issuer_html_hash_only_until_holdings_parser_source_vintage_and_redistribution_terms_are_verified",
    )


def _raw_only_21shares_toxr_issuer_page(payload: Any, *, captured: datetime, **_kwargs):
    """Validate 21Shares TOXR issuer-page identity; retain only a digest receipt."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("21Shares TOXR issuer page response must contain HTML text")
    normalized = payload["html_text"].casefold()
    required_markers = ("21shares xrp etf", "toxr", "holdings", "as of")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("21Shares TOXR issuer-page identity or holdings markers are missing")
    return (
        [],
        None,
        False,
        "primary_issuer_html_hash_only_until_holdings_parser_source_vintage_and_redistribution_terms_are_verified",
    )


def _raw_only_ripple_rlusd_transparency_page(payload: Any, *, captured: datetime, **_kwargs):
    """Retain Ripple's issuer transparency dashboard without promoting dashboard values to features."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("Ripple RLUSD transparency page response must contain HTML text")
    normalized = payload["html_text"].casefold()
    required_markers = ("ripple usd", "rlusd", "total circulating rlusd", "rlusd reserve funds")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("Ripple RLUSD issuer-transparency identity or reserve markers are missing")
    return (
        [],
        None,
        False,
        "primary_issuer_transparency_html_retained_raw_only_until_supply_and_attestation_vintages_are_normalized",
    )


def _raw_only_xrpldashboard_rlusd_page(payload: Any, *, captured: datetime, **_kwargs):
    """Retain the cross-chain RLUSD dashboard as a secondary, non-feature research receipt."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("XRPL Dashboard RLUSD page response must contain HTML text")
    normalized = payload["html_text"].casefold()
    required_markers = ("rlusd", "ethereum", "xrp ledger")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("XRPL Dashboard RLUSD cross-chain identity markers are missing")
    return (
        [],
        None,
        False,
        "secondary_cross_chain_supply_html_retained_raw_only_until_chain_supply_and_timestamp_are_reconciled",
    )


def _raw_only_circle_transparency_page(payload: Any, *, captured: datetime, **_kwargs):
    """Retain Circle's issuer transparency page without parsing dynamic values into features."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("Circle transparency page response must contain HTML text")
    normalized = payload["html_text"].casefold()
    required_markers = ("transparency", "usdc", "eurc", "reserves")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("Circle stablecoin-transparency identity or reserve markers are missing")
    return (
        [],
        None,
        False,
        "primary_issuer_transparency_html_retained_raw_only_until_dynamic_supply_and_reserve_fields_are_normalized",
    )


def _raw_only_sbi_vc_trade_lending_page(payload: Any, *, captured: datetime, **_kwargs):
    """Validate SBI VC Trade's lending-page identity; keep it digest-only and model-ineligible."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("SBI VC Trade lending page response must contain HTML text")
    normalized = payload["html_text"].casefold()
    required_markers = ("sbi vcトレード", "貸コイン", "usdc", "xrp")
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("SBI VC Trade lending-page identity or asset markers are missing")
    return (
        [],
        None,
        False,
        "sbi_vc_trade_lending_page_digest_only_until_offer_terms_are_versioned_and_actual_lending_balances_are_disclosed",
    )



def _ordered_bybit_history_rows(
    rows: Any,
    *,
    timestamp_key: str,
    source_name: str,
    captured: datetime,
) -> list[tuple[datetime, Mapping[str, Any]]]:
    if not isinstance(rows, list) or not rows:
        raise XRPIngestionError(f"Bybit {source_name} history must be a non-empty array")
    parsed: list[tuple[datetime, Mapping[str, Any]]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise XRPIngestionError(f"Bybit {source_name} history row shape mismatch")
        event_time = _from_ms(row.get(timestamp_key), f"Bybit {source_name} {timestamp_key}")
        if event_time > captured:
            raise XRPIngestionError(f"Bybit {source_name} event time is later than capture time")
        event_s = _iso(event_time)
        if event_s in seen:
            raise XRPIngestionError(f"Bybit {source_name} history contains a duplicate event timestamp")
        seen.add(event_s)
        parsed.append((event_time, row))
    if len(parsed) > 1:
        ascending = all(parsed[i][0] < parsed[i + 1][0] for i in range(len(parsed) - 1))
        descending = all(parsed[i][0] > parsed[i + 1][0] for i in range(len(parsed) - 1))
        if descending:
            parsed.reverse()
        elif not ascending:
            raise XRPIngestionError(f"Bybit {source_name} history is not strictly monotonic")
    return parsed


def _parse_bybit_linear_ticker(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
):
    """Parse Bybit XRPUSDT linear-perpetual ticker without normalizing venue units."""
    result = _bybit_result(payload, "linear ticker")
    if result.get("category") != "linear":
        raise XRPIngestionError("Bybit ticker category is not linear")
    rows = result.get("list")
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], Mapping):
        raise XRPIngestionError("Bybit linear ticker must contain exactly one row")
    row = rows[0]
    if row.get("symbol") != "XRPUSDT":
        raise XRPIngestionError("Bybit linear ticker symbol mismatch")

    source_time = _from_ms(payload.get("time"), "Bybit linear ticker response time")
    if source_time > captured:
        raise XRPIngestionError("Bybit linear ticker response time is later than capture time")
    eligible, reason, quality = _live_eligibility(source_time, captured, MAX_LIVE_AGE_SECONDS)
    event_s, captured_s = _iso(source_time), _iso(captured)

    bid = _number(row.get("bid1Price"), "Bybit linear best bid", allow_zero=False)
    ask = _number(row.get("ask1Price"), "Bybit linear best ask", allow_zero=False)
    if ask <= bid:
        raise XRPIngestionError("Bybit linear ticker bid/ask is crossed or locked")

    interval_hours = None
    interval_raw = row.get("fundingIntervalHour")
    if interval_raw not in (None, ""):
        interval_value = _number(interval_raw, "Bybit fundingIntervalHour", allow_zero=False)
        if not interval_value.is_integer() or not 1 <= interval_value <= 24:
            raise XRPIngestionError("Bybit fundingIntervalHour must be a whole number from 1 to 24")
        interval_hours = int(interval_value)

    limitations = [
        "Single Bybit XRPUSDT linear-perpetual venue; USDT is not converted to USD.",
        "The top-level Bybit time field is REST response/server time, not an individual trade or funding-settlement event time.",
        "Bybit documents openInterest and openInterestValue as both-sides totals and the singleOpenInterest fields as single-side values; preserve both conventions separately.",
        "The ticker fundingRate is a current snapshot, not a settled historical funding event; use the funding-history endpoint for settlement events.",
    ]
    fields = (
        ("lastPrice", "last_price", "USDT/XRP", False, ""),
        ("markPrice", "mark_price", "USDT/XRP", False, ""),
        ("indexPrice", "index_price", "USDT/XRP", False, ""),
        ("bid1Price", "best_bid", "USDT/XRP", False, ""),
        ("ask1Price", "best_ask", "USDT/XRP", False, ""),
        ("openInterest", "open_interest_xrp_both_sides", "XRP (venue-reported both sides)", False, ""),
        ("singleOpenInterest", "open_interest_xrp_single_side", "XRP (venue-reported single side)", False, ""),
        ("openInterestValue", "open_interest_value_usdt_both_sides", "USDT (venue-reported both sides)", False, ""),
        ("singleOpenInterestValue", "open_interest_value_usdt_single_side", "USDT (venue-reported single side)", False, ""),
        ("volume24h", "base_volume_24h", "XRP/24h", True, "24h"),
        ("turnover24h", "quote_volume_24h", "USDT/24h", True, "24h"),
    )
    records = []
    for field, name, unit, allow_zero, window in fields:
        records.append(
            _feature_record(
                feature_id=f"xrp.perpetual.bybit.{name}",
                value=_number(row.get(field), f"Bybit linear ticker {field}", allow_zero=allow_zero),
                unit=unit,
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="bybit",
                venue="Bybit",
                instrument="XRPUSDT linear perpetual",
                currency_pair="XRP/USDT",
                market_type="perpetual",
                aggregation_window=window,
                model_eligible=eligible,
                eligibility_reason=reason,
                quality_status=quality,
                limitations=limitations,
            )
        )

    funding_rate = _signed_number(row.get("fundingRate"), "Bybit current fundingRate")
    funding_eligible = eligible and interval_hours is not None
    funding_reason = reason if not eligible else ("" if interval_hours is not None else "funding_interval_missing")
    funding_quality = quality if interval_hours is not None else "unverified"
    records.append(
        _feature_record(
            feature_id="xrp.perpetual.bybit.current_funding_rate",
            value=funding_rate,
            unit="fraction_per_funding_interval",
            event_time_utc=event_s,
            source_data_as_of_utc=event_s,
            captured_at_utc=captured_s,
            source_id=source_id,
            source_uri=url,
            raw_sha256=digest,
            independence_group="bybit",
            venue="Bybit",
            instrument="XRPUSDT linear perpetual",
            currency_pair="XRP/USDT",
            market_type="perpetual",
            aggregation_window="current_rate",
            model_eligible=funding_eligible,
            eligibility_reason=funding_reason,
            quality_status=funding_quality,
            limitations=limitations + [
                "The current funding rate is not annualized and is not assumed to be an eight-hour rate; its reported interval is stored separately."
            ],
        )
    )
    if interval_hours is not None:
        records.append(
            _feature_record(
                feature_id="xrp.perpetual.bybit.funding_interval_hours",
                value=float(interval_hours),
                unit="hours",
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="bybit",
                venue="Bybit",
                instrument="XRPUSDT linear perpetual",
                currency_pair="XRP/USDT",
                market_type="perpetual",
                model_eligible=eligible,
                eligibility_reason=reason,
                quality_status=quality,
                limitations=limitations,
            )
        )
    return records, event_s, eligible, reason


def _parse_bybit_linear_open_interest_history(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
):
    result = _bybit_result(payload, "linear open-interest history")
    if result.get("category") != "linear" or result.get("symbol") != "XRPUSDT":
        raise XRPIngestionError("Bybit linear open-interest history identity mismatch")
    ordered = _ordered_bybit_history_rows(
        result.get("list"),
        timestamp_key="timestamp",
        source_name="linear open-interest",
        captured=captured,
    )
    captured_s = _iso(captured)
    limitations = [
        "Single Bybit XRPUSDT linear-perpetual venue; linear open-interest size is retained in the base asset (XRP), with no USD or contract-count conversion.",
        "Bybit openInterest is the venue-reported sum of both sides; singleOpenInterest is the venue-reported single-side value. They are retained as separate features.",
        "Historical rows are first known to this collector at captured_at_utc and cannot be used at earlier point-in-time origins.",
        "The public endpoint returns at most 200 rows per request; this collector captures one page and does not claim a complete lifetime history.",
    ]
    if any(row.get("singleOpenInterest") in (None, "") for _event_time, row in ordered):
        limitations.append("At least one Bybit history row omitted singleOpenInterest; no single-side value is inferred from the both-sides total.")
    if result.get("nextPageCursor"):
        limitations.append("Bybit returned a nextPageCursor; additional historical pages exist and were not fetched by this one-page adapter.")
    records = []
    for event_time, row in ordered:
        if row.get("symbol") not in (None, "XRPUSDT"):
            raise XRPIngestionError("Bybit linear open-interest history row symbol mismatch")
        event_s = _iso(event_time)
        records.append(
            _feature_record(
                feature_id="xrp.perpetual.bybit.1h.open_interest_xrp_both_sides",
                value=_number(row.get("openInterest"), "Bybit historical openInterest", allow_zero=False),
                unit="XRP (venue-reported both-sides open-interest size)",
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="bybit",
                venue="Bybit",
                instrument="XRPUSDT linear perpetual",
                currency_pair="XRP/USDT",
                market_type="perpetual",
                aggregation_window="1h",
                model_eligible=True,
                quality_status="verified",
                limitations=limitations,
            )
        )
        single_value = row.get("singleOpenInterest")
        if single_value not in (None, ""):
            records.append(
                _feature_record(
                    feature_id="xrp.perpetual.bybit.1h.open_interest_xrp_single_side",
                    value=_number(single_value, "Bybit historical singleOpenInterest", allow_zero=False),
                    unit="XRP (venue-reported single-side open-interest size)",
                    event_time_utc=event_s,
                    source_data_as_of_utc=event_s,
                    captured_at_utc=captured_s,
                    source_id=source_id,
                    source_uri=url,
                    raw_sha256=digest,
                    independence_group="bybit",
                    venue="Bybit",
                    instrument="XRPUSDT linear perpetual",
                    currency_pair="XRP/USDT",
                    market_type="perpetual",
                    aggregation_window="1h",
                    model_eligible=True,
                    quality_status="verified",
                    limitations=limitations,
                )
            )
    return records, _iso(ordered[-1][0]), True, ""


def _parse_bybit_linear_funding_history(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
):
    result = _bybit_result(payload, "linear funding history")
    if result.get("category") != "linear":
        raise XRPIngestionError("Bybit funding-history category is not linear")
    ordered = _ordered_bybit_history_rows(
        result.get("list"),
        timestamp_key="fundingRateTimestamp",
        source_name="linear funding",
        captured=captured,
    )
    captured_s = _iso(captured)
    limitations = [
        "Single Bybit XRPUSDT linear-perpetual venue.",
        "Funding is a signed fraction per actual settlement event; interval length is not assumed to be eight hours or annualized.",
        "Historical rows are first known to this collector at captured_at_utc and cannot be used at earlier point-in-time origins.",
        "The public endpoint returns at most 200 settlement events per request; this collector captures one page and does not claim a complete lifetime history.",
    ]
    records = []
    for event_time, row in ordered:
        if row.get("symbol") != "XRPUSDT":
            raise XRPIngestionError("Bybit funding-history symbol mismatch")
        event_s = _iso(event_time)
        records.append(
            _feature_record(
                feature_id="xrp.perpetual.bybit.funding_rate",
                value=_signed_number(row.get("fundingRate"), "Bybit historical fundingRate"),
                unit="fraction_per_settlement",
                event_time_utc=event_s,
                source_data_as_of_utc=event_s,
                captured_at_utc=captured_s,
                source_id=source_id,
                source_uri=url,
                raw_sha256=digest,
                independence_group="bybit",
                venue="Bybit",
                instrument="XRPUSDT linear perpetual",
                currency_pair="XRP/USDT",
                market_type="perpetual",
                aggregation_window="funding_event",
                model_eligible=True,
                quality_status="verified",
                limitations=limitations,
            )
        )
    return records, _iso(ordered[-1][0]), True, ""


def _parse_cftc_contract_status_index(
    payload: Any, *, source_id: str, url: str, digest: str, captured: datetime
):
    html_text = payload.get("html_text") if isinstance(payload, Mapping) else None
    status = parse_cftc_contract_status(html_text)
    if not status.get("reports_dated"):
        raise XRPIngestionError("CFTC contract-status index has no report date")
    report_date = datetime.strptime(
        status["reports_dated"], "%Y-%m-%d"
    ).replace(tzinfo=timezone.utc)
    if report_date.date() > captured.astimezone(timezone.utc).date():
        raise XRPIngestionError("CFTC contract-status report date is later than capture time")
    return (
        [],
        _iso(report_date),
        False,
        "official_cftc_weekly_added_dropped_contract_index_research_only",
    )


def _parse_cftc_tff(
    payload: Any,
    *,
    source_id: str,
    url: str,
    digest: str,
    captured: datetime,
    contract_status_html: str | None = None,
):
    html_text = payload.get("html_text") if isinstance(payload, Mapping) else None
    parsed = parse_cftc_tff_report(
        html_text, contract_status_html=contract_status_html
    )
    report_date = datetime.strptime(parsed["positions_as_of_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if report_date.date() > captured.astimezone(timezone.utc).date():
        raise XRPIngestionError("CFTC TFF positions-as-of date is later than capture time")
    event_s = _iso(report_date)
    captured_s = _iso(captured)
    limitations_base = [
        "The CFTC TFF report is futures-only positioning, not spot holdings, exchange flows, cash capital, or collateral utilization.",
        "The report provides a date-only positions-as-of field; event_time_utc is a date anchor, while captured_at_utc is the first verified availability time.",
        "CFTC trader categories are based on predominant business purpose and do not disclose individual trader identities or the specific reason for a position.",
        "Spreading positions are preserved in the raw report and are not included in long-minus-short net features.",
        "Optional historical contracts absent from the current report are never zero-filled; the same-date CFTC added/dropped index is retained separately.",
    ]
    category_metrics = (
        ("dealer_intermediary_net_contracts", "dealer_intermediary"),
        ("asset_manager_institutional_net_contracts", "asset_manager_institutional"),
        ("leveraged_funds_net_contracts", "leveraged_funds"),
        ("other_reportables_net_contracts", "other_reportables"),
        ("nonreportable_net_contracts", "nonreportable"),
    )
    records = []
    for contract in parsed["contracts"]:
        if contract["reporting_status"] != "reported":
            continue
        instrument = (
            f"{contract['name']} ({contract['code']}; "
            f"{contract['contract_multiplier_xrp']} XRP per contract)"
        )
        metrics = [
            ("open_interest_contracts", contract["open_interest_contracts"], "contracts"),
            ("open_interest_change_contracts", contract["open_interest_change_contracts"], "contracts"),
            (
                "open_interest_xrp_equivalent",
                contract["open_interest_xrp_equivalent"],
                "xrp_equivalent_contracts",
            ),
        ]
        if contract["open_interest_change_contracts"] is not None:
            metrics.append(
                (
                    "open_interest_change_xrp_equivalent",
                    contract["open_interest_change_contracts"] * contract["contract_multiplier_xrp"],
                    "xrp_equivalent_contracts",
                )
            )
        if contract["total_traders"] is not None:
            metrics.append(("total_traders", contract["total_traders"], "traders"))
        metrics.extend(
            (
                metric_name,
                contract["positions"][category_slug]["net_long_short_contracts"],
                "contracts",
            )
            for metric_name, category_slug in category_metrics
        )
        limitations = [
            *limitations_base,
            f"Contract multiplier is {contract['contract_multiplier_xrp']} XRP per contract; contract counts are not USD notional.",
            f"Positions changed from {contract['change_from_date']} to {parsed['positions_as_of_date']}; weekly deltas are not intraday flows.",
        ]
        for metric_name, value, unit in metrics:
            records.append(
                _feature_record(
                    feature_id=f"xrp.derivatives.cftc.tff.{contract['slug']}.{metric_name}",
                    value=value,
                    unit=unit,
                    event_time_utc=event_s,
                    source_data_as_of_utc=event_s,
                    captured_at_utc=captured_s,
                    source_id=source_id,
                    source_uri=url,
                    raw_sha256=digest,
                    independence_group="cftc",
                    venue=contract["venue"],
                    instrument=instrument,
                    currency_pair="XRP/USD",
                    market_type="futures",
                    aggregation_window="weekly_tff",
                    model_eligible=False,
                    eligibility_reason=(
                        "CFTC TFF positions are date-only weekly futures positioning; "
                        "retained for research, not admitted to directional XRP forecasts."
                    ),
                    quality_status="unverified",
                    limitations=limitations,
                )
            )
    reason = (
        "official_cftc_tff_futures_only_positions_as_of_"
        f"{parsed['positions_as_of_date']}_parsed_research_only_date_only_not_model_admitted"
    )
    return records, event_s, False, reason


def _morpho_data(payload: Any, source_id: str) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping) or not isinstance(payload.get("data"), Mapping):
        raise XRPIngestionError(f"Morpho {source_id} response must contain a data object")
    return payload["data"]


def _morpho_uint(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise XRPIngestionError(f"Morpho {field} must be an unsigned integer")
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]+", value.strip()):
        return int(value.strip())
    raise XRPIngestionError(f"Morpho {field} must be an unsigned integer")


def _morpho_address(value: Any, field: str) -> str:
    if isinstance(value, Mapping):
        value = value.get("address")
    if not isinstance(value, str) or not re.fullmatch(r"0x[0-9a-fA-F]{40}", value):
        raise XRPIngestionError(f"Morpho {field} address is invalid")
    return value.lower()


def _morpho_market_identity(data: Mapping[str, Any], source_id: str, *, require: bool = True) -> None:
    chain_value = data.get("chain_id", data.get("chainId"))
    market_value = data.get("market_id", data.get("marketId", data.get("unique_key", data.get("id"))))
    if chain_value is None and market_value is None:
        if require:
            raise XRPIngestionError(f"Morpho {source_id} market identity is incomplete")
        return
    if chain_value is not None and _morpho_uint(chain_value, f"{source_id} chain_id") != MORPHO_CBXRP_CHAIN_ID:
        raise XRPIngestionError(f"Morpho {source_id} chain ID does not match Base")
    if market_value is not None and (
        not isinstance(market_value, str) or market_value.lower() != MORPHO_CBXRP_MARKET_ID
    ):
        raise XRPIngestionError(f"Morpho {source_id} market ID does not match cbXRP/USDC")
    if require and (chain_value is None or market_value is None):
        raise XRPIngestionError(f"Morpho {source_id} market identity is incomplete")


def _raw_only_morpho_cbxrp_market_parameters(
    payload: Any, *, source_id: str, captured: datetime, **_kwargs
):
    """Validate the immutable Base cbXRP/USDC market identity; retain only its digest receipt."""
    data = _morpho_data(payload, source_id)
    _morpho_market_identity(data, source_id, require=False)
    loan_address = _morpho_address(data.get("loan_token", data.get("loanToken")), "loan token")
    collateral_address = _morpho_address(data.get("collateral_token", data.get("collateralToken")), "collateral token")
    oracle_address = _morpho_address(data.get("oracle_address", data.get("oracleAddress")), "oracle")
    if loan_address != MORPHO_CBXRP_LOAN_TOKEN_ADDRESS:
        raise XRPIngestionError("Morpho cbXRP market loan token is not Base USDC")
    if collateral_address != MORPHO_CBXRP_COLLATERAL_TOKEN_ADDRESS:
        raise XRPIngestionError("Morpho market collateral token is not Coinbase cbXRP")
    if oracle_address != MORPHO_CBXRP_ORACLE_ADDRESS:
        raise XRPIngestionError("Morpho cbXRP market oracle address changed")
    lltv = _morpho_uint(data.get("lltv_wad", data.get("lltvWad")), "LLTV")
    if lltv != 625_000_000_000_000_000:
        raise XRPIngestionError("Morpho cbXRP market LLTV is not the expected 62.5%")
    return [], None, False, "morpho_immutable_market_parameters_raw_only_until_token_decimals_and_market_lineage_are_normalized"


def _raw_only_morpho_cbxrp_market_state(
    payload: Any, *, source_id: str, captured: datetime, **_kwargs
):
    """Validate current raw-unit supply/borrow state without promoting it to USD or XRP features."""
    data = _morpho_data(payload, source_id)
    _morpho_market_identity(data, source_id)
    for field in (
        "total_supply_assets", "total_borrow_assets",
        "total_supply_shares", "total_borrow_shares",
        "fee_wad", "last_indexed_block", "last_accrual_timestamp",
    ):
        _morpho_uint(data.get(field), field)
    return [], None, False, "morpho_current_market_state_raw_only_until_token_units_and_indexer_block_time_are_normalized"



def _raw_only_morpho_cbxrp_market_liquidity(
    payload: Any, *, source_id: str, captured: datetime, **_kwargs
):
    """Validate current market and allocator liquidity without promoting raw token units to USD."""
    data = _morpho_data(payload, source_id)
    _morpho_market_identity(data, source_id)
    for field in (
        "market_liquidity",
        "reallocatable_liquidity",
        "borrow_amount_to_target_utilization",
        "last_indexed_block",
    ):
        _morpho_uint(data.get(field), field)
    return [], None, False, "morpho_market_liquidity_raw_only_until_token_units_and_indexer_block_alignment_are_normalized"


def _raw_only_morpho_cbxrp_market_state_history(
    payload: Any, *, source_id: str, captured: datetime, **_kwargs
):
    """Validate historical collateral totals and preserve the latest provider event timestamp."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("data"), list) or not payload["data"]:
        raise XRPIngestionError("Morpho cbXRP market-state history must contain a non-empty data array")
    params = payload.get("params")
    if isinstance(params, Mapping):
        _morpho_market_identity(params, source_id)
    previous_timestamp = 0
    latest_event = None
    if payload.get("last_indexed_block") is not None:
        _morpho_uint(payload["last_indexed_block"], "last_indexed_block")
    for row in payload["data"]:
        if not isinstance(row, Mapping):
            raise XRPIngestionError("Morpho cbXRP market-state history row is invalid")
        timestamp = _morpho_uint(row.get("timestamp"), "history timestamp")
        if timestamp <= previous_timestamp:
            raise XRPIngestionError("Morpho cbXRP market-state history timestamps are not strictly increasing")
        if timestamp > int(captured.timestamp()) + 60:
            raise XRPIngestionError("Morpho cbXRP market-state history contains a future event")
        for field in (
            "total_supply_assets", "total_borrow_assets",
            "total_supply_shares", "total_borrow_shares",
            "total_collateral_assets",
        ):
            _morpho_uint(row.get(field), field)
        previous_timestamp = timestamp
        latest_event = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    source_as_of = latest_event.isoformat().replace("+00:00", "Z") if latest_event else None
    return [], source_as_of, False, "morpho_market_state_history_raw_only_until_token_decimals_and_indexer_vintage_are_normalized"


def _raw_only_morpho_cbxrp_oracle_state(
    payload: Any, *, source_id: str, captured: datetime, **_kwargs
):
    """Validate the market oracle identity and retain its raw quote without assuming quote scale."""
    data = _morpho_data(payload, source_id)
    chain_value = data.get("chain_id", data.get("chainId"))
    if chain_value is not None and _morpho_uint(chain_value, "oracle chain_id") != MORPHO_CBXRP_CHAIN_ID:
        raise XRPIngestionError("Morpho cbXRP oracle chain ID does not match Base")
    oracle_value = data.get("oracle_address", data.get("oracleAddress", data.get("address")))
    if oracle_value is not None and _morpho_address(oracle_value, "oracle") != MORPHO_CBXRP_ORACLE_ADDRESS:
        raise XRPIngestionError("Morpho cbXRP oracle address does not match the market configuration")
    price = data.get("price")
    if price is not None:
        _morpho_uint(price, "oracle price")
    indexed_block = data.get("last_indexed_block")
    if indexed_block is not None:
        _morpho_uint(indexed_block, "oracle last_indexed_block")
    updated = data.get("last_updated_at", data.get("lastUpdatedAt"))
    source_as_of = None
    if updated is not None:
        if isinstance(updated, bool):
            raise XRPIngestionError("Morpho oracle update timestamp is invalid")
        if isinstance(updated, (int, float)) or (isinstance(updated, str) and updated.isdigit()):
            source_as_of = datetime.fromtimestamp(int(updated), tz=timezone.utc)
        elif isinstance(updated, str):
            try:
                parsed = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            except ValueError:
                raise XRPIngestionError("Morpho oracle update timestamp is invalid") from None
            if parsed.tzinfo is None:
                raise XRPIngestionError("Morpho oracle update timestamp must include a timezone")
            source_as_of = parsed.astimezone(timezone.utc)
        else:
            raise XRPIngestionError("Morpho oracle update timestamp is invalid")
        if source_as_of > captured + timedelta(seconds=60):
            raise XRPIngestionError("Morpho oracle update timestamp is later than capture time")
    source_as_of_text = source_as_of.isoformat().replace("+00:00", "Z") if source_as_of else None
    return [], source_as_of_text, False, "morpho_oracle_state_raw_only_until_quote_scale_and_update_timestamp_semantics_are_normalized"


def _raw_only_coinbase_cbxrp_proof_of_reserves(
    payload: Any, *, source_id: str, captured: datetime, **_kwargs
):
    """Validate Coinbase's cbXRP 1:1 reserve page; never infer a UTC event time from locale labels."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("html_text"), str):
        raise XRPIngestionError("Coinbase cbXRP proof-of-reserves response must contain HTML text")
    normalized = payload["html_text"].casefold()
    required_markers = (
        "cbxrp proof of reserves",
        "backed 1:1 by xrp held by coinbase",
        "total reserve",
        "total supply",
        "supply by network",
    )
    if any(marker not in normalized for marker in required_markers):
        raise XRPIngestionError("Coinbase cbXRP proof-of-reserves identity or reserve markers are missing")
    return [], None, False, "coinbase_cbxrp_proof_of_reserves_raw_only_until_locale_refresh_timezone_and_cache_semantics_are_verified"


PARSERS = {
    "xrpl_inftf_server_info": _parse_xrpl_server_info,
    "xrpl_honeycluster_server_info": _parse_xrpl_server_info,
    "binance_spot_ticker": _parse_binance_ticker,
    "binance_spot_klines": _parse_binance_klines,
    "binance_perp_premium": _parse_binance_premium,
    "binance_perp_open_interest": _parse_binance_open_interest,
    "binance_perp_funding_history": _parse_binance_funding_history,
    "binance_perp_open_interest_history": _parse_binance_open_interest_history,
    "binance_perp_global_long_short_ratio": _parse_binance_global_long_short_ratio,
    "coinbase_spot_ticker": _parse_coinbase_ticker,
    "coinbase_spot_candles": _parse_coinbase_candles,
    "coinbase_spot_book": _raw_only_coinbase_book,
    "bitbank_spot_circuit_break": _parse_bitbank_circuit_break,
    "bitbank_spot_transactions": _parse_bitbank_transactions,
    "bitbank_spot_ticker": _parse_bitbank_ticker,
    "bitbank_spot_depth": _parse_bitbank_depth,
    "kraken_spot_ticker": _parse_kraken_ticker,
    "kraken_spot_depth": _parse_kraken_depth,
    "okx_spot_ticker": _parse_okx_ticker,
    "okx_spot_depth": _parse_okx_depth,
    "bybit_spot_ticker": _parse_bybit_ticker,
    "bybit_spot_depth": _parse_bybit_depth,
    "bybit_linear_ticker": _parse_bybit_linear_ticker,
    "bybit_linear_open_interest": _parse_bybit_linear_open_interest_history,
    "bybit_linear_funding_history": _parse_bybit_linear_funding_history,
    "binance_spot_depth": _raw_only_binance_depth,
    "xrp_etf_flows_aggregator": _raw_only_xrp_insights_etf_flows,
    "xrp_exchange_balances_json": _raw_only_xrp_exchange_balances,
    "xrp_etf_flows_csv": _raw_only_xrp_insights_etf_csv,
    "xrp_etf_xrpr_issuer_page": _raw_only_xrpr_issuer_page,
    "xrp_etf_bitwise_issuer_page": _raw_only_bitwise_xrp_etf_page,
    "xrp_etf_grayscale_gxrp_issuer_page": _raw_only_grayscale_gxrp_issuer_page,
    "xrp_etf_franklin_xrpz_issuer_page": _raw_only_franklin_xrpz_issuer_page,
    "xrp_etf_canary_xrpc_issuer_page": _raw_only_canary_xrpc_issuer_page,
    "xrp_etf_21shares_toxr_issuer_page": _raw_only_21shares_toxr_issuer_page,
    "ripple_rlusd_transparency_dashboard": _raw_only_ripple_rlusd_transparency_page,
    "xrpldashboard_rlusd_cross_chain_supply": _raw_only_xrpldashboard_rlusd_page,
    "circle_usdc_transparency_dashboard": _raw_only_circle_transparency_page,
    "sbi_vc_trade_lending_page": _raw_only_sbi_vc_trade_lending_page,
    "morpho_cbxrp_market_parameters": _raw_only_morpho_cbxrp_market_parameters,
    "morpho_cbxrp_market_state": _raw_only_morpho_cbxrp_market_state,
    "morpho_cbxrp_market_liquidity": _raw_only_morpho_cbxrp_market_liquidity,
    "morpho_cbxrp_market_state_history": _raw_only_morpho_cbxrp_market_state_history,
    "morpho_cbxrp_oracle_state": _raw_only_morpho_cbxrp_oracle_state,
    "coinbase_cbxrp_proof_of_reserves": _raw_only_coinbase_cbxrp_proof_of_reserves,
    "cftc_contract_status_index": _parse_cftc_contract_status_index,
    "cftc_tff_financial_futures": _parse_cftc_tff,
}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(_canonical(value))
        handle.write("\n")


def _feature_identity(record: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        record["asset"],
        record["feature_id"],
        record["event_time_utc"],
        record.get("venue"),
        record.get("instrument"),
        record.get("currency_pair"),
        record.get("market_type"),
        tuple(sorted(source["source_id"] for source in record["sources"])),
    )


def _feature_semantics(record: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        record["value"],
        record["unit"],
        record["source_data_as_of_utc"],
        record["quality_status"],
        record["model_eligible"],
    )


def _base_feature_record_id(record_id: str) -> str:
    return re.sub(r":v[0-9]+$", "", record_id)


def _prepare_feature_delta(
    history: list[dict[str, Any]],
    current_records: list[dict[str, Any]],
    *,
    captured_at_utc: str,
    store_cutoff_utc: str,
) -> list[dict[str, Any]]:
    """Persist only new or revised features; raw receipts remain per-run."""
    latest_by_identity: dict[tuple[Any, ...], dict[str, Any]] = {}
    for record in history:
        identity = _feature_identity(record)
        previous = latest_by_identity.get(identity)
        if previous is None or record["feature_version"] > previous["feature_version"]:
            latest_by_identity[identity] = record

    delta: list[dict[str, Any]] = []
    for raw_record in current_records:
        candidate = dict(raw_record)
        candidate["ingested_at_utc"] = store_cutoff_utc
        candidate["revision_available_at_utc"] = store_cutoff_utc
        if not candidate.get("model_eligible", False):
            candidate["record_id"] = f"{candidate['record_id']}:excluded:{captured_at_utc}"
            delta.append(candidate)
            continue

        identity = _feature_identity(candidate)
        previous = latest_by_identity.get(identity)
        if previous is None:
            candidate["feature_version"] = 1
            candidate["revision_status"] = "original"
            candidate["supersedes_record_id"] = None
            delta.append(candidate)
            latest_by_identity[identity] = candidate
            continue
        if _feature_semantics(previous) == _feature_semantics(candidate):
            continue
        if candidate["unit"] != previous["unit"]:
            raise XRPIngestionError("feature unit changed across point-in-time snapshots")

        version = previous["feature_version"] + 1
        candidate["record_id"] = f"{_base_feature_record_id(candidate['record_id'])}:v{version}"
        candidate["feature_version"] = version
        candidate["revision_status"] = "revised"
        candidate["supersedes_record_id"] = previous["record_id"]
        delta.append(candidate)
        latest_by_identity[identity] = candidate
    return delta


def _normalize_walk_forward_horizons(value: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    if isinstance(value, str):
        parts = value.split(",")
    elif isinstance(value, (tuple, list)):
        parts = list(value)
    else:
        raise XRPIngestionError("walk_forward_horizons must be a comma-separated string, tuple or list")
    if not parts or all(isinstance(part, str) and not part.strip() for part in parts):
        raise XRPIngestionError("walk_forward_horizons must contain at least one supported horizon")
    normalized: list[str] = []
    for part in parts:
        if not isinstance(part, str) or not part.strip():
            raise XRPIngestionError("walk_forward_horizons must contain non-empty horizon labels")
        label = part.strip().lower()
        if label not in WALK_FORWARD_HORIZON_SECONDS:
            raise XRPIngestionError(f"unsupported walk-forward horizon: {label}")
        if label in normalized:
            raise XRPIngestionError(f"duplicate walk-forward horizon: {label}")
        normalized.append(label)
    return tuple(normalized)


def _walk_forward_report(
    store: HistoricalFeatureStore,
    *,
    evaluation_as_of_utc: str,
    horizons: tuple[str, ...] | list[str] | str = DEFAULT_WALK_FORWARD_HORIZONS,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    horizon_labels = _normalize_walk_forward_horizons(horizons)
    history = store.records_through("XRP", evaluation_as_of_utc)
    evaluations: dict[str, Any] = {}
    configurations = (
        {
            "key": "binance_xrpusdt",
            "feature_id": "xrp.spot.binance.1h.close_price",
            "venue": "binance",
            "currency_pair": "XRP/USDT",
        },
        {
            "key": "coinbase_xrpusd",
            "feature_id": "xrp.spot.coinbase.1h.close_price",
            "venue": "coinbase",
            "currency_pair": "XRP/USD",
        },
    )
    for config in configurations:
        for horizon_label in horizon_labels:
            horizon_seconds = WALK_FORWARD_HORIZON_SECONDS[horizon_label]
            evaluation_key = f"{config['key']}_{horizon_label}"
            try:
                result = evaluate_chronological_walk_forward(
                    history,
                    feature_id=config["feature_id"],
                    evaluation_as_of_utc=evaluation_as_of_utc,
                    horizon_seconds=horizon_seconds,
                    embargo_seconds=horizon_seconds,
                    min_train_samples=100,
                    min_out_of_sample_samples=100,
                    target_tolerance_seconds=300,
                    max_origin_age_seconds=3600,
                    venue=config["venue"],
                    currency_pair=config["currency_pair"],
                )
                result = dict(result)
                result["horizon_label"] = horizon_label
                evaluations[evaluation_key] = result
            except WalkForwardEvaluationError as exc:
                evaluations[evaluation_key] = {
                    "status": "BLOCKED",
                    "reason": str(exc),
                    "venue": config["venue"],
                    "currency_pair": config["currency_pair"],
                    "feature_id": config["feature_id"],
                    "horizon_label": horizon_label,
                    "horizon_seconds": horizon_seconds,
                    "embargo_seconds": horizon_seconds,
                    "forecast_count": 0,
                    "forecasts": [],
                    "live_forecast_issued": False,
                    "paper_trade_executed": False,
                }
    forecast_count = sum(
        int(result.get("forecast_count", 0))
        for result in evaluations.values()
    )
    statuses = {result.get("status", "UNKNOWN") for result in evaluations.values()}
    all_venue_horizon_pairs_scored = (
        len(evaluations) == len(configurations) * len(horizon_labels)
        and bool(evaluations)
        and all(result.get("status") == "SCORED" for result in evaluations.values())
    )
    all_horizons_scored = all(
        all(
            evaluations.get(f"{config['key']}_{horizon_label}", {}).get("status") == "SCORED"
            for config in configurations
        )
        for horizon_label in horizon_labels
    )
    if all_venue_horizon_pairs_scored:
        overall_status = "SCORED"
    elif "SCORED" in statuses or "BLOCKED" in statuses:
        overall_status = "PARTIAL_OR_BLOCKED"
    else:
        overall_status = "INSUFFICIENT_HISTORY"
    report = {
        "schema_version": 1,
        "artifact_type": "xrp_historical_walk_forward_evaluation",
        "evaluation_matrix_version": WALK_FORWARD_REPORT_VERSION,
        "evaluation_as_of_utc": evaluation_as_of_utc,
        "history_record_count": len(history),
        "feature_store_snapshot_count": store.snapshot_count(),
        "requested_horizons": list(horizon_labels),
        "requested_horizons_seconds": [WALK_FORWARD_HORIZON_SECONDS[label] for label in horizon_labels],
        "evaluation_count": len(evaluations),
        "overall_status": overall_status,
        "all_venues_scored": all_venue_horizon_pairs_scored,
        "all_venue_horizon_pairs_scored": all_venue_horizon_pairs_scored,
        "all_horizons_scored": all_horizons_scored,
        "forecast_count": forecast_count,
        "evaluations": evaluations,
        "historical_backtest_only": True,
        "live_forecast_issued": False,
        "paper_trade_executed": False,
        "model_eligible": False,
        "oos_dependence_policy": (
            "Origins remain hourly. For horizons longer than one hour, target windows overlap and "
            "out-of-sample scores are dependent; no block bootstrap, HAC interval or effective-sample-size "
            "adjustment is implemented. Results remain descriptive and model-ineligible."
        ),
        "limitations": [
            "These are chronological historical baseline evaluations, not live directional forecasts.",
            "The evaluator uses Binance XRP/USDT and Coinbase XRP/USD hourly close features across the configured horizon matrix.",
            "The hourly schedule evaluates only 1h; the daily 00:15 UTC schedule and manual dispatch evaluate 1h, 4h, 24h, 7d and 30d.",
            "Every horizon uses an embargo equal to its horizon and requires at least 100 point-in-time training examples and 100 out-of-sample origins; insufficient history is reported, never relaxed.",
            "Origins remain hourly and target windows overlap for horizons longer than one hour; dependence-aware confidence intervals and block-bootstrap scoring are not implemented.",
            "The feature store cache is derived and evictable; raw per-run artifacts are the source receipts.",
            "Rolling temporal temperature scaling is applied only to deterministic baseline probabilities using earlier resolved out-of-sample outcomes; this is not a trained model or independent shadow evaluation.",
            "Shadow evaluation remains unimplemented. A separate univariate PSI drift report is generated by the scheduled collector but does not measure label/concept drift or authorize forecasts.",
        ],
    }
    return report, history

def _default_public_fetcher(source_id: str, url: str) -> Mapping[str, Any]:
    if source_id in XRPL_NODE_SOURCES:
        return fetch_public_rpc(source_id, url)
    if source_id in {"xrp_etf_xrpr_issuer_page", "xrp_etf_bitwise_issuer_page", "xrp_etf_grayscale_gxrp_issuer_page", "xrp_etf_franklin_xrpz_issuer_page", "xrp_etf_canary_xrpc_issuer_page", "xrp_etf_21shares_toxr_issuer_page", "ripple_rlusd_transparency_dashboard", "xrpldashboard_rlusd_cross_chain_supply", "circle_usdc_transparency_dashboard", "sbi_vc_trade_lending_page", "coinbase_cbxrp_proof_of_reserves", "cftc_contract_status_index", "cftc_tff_financial_futures"}:
        return fetch_public_html(source_id, url)
    if source_id == "xrp_etf_flows_csv":
        return fetch_public_csv(source_id, url)
    return fetch_public_json(source_id, url)


def _run_coinbase_candle_backfill(
    *,
    fetcher: Callable[[str, str], Mapping[str, Any]],
    archive: RawReceiptArchive,
    captured: datetime,
    captured_s: str,
    oldest_open: datetime,
    days: int,
    receipts: list[dict[str, Any]],
    records: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    raw_only: list[dict[str, Any]],
) -> dict[str, Any]:
    ranges = _coinbase_candle_backfill_ranges(oldest_open, days)
    state = {
        "status": "RUNNING",
        "mode": "MANUAL_ONLY_ADDITIONAL_HISTORY",
        "requested_days_before_oldest_latest_page_candle": days,
        "baseline_oldest_candle_open_utc": _iso(oldest_open),
        "range_start_utc": _iso(ranges[0][0]),
        "range_end_utc": _iso(ranges[-1][1]),
        "pages_requested": len(ranges),
        "pages_completed": 0,
        "pages_failed": 0,
        "empty_pages": 0,
        "candles_ingested": 0,
        "max_candles_per_request": COINBASE_CANDLES_PER_REQUEST,
        "max_days_per_invocation": MAX_COINBASE_BACKFILL_DAYS,
        "page_delay_seconds": COINBASE_BACKFILL_PAGE_DELAY_SECONDS,
    }
    observed_candles = set()
    parser = PARSERS["coinbase_spot_candles"]
    for page_index, (page_start, page_end) in enumerate(ranges, start=1):
        page_source_id = f"coinbase_spot_candles_backfill_page_{page_index:03d}"
        page_url = _coinbase_candle_page_url(page_start, page_end)
        response: Mapping[str, Any] | None = None
        raw_bytes: bytes | None = None
        parsed_records = []
        source_as_of = None
        source_eligible = False
        reason = ""
        try:
            response = fetcher("coinbase_spot_candles", page_url)
            if not isinstance(response, Mapping):
                raise XRPIngestionError("Coinbase backfill fetcher response must be a mapping")
            raw_bytes = response.get("raw_bytes")
            payload = response.get("payload")
            if not isinstance(raw_bytes, bytes) or not raw_bytes:
                raise XRPIngestionError("Coinbase backfill raw response must be non-empty bytes")
            digest = hashlib.sha256(raw_bytes).hexdigest()
            parsed_records, source_as_of, source_eligible, reason = parser(
                payload,
                source_id=page_source_id,
                url=page_url,
                digest=digest,
                captured=captured,
                page_start_utc=_iso(page_start),
                page_end_utc=_iso(page_end),
            )
        except Exception as exc:
            failure = _source_failure_record(page_source_id, page_url, captured_s, exc)
            failure.update({
                "source_family_id": "coinbase_spot_candles",
                "page_index": page_index,
            })
            if isinstance(response, Mapping) and isinstance(raw_bytes, bytes) and raw_bytes:
                raw_reason = f"source_processing_failure:{type(exc).__name__}"
                receipt = archive.store(
                    source_id=page_source_id,
                    source_uri=page_url,
                    captured_at_utc=captured_s,
                    raw_bytes=raw_bytes,
                    source_data_as_of_utc=None,
                    model_eligible=False,
                    raw_only_reason=raw_reason,
                    source_http_date=response.get("http_date"),
                    source_http_headers=response.get("http_headers"),
                )
                receipts.append(receipt)
                raw_only.append(
                    {
                        "source_id": page_source_id,
                        "reason": raw_reason,
                        "receipt_id": receipt["receipt_id"],
                    }
                )
                failure["raw_receipt_id"] = receipt["receipt_id"]
                failure["raw_content_sha256"] = receipt["raw_content_sha256"]
            failures.append(failure)
            state["pages_failed"] += 1
        else:
            receipt_reason = reason or ("" if source_eligible else "coinbase_backfill_page_not_model_eligible")
            receipt = archive.store(
                source_id=page_source_id,
                source_uri=page_url,
                captured_at_utc=captured_s,
                raw_bytes=raw_bytes,
                source_data_as_of_utc=source_as_of,
                model_eligible=source_eligible,
                raw_only_reason=receipt_reason,
                source_http_date=response.get("http_date"),
                    source_http_headers=response.get("http_headers"),
            )
            receipts.append(receipt)
            records.extend(parsed_records)
            state["pages_completed"] += 1
            if not parsed_records:
                state["empty_pages"] += 1
            for item in parsed_records:
                observed_candles.add(item["event_time_utc"])
            if reason:
                raw_only.append(
                    {
                        "source_id": page_source_id,
                        "reason": reason,
                        "receipt_id": receipt["receipt_id"],
                    }
                )
        if page_index < len(ranges):
            time.sleep(COINBASE_BACKFILL_PAGE_DELAY_SECONDS)

    state["candles_ingested"] = len(observed_candles)
    if state["pages_failed"]:
        state["status"] = "PARTIAL" if state["pages_completed"] else "FAILED"
    else:
        state["status"] = "COMPLETED"
    return state


def run_ingestion(
    output_dir: str | Path,
    *,
    fetcher: Callable[[str, str], Mapping[str, Any]] = _default_public_fetcher,
    now: datetime | None = None,
    include_noncommercial_xrpl_nodes: bool = False,
    coinbase_backfill_days: int = 0,
    walk_forward_horizons: tuple[str, ...] | list[str] | str = DEFAULT_WALK_FORWARD_HORIZONS,
) -> dict[str, Any]:
    """Capture public XRP data; scheduled hourly runs use 1h and daily runs may evaluate the full horizon matrix."""
    if not isinstance(include_noncommercial_xrpl_nodes, bool):
        raise XRPIngestionError("include_noncommercial_xrpl_nodes must be a boolean")
    if isinstance(coinbase_backfill_days, bool) or not isinstance(coinbase_backfill_days, int) or not 0 <= coinbase_backfill_days <= MAX_COINBASE_BACKFILL_DAYS:
        raise XRPIngestionError(f"coinbase_backfill_days must be an integer from 0 to {MAX_COINBASE_BACKFILL_DAYS}")
    normalized_walk_forward_horizons = _normalize_walk_forward_horizons(walk_forward_horizons)
    captured = now or datetime.now(timezone.utc)
    captured_s = _iso(captured)
    selected_endpoints = list(SCHEDULED_ENDPOINTS)
    if include_noncommercial_xrpl_nodes:
        selected_endpoints.extend(
            (source_id, url)
            for source_id, url in ENDPOINTS
            if source_id in NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS
        )
    weekly_endpoints = _weekly_endpoints_for_capture(captured)
    selected_endpoints.extend(weekly_endpoints)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    archive = RawReceiptArchive(output / "raw")
    receipts = []
    records = []
    failures = []
    raw_only = []
    research_only_observations = []
    parsed_weekly_source_ids = []
    xrp_insights_metadata_payload: Mapping[str, Any] | None = None
    bitbank_circuit_break_payload: Mapping[str, Any] | None = None
    cftc_contract_status_payload: Mapping[str, Any] | None = None
    xrpl_node_payloads: dict[str, Mapping[str, Any]] = {}

    for source_id, url in selected_endpoints:
        response: Mapping[str, Any] | None = None
        raw_bytes: bytes | None = None
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
            if source_id in {"coinbase_spot_ticker", "kraken_spot_ticker", "kraken_spot_depth"} or source_id in XRPL_NODE_SOURCES or source_id in BITBANK_SOURCE_IDS:
                parser_kwargs["http_date"] = response.get("http_date")
            if source_id in {"bitbank_spot_ticker", "bitbank_spot_depth"}:
                parser_kwargs["circuit_break_info"] = bitbank_circuit_break_payload
            if source_id == "xrp_etf_flows_csv":
                parser_kwargs["metadata_payload"] = xrp_insights_metadata_payload
            if source_id == "cftc_tff_financial_futures":
                parser_kwargs["contract_status_html"] = (
                    cftc_contract_status_payload.get("html_text")
                    if isinstance(cftc_contract_status_payload, Mapping)
                    else None
                )
            parsed_records, source_as_of, source_eligible, reason = parser(
                payload,
                **parser_kwargs,
            )
            cache_age_reason = _apply_http_cache_age_gate(
                source_id,
                response.get("http_headers"),
                parsed_records,
            )
            if cache_age_reason:
                source_eligible = False
                reason = cache_age_reason
            if source_id in WEEKLY_SOURCE_IDS and parsed_records:
                parsed_weekly_source_ids.append(source_id)
            if source_id == "xrp_etf_flows_aggregator":
                xrp_insights_metadata_payload = payload
            if source_id == "cftc_contract_status_index":
                cftc_contract_status_payload = payload
            if source_id == "bitbank_spot_circuit_break":
                bitbank_circuit_break_payload = payload
            if source_id in XRPL_NODE_SOURCES and source_as_of is not None:
                xrpl_node_payloads[source_id] = payload
        except Exception as exc:
            failure = _source_failure_record(source_id, url, captured_s, exc)
            # A successfully captured response remains evidence even when its
            # parser or schema validation fails. Preserve the exact bytes as a
            # raw-only receipt; never infer a data-as-of time from failed parsing.
            if isinstance(response, Mapping) and isinstance(raw_bytes, bytes) and raw_bytes:
                raw_reason = f"source_processing_failure:{type(exc).__name__}"
                receipt = archive.store(
                    source_id=source_id,
                    source_uri=url,
                    captured_at_utc=captured_s,
                    raw_bytes=raw_bytes,
                    source_data_as_of_utc=None,
                    model_eligible=False,
                    raw_only_reason=raw_reason,
                    source_http_date=response.get("http_date"),
                    source_http_headers=response.get("http_headers"),
                    retain_raw_bytes=source_id not in DIGEST_ONLY_RAW_SOURCE_REASONS,
                    raw_retention_reason=DIGEST_ONLY_RAW_SOURCE_REASONS.get(source_id, ""),
                )
                receipts.append(receipt)
                raw_only.append(
                    {
                        "source_id": source_id,
                        "reason": raw_reason,
                        "receipt_id": receipt["receipt_id"],
                    }
                )
                failure["raw_receipt_id"] = receipt["receipt_id"]
                failure["raw_content_sha256"] = receipt["raw_content_sha256"]
            failures.append(failure)
            continue

        # Receipt writes are outside the source-error handler. Archive corruption
        # or a content-address collision must fail the run closed.
        receipt = archive.store(
            source_id=source_id,
            source_uri=url,
            captured_at_utc=captured_s,
            raw_bytes=raw_bytes,
            source_data_as_of_utc=source_as_of,
            model_eligible=source_eligible,
            raw_only_reason=reason,
            source_http_date=response.get("http_date"),
                    source_http_headers=response.get("http_headers"),
            retain_raw_bytes=source_id not in DIGEST_ONLY_RAW_SOURCE_REASONS,
            raw_retention_reason=DIGEST_ONLY_RAW_SOURCE_REASONS.get(source_id, ""),
        )
        receipts.append(receipt)
        if source_id == "bitbank_spot_transactions":
            observation = _bitbank_transactions_research_summary(payload)
            if observation is not None:
                research_only_observations.append(
                    {
                        **observation,
                        "source_id": source_id,
                        "source_uri": url,
                        "raw_content_sha256": receipt["raw_content_sha256"],
                        "receipt_id": receipt["receipt_id"],
                        "raw_bytes_retained": receipt["raw_bytes_retained"],
                        "captured_at_utc": captured_s,
                    }
                )
            records.extend(parsed_records)
        elif source_id == "xrp_etf_flows_csv":
            metadata = (xrp_insights_metadata_payload or {}).get("metadata", {})
            for observation in parsed_records:
                research_only_observations.append(
                    {
                        **observation,
                        "source_id": source_id,
                        "source_uri": url,
                        "raw_content_sha256": receipt["raw_content_sha256"],
                        "receipt_id": receipt["receipt_id"],
                        "raw_bytes_retained": receipt["raw_bytes_retained"],
                        "captured_at_utc": captured_s,
                        "metadata_generated_at_utc": metadata.get("generated_at"),
                    }
                )
        elif source_id == "cftc_contract_status_index":
            status = parse_cftc_contract_status(payload.get("html_text", ""))
            research_only_observations.append(
                {
                    "observation_type": "cftc_weekly_contract_reporting_status",
                    "source_id": source_id,
                    "source_uri": url,
                    "raw_content_sha256": receipt["raw_content_sha256"],
                    "receipt_id": receipt["receipt_id"],
                    "raw_bytes_retained": receipt["raw_bytes_retained"],
                    "captured_at_utc": captured_s,
                    "source_data_as_of_utc": source_as_of,
                    "reports_dated": status["reports_dated"],
                    "futures_only_added": status["futures_only_added"],
                    "futures_only_dropped": status["futures_only_dropped"],
                    "futures_and_options_combined_added": status["futures_and_options_combined_added"],
                    "futures_and_options_combined_dropped": status["futures_and_options_combined_dropped"],
                    "model_eligible": False,
                    "interpretation_limits": [
                        "This is a reporting-universe status index, not open interest or position data.",
                        "A dropped contract is missing from the current report; its positions must not be interpreted as zero or as proof that positions were closed.",
                    ],
                }
            )
        elif source_id == "cftc_tff_financial_futures":
            research_only_observations.append(
                {
                    "observation_type": "cftc_tff_xrp_futures_only_position_features",
                    "source_id": source_id,
                    "source_uri": url,
                    "raw_content_sha256": receipt["raw_content_sha256"],
                    "receipt_id": receipt["receipt_id"],
                    "raw_bytes_retained": receipt["raw_bytes_retained"],
                    "captured_at_utc": captured_s,
                    "source_data_as_of_utc": source_as_of,
                    "timestamp_precision": "date_only",
                    "model_eligible": False,
                    "feature_count": len(parsed_records),
                    "features": [
                        {
                            "feature_id": record["feature_id"],
                            "value": record["value"],
                            "unit": record["unit"],
                            "instrument": record["instrument"],
                        }
                        for record in parsed_records
                    ],
                    "interpretation_limits": [
                        "Futures-only positions are not spot holdings, net exchange flows, cash subscriptions, collateral utilization, or actual capital deployed.",
                        "The as-of date has no intraday timestamp; captured_at_utc is the known-at time.",
                        "CFTC categories do not identify individual traders or disclose position intent.",
                        "The three contract families have different multipliers and should not be summed as raw contract counts.",
                    ],
                }
            )
            records.extend(parsed_records)
        else:
            records.extend(parsed_records)
        if reason and not source_eligible and source_id != "cftc_tff_financial_futures":
            raw_only.append({"source_id": source_id, "reason": reason})
        elif reason and source_id in {"binance_spot_klines", "coinbase_spot_candles"}:
            raw_only.append({"source_id": source_id, "reason": reason})

    coinbase_backfill = {
        "status": "NOT_REQUESTED",
        "mode": "MANUAL_ONLY_ADDITIONAL_HISTORY",
        "requested_days_before_oldest_latest_page_candle": coinbase_backfill_days,
        "pages_requested": 0,
        "pages_completed": 0,
        "pages_failed": 0,
        "empty_pages": 0,
        "candles_ingested": 0,
        "max_days_per_invocation": MAX_COINBASE_BACKFILL_DAYS,
    }
    if coinbase_backfill_days:
        latest_coinbase_close_times = [
            record["event_time_utc"]
            for record in records
            if record.get("feature_id") == "xrp.spot.coinbase.1h.close_price"
            and any(
                source.get("source_id") == "coinbase_spot_candles"
                for source in record.get("sources", [])
                if isinstance(source, Mapping)
            )
        ]
        if not latest_coinbase_close_times:
            coinbase_backfill["status"] = "BLOCKED_NO_BASELINE_CANDLE_BOUNDARY"
            coinbase_backfill["reason"] = "the latest Coinbase candle page produced no usable completed candle boundary"
        else:
            oldest_open = _from_iso8601(min(latest_coinbase_close_times), "oldest Coinbase candle open time")
            coinbase_backfill = _run_coinbase_candle_backfill(
                fetcher=fetcher,
                archive=archive,
                captured=captured,
                captured_s=captured_s,
                oldest_open=oldest_open,
                days=coinbase_backfill_days,
                receipts=receipts,
                records=records,
                failures=failures,
                raw_only=raw_only,
            )

    receipt_chain_verification = archive.write_manifest(output / "receipt_chain_manifest.json")

    if include_noncommercial_xrpl_nodes:
        xrpl_node_reconciliation = _reconcile_xrpl_node_records(records, xrpl_node_payloads)
    else:
        xrpl_node_reconciliation = {
            "status": "NOT_COLLECTED_PROVIDER_TERMS_POLICY",
            "reason": "free_noncommercial_xrpl_nodes_are_excluded_from_default_and_scheduled_collection",
            "required_source_count": len(XRPL_NODE_SOURCES),
            "observed_source_count": 0,
            "observed_source_ids": [],
            "observations": {},
            "integrity_check_only": True,
            "model_admission_allowed": False,
            "model_admission_reason": "provider_terms_policy_blocks_scheduled_use",
        }
    if xrpl_node_reconciliation["status"] != "AGREED":
        for source_id in xrpl_node_reconciliation["observed_source_ids"]:
            raw_only.append(
                {
                    "source_id": source_id,
                    "reason": xrpl_node_reconciliation["reason"],
                }
            )

    database = output / "feature_store.sqlite3"
    store = HistoricalFeatureStore(database)
    store_cutoff = datetime.now(timezone.utc)
    store_cutoff_s = _iso(store_cutoff)
    prior_history = store.records_through("XRP", store_cutoff_s)
    previous_snapshot = store.snapshot_as_of("XRP", store_cutoff_s)
    previous_snapshot_id = previous_snapshot.get("snapshot_id") if previous_snapshot else None
    delta_records = _prepare_feature_delta(
        prior_history,
        records,
        captured_at_utc=captured_s,
        store_cutoff_utc=store_cutoff_s,
    )

    snapshot = None
    stored = None
    store_verification = {"valid": True, "status": "no_new_snapshot"}
    snapshot_status = "no_new_eligible_features"
    snapshot_blocked_path = output / "snapshot_blocked.json"
    if any(record.get("model_eligible") is True for record in delta_records):
        snapshot = build_feature_snapshot(
            delta_records,
            cutoff_utc=store_cutoff_s,
            captured_at_utc=store_cutoff_s,
            asset_scope=["XRP"],
        )
        stored = store.append_snapshot(snapshot)
        store_verification = store.verify_snapshot(snapshot["snapshot_id"])
        if not store_verification.get("valid"):
            raise FeatureStoreError("newly appended XRP delta snapshot failed verification")
        snapshot_status = "verified"
        snapshot_blocked_path.unlink(missing_ok=True)
        _write_json(output / "snapshot.json", snapshot)
    else:
        snapshot_blocked_path.unlink(missing_ok=True)
        _write_json(
            output / "snapshot.json",
            {
                "schema_version": 1,
                "artifact_type": "xrp_feature_store_run_delta",
                "status": snapshot_status,
                "captured_at_utc": captured_s,
                "feature_store_cutoff_utc": store_cutoff_s,
                "previous_snapshot_id": previous_snapshot_id,
                "delta_record_count": 0,
                "snapshot_id": None,
            },
        )

    evaluation_as_of = datetime.now(timezone.utc)
    evaluation_as_of_s = _iso(evaluation_as_of)
    walk_forward, history_records = _walk_forward_report(
        store,
        evaluation_as_of_utc=evaluation_as_of_s,
        horizons=normalized_walk_forward_horizons,
    )
    drift_report = monitor_feature_drift(
        history_records,
        cutoff_utc=evaluation_as_of_s,
        reference_days=30,
        current_days=7,
        min_samples_per_window=30,
    )
    _write_json(output / "drift_report.json", drift_report)
    checkpoint = store.checkpoint()
    _write_json(output / "walk_forward.json", walk_forward)

    _write_json(output / "receipt_manifest.json", receipts)
    _write_json(output / "source_failures.json", failures)
    _write_json(output / "raw_only_sources.json", raw_only)
    _write_json(
        output / "research_only_observations.json",
        {
            "schema_version": 1,
            "artifact_type": "xrp_research_only_observations",
            "captured_at_utc": captured_s,
            "observation_count": len(research_only_observations),
            "model_eligible": False,
            "observations": research_only_observations,
        },
    )
    summary = {
        "schema_version": 1,
        "artifact_type": "xrp_public_market_ingestion_run",
        "adapter_version": ADAPTER_VERSION,
        "parser_version": PARSER_VERSION,
        "captured_at_utc": captured_s,
        "data_cutoff_utc": captured_s,
        "feature_store_cutoff_utc": store_cutoff_s,
        "evaluation_as_of_utc": evaluation_as_of_s,
        "source_receipt_count": len(receipts),
        "coinbase_backfill": coinbase_backfill,
        "receipt_chain_manifest_path": "receipt_chain_manifest.json",
        "receipt_chain_verification": receipt_chain_verification,
        "source_failure_count": len(failures),
        "raw_only_source_count": len(raw_only),
        "research_only_observation_count": len(research_only_observations),
        "research_only_observations_path": "research_only_observations.json",
        "collection_policy": {
            "noncommercial_xrpl_nodes_included": include_noncommercial_xrpl_nodes,
            "default_scheduled_endpoints_exclude_noncommercial_xrpl_nodes": True,
            "excluded_noncommercial_xrpl_node_source_ids": (
                [] if include_noncommercial_xrpl_nodes else sorted(NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS)
            ),
            "reason": (
                "The official XRPL public-server directory classifies the free InFTF and Honeycluster endpoints as non-commercial. "
                "Scheduled collection requires a self-hosted or contracted commercial endpoint."
            ),
        },
        "weekly_source_policy": {
            "source_ids": sorted(WEEKLY_SOURCE_IDS),
            "capture_window_utc": (
                "Saturday 00:10-01:59 UTC after standard Friday releases; "
                "21:03-21:59 UTC on official delayed Monday dates; "
                "Wednesday/Friday 21:03-21:59 UTC only after a confirmed semiweekly effective date"
            ),
            "captured_source_ids": [source_id for source_id, _url in weekly_endpoints],
            "parsed_source_ids": parsed_weekly_source_ids,
            "raw_only_source_ids": [
                source_id for source_id, _url in weekly_endpoints
                if source_id not in parsed_weekly_source_ids
            ],
            "scheduled_delayed_release_dates_utc": sorted(CFTC_DELAYED_RELEASE_DATES_2026),
            "semiweekly_effective_date_confirmed": CFTC_SEMIWEEKLY_EFFECTIVE_DATE,
            "planned_semiweekly_release_days": ["Wednesday", "Friday"],
            "skipped_source_ids": sorted(
                WEEKLY_SOURCE_IDS - {source_id for source_id, _url in weekly_endpoints}
            ),
            "reason": (
                "The weekly CFTC COT index and Traders in Financial Futures report are captured together after the official release. "
                "The TFF report is parsed into date-only futures-position research features for reported XRP contract families; "
                "the added/dropped index is stored as a separate research-only reporting-universe observation. "
                "All CFTC features remain model-ineligible, and missing or dropped contracts are never zero-filled. "
                "The official release schedule lists delayed 2026 dates on November 16, November 30, and December 28; "
                "the adapter captures the listed Monday releases after 15:30 America/New_York. CFTC announced on "
                "October 27 a plan to publish Monday data on Wednesday and Wednesday data on Friday, but no effective "
                "date has been confirmed; the semiweekly capture path remains disabled until that date is set."
            ),
        },
        "xrpl_node_reconciliation": xrpl_node_reconciliation,
        "input_feature_record_count": len(records),
        "delta_feature_record_count": len(delta_records),
        "snapshot_status": snapshot_status,
        "snapshot_id": snapshot.get("snapshot_id") if snapshot else None,
        "eligible_feature_record_count": snapshot.get("eligible_record_count", 0) if snapshot else 0,
        "excluded_feature_record_count": snapshot.get("excluded_record_count", 0) if snapshot else 0,
        "previous_snapshot_id": previous_snapshot_id,
        "store_receipt": stored,
        "store_verification": store_verification,
        "feature_store_checkpoint": checkpoint,
        "feature_store_snapshot_count": store.snapshot_count(),
        "feature_store_history_record_count": len(history_records),
        "feature_store_restore_source": os.getenv("BARROT_FEATURE_STORE_RESTORE_SOURCE", "unknown"),
        "walk_forward_status": walk_forward["overall_status"],
        "walk_forward_forecast_count": walk_forward["forecast_count"],
        "walk_forward_report_version": WALK_FORWARD_REPORT_VERSION,
        "walk_forward_horizon_labels": list(normalized_walk_forward_horizons),
        "walk_forward_horizons_seconds": [WALK_FORWARD_HORIZON_SECONDS[label] for label in normalized_walk_forward_horizons],
        "drift_monitor_version": DRIFT_MONITOR_VERSION,
        "drift_status": drift_report["status"],
        "drift_report_path": "drift_report.json",
        "drift_report_retention_days": DRIFT_REPORT_RETENTION_DAYS,
        "drift_report_sha256": drift_report["report_sha256"],
        "drift_feature_count": drift_report["feature_count"],
        "drift_evaluated_feature_count": drift_report["evaluated_feature_count"],
        "drift_forecast_issuance_allowed": drift_report["forecast_issuance_allowed"],
        "forecast_status": "NOT_ISSUED",
        "forecast_model_eligible": False,
        "paper_trade_executed": False,
        "storage_scope": (
            "append-only SQLite feature history restored from an exact-key GitHub Actions cache; "
            "when no exact cache key exists, the latest successful per-run feature-store checkpoint "
            "(7-day retention) is restored, with the daily/manual feature-store archive "
            "(90-day retention) as fallback; per-run raw-source artifacts are retained 90 days; "
            "cache is derived and evictable, not an immutable source of truth"
        ),
        "artifact_retention_days": 90,
        "feature_store_backup_retention_days": 90,
        "feature_store_backup_frequency": "daily_plus_manual_dispatch",
        "feature_store_checkpoint_retention_days": 7,
        "feature_store_checkpoint_frequency": "every_ingestion_run",
        "feature_store_restore_strategy": "exact_cache_key_then_latest_per_run_checkpoint_then_daily_archive",
        "feature_store_restore_search_max_pages": 30,
        "feature_store_rebuild_from_raw_artifacts_implemented": False,
        "limitations": [
            "Spot coverage includes Binance, Coinbase, Kraken and OKX XRP-USDT; derivatives history is Binance USD-M XRPUSDT only.",
            "USDT quotes and Binance-reported open-interest value are not converted to USD; open-interest contracts, quote value, funding fractions and account ratios remain separate units.",
            "Historical Binance funding settlements are timestamped per event; the actual funding interval is not assumed fixed. Binance open-interest and global long/short history are one-hour observations limited to the latest 30 days, with no-trade gaps preserved as missing.",
            "Binance and Coinbase order-book snapshots remain raw-only because no exchange timestamp/sequence bridge is maintained; Kraken depth requires a fresh HTTP Date header; OKX depth is admitted only with a fresh exchange-provided snapshot timestamp and does not establish sequence continuity.",
            "Historical Binance and Coinbase candles are known to this collector only at captured_at_utc; they cannot be used at earlier historical cutoffs. Coinbase history beyond the latest endpoint page is manual-only, bounded to 365 additional days, paged at no more than 300 hourly candles per request, and never polled by the scheduled workflow.",
            "Raw source bytes and receipts are retained in per-run artifacts for 90 days; independent external timestamp anchoring and long-term immutable object storage are not configured.",
            "The cumulative SQLite feature store uses an exact-key cache when available, otherwise the latest successful per-run checkpoint (7-day retention), with the daily/manual archive (90-day retention) as fallback. Cache remains derived and evictable; if no checkpoint or daily archive is available, continuity can still fall back to bootstrap. Automatic rebuild from raw receipts is not yet implemented.",
            "The historical evaluator covers Binance XRP/USDT and Coinbase XRP/USD hourly closes across the configured 1h, 4h, 24h, 7d and 30d horizon matrix; hourly scheduled runs evaluate 1h, while daily/manual runs evaluate the full matrix with horizon-sized embargoes. Multi-day target windows overlap and no dependence-aware confidence interval or block-bootstrap adjustment is implemented; results remain descriptive and model-ineligible.",
            "XRP Insights attributed exchange-wallet balances are scheduled for hash-only raw capture; they are not promoted to exchange-flow features until date, wallet-set, same-wallet and coverage-change semantics are parsed and independently checked.",
            "XRP Insights ETF metadata is retained with a raw receipt; its CSV is schema-validated in memory, recorded as a hash-only receipt under the publisher redistribution terms, and reduced to one attributed latest-date aggregate that is never promoted to model features.",
            "Bitwise XRP ETF, Grayscale GXRP and REX XRPR primary issuer pages are captured as SHA-256-receipted raw-only HTML; holdings are not parsed into features until page-vintage and parser validation are implemented.",
            "The historical evaluator uses naive, momentum, mean-reversion and volatility baselines. Rolling temporal temperature scaling is applied only to deterministic baseline probabilities using earlier resolved out-of-sample outcomes; this is not a trained predictive model or independent shadow evaluation.",
            "A univariate PSI feature-distribution drift report is generated on every scheduled ingestion. It does not measure label/concept drift, uses provisional thresholds, and never authorizes forecast issuance.",
            "The default scheduled collector excludes the free InFTF and Honeycluster XRPL public-node endpoints because the official directory classifies them as non-commercial. A self-hosted or contracted commercial endpoint is required for sustained collection.",
            "An explicit one-off non-commercial research capture may compare the two nodes' validated-ledger index/hash, but node agreement is integrity-only, never model-eligible, and never independent economic corroboration.",
            "This collector does not issue directional forecasts, trading signals, recommendations or paper trades.",
        ],
    }
    _write_json(output / "summary.json", summary)
    return summary

def main() -> None:
    parser = argparse.ArgumentParser(description="Capture public XRP spot, order-book, funding, open-interest and positioning data.")
    parser.add_argument("--output-dir", default="artifacts/xrp_ingestion")
    parser.add_argument(
        "--coinbase-backfill-days",
        type=int,
        default=0,
        help="Manual-only additional Coinbase XRP-USD hourly history before the latest candle page (0 disables; maximum 365 days).",
    )
    parser.add_argument(
        "--walk-forward-horizons",
        default="1h",
        help="Comma-separated historical evaluation horizons: 1h,4h,24h,7d,30d. The scheduled workflow selects 1h hourly and the full matrix daily.",
    )
    args = parser.parse_args()
    horizons = _normalize_walk_forward_horizons(args.walk_forward_horizons)
    summary = run_ingestion(
        args.output_dir,
        coinbase_backfill_days=args.coinbase_backfill_days,
        walk_forward_horizons=horizons,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
