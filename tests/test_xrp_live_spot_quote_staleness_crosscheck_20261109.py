from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261109T062905Z-live-spot-quote-staleness-crosscheck.json"


def test_live_spot_quote_staleness_receipts_and_model_exclusion():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "20261109T062905Z-live-spot-quote-staleness-crosscheck"
    assert data["capture_policy"]["lawful_public_sources_only"] is True
    assert data["spot"]["kraken_xrpusd"]["provider_event_time_utc"] is None
    assert hashlib.sha256(data["spot"]["kraken_xrpusd"]["raw_response_text"].encode()).hexdigest() == data["spot"]["kraken_xrpusd"]["raw_response_sha256"]
    assert data["spot"]["okx_xrpusdt"]["provider_event_time_utc"] == "2026-11-09T06:14:09.665Z"
    assert data["spot"]["okx_xrpusdt"]["age_seconds_at_capture"] > 300
    assert hashlib.sha256(data["spot"]["okx_xrpusdt"]["raw_response_text"].encode()).hexdigest() == data["spot"]["okx_xrpusdt"]["raw_response_sha256"]
    assert data["spot"]["kraken_xrpusd"]["quality"]["model_eligible"] is False
    assert data["spot"]["okx_xrpusdt"]["quality"]["model_eligible"] is False
    assert data["evidence_assessment"]["model_admission"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
