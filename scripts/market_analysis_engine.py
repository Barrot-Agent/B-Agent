#!/usr/bin/env python3
"""Legacy signal-history review, retained as a fail-closed descriptive-only tool.

This is not the Barrot XRP prediction engine. It cannot issue forecasts or trade
recommendations and is disabled unless a separate explicit local opt-in is set.
The GitHub workflow that previously invoked it is disabled.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen


QUERY = (
    "SELECT date, direction, confidence, accuracy "
    "FROM workspace.barrot.signals ORDER BY date DESC LIMIT 30"
)
ANALYSIS_KEYS = {
    "summary",
    "observations",
    "data_quality",
    "competing_hypotheses",
    "validation_gaps",
    "forecast_status",
    "trade_recommendations",
}


def legacy_market_analysis_enabled() -> bool:
    return os.environ.get("BARROT_ENABLE_LEGACY_MARKET_ANALYSIS", "").strip() == "YES"


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required configuration: {name}")
    return value


def query_databricks(query: str) -> dict:
    """Run one bounded read-only SELECT and return its receipt and rows."""
    normalized = query.strip()
    if not normalized.lower().startswith("select ") or ";" in normalized:
        raise ValueError("Only one read-only SELECT statement is permitted")

    host = _required_env("DATABRICKS_HOST")
    if host.startswith("https://"):
        host = host[len("https://") :]
    if "://" in host or "/" in host or not re.fullmatch(r"[A-Za-z0-9.-]+(?::[0-9]+)?", host):
        raise ValueError("DATABRICKS_HOST must be a hostname without a path")
    token = _required_env("DATABRICKS_TOKEN")
    warehouse_id = _required_env("DATABRICKS_WAREHOUSE_ID")

    request_body = {
        "statement": normalized,
        "warehouse_id": warehouse_id,
        "wait_timeout": "50s",
        "on_wait_timeout": "CANCEL",
        "format": "JSON_ARRAY",
        "disposition": "INLINE",
        "row_limit": 100,
        "byte_limit": 1048576,
    }
    request = Request(
        f"https://{host}/api/2.0/sql/statements",
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            raw_response = response.read()
    except Exception:
        # Do not print provider bodies, URLs with credentials, or raw error text.
        raise RuntimeError("Databricks read failed; provider response suppressed") from None

    try:
        payload = json.loads(raw_response)
    except (TypeError, ValueError):
        raise RuntimeError("Databricks returned invalid JSON") from None

    state = payload.get("status", {}).get("state")
    if state != "SUCCEEDED":
        raise RuntimeError(f"Databricks SQL did not succeed (state={state or 'missing'})")

    manifest = payload.get("manifest", {})
    if manifest.get("truncated"):
        raise RuntimeError("Databricks result was truncated")
    columns = manifest.get("schema", {}).get("columns", [])
    rows = payload.get("result", {}).get("data_array", [])
    names = [column.get("name") for column in columns]
    if not names or any(not isinstance(name, str) or not name for name in names):
        raise RuntimeError("Databricks result has no valid column manifest")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Databricks returned no signal-history rows")

    records = []
    for row in rows:
        if not isinstance(row, list) or len(row) != len(names):
            raise RuntimeError("Databricks row does not match its manifest")
        records.append(dict(zip(names, row)))

    cutoffs = [str(row["date"]) for row in records if row.get("date") is not None]
    return {
        "rows": records,
        "record_count": len(records),
        "data_cutoff_utc": max(cutoffs) if cutoffs else None,
        "raw_response_sha256": hashlib.sha256(raw_response).hexdigest(),
    }


def call_groq(prompt: str) -> str:
    key = _required_env("GROQ_API_KEY")
    body = json.dumps(
        {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a descriptive research analyst. This is legacy signal-history "
                        "data, not a validated predictive model. Do not issue price forecasts, "
                        "buy/sell/hold calls, trade instructions, position sizes, capital "
                        "allocations, price targets, or recommendations. Return strict JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1500,
            "temperature": 0.1,
        }
    ).encode("utf-8")
    request = Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            payload = json.loads(response.read())
    except Exception:
        raise RuntimeError("Groq analysis failed; provider response suppressed") from None
    try:
        return payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Groq response did not contain a message") from None


_PROHIBITED_OUTPUT_PATTERNS = (
    re.compile(r"\\b(?:buy|sell|short|long)\\s+(?:all\\s+)?(?:xrp|bitcoin|btc|ethereum|eth|crypto(?:currency)?|now|here)\\b", re.IGNORECASE),
    re.compile(r"\\b(?:buy|sell|hold)\\s+(?:signal|call|recommendation)\\b", re.IGNORECASE),
    re.compile(r"\\b(?:price\\s+)?target(?:\\s+price)?\\s*(?:is|at|of|:|=)?\\s*\\$?\\s*\\d+(?:\\.\\d+)?\\b", re.IGNORECASE),
    re.compile(r"\\b(?:will(?:\\s+not)?|is\\s+expected\\s+to|are\\s+expected\\s+to|expected\\s+to|is\\s+likely\\s+to|are\\s+likely\\s+to|should)\\s+(?:rise|fall|rally|drop|surge|decline|break|reach|hit|trade|move)\\b", re.IGNORECASE),
    re.compile(r"\\b(?:entry|exit)\\s+(?:price|level)\\s*(?:is|at|of|:|=)?\\s*\\$?\\s*\\d+(?:\\.\\d+)?\\b", re.IGNORECASE),
    re.compile(r"\\b(?:stop[- ]loss|take[- ]profit)\\b", re.IGNORECASE),
)


def _validate_descriptive_text(result: dict) -> None:
    text_fields = ("summary", "observations", "data_quality", "competing_hypotheses", "validation_gaps")
    for field in text_fields:
        values = result[field] if isinstance(result[field], list) else [result[field]]
        for value in values:
            if not isinstance(value, str):
                continue
            if any(pattern.search(value) for pattern in _PROHIBITED_OUTPUT_PATTERNS):
                raise ValueError(
                    f"{field} contains prohibited forecast or trading language"
                )


def validate_analysis_response(text: str) -> dict:
    try:
        result = json.loads(text)
    except (TypeError, ValueError):
        raise ValueError("Analysis response must be strict JSON") from None
    if not isinstance(result, dict) or set(result) != ANALYSIS_KEYS:
        raise ValueError("Analysis response schema mismatch")
    if result.get("forecast_status") != "NOT_ISSUED":
        raise ValueError("Legacy analysis cannot issue a forecast")
    if result.get("trade_recommendations") != []:
        raise ValueError("Legacy analysis cannot issue trade recommendations")
    if not isinstance(result.get("summary"), str) or not result["summary"].strip():
        raise ValueError("Analysis summary must be non-empty text")
    for key in ("observations", "data_quality", "competing_hypotheses", "validation_gaps"):
        values = result.get(key)
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise ValueError(f"{key} must be a list of strings")
    _validate_descriptive_text(result)
    return result


def analyze_market() -> str:
    data = query_databricks(QUERY)
    prompt = (
        "Review these legacy signal-history rows descriptively. Identify observed patterns, "
        "data-quality limitations, competing explanations and validation gaps. Do not infer "
        "predictive performance from self-reported accuracy. The required forecast status is "
        "NOT_ISSUED and trade_recommendations must be an empty array.\n\n"
        f"Rows:\n{json.dumps(data['rows'], indent=2)[:12000]}"
    )
    analysis = validate_analysis_response(call_groq(prompt))
    captured_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    output = {
        "schema_version": 1,
        "artifact_type": "descriptive_legacy_signal_history_review",
        "captured_at_utc": captured_at,
        "data_cutoff_utc": data["data_cutoff_utc"],
        "source": {
            "table": "workspace.barrot.signals",
            "record_count": data["record_count"],
            "raw_response_sha256": data["raw_response_sha256"],
        },
        "analysis": analysis,
        "forecast_status": "NOT_ISSUED",
        "model_eligible": False,
        "trade_recommendations": [],
        "limitations": [
            "This legacy signal table is not a point-in-time XRP feature store.",
            "No leakage-safe walk-forward evaluation or baseline comparison is attached.",
            "Self-reported historical accuracy is not verified out-of-sample performance.",
            "This artifact is descriptive research only and is not a forecast or trading instruction.",
        ],
    }
    filename = f"market_analysis_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as output_file:
        json.dump(output, output_file, indent=2, sort_keys=True)
        output_file.write("\n")
    return filename


def main() -> None:
    if not legacy_market_analysis_enabled():
        raise SystemExit(
            "Legacy market analysis is disabled. Use the verified XRP feature store and "
            "forecast ledger after production ingestion and out-of-sample validation."
        )
    analyze_market()


if __name__ == "__main__":
    main()
