#!/usr/bin/env python3
"""Ingest a live market snapshot through the guard.

    python3 scripts/ingest_live.py                 # CoinGecko markets + global
    python3 scripts/ingest_live.py --dry-run       # print what it would write

Writes `market/live-<timestamp>.json` with provenance `RECORDED_FEED`, which is
the provenance the confidence gate will accept. Two GETs, both unauthenticated,
both through `network_guard.guarded_get`.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from barrot_agent.network_guard import guarded_get  # noqa: E402

IDS = {
    "ripple": "XRP",
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "stellar": "XLM",
    "tether": "USDT",
}
MARKETS_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&ids=" + ",".join(IDS)
    + "&order=market_cap_desc&price_change_percentage=24h,7d,30d"
)
GLOBAL_URL = "https://api.coingecko.com/api/v3/global"


def fetch_json(url: str, purpose: str) -> tuple[dict | None, str]:
    result = guarded_get(url, purpose=purpose)
    if not result["ok"]:
        return None, result["reason"] or f"HTTP {result['status']}"
    try:
        return json.loads(result["body"]), "ok"
    except json.JSONDecodeError:
        return None, "response was not JSON"


def build_snapshot(markets: list, global_data: dict, captured_at: str) -> dict:
    prices, change, caps, volumes = {}, {}, {}, {}
    for row in markets:
        asset = IDS.get(row["id"])
        if not asset:
            continue
        prices[asset] = float(row["current_price"])
        caps[asset] = float(row.get("market_cap") or 0.0)
        volumes[asset] = float(row.get("total_volume") or 0.0)
        change[asset] = {
            "24h": _num(row.get("price_change_percentage_24h_in_currency")),
            "7d": _num(row.get("price_change_percentage_7d_in_currency")),
            "30d": _num(row.get("price_change_percentage_30d_in_currency")),
        }

    dominance = (global_data or {}).get("data", {}).get("market_cap_percentage", {})
    btc_dominance = _num(dominance.get("btc"))
    xrp_price = prices.get("XRP")
    xrp_24h = change.get("XRP", {}).get("24h")
    btc_24h = change.get("BTC", {}).get("24h")
    regime = "UNKNOWN"
    if xrp_24h is not None and btc_24h is not None:
        if btc_24h < 0 and xrp_24h > 0:
            regime = "BEARISH_WITH_XRP_RELATIVE_STRENGTH"
        elif btc_24h < 0:
            regime = "BEARISH"
        elif btc_24h > 0:
            regime = "RISK_ON"

    return {
        "schema_version": "1.0",
        "record_type": "market_snapshot",
        "snapshot_id": "live-" + captured_at.replace(":", "").replace("-", "")[:15],
        "captured_at_utc": captured_at,
        "source": "COINGECKO_PUBLIC_API",
        "provenance": "RECORDED_FEED",
        "verification": {
            "exchange_api_queried": True,
            "provider": "api.coingecko.com",
            "authenticated": False,
            "note": "Public unauthenticated endpoint, read-only, fetched through network_guard.",
        },
        "regime": {
            "label": regime,
            "market_trend": "DOWN" if (btc_24h or 0) < 0 else "UP",
            "btc_dominance_pct": btc_dominance or 0.0,
            "xrp_24h_pct": xrp_24h,
            "btc_24h_pct": btc_24h,
            "xrp_outperforming_24h": (xrp_24h or 0) > (btc_24h or 0),
        },
        "prices_usd": prices,
        "change_pct": change,
        "market_cap_usd": caps,
        "volume_24h_usd": volumes,
        "balances_start": {"xrp": 102.27, "usd_value": round(102.27 * (xrp_price or 0), 2),
                           "btc_equiv": round(102.27 * (xrp_price or 0) / prices.get("BTC", 1), 8)},
        "disabled_assets": [],
    }


def _num(value) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest a live snapshot. Read-only.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    captured_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    markets, why = fetch_json(MARKETS_URL, "coingecko markets")
    if markets is None:
        print(f"markets pull failed: {why}")
        return 2
    time.sleep(2.1)
    global_data, why = fetch_json(GLOBAL_URL, "coingecko global")
    if global_data is None:
        print(f"global pull failed: {why}; continuing with dominance 0")

    snapshot = build_snapshot(markets, global_data or {}, captured_at)
    payload = json.dumps(snapshot, indent=2)
    target = ROOT / "market" / f"live-{captured_at.replace(':', '')}.json"
    if args.dry_run:
        print(payload[:1200])
        return 0
    target.write_text(payload, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)}")
    print(f"  provenance {snapshot['provenance']}  regime {snapshot['regime']['label']}")
    for asset in ("BTC", "ETH", "XRP", "SOL", "XLM", "USDT"):
        print(f"  {asset:<5} ${snapshot['prices_usd'][asset]:<12} "
              f"24h {snapshot['change_pct'][asset]['24h']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
