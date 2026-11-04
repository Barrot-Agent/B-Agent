from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from barrot_agent.evolution.xrp_public_ingestion import (
    RawReceiptArchive,
    XRPIngestionError,
    fetch_public_json,
    run_ingestion,
)


def _iso_ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def _fake_fetcher(captured: datetime):
    captured_ms = _iso_ms(captured)

    def fetcher(source_id: str, url: str):
        if source_id == "binance_spot_ticker":
            payload = {
                "symbol": "XRPUSDT",
                "closeTime": captured_ms - 1000,
                "lastPrice": "1.29",
                "bidPrice": "1.2899",
                "askPrice": "1.2901",
                "bidQty": "1000",
                "askQty": "900",
                "volume": "1000000",
                "quoteVolume": "1290000",
                "weightedAvgPrice": "1.28",
            }
        elif source_id == "binance_spot_klines":
            payload = [
                [captured_ms - 7200000, "1.20", "1.30", "1.19", "1.27", "1000", captured_ms - 3600001, "1270", 25, "500", "635", "0"],
                [captured_ms, "1.29", "1.31", "1.28", "1.30", "100", captured_ms + 3599999, "130", 5, "50", "65", "0"],
            ]
        elif source_id == "binance_perp_premium":
            payload = {
                "symbol": "XRPUSDT",
                "time": captured_ms - 2000,
                "markPrice": "1.291",
                "indexPrice": "1.290",
                "lastFundingRate": "0.0001",
                "nextFundingTime": captured_ms + 8 * 3600000,
            }
        elif source_id == "binance_perp_open_interest":
            payload = {"symbol": "XRPUSDT", "time": captured_ms - 3000, "openInterest": "2500000"}
        elif source_id == "kraken_spot_depth":
            ts = captured.timestamp() - 5
            payload = {
                "error": [],
                "result": {
                    "XXRPZUSD": {
                        "bids": [["1.289", "1000", str(ts)], ["1.288", "2000", str(ts)]],
                        "asks": [["1.291", "1200", str(ts)], ["1.292", "1800", str(ts)]],
                    }
                },
            }
        elif source_id == "binance_spot_depth":
            payload = {
                "lastUpdateId": 123456,
                "bids": [["1.289", "1000"]],
                "asks": [["1.291", "1200"]],
            }
        else:
            raise AssertionError(source_id)
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return {"raw_bytes": raw, "payload": payload}

    return fetcher


def test_raw_receipt_archive_is_content_addressed_and_write_once(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    raw = b'{"x":1}'
    first = archive.store(
        source_id="test",
        source_uri="https://api.binance.com/test",
        captured_at_utc="2026-11-04T12:00:00.000000Z",
        raw_bytes=raw,
        source_data_as_of_utc="2026-11-04T11:59:59.000000Z",
        model_eligible=True,
    )
    path = tmp_path / first["raw_payload_path"]
    assert path.read_bytes() == raw
    assert first["raw_content_sha256"] == hashlib.sha256(raw).hexdigest()
    assert len(first["receipt_id"]) == 64

    second = archive.store(
        source_id="test",
        source_uri="https://api.binance.com/test",
        captured_at_utc="2026-11-04T12:00:01.000000Z",
        raw_bytes=raw,
        source_data_as_of_utc="2026-11-04T11:59:59.000000Z",
        model_eligible=True,
    )
    assert second["raw_content_sha256"] == first["raw_content_sha256"]
    assert len(archive.receipts_path.read_text(encoding="utf-8").splitlines()) == 2

    path.write_bytes(b'{"x":2}')
    with pytest.raises(XRPIngestionError, match="tampering"):
        archive.store(
            source_id="test",
            source_uri="https://api.binance.com/test",
            captured_at_utc="2026-11-04T12:00:02.000000Z",
            raw_bytes=raw,
            source_data_as_of_utc="2026-11-04T11:59:59.000000Z",
            model_eligible=True,
        )


def test_fetcher_rejects_non_allowlisted_hosts_without_network():
    with pytest.raises(XRPIngestionError, match="allowlisted"):
        fetch_public_json("bad", "https://example.com/public.json")
    with pytest.raises(XRPIngestionError, match="allowlisted"):
        fetch_public_json("bad", "http://api.binance.com/api/v3/ticker/24hr")


def test_public_ingestion_builds_verified_point_in_time_snapshot_and_preserves_backfill_receipt(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    summary = run_ingestion(tmp_path / "run", fetcher=_fake_fetcher(captured), now=captured)

    assert summary["snapshot_status"] == "verified"
    assert summary["forecast_status"] == "NOT_ISSUED"
    assert summary["forecast_model_eligible"] is False
    assert summary["source_receipt_count"] == 6
    assert summary["source_failure_count"] == 0
    assert summary["eligible_feature_record_count"] > 0
    assert summary["store_verification"]["valid"] is True

    snapshot = json.loads((tmp_path / "run" / "snapshot.json").read_text(encoding="utf-8"))
    historical = next(
        item for item in snapshot["records"]
        if item["feature_id"] == "xrp.spot.binance.1h.close_price"
    )
    assert historical["event_time_utc"] < historical["known_at_utc"]
    assert historical["known_at_utc"] == "2026-11-04T12:30:00.000000Z"
    assert "first observed at this capture time" in historical["limitations"][0]

    raw_only = json.loads((tmp_path / "run" / "raw_only_sources.json").read_text(encoding="utf-8"))
    assert any(item["source_id"] == "binance_spot_depth" for item in raw_only)
    receipts = json.loads((tmp_path / "run" / "receipt_manifest.json").read_text(encoding="utf-8"))
    assert all(len(item["raw_content_sha256"]) == 64 for item in receipts)
    assert (tmp_path / "run" / "feature_store.sqlite3").exists()


def test_stale_live_sources_are_excluded_but_historical_backfill_remains_known_at_capture(tmp_path):
    captured = datetime(2026, 11, 4, 12, 30, tzinfo=timezone.utc)
    stale = captured - timedelta(minutes=20)
    fetcher = _fake_fetcher(captured)

    def stale_fetcher(source_id: str, url: str):
        response = fetcher(source_id, url)
        if source_id == "binance_spot_ticker":
            payload = dict(response["payload"], closeTime=_iso_ms(stale))
            raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            return {"raw_bytes": raw, "payload": payload}
        return response

    summary = run_ingestion(tmp_path / "stale-run", fetcher=stale_fetcher, now=captured)
    snapshot = json.loads((tmp_path / "stale-run" / "snapshot.json").read_text(encoding="utf-8"))
    assert summary["snapshot_status"] == "verified"
    assert any(
        "quality_stale" in item["reasons"]
        for item in snapshot["excluded_records"]
    )
    assert all(
        record["known_at_utc"] == "2026-11-04T12:30:00.000000Z"
        for record in snapshot["records"]
    )


def test_scheduled_ingestion_workflow_is_read_only_artifact_only():
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "xrp-public-ingestion.yml").read_text(encoding="utf-8")
    assert "cron: '3 * * * *'" in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "persist-credentials: false" in workflow
    assert "upload-artifact@v7" in workflow
    assert "retention-days: 90" in workflow
    assert "secrets." not in workflow
    assert "contents: write" not in workflow
    assert "git push" not in workflow
