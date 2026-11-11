from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest

from barrot_agent.evolution.xrp_public_ingestion import _parse_kraken_ticker


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261109T132446Z-market-repeat-and-kraken-utc-day-open-correction.json"
)
PRIOR_ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261109T062905Z-live-spot-quote-staleness-crosscheck.json"
)


def test_repeat_capture_and_kraken_utc_day_open_correction_are_explicit():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    kraken = data["spot"]["kraken_xrpusd"]
    okx = data["spot"]["okx_xrpusdt"]
    prior = json.loads(PRIOR_ARTIFACT.read_text(encoding="utf-8"))

    assert data["artifact_id"] == "20261109T132446Z-market-repeat-and-kraken-utc-day-open-correction"
    assert data["capture_policy"]["lawful_public_sources_only"] is True
    assert data["repeat_capture"]["interval_seconds"] == 279
    assert data["repeat_capture"]["kraken_identical_payload"] is True
    assert data["repeat_capture"]["okx_identical_payload"] is True
    assert data["repeat_capture"]["cache_assessment"] == "UNRESOLVED_IDENTICAL_RENDERED_PAYLOAD"
    assert hashlib.sha256(kraken["raw_response_text"].encode()).hexdigest() == kraken["raw_response_sha256"]
    assert hashlib.sha256(okx["raw_response_text"].encode()).hexdigest() == okx["raw_response_sha256"]

    assert kraken["observations"]["utc_day_open_usd"] == pytest.approx(1.11203)
    assert kraken["observations"]["open_24h_usd"] is None
    assert kraken["observations"]["open_24h_status"] == "NOT_RETURNED_BY_ENDPOINT"
    assert kraken["observations"]["last_vs_utc_day_open_pct"] == pytest.approx(-1.433414566)
    assert kraken["quality"]["model_eligible"] is False

    assert prior["spot"]["kraken_xrpusd"]["observations"]["open_24h_usd"] == pytest.approx(1.11203)
    assert "spot.kraken_xrpusd.observations.open_24h_usd" in data["correction"]["invalidated_legacy_fields"]
    assert data["correction"]["prior_artifact_preserved_unchanged"] is True

    assert okx["age_seconds_at_capture"] == pytest.approx(1010.428)
    assert okx["quality"]["model_eligible"] is False
    assert data["secondary_market_structure"]["age_seconds_at_capture"] == 946
    assert data["secondary_market_structure"]["market_type"] == "XRP perpetual futures"
    assert data["secondary_market_structure"]["quality"]["model_eligible"] is False
    assert data["evidence_assessment"]["model_admission"] is False
    assert data["forecast_status"] == "NOT_ISSUED"


def test_kraken_adapter_emits_o_as_utc_day_open_not_24h_open():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    source = data["spot"]["kraken_xrpusd"]
    payload = json.loads(source["raw_response_text"])
    captured = datetime.fromisoformat(data["captured_at_utc"].replace("Z", "+00:00"))

    records, event_time, eligible, reason = _parse_kraken_ticker(
        payload,
        source_id="kraken_spot_ticker",
        url=source["endpoint"],
        digest=source["raw_response_sha256"],
        captured=captured,
        # Synthetic HTTP Date for deterministic parser testing only.
        http_date="Mon, 09 Nov 2026 13:24:46 GMT",
    )
    by_id = {record["feature_id"]: record for record in records}

    utc_day_open = by_id["xrp.spot.kraken.utc_day_open"]
    assert utc_day_open["value"] == pytest.approx(1.11203)
    assert utc_day_open["aggregation_window"] == "utc_day"
    assert by_id["xrp.spot.kraken.vwap_24h"]["value"] == pytest.approx(1.11442417)
    assert by_id["xrp.spot.kraken.base_volume_24h"]["value"] == pytest.approx(43096646.23133267)
    assert not any(record["feature_id"] == "xrp.spot.kraken.open_24h" for record in records)
    assert eligible is True
    assert reason == ""
    assert event_time.startswith("2026-11-09T13:24:46")
