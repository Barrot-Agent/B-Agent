from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

SOURCE_ID = "xrpldashboard_rlusd_cross_chain_supply"
EXPECTED_SOURCE_URI = "https://xrpldashboard.com/rlusd"
NORMALIZER_VERSION = "0.1.0"
DEFAULT_MAX_CACHE_AGE_SECONDS = 300
METHODOLOGY_MARKERS = ("totalSupply()", "gateway_balances")


class RlusdResearchIntegrityError(RuntimeError):
    """Raised when an immutable raw receipt or its payload fails integrity validation."""


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _extract_js_object(html: str) -> dict[str, Any]:
    marker_index = html.find("window.__RLUSD_INITIAL__")
    if marker_index < 0:
        raise ValueError("missing window.__RLUSD_INITIAL__")
    start = html.find("{", marker_index)
    if start < 0:
        raise ValueError("missing RLUSD initial object")

    depth = 0
    in_string = False
    escaped = False
    quote = ""
    end = -1
    for index in range(start, len(html)):
        char = html[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                in_string = False
            continue
        if char in ('"', "'"):
            in_string = True
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end < 0:
        raise ValueError("unterminated RLUSD initial object")

    block = html[start:end]
    # The observed server-rendered object uses unquoted top-level keys on
    # separate lines and JSON-compatible values. Never execute JavaScript.
    normalized = re.sub(
        r"(?m)^(\s*)([A-Za-z_$][A-Za-z0-9_$]*)\s*:",
        r'\1"\2":',
        block,
    )
    normalized = re.sub(r",\s*([}\]])", r"\1", normalized)
    parsed = json.loads(normalized)
    if not isinstance(parsed, dict):
        raise ValueError("RLUSD initial payload is not an object")
    return parsed


def _decimal(payload: dict[str, Any], key: str, *, allow_negative: bool = False) -> Decimal:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{key} must be numeric")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{key} is not a valid decimal") from exc
    if not number.is_finite():
        raise ValueError(f"{key} must be finite")
    if not allow_negative and number < 0:
        raise ValueError(f"{key} must be non-negative")
    return number


def _blocked(
    status: str,
    reason: str,
    *,
    receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = receipt or {}
    return {
        "schema_version": 1,
        "artifact_type": "rlusd_cross_chain_research_snapshot",
        "normalizer_version": NORMALIZER_VERSION,
        "status": status,
        "reason": reason,
        "source_id": SOURCE_ID,
        "source_uri": source.get("source_uri"),
        "captured_at_utc": source.get("captured_at_utc"),
        "raw_content_sha256": source.get("raw_content_sha256"),
        "model_eligible": False,
        "feature_store_admitted": False,
        "observations": [],
    }


def build_research_snapshot(
    input_dir: Path,
    *,
    max_cache_age_seconds: int = DEFAULT_MAX_CACHE_AGE_SECONDS,
) -> dict[str, Any]:
    """Build a research-only snapshot from a captured, hash-verified raw receipt.

    This deliberately does not create feature-store records or model inputs. The
    dashboard is a secondary source and its two-chain scope is incomplete.
    """
    if max_cache_age_seconds < 0:
        raise ValueError("max_cache_age_seconds must be non-negative")
    root = input_dir.resolve()
    receipts_path = root / "raw" / "receipts.jsonl"
    if not receipts_path.is_file():
        return _blocked("BLOCKED_MISSING_RECEIPTS", "raw/receipts.jsonl is absent")

    receipts: list[dict[str, Any]] = []
    try:
        receipt_lines = receipts_path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(receipt_lines, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise RlusdResearchIntegrityError(
                    f"receipt line {line_number} is not an object"
                )
            if item.get("source_id") == SOURCE_ID:
                receipts.append(item)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RlusdResearchIntegrityError("raw receipt log is malformed") from exc

    if not receipts:
        return _blocked("BLOCKED_MISSING_RECEIPT", "no RLUSD dashboard receipt in this run")
    if len(receipts) != 1:
        return _blocked("BLOCKED_AMBIGUOUS_RECEIPT", "expected exactly one RLUSD dashboard receipt")
    receipt = receipts[0]

    if receipt.get("source_uri") != EXPECTED_SOURCE_URI:
        return _blocked(
            "BLOCKED_SOURCE_URI_MISMATCH",
            "receipt URI does not match the approved dashboard",
            receipt=receipt,
        )
    if receipt.get("raw_bytes_retained") is not True:
        return _blocked(
            "BLOCKED_RAW_BYTES_NOT_RETAINED", "raw payload was not retained", receipt=receipt
        )

    relative_payload_path = receipt.get("raw_payload_path")
    if not isinstance(relative_payload_path, str) or not relative_payload_path:
        return _blocked(
            "BLOCKED_MISSING_RAW_PATH", "receipt has no raw_payload_path", receipt=receipt
        )
    payload_path = (root / relative_payload_path).resolve()
    try:
        payload_path.relative_to(root)
    except ValueError as exc:
        raise RlusdResearchIntegrityError(
            "raw payload path escapes the artifact directory"
        ) from exc
    if not payload_path.is_file():
        return _blocked(
            "BLOCKED_MISSING_RAW_PAYLOAD", "receipt payload file is absent", receipt=receipt
        )

    raw_bytes = payload_path.read_bytes()
    observed_hash = hashlib.sha256(raw_bytes).hexdigest()
    expected_hash = receipt.get("raw_content_sha256")
    if not isinstance(expected_hash, str) or observed_hash != expected_hash:
        raise RlusdResearchIntegrityError("raw payload SHA-256 does not match its receipt")

    captured_at_value = receipt.get("captured_at_utc")
    if not isinstance(captured_at_value, str):
        return _blocked(
            "BLOCKED_MISSING_CAPTURE_TIME", "receipt capture time is absent", receipt=receipt
        )

    try:
        captured_at = _parse_utc(captured_at_value)
        html = raw_bytes.decode("utf-8")
        methodology_present = all(marker in html for marker in METHODOLOGY_MARKERS)
        if not methodology_present:
            raise ValueError("dashboard methodology markers changed or are absent")
        payload = _extract_js_object(html)
        cached_at_value = payload.get("cachedAt")
        if isinstance(cached_at_value, bool) or not isinstance(cached_at_value, (int, float)):
            raise ValueError("cachedAt must be a Unix timestamp in seconds")
        cached_at = datetime.fromtimestamp(float(cached_at_value), tz=timezone.utc)
        fresh = payload.get("fresh")
        if not isinstance(fresh, bool):
            raise ValueError("fresh must be boolean")
        eth_supply = _decimal(payload, "ethSupply")
        xrpl_supply = _decimal(payload, "xrplSupply")
        eth_mints_24h = _decimal(payload, "ethMints24h")
        eth_burns_24h = _decimal(payload, "ethBurns24h")
        xrpl_net_24h = _decimal(payload, "xrplNet24h", allow_negative=True)
        events = payload.get("events")
        if not isinstance(events, list):
            raise ValueError("events must be a list")
        event_timestamps: list[int] = []
        event_chains: Counter[str] = Counter()
        event_types: Counter[str] = Counter()
        for event in events:
            if not isinstance(event, dict):
                raise ValueError("event sample contains a non-object")
            timestamp = event.get("ts")
            chain = event.get("chain")
            event_type = event.get("type")
            if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
                raise ValueError("event sample timestamp is not numeric")
            if not isinstance(chain, str) or not isinstance(event_type, str):
                raise ValueError("event sample chain/type is not a string")
            event_timestamps.append(int(timestamp))
            event_chains[chain] += 1
            event_types[event_type] += 1
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError, OSError, OverflowError) as exc:
        return _blocked("BLOCKED_SCHEMA_CHANGE", str(exc), receipt=receipt)

    cache_age = (captured_at - cached_at).total_seconds()
    if cache_age < 0:
        status = "BLOCKED_FUTURE_CACHE_TIME"
        reason = "dashboard cache timestamp is after receipt capture"
    elif not fresh or cache_age > max_cache_age_seconds:
        status = "BLOCKED_STALE"
        reason = "dashboard fresh flag is false or cache age exceeds the configured limit"
    else:
        status = "RESEARCH_ONLY_FRESH"
        reason = "fresh, hash-verified secondary snapshot; not independently validated on-chain"

    if event_timestamps and max(event_timestamps) > int(cached_at.timestamp()) + 30:
        status = "BLOCKED_EVENT_TIME_MISMATCH"
        reason = "sampled event timestamp is materially after dashboard cache time"

    covered_total = eth_supply + xrpl_supply
    if covered_total <= 0:
        return _blocked(
            "BLOCKED_INVALID_SUPPLY_TOTAL",
            "covered-chain supply total is not positive",
            receipt=receipt,
        )

    http_date = receipt.get("source_http_date")
    headers = receipt.get("source_http_headers")
    headers = headers if isinstance(headers, dict) else {}
    age_header = headers.get("age")
    try:
        http_cache_age_seconds = int(age_header) if age_header is not None else None
    except (TypeError, ValueError):
        http_cache_age_seconds = None

    latest_event_at = None
    if event_timestamps:
        latest_event_at = (
            datetime.fromtimestamp(max(event_timestamps), tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    observation = {
        "source_id": SOURCE_ID,
        "source_uri": EXPECTED_SOURCE_URI,
        "source_type": "secondary_onchain_dashboard",
        "source_independence_group": "xrpldashboard.com",
        "receipt_id": receipt.get("receipt_id"),
        "raw_content_sha256": observed_hash,
        "captured_at_utc": captured_at.isoformat().replace("+00:00", "Z"),
        "receipt_source_data_as_of_utc": receipt.get("source_data_as_of_utc"),
        "derived_source_data_as_of_utc": cached_at.isoformat().replace("+00:00", "Z"),
        "source_timestamp_method": "window.__RLUSD_INITIAL__.cachedAt (dashboard cache timestamp)",
        "source_http_date": http_date,
        "http_cache_age_header_seconds": http_cache_age_seconds,
        "cache_age_seconds": round(cache_age, 3),
        "fresh_flag": fresh,
        "chain_scope": ["Ethereum", "XRPL"],
        "scope_note": (
            "Covered-chain total only; this page snapshot exposes Ethereum and XRPL, "
            "not all RLUSD chains."
        ),
        "source_methodology_claim": (
            "Page states Ethereum supply is read from totalSupply() and XRPL supply from "
            "gateway_balances; not independently re-queried in this normalizer."
        ),
        "source_reported_values": {
            "ethereum_supply_usd": float(eth_supply),
            "xrpl_supply_usd": float(xrpl_supply),
            "ethereum_mints_24h_usd_reported": float(eth_mints_24h),
            "ethereum_burns_24h_usd_reported": float(eth_burns_24h),
            "xrpl_net_24h_usd_reported": float(xrpl_net_24h),
        },
        "derived_values": {
            "covered_chain_supply_total_usd": float(covered_total),
            "ethereum_share_of_covered_chains": float(eth_supply / covered_total),
            "xrpl_share_of_covered_chains": float(xrpl_supply / covered_total),
        },
        "event_sample": {
            "sample_count": len(events),
            "latest_sample_event_at_utc": latest_event_at,
            "sampled_chain_counts": dict(sorted(event_chains.items())),
            "sampled_type_counts": dict(sorted(event_types.items())),
            "aggregation_warning": (
                "The event array is a sample; do not sum it as gross volume or net capital flow."
            ),
        },
        "quality_gates": {
            "raw_hash_verified": True,
            "dashboard_methodology_markers_present": methodology_present,
            "dashboard_fresh_flag": fresh,
            "cache_age_within_limit": 0 <= cache_age <= max_cache_age_seconds,
            "source_timestamp_derived": True,
            "independent_direct_onchain_crosscheck": False,
            "feature_store_admitted": False,
            "model_eligible": False,
        },
        "status": status,
        "reason": reason,
        "model_eligible": False,
        "feature_store_admitted": False,
        "limitations": [
            "Secondary dashboard; the claimed RPC methods were not independently executed here.",
            "Only Ethereum and XRPL balances are exposed; do not call this global RLUSD supply.",
            "The event array is a recent sample, not a complete transfer ledger.",
            (
                "Provider-reported 24-hour flow fields are not independently reconciled "
                "to mint/burn events."
            ),
            (
                "Stablecoin supply or transfers do not imply equivalent XRP spot demand "
                "or net capital inflow."
            ),
        ],
    }
    return {
        "schema_version": 1,
        "artifact_type": "rlusd_cross_chain_research_snapshot",
        "normalizer_version": NORMALIZER_VERSION,
        "status": status,
        "model_eligible": False,
        "feature_store_admitted": False,
        "observations": [observation],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize captured RLUSD cross-chain dashboard data as research-only evidence."
    )
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-cache-age-seconds", type=int, default=DEFAULT_MAX_CACHE_AGE_SECONDS)
    args = parser.parse_args()
    try:
        result = build_research_snapshot(
            args.input_dir, max_cache_age_seconds=args.max_cache_age_seconds
        )
    except RlusdResearchIntegrityError as exc:
        parser.exit(2, f"integrity failure: {exc}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    args.output.write_text(rendered, encoding="utf-8")
    summary = {"status": result["status"], "model_eligible": False, "output": str(args.output)}
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
