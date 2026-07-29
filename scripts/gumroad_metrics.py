#!/usr/bin/env python3
"""
BARROT-Ω GUMROAD METRICS — real, aggregate-only product performance data
for Barrot's metacognitive integrity. Deliberately uses GET /v2/products
(view_sales scope), NOT /v2/sales - the products endpoint gives
aggregate counts per Gumroad's own scope description ("sales counts"),
while /sales returns individual purchaser emails and per-transaction
records. This script should never touch or store individual customer
data - only product-level aggregates.

First real run: prints the full raw product JSON for the XRP Signal
Service product so exact field names can be confirmed and locked in,
same discipline as every other new API integration this project has
built - don't assume field names, verify against a real response.
"""

import json
import os
import sys
import urllib.request

PRODUCT_PERMALINK = "opvxi"
OUT_PATH = "ping-pongings/knowledge-base/gumroad_metrics.json"

TOKEN = os.environ.get("GUMROAD_ACCESS_TOKEN", "")


def fetch_products():
    url = f"https://api.gumroad.com/v2/products?access_token={TOKEN}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    if not TOKEN:
        sys.exit("GUMROAD_ACCESS_TOKEN not set")

    data = fetch_products()
    if not data.get("success"):
        sys.exit(f"Gumroad API error: {data.get('message')}")

    products = data.get("products", [])
    target = next((p for p in products if p.get("custom_permalink") == PRODUCT_PERMALINK), None)
    if not target:
        print(f"Product with permalink '{PRODUCT_PERMALINK}' not found. "
              f"Real permalinks available: {[p.get('custom_permalink') for p in products]}")
        target = products[0] if products else {}

    print("=== RAW real product response (verify field names against this) ===")
    print(json.dumps(target, indent=2))
    print("=== end raw response ===\n")

    # Extract only aggregate, non-identifying fields. Field names below
    # are best-guess from Gumroad's own docs (sales_count, price) -
    # confirm against the raw output above and adjust if names differ.
    aggregate = {
        "note": (
            "Aggregate product performance only. Deliberately excludes "
            "individual sales records, purchaser emails, or any "
            "customer-identifying data - uses GET /products (view_sales "
            "scope), not GET /sales."
        ),
        "product_name": target.get("name"),
        "permalink": target.get("custom_permalink"),
        "sales_count": target.get("sales_count"),
        "price_cents": target.get("price"),
        "currency": target.get("currency"),
        "published": target.get("published"),
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2)

    print(f"Written to {OUT_PATH}")
    print(json.dumps(aggregate, indent=2))


if __name__ == "__main__":
    main()
