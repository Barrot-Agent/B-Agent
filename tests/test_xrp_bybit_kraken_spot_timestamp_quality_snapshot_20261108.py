import hashlib
import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T135008Z-bybit-kraken-spot-timestamp-quality-snapshot.json"
)


def test_bybit_kraken_spot_receipts_preserve_exact_rendered_payload_hashes():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    receipts = {item["source_id"]: item for item in artifact["source_receipts"]}

    assert set(receipts) == {
        "bybit_spot_xrpusdt_ticker_20261108_135008",
        "kraken_xrp_usd_ticker_20261108_retrieval",
    }
    for receipt in receipts.values():
        digest = hashlib.sha256(receipt["response_text"].encode("utf-8")).hexdigest()
        assert digest == receipt["sha256"]
        assert receipt["model_eligible"] is False
        assert receipt["retrieved_at_utc"] is None


def test_bybit_exchange_server_timestamp_and_quote_currency_are_exact():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    receipt = next(
        item for item in artifact["source_receipts"]
        if item["publisher"] == "Bybit"
    )
    payload = json.loads(receipt["response_text"])
    ticker = payload["result"]["list"][0]

    assert payload["retCode"] == 0
    assert ticker["symbol"] == "XRPUSDT"
    assert payload["time"] == 1794145808596
    assert receipt["source_time_utc"] == "2026-11-08T13:50:08.596Z"
    assert receipt["quote_currency"] == "USDT"
    assert ticker["turnover24h"] == "12543781.48148"
    assert ticker["usdIndexPrice"] == "1.158787"


def test_kraken_timestamp_absence_is_not_filled_from_capture_reference():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    receipt = next(
        item for item in artifact["source_receipts"]
        if item["publisher"] == "Kraken"
    )
    payload = json.loads(receipt["response_text"])

    assert payload["error"] == []
    assert "XXRPZUSD" in payload["result"]
    assert receipt["source_time_utc"] is None
    assert receipt["retrieved_at_utc"] is None
    assert receipt["quote_currency"] == "USD"


def test_unsynchronized_cross_currency_quotes_are_not_compared_or_admitted():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["data_cutoff_utc"] is None
    assert artifact["comparison"]["status"] == "not_comparable"
    assert artifact["comparison"]["naive_midpoint_difference_bps"] is None
    assert artifact["comparison"]["normalized_quote_currency_difference"] is None
    assert artifact["quality_controls"]["synchronized_cross_venue_cutoff"] is False
    assert artifact["quality_controls"]["market_feature_store_write"] is False
    assert artifact["quality_controls"]["model_admission"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"


def test_bybit_age_is_a_lower_bound_and_turnover_is_not_usd():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    bybit = artifact["observations"]["bybit"]

    assert math.isclose(bybit["age_seconds_at_reference"], 901.404, abs_tol=0.001)
    assert bybit["age_is_lower_bound_at_actual_retrieval"] is True
    assert bybit["turnover_24h_usdt"] == 12543781.48148
    assert "turnover_24h_usd" not in bybit
