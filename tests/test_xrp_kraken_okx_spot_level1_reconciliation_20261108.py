from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261108T033950Z-xrp-kraken-okx-spot-level1-reconciliation.json"
)


def test_exact_surfaced_exchange_response_bodies_match_sha256_receipts():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sources = {source["source_id"]: source for source in artifact["source_registry"]}

    assert set(sources) == {"kraken_xrp_usd_ticker", "okx_xrp_usdt_ticker"}
    for source in sources.values():
        body = source["raw_response"]
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]
        assert len(body.encode("utf-8")) == source["raw_response_utf8_bytes"]


def test_provider_freshness_and_ineligible_status_are_preserved():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sources = {source["source_id"]: source for source in artifact["source_registry"]}

    assert sources["kraken_xrp_usd_ticker"]["provider_event_time_utc"] is None
    assert sources["okx_xrp_usdt_ticker"]["provider_event_time_utc"] == "2026-11-08T03:37:17.569Z"
    assert sources["okx_xrp_usdt_ticker"]["age_at_artifact_assembly_seconds"] == 152.431
    assert artifact["data_quality"]["model_eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"


def test_conflicting_level_one_imbalances_do_not_create_directional_signal():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    kraken = artifact["market_snapshot"]["kraken"]
    okx = artifact["market_snapshot"]["okx"]

    assert kraken["top_level_bid_share"] < 0.02
    assert okx["top_level_bid_share"] > 0.80
    assert artifact["cross_venue_comparison"]["comparable"] is False
    assert artifact["data_quality"]["multi_level_order_book_captured"] is False
    assert artifact["data_quality"]["trade_tape_captured"] is False
    assert artifact["data_quality"]["exchange_flow_data_captured"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
