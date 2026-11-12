from __future__ import annotations

import hashlib
import json

import pytest

import barrot_agent.evolution.xrp_public_ingestion as ingestion
from barrot_agent.evolution.xrp_public_ingestion import (
    RawReceiptArchive,
    XRPIngestionError,
    _apply_http_cache_age_gate,
    _capture_http_headers,
    _http_cache_age_exclusion_reason,
    fetch_public_json,
)


def _receipt(archive: RawReceiptArchive, headers=None):
    return archive.store(
        source_id="public_test",
        source_uri="https://api.binance.com/test",
        captured_at_utc="2026-11-10T02:00:00.000000Z",
        raw_bytes=b'{"value":1}',
        source_data_as_of_utc="2026-11-10T01:59:59.000000Z",
        model_eligible=True,
        source_http_date="Tue, 10 Nov 2026 02:00:00 GMT",
        source_http_headers=headers,
    )


def test_http_header_capture_is_allowlisted_bounded_and_case_normalized():
    headers = {
        "Age": "301",
        "ETag": '"revision-7"',
        "Cache-Control": "public, max-age=60",
        "Last-Modified": "Tue, 10 Nov 2026 01:55:00 GMT",
        "Set-Cookie": "session=must-not-be-retained",
        "Authorization": "Bearer must-not-be-retained",
        "X-Cache": "HIT",
    }
    captured = _capture_http_headers(headers)
    assert captured == {
        "age": "301",
        "cache-control": "public, max-age=60",
        "etag": '"revision-7"',
        "last-modified": "Tue, 10 Nov 2026 01:55:00 GMT",
        "x-cache": "HIT",
    }
    assert "set-cookie" not in captured
    assert "authorization" not in captured


def test_json_fetch_preserves_exact_body_and_selected_response_headers(monkeypatch):
    raw = b'{"symbol":"XRPUSDT","lastPrice":"1.10"}'

    class Response:
        headers = {
            "Date": "Tue, 10 Nov 2026 02:00:00 GMT",
            "Age": "12",
            "ETag": '"xrp-v12"',
            "Cache-Control": "public, max-age=30",
            "Set-Cookie": "not-retained",
        }

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def geturl(self):
            return "https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT"

        def read(self, _limit):
            return raw

    monkeypatch.setattr(ingestion, "_open_public_request", lambda *_args, **_kwargs: Response())
    result = fetch_public_json(
        "binance_spot_ticker",
        "https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT",
    )
    assert result["raw_bytes"] == raw
    assert hashlib.sha256(result["raw_bytes"]).hexdigest() == hashlib.sha256(raw).hexdigest()
    assert result["http_date"] == "Tue, 10 Nov 2026 02:00:00 GMT"
    assert result["http_headers"] == {
        "age": "12",
        "cache-control": "public, max-age=30",
        "etag": '"xrp-v12"',
    }


def test_raw_receipt_binds_http_headers_into_receipt_id_and_chain(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    receipt = _receipt(
        archive,
        {"Age": "12", "ETag": '"revision-1"', "Cache-Control": "public, max-age=30"},
    )
    assert receipt["source_http_headers"] == {
        "age": "12",
        "cache-control": "public, max-age=30",
        "etag": '"revision-1"',
    }
    assert archive.verify()["verified"] is True

    stored = json.loads(archive.receipts_path.read_text(encoding="utf-8"))
    stored["source_http_headers"]["age"] = "13"
    archive.receipts_path.write_text(
        json.dumps(stored, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(XRPIngestionError, match="receipt ID does not match"):
        archive.verify()


def test_raw_receipt_rejects_unapproved_or_unbounded_http_headers(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    with pytest.raises(XRPIngestionError, match="not allowlisted"):
        _receipt(archive, {"Authorization": "Bearer secret"})
    with pytest.raises(XRPIngestionError, match="bounded printable"):
        _receipt(archive, {"etag": "x" * 513})


def test_legacy_receipt_schema_remains_verifiable_without_http_header_metadata(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    receipt = _receipt(archive)
    receipt.pop("source_http_headers")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_id"}
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    receipt["receipt_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    archive.receipts_path.write_text(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    archive.chain_path.unlink()

    migrated = RawReceiptArchive(tmp_path / "raw")
    verification = migrated.verify()
    assert migrated._legacy_chain_bootstrap is True
    assert verification["verified"] is True
    assert verification["receipt_count"] == 1


@pytest.mark.parametrize(
    ("source_id", "headers", "expected"),
    [
        ("binance_spot_ticker", {"age": "300"}, ""),
        ("binance_spot_ticker", {"age": "301"}, "http_cache_age_exceeds_300_seconds"),
        ("coinbase_spot_book", {"age": "61"}, "http_cache_age_exceeds_60_seconds"),
        ("kraken_spot_depth", {"age": "60"}, ""),
        ("binance_spot_ticker", {"age": "unknown"}, "invalid_http_cache_age_header"),
        ("binance_spot_klines", {"age": "9999"}, ""),
        ("xrp_etf_flows_aggregator", {"age": "9999"}, ""),
    ],
)
def test_http_cache_age_policy_is_source_specific(source_id, headers, expected):
    assert _http_cache_age_exclusion_reason(source_id, headers) == expected


def test_http_cache_age_gate_marks_live_features_stale_but_preserves_values():
    records = [{
        "feature_id": "xrp.spot.binance.last_price",
        "value": 1.1,
        "model_eligible": True,
        "eligibility_reason": "",
        "quality_status": "verified",
    }]
    reason = _apply_http_cache_age_gate("binance_spot_ticker", {"age": "301"}, records)
    assert reason == "http_cache_age_exceeds_300_seconds"
    assert records[0]["value"] == 1.1
    assert records[0]["model_eligible"] is False
    assert records[0]["eligibility_reason"] == reason
    assert records[0]["quality_status"] == "stale"


def test_ingestion_source_wires_cache_age_gate_before_feature_admission():
    import inspect

    source = inspect.getsource(ingestion.run_ingestion)
    assert "_apply_http_cache_age_gate(" in source
    assert source.index("_apply_http_cache_age_gate(") < source.index("archive.store(")
