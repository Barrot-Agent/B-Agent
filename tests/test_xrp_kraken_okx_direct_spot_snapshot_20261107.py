from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T231833Z-xrp-kraken-okx-direct-spot-snapshot.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_and_okx_quotes_preserve_exact_body_receipts() -> None:
    data = _artifact()
    kraken = next(source for source in data["sources"] if source["source_id"] == "kraken_xrp_usd_ticker")
    okx = next(source for source in data["sources"] if source["source_id"] == "okx_xrp_usdt_ticker")

    assert hashlib.sha256(kraken["exact_body_text"].encode("utf-8")).hexdigest() == kraken["body_text_sha256"]
    assert hashlib.sha256(okx["exact_body_text"].encode("utf-8")).hexdigest() == okx["body_text_sha256"]
    assert kraken["parsed_values"]["last_usd"] == 1.15877
    assert okx["parsed_values"]["last_usdt"] == 1.1606


def test_quote_freshness_and_currency_basis_fail_closed() -> None:
    data = _artifact()
    kraken = next(source for source in data["sources"] if source["source_id"] == "kraken_xrp_usd_ticker")
    okx = next(source for source in data["sources"] if source["source_id"] == "okx_xrp_usdt_ticker")

    assert kraken["provider_event_timestamp"] is None
    assert kraken["freshness_status"] == "UNVERIFIABLE_NO_PROVIDER_EVENT_TIMESTAMP"
    assert okx["age_at_capture_seconds"] == 1271.329
    assert okx["freshness_status"] == "STALE"
    assert data["cross_venue_comparison"]["comparison_status"] == "NOT_AN_ARBITRAGE_SIGNAL"
    assert data["feature_admission"]["model_feature_eligible"] is False


def test_level_one_spread_is_not_mislabeled_as_full_depth() -> None:
    data = _artifact()
    assert data["order_book_depth"]["full_depth_captured"] is False
    assert data["order_book_depth"]["level_one_only"] is True
    assert "not full order-book depth" in data["order_book_depth"]["interpretation"]
    assert data["sources"][2]["capture_status"] == "HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS"


def test_spot_snapshot_never_issues_forecasts_or_trades() -> None:
    data = _artifact()
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["no_paper_trade"] is True
    assert data["no_real_money_action"] is True
