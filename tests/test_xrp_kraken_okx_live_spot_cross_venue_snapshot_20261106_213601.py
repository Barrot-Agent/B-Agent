from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T213601Z-xrp-kraken-okx-live-spot-cross-venue-snapshot.json"
)


def test_kraken_okx_snapshot_raw_receipts_are_content_addressed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["captured_at_utc"] == "2026-11-06T21:36:01Z"
    assert len(artifact["observations"]) == 2
    for observation in artifact["observations"]:
        raw = observation["raw_response_text"]
        encoded = raw.encode("utf-8")
        assert len(encoded) == observation["raw_response_bytes"]
        assert hashlib.sha256(encoded).hexdigest() == observation["raw_response_sha256"]
        assert json.loads(raw)
        assert observation["raw_response_hash_scope"].startswith(
            "SHA-256 of the exact JSON response text"
        )


def test_venue_quote_units_and_source_timestamp_quality_remain_separate():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    by_venue = {item["venue"]: item for item in artifact["observations"]}

    kraken = by_venue["Kraken"]
    assert kraken["instrument"] == "XRP/USD"
    assert kraken["source_data_as_of_utc"] is None
    assert kraken["parsed"]["last_usd"] == 1.17843
    assert kraken["parsed"]["volume_rolling_24h_xrp"] == 35343941.94300453

    okx = by_venue["OKX"]
    assert okx["instrument"] == "XRP-USDT"
    assert okx["source_data_as_of_utc"] == "2026-11-06T21:35:28.571Z"
    assert okx["parsed"]["last_usdt"] == 1.1741
    assert okx["parsed"]["volume_rolling_24h_xrp"] == 62911605.626857

    capture = datetime.fromisoformat(artifact["captured_at_utc"].replace("Z", "+00:00"))
    provider = datetime.fromisoformat(okx["source_data_as_of_utc"].replace("Z", "+00:00"))
    assert (capture - provider).total_seconds() == 32.429
    assert artifact["comparison"]["okx_provider_timestamp_age_seconds"] == 32.429


def test_cross_venue_snapshot_does_not_claim_executable_spread_or_forecast():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["comparison"]["okx_last_vs_kraken_last_pct"] == -0.3674
    assert artifact["comparison"]["quote_currency_warning"].startswith(
        "Kraken is XRP/USD; OKX is XRP/USDT."
    )
    assert artifact["model_eligibility"] == "raw_snapshot_only_not_yet_admitted_as_a_model_feature"
    assert artifact["forecast_issued"] is False
    assert artifact["directional_forecast_eligible"] is False
    assert artifact["paper_trade_or_real_money_action"] is False
    assert any("not full order-book depth" in item for item in artifact["interpretation"])
