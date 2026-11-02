#!/usr/bin/env python3
"""Fetch aggregate Gumroad product metrics; never read individual sales records."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import sys
import urllib.request

PRODUCT_PERMALINK = "opvxi"
OUT_PATH = "ping-pongings/knowledge-base/gumroad_metrics.json"
TOKEN = os.environ.get("GUMROAD_ACCESS_TOKEN", "")


def fetch_products():
    if not TOKEN:
        raise RuntimeError("GUMROAD_ACCESS_TOKEN is not set")
    url = f"https://api.gumroad.com/v2/products?access_token={TOKEN}"
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def real_permalink(product):
    url = product.get("short_url") or product.get("landing_url") or ""
    return product.get("custom_permalink") or url.rstrip("/").rsplit("/", 1)[-1]


def build_aggregate(data, captured_at_utc):
    if not isinstance(data, dict) or data.get("success") is not True:
        raise ValueError("Gumroad products response did not report success")
    products = data.get("products")
    if not isinstance(products, list):
        raise ValueError("Gumroad products response has no products list")
    target = next(
        (product for product in products if isinstance(product, dict) and real_permalink(product) == PRODUCT_PERMALINK),
        None,
    )
    if target is None:
        raise LookupError(f"Target product {PRODUCT_PERMALINK!r} was not found; refusing to substitute another product")

    sales_count = target.get("sales_count")
    price_cents = target.get("price")
    currency = target.get("currency")
    if isinstance(sales_count, bool) or not isinstance(sales_count, int) or sales_count < 0:
        raise ValueError("Target product sales_count is missing or invalid")
    if isinstance(price_cents, bool) or not isinstance(price_cents, int) or price_cents < 0:
        raise ValueError("Target product price is missing or invalid")
    if not isinstance(currency, str) or not currency.strip():
        raise ValueError("Target product currency is missing or invalid")

    return {
        "schema_version": "2.0",
        "captured_at_utc": captured_at_utc,
        "source_endpoint": "https://api.gumroad.com/v2/products",
        "data_scope": "single-product aggregate fields only; no individual sales or purchaser records",
        "product_name": target.get("name"),
        "permalink": PRODUCT_PERMALINK,
        "sales_count": sales_count,
        "price_cents": price_cents,
        "currency": currency,
        "published": target.get("published") if isinstance(target.get("published"), bool) else None,
    }


def main() -> int:
    if not TOKEN:
        print("GUMROAD_ACCESS_TOKEN is not set", file=sys.stderr)
        return 2
    try:
        data = fetch_products()
        captured_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        aggregate = build_aggregate(data, captured_at)
    except (OSError, ValueError, LookupError, RuntimeError) as exc:
        print(f"Gumroad aggregate metrics not written: {exc}", file=sys.stderr)
        return 2

    output_path = OUT_PATH
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(aggregate, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # Only the allowlisted aggregate is emitted. The raw provider response is never logged.
    print(json.dumps(aggregate, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
