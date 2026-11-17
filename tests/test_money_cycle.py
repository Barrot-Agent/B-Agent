"""Money cycle data must be internally consistent and honest about grades."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[1]


def test_market_scan_has_five_ranked_products_with_fetched_counts():
    payload = json.loads((ROOT / "data" / "money" / "market.json").read_text(encoding="utf-8"))
    products = payload["products"]
    assert len(products) == 5
    assert [p["rank"] for p in products] == [1, 2, 3, 4, 5]
    assert products[0]["score"] >= products[-1]["score"]
    for product in products:
        assert product["competition_repos"] > 0
        assert product["demand"] is None or product["demand"] >= 0
        assert product["demand_source"]
        assert product["status"] in {"Q", "E"}


def test_bounty_scan_admits_zero_verified_payouts():
    payload = json.loads((ROOT / "data" / "money" / "bounties.json").read_text(encoding="utf-8"))
    assert payload["records"] >= 100
    assert sum(payload["grades"].values()) == payload["records"]
    # If a Q ever appears, it must still carry a literal amount and a real repo.
    for record in payload["records_list"]:
        if record["status"] == "Q":
            assert record["amount_usd"], record["url"]
            assert record["repo_stars"] >= 20
            assert record["amount_literal"] in (
                record["title"] + " " + (record.get("body") or "")
            ) or record["amount_source"] in {"title", "body"}


def test_webmcp_quotes_all_matched():
    payload = json.loads((ROOT / "data" / "mcp" / "webmcp_check.json").read_text(encoding="utf-8"))
    assert payload["all_found"] is True
    assert len(payload["quotes"]) == 4
    for item in payload["quotes"]:
        assert item["found"] is True


def test_listing_doc_states_webmcp_is_not_a_marketplace():
    doc = (ROOT / "docs" / "mcp" / "LISTING.md").read_text(encoding="utf-8")
    assert "not a directory, not a marketplace" in doc
    assert "There is no such thing as \"listing a server on\nWebMCP\"" in doc


def test_doi_audit_found_no_retracted_source_in_any_claims_file():
    payload = json.loads((ROOT / "data" / "research" / "doi_audit.json").read_text(encoding="utf-8"))
    claims = (ROOT / "data" / "millennium" / "claims").rglob("*.json")
    claims_dois = set()
    for path in claims:
        text = path.read_text(encoding="utf-8")
        for entry in payload["entries"]:
            if entry["doi"] in text:
                claims_dois.add(entry["doi"])
    retracted = {entry["doi"] for entry in payload["retracted"]}
    assert claims_dois.isdisjoint(retracted)


def test_products_doc_names_the_falsifier_and_the_zero_revenue():
    doc = (ROOT / "docs" / "money" / "PRODUCTS.md").read_text(encoding="utf-8")
    assert "Revenue to date: $0.00" in doc
    assert "no PR was opened against an unverified bounty" in doc
    assert "Price" in doc or "pricing" in doc.lower()
