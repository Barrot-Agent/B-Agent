import json
from datetime import datetime, timezone
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T050741Z-kraken-xrpusd-current-retrieval-interval-snapshot.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def parse_utc(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def test_capture_uses_bounded_retrieval_interval_not_fabricated_event_time():
    data = load_artifact()
    capture = data["capture"]
    assert capture["exact_per_source_retrieval_timestamp_utc"] is None
    assert capture["provider_event_timestamp_utc"] is None
    assert capture["raw_http_wire_bytes_captured"] is False
    assert parse_utc(capture["retrieval_interval_start_utc"]) <= parse_utc(
        capture["retrieval_interval_end_utc"]
    )
    assert parse_utc(capture["conservative_data_cutoff_utc"]) == parse_utc(
        capture["retrieval_interval_end_utc"]
    )


def test_rendered_response_hash_is_scoped_and_not_claimed_as_raw_wire_hash():
    data = load_artifact()
    capture = data["capture"]
    assert re.fullmatch(r"[0-9a-f]{64}", capture["rendered_response_text_sha256"])
    assert "not a byte-exact" in capture["hash_scope"]
    source = data["source_registry"][0]
    assert source["rendered_response_text_sha256"] == capture[
        "rendered_response_text_sha256"
    ]
    assert source["raw_http_wire_bytes_captured"] is False
    assert source["exact_retrieval_timestamp_utc"] is None


def test_spot_arithmetic_and_asynchronous_last_trade_are_preserved():
    spot = load_artifact()["spot_market"]
    expected_spread = (
        (spot["best_ask_usd"] - spot["best_bid_usd"])
        / ((spot["best_ask_usd"] + spot["best_bid_usd"]) / 2)
        * 10000
    )
    assert abs(expected_spread - spot["displayed_spread_bps"]) < 1e-10
    assert spot["last_trade_below_best_bid"] if "last_trade_below_best_bid" in spot else (
        spot["last_trade_usd"] < spot["best_bid_usd"]
    )
    assert spot["quote_component_quality"]["last_trade_below_best_bid"] is True
    assert spot["quote_component_quality"]["components_synchronized"] is False
    assert spot["utc_day_open_usd"] == 1.20567
    assert spot["rolling_24h_vwap_usd"] == 1.25270707


def test_derived_comparisons_are_reproducible():
    spot = load_artifact()["spot_market"]
    expected = {
        "last_vs_utc_day_open_percent": (
            spot["last_trade_usd"] / spot["utc_day_open_usd"] - 1
        ) * 100,
        "last_vs_rolling_24h_vwap_percent": (
            spot["last_trade_usd"] / spot["rolling_24h_vwap_usd"] - 1
        ) * 100,
        "last_above_rolling_24h_low_percent": (
            spot["last_trade_usd"] / spot["rolling_24h_low_usd"] - 1
        ) * 100,
    }
    for key, value in expected.items():
        assert abs(value - spot["derived_comparisons"][key]) < 1e-10


def test_snapshot_is_not_admitted_or_used_for_forecast():
    data = load_artifact()
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["status"] == "RESEARCH_ONLY"
    assert data["forecast"]["issued"] is False
    assert len(data["competing_hypotheses"]) >= 3
    assert all(item["support"] or item.get("supporting_evidence") for item in data["competing_hypotheses"])
    assert all(
        item["disconfirming_or_missing"] and item["tests"]
        for item in data["competing_hypotheses"]
    )
