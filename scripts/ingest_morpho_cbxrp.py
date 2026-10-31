#!/usr/bin/env python3
"""Read-only, timestamped Morpho cbXRP/USDC market snapshot.

Uses only Morpho's public GET API. No wallet, key, signing or write capability.
A partial/rate-limited response is still recorded, but never admitted as a
prediction feature. Market-wide positions and liquidation events require
separate on-chain ingestion; they are not exposed by this REST API.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

API_BASE = "https://api.morpho.org"
CHAIN_ID = 8453
MARKET_ID = "0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109"
CBXRP_ADDRESS = "0xcb585250f852c6c6bf90434ab21a00f02833a4af"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
LOOKBACK = "thirty_days"
EXPECTED_LLTV = Decimal("0.625")
USER_AGENT = "Barrot-XRP-Research/1.0"


class ProviderHTTPError(Exception):
    def __init__(self, status: int, retry_after: str | None = None, body: str = ""):
        super().__init__(f"Morpho API HTTP {status}")
        self.status = status
        self.retry_after = retry_after
        self.body = body[:500]


def _request_json(url: str, timeout: int = 20) -> tuple[dict[str, Any] | list[Any], int]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(getattr(response, "status", 200))
            raw = response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ProviderHTTPError(
            int(exc.code),
            exc.headers.get("Retry-After") if exc.headers else None,
            body,
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"network error: {exc.reason}") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid JSON from {url}") from exc
    if not isinstance(payload, (dict, list)):
        raise RuntimeError(f"unexpected JSON root from {url}")
    return payload, status


def build_request_urls() -> dict[str, str]:
    market_selector = f"{CHAIN_ID}:{MARKET_ID}"
    loan_selector = f"{CHAIN_ID}:{USDC_ADDRESS}"
    collateral_selector = f"{CHAIN_ID}:{CBXRP_ADDRESS}"
    params = urllib.parse.urlencode(
        {
            "chain_id": CHAIN_ID,
            "loan_token": loan_selector,
            "collateral_token": collateral_selector,
            "listed": "true",
            "limit": 100,
        }
    )
    root = f"{API_BASE}/v0/blue/markets/{market_selector}"
    return {
        "market_list": f"{API_BASE}/v1/blue/markets?{params}",
        "market": root,
        "state": f"{root}/state",
        "market_liquidity": f"{root}/liquidity",
        "apy_averages": f"{root}/apy-averages",
        "state_history": f"{root}/state/history?lookback={LOOKBACK}",
        "apy_history": f"{root}/apy/history?lookback={LOOKBACK}",
        "cbxrp_price": f"{API_BASE}/v0/tokens/{collateral_selector}/price",
        "usdc_price": f"{API_BASE}/v0/tokens/{loan_selector}/price",
    }


def _data(payload: Any) -> Any:
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def _field(obj: Any, *names: str) -> Any:
    if not isinstance(obj, dict):
        return None
    for name in names:
        if name in obj:
            return obj[name]
    return None


def _address(value: Any) -> str | None:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        raw = _field(value, "address", "token_address", "tokenAddress")
        return raw.lower() if isinstance(raw, str) else None
    return None


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _iso_utc(value: Any) -> dt.datetime | None:
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc)
        text = str(value)
        if text.isdigit():
            return dt.datetime.fromtimestamp(int(text), tz=dt.timezone.utc)
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return None


def _sha256(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _market_list_items(payload: Any) -> list[dict[str, Any]]:
    value = _data(payload)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ("items", "markets", "results"):
            candidate = value.get(key)
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]
    return []


def _market_list_cursor(payload: Any) -> Any:
    # Morpho list responses place the pagination cursor beside the data field.
    # Keep compatibility with wrappers that nest pagination metadata in data.
    cursor = _field(payload, "next_cursor", "nextCursor", "cursor")
    if cursor is not None:
        return cursor
    value = _data(payload)
    return _field(value, "next_cursor", "nextCursor", "cursor") if isinstance(value, dict) else None


def collect_snapshot(
    fetch_json: Callable[[str], tuple[dict[str, Any] | list[Any], int]] = _request_json,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    captured = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    urls = build_request_urls()
    raw: dict[str, Any] = {}
    request_log: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    rate_limited = False

    for name, url in urls.items():
        try:
            payload, status = fetch_json(url)
            raw[name] = payload
            request_log.append(
                {"name": name, "url": url, "http_status": status, "sha256": _sha256(payload)}
            )
            if status == 206:
                errors.append({"name": name, "kind": "PARTIAL_CONTENT_206", "message": "price may be null"})
        except ProviderHTTPError as exc:
            request_log.append(
                {"name": name, "url": url, "http_status": exc.status, "retry_after": exc.retry_after}
            )
            errors.append(
                {"name": name, "kind": "HTTP_ERROR", "status": exc.status, "retry_after": exc.retry_after}
            )
            if exc.status == 429:
                rate_limited = True
            break
        except Exception as exc:  # preserve a partial snapshot; do not hammer a failed provider
            request_log.append({"name": name, "url": url, "http_status": None})
            errors.append({"name": name, "kind": "PROVIDER_ERROR", "message": str(exc)[:500]})
            break

    market = _data(raw.get("market"))
    state = _data(raw.get("state"))
    market_list = raw.get("market_list")
    flags: list[str] = []

    listed = _market_list_items(market_list) if market_list is not None else []
    listed_ids = set()
    for item in listed:
        raw_id = str(_field(item, "unique_key", "market_id", "marketId", "id") or "").lower()
        listed_ids.add(raw_id.split(":", 1)[-1])
    if market_list is not None and MARKET_ID.lower() not in listed_ids:
        flags.append("MARKET_NOT_FOUND_IN_FILTERED_LIST")
    if market_list is not None and _market_list_cursor(market_list):
        flags.append("MARKET_LIST_PAGINATION_INCOMPLETE")

    if not isinstance(market, dict):
        flags.append("MARKET_CONFIG_MISSING")
        market = {}
    loan_address = _address(_field(market, "loan_token", "loanToken"))
    collateral_address = _address(_field(market, "collateral_token", "collateralToken"))
    chain_value = _field(market, "chain_id", "chainId")
    if chain_value is not None and int(chain_value) != CHAIN_ID:
        flags.append("CHAIN_ID_MISMATCH")
    if loan_address and loan_address != USDC_ADDRESS.lower():
        flags.append("LOAN_TOKEN_MISMATCH")
    if collateral_address and collateral_address != CBXRP_ADDRESS.lower():
        flags.append("COLLATERAL_TOKEN_MISMATCH")
    if not loan_address:
        flags.append("LOAN_TOKEN_ADDRESS_MISSING")
    if not collateral_address:
        flags.append("COLLATERAL_TOKEN_ADDRESS_MISSING")

    lltv_raw = _field(market, "lltv_wad", "lltvWad")
    lltv = _decimal(lltv_raw)
    lltv_fraction = (lltv / Decimal(10**18)) if lltv is not None else None
    if lltv_fraction is None:
        flags.append("LLTV_MISSING")
    elif lltv_fraction != EXPECTED_LLTV:
        flags.append("LLTV_NOT_EXPECTED_62_5_PERCENT")

    if not isinstance(state, dict):
        flags.append("MARKET_STATE_MISSING")
        state = {}
    supply = _decimal(_field(state, "total_supply_assets", "totalSupplyAssets"))
    borrow = _decimal(_field(state, "total_borrow_assets", "totalBorrowAssets"))
    utilization = None
    available = None
    if supply is None or borrow is None:
        flags.append("SUPPLY_OR_BORROW_STATE_MISSING")
    elif supply <= 0:
        flags.append("NON_POSITIVE_TOTAL_SUPPLY")
    else:
        utilization = borrow / supply
        available = supply - borrow
        if borrow > supply:
            flags.append("BORROW_EXCEEDS_SUPPLY")

    oracle_address = _address(_field(market, "oracle_address", "oracleAddress"))
    oracle_state = None
    if oracle_address:
        oracle_selector = f"{CHAIN_ID}:{oracle_address}"
        oracle_url = f"{API_BASE}/v0/oracles/{oracle_selector}/state"
        try:
            payload, status = fetch_json(oracle_url)
            oracle_state = _data(payload)
            request_log.append(
                {"name": "oracle_state", "url": oracle_url, "http_status": status, "sha256": _sha256(payload)}
            )
            if status == 206:
                errors.append({"name": "oracle_state", "kind": "PARTIAL_CONTENT_206"})
        except ProviderHTTPError as exc:
            request_log.append({"name": "oracle_state", "url": oracle_url, "http_status": exc.status})
            errors.append({"name": "oracle_state", "kind": "HTTP_ERROR", "status": exc.status, "retry_after": exc.retry_after})
            rate_limited = rate_limited or exc.status == 429
        except Exception as exc:
            request_log.append({"name": "oracle_state", "url": oracle_url, "http_status": None})
            errors.append({"name": "oracle_state", "kind": "PROVIDER_ERROR", "message": str(exc)[:500]})
    else:
        flags.append("ORACLE_ADDRESS_MISSING")

    if isinstance(oracle_state, dict):
        oracle_updated = _iso_utc(_field(oracle_state, "last_updated_at", "lastUpdatedAt"))
        if oracle_updated is None:
            flags.append("ORACLE_UPDATE_TIMESTAMP_MISSING")
        elif (captured - oracle_updated).total_seconds() > 86400:
            flags.append("ORACLE_STALE_OVER_24H")

    for price_key in ("cbxrp_price", "usdc_price"):
        price_payload = _data(raw.get(price_key))
        price_value = _field(price_payload, "price") if isinstance(price_payload, dict) else None
        if price_value is None:
            flags.append(f"{price_key.upper()}_UNAVAILABLE")

    normalized = {
        "chain_id": CHAIN_ID,
        "market_id": MARKET_ID,
        "loan_token_address": loan_address,
        "collateral_token_address": collateral_address,
        "oracle_address": oracle_address,
        "lltv_wad": str(lltv_raw) if lltv_raw is not None else None,
        "lltv_fraction": str(lltv_fraction) if lltv_fraction is not None else None,
        "total_supply_assets_raw": str(supply) if supply is not None else None,
        "total_borrow_assets_raw": str(borrow) if borrow is not None else None,
        "available_liquidity_assets_raw": str(available) if available is not None else None,
        "utilization_from_raw_assets": str(utilization) if utilization is not None else None,
        "market_liquidity": _data(raw.get("market_liquidity")),
        "oracle_state": oracle_state,
        "cbxrp_price": _data(raw.get("cbxrp_price")),
        "usdc_price": _data(raw.get("usdc_price")),
    }
    status = "COMPLETE" if not errors and not flags else "PARTIAL"
    if rate_limited:
        status = "PARTIAL_RATE_LIMITED"
    return {
        "schema_version": "1.0",
        "record_type": "morpho_cbxrp_market_snapshot",
        "captured_at_utc": captured.isoformat().replace("+00:00", "Z"),
        "data_cutoff_utc": captured.isoformat().replace("+00:00", "Z"),
        "provider": "Morpho public REST API",
        "provider_base_url": API_BASE,
        "provider_rate_limit_policy": "No retry on 429; record Retry-After and defer next scheduled poll.",
        "market_selector": f"{CHAIN_ID}:{MARKET_ID}",
        "lookback": LOOKBACK,
        "status": status,
        "market_features_admitted": False,
        "data_quality_flags": sorted(set(flags)),
        "request_log": request_log,
        "errors": errors,
        "normalized_market": normalized,
        "raw_responses": raw,
        "limitations": [
            "REST does not enumerate every position in a Morpho Blue market.",
            "REST does not provide Morpho Blue liquidation event history; use Base logs/contracts.",
            "REST does not provide USD-denominated market state history or oracle feed composition.",
            "The market UI utilization and oracle value-secured fields are not used as normalized inputs.",
            "Coinbase-originated share of this permissionless market is unknown."
        ],
        "response_sha256": _sha256(raw),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="artifacts/morpho-cbxrp-snapshot.json")
    args = parser.parse_args()
    snapshot = collect_snapshot()
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": snapshot["status"],
        "captured_at_utc": snapshot["captured_at_utc"],
        "request_count": len(snapshot["request_log"]),
        "error_count": len(snapshot["errors"]),
        "data_quality_flags": snapshot["data_quality_flags"],
        "market_features_admitted": False,
        "output": str(output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
