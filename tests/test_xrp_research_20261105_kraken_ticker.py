import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T021146Z-kraken-xrpusd-ticker-receipt.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_tool_text_hash_is_reproducible_but_not_mislabeled_as_http_bytes():
    data = load()
    source = data["source_registry"][0]
    raw = source["raw_response_text"].encode("utf-8")
    assert len(raw) == source["raw_content_bytes"] == 311
    assert hashlib.sha256(raw).hexdigest() == source["raw_content_sha256"]
    assert source["raw_capture_status"] == "tool_returned_text_hashed_not_original_http_byte_stream"
    assert source["source_time_utc"] is None
    assert source["retrieved_at_utc"] is None


def test_kraken_narrow_spread_does_not_hide_shallow_best_bid():
    data = load()
    quote = data["market_observation"]
    assert quote["last_usd"] == 1.30795
    assert quote["spread_basis_points"] == 0.0764558143
    assert quote["best_bid_size_xrp"] == 4
    assert quote["best_ask_size_xrp"] == 661
    assert "not total depth" in quote["interpretation"]
    assert quote["model_eligible"] is False
    assert data["forecast_issued"] is False
