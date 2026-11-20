from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261108T035906Z-bny-sbi-kamilah-and-spot-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exchange_response_receipts_match_exact_surfaced_json():
    artifact = load_artifact()
    sources = {item["source_id"]: item for item in artifact["source_registry"]}
    for source_id in (
        "kraken_xrp_usd_ticker_20261108T035906Z",
        "okx_xrp_usdt_ticker_20261108T035906Z",
    ):
        source = sources[source_id]
        body = source["raw_response"]
        assert hashlib.sha256(body.encode("utf-8")).hexdigest() == source["raw_response_sha256"]
        assert len(body.encode("utf-8")) == source["raw_response_utf8_bytes"]


def test_stale_or_missing_exchange_event_time_blocks_model_admission():
    artifact = load_artifact()
    sources = {item["source_id"]: item for item in artifact["source_registry"]}
    assert sources["kraken_xrp_usd_ticker_20261108T035906Z"]["provider_event_time_utc"] is None
    assert sources["okx_xrp_usdt_ticker_20261108T035906Z"]["age_at_artifact_assembly_seconds"] > 300
    assert artifact["data_quality"]["model_eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"


def test_conflicting_level_one_imbalance_is_not_a_directional_signal():
    artifact = load_artifact()
    market = artifact["market_snapshot"]
    assert market["kraken"]["level1_bid_share"] < 0.30
    assert market["okx"]["level1_bid_share"] > 0.80
    assert artifact["cross_venue_comparison"]["comparable"] is False
    assert artifact["data_quality"]["multi_level_order_book_captured"] is False
    assert artifact["data_quality"]["trade_tape_captured"] is False


def test_bny_custody_is_separated_from_future_plans_and_actual_balances():
    bny = load_artifact()["institutional_findings"]["bny_ripple"]
    assert "supports XRP and RLUSD custody" in bny["current_capability"]
    assert bny["actual_xrp_holdings_disclosed"] is False
    assert bny["xrp_purchases_established"] is False
    assert bny["production_trade_finance_established"] is False
    assert len(bny["future_plans"]) == 3


def test_sbi_blackrock_mou_does_not_claim_xrp_settlement():
    sbi = load_artifact()["institutional_findings"]["sbi_startale_blackrock"]
    assert sbi["status"] == "MOU_EXPLORATORY"
    assert sbi["production_xrp_settlement"] is False
    assert sbi["xrp_bridge_asset_named"] is False


def test_glasp_video_attributions_remain_candidates_not_personal_channel_uploads():
    findings = load_artifact()["exact_phrase_findings"]["kamilah_stevenson"]
    assert findings["new_public_video_attributions"] == 2
    assert findings["personal_channel_uploads_verified"] == 0
    assert findings["canonical_channel_id_verified"] is False
    sources = [s for s in load_artifact()["source_registry"] if s["source_id"].startswith("glasp_kamilah_")]
    assert len(sources) == 2
    assert all(
        s["source_type"] in {
            "secondary_video_index_and_summary",
            "secondary_video_index_and_transcript_excerpt",
        }
        for s in sources
    )


def test_exact_phrase_entity_boundaries_are_preserved():
    findings = load_artifact()["exact_phrase_findings"]
    assert findings["ask_coin"]["new_primary_match"] is False
    assert findings["actual_capital"]["issuer_defined_metric_found"] is False
    assert findings["sbic_chatgpt"]["exact_phrase_entity_found"] is False
    assert load_artifact()["forecast"]["status"] == "NOT_ISSUED"
