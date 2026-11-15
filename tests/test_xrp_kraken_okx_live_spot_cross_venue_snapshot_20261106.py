from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T210520Z-xrp-kraken-okx-live-spot-cross-venue-snapshot.json"
)


def test_kraken_and_okx_raw_spot_receipts_are_content_addressed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["asset"] == "XRP"
    assert artifact["captured_at_utc"] == "2026-11-06T21:05:20Z"
    assert len(artifact["observations"]) == 2

    for observation in artifact["observations"]:
        raw = observation["raw_response_text"]
        encoded = raw.encode("utf-8")
        assert len(encoded) == observation["raw_response_bytes"]
        assert hashlib.sha256(encoded).hexdigest() == observation["raw_response_sha256"]
        assert observation["raw_response_hash_scope"].startswith(
            "SHA-256 of the exact JSON response text"
        )
        assert json.loads(raw)


def test_spot_snapshot_preserves_venue_specific_quote_and_timestamp_semantics():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    by_venue = {item["venue"]: item for item in artifact["observations"]}

    kraken = by_venue["Kraken"]
    assert kraken["instrument"] == "XRP/USD"
    assert kraken["source_data_as_of_utc"] is None
    assert kraken["parsed"]["last_usd"] == 1.17255
    assert kraken["parsed"]["volume_rolling_24h_xrp"] == 35852127.22413252

    okx = by_venue["OKX"]
    assert okx["instrument"] == "XRP-USDT"
    assert okx["source_data_as_of_utc"] == "2026-11-06T21:05:06.565Z"
    assert okx["parsed"]["last_usdt"] == 1.1756
    assert okx["parsed"]["volume_rolling_24h_xrp"] == 64668838.286536


def test_cross_venue_snapshot_does_not_claim_consolidated_depth_or_forecast():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["comparison"]["quote_currency_warning"].startswith(
        "Kraken is XRP/USD; OKX is XRP/USDT."
    )
    assert artifact["model_eligibility"] == "raw_snapshot_only_not_yet_admitted_as_a_model_feature"
    assert artifact["forecast_issued"] is False
    assert artifact["directional_forecast_eligible"] is False
    assert artifact["paper_trade_or_real_money_action"] is False
    assert any("not full order-book depth" in item for item in artifact["interpretation"])
