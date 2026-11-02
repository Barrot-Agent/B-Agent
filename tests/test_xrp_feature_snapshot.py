import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from knowledge_distill import select_todo
from xrp_feature_snapshot import build_snapshot, write_snapshot


def _write_jsonl(path, rows, malformed=False):
    lines = [json.dumps(row) for row in rows]
    if malformed:
        lines.append("{not-json")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_snapshot_uses_capture_time_and_preserves_quality_gaps(tmp_path):
    now = datetime(2026, 11, 2, 8, 0, tzinfo=timezone.utc)
    log = tmp_path / "log.jsonl"
    config = tmp_path / "config.json"
    config.write_text('{"sources": {}}', encoding="utf-8")
    rows = [
        {
            "url": "https://example.com/a",
            "feed": "feed-a",
            "ingested_at": (now - timedelta(hours=1)).isoformat(),
            "distilled": True,
            "distill": {"sentiment": "bullish", "xrp_relevance": 0.8, "entities": ["Ripple", "XRP"]},
        },
        {
            "url": "https://example.com/a",
            "feed": "feed-a",
            "ingested_at": (now - timedelta(hours=2)).isoformat(),
            "distilled": True,
            "distill": {"sentiment": "bearish", "xrp_relevance": 0.2, "entities": ["XRP"]},
        },
        {
            "url": "https://example.com/b",
            "feed": "feed-b",
            "ingested_at": (now - timedelta(hours=25)).isoformat(),
            "distilled": True,
            "distill": {"sentiment": "bearish", "xrp_relevance": 1.0, "entities": ["SEC"]},
        },
        {"url": "https://example.com/c", "feed": "feed-c", "distilled": False},
        {
            "url": "https://example.com/d",
            "feed": "feed-d",
            "ingested_at": (now + timedelta(hours=1)).isoformat(),
            "distilled": False,
        },
    ]
    _write_jsonl(log, rows, malformed=True)

    snapshot = build_snapshot(log, config, now=now, restore_status="TEST_SEED")

    assert snapshot["entries_total"] == 5
    assert snapshot["unique_url_count"] == 4
    assert snapshot["duplicate_url_count"] == 1
    assert snapshot["malformed_jsonl_lines"] == 1
    assert snapshot["missing_ingested_at"] == 1
    assert snapshot["future_ingested_at"] == 1
    assert snapshot["recent_24h_entries"] == 2
    assert snapshot["prior_24h_entries"] == 1
    assert snapshot["recent_24h_weighted_sentiment_score"] == 80
    assert snapshot["prior_24h_weighted_sentiment_score"] == 0
    assert snapshot["sentiment_shift_points"] == 80
    assert snapshot["status"] == "DEGRADED"
    assert snapshot["forecast_status"] == "NOT_ISSUED"
    assert snapshot["source_files"]["log_sha256"] is not None


def test_snapshot_is_stale_when_no_entries_fall_in_recent_window(tmp_path):
    now = datetime(2026, 11, 2, 8, 0, tzinfo=timezone.utc)
    log = tmp_path / "log.jsonl"
    _write_jsonl(log, [{
        "url": "https://example.com/old",
        "ingested_at": (now - timedelta(hours=60)).isoformat(),
        "distilled": True,
        "distill": {"sentiment": "neutral", "xrp_relevance": 1.0, "entities": []},
    }])
    snapshot = build_snapshot(log, tmp_path / "missing-config.json", now=now)
    assert snapshot["status"] == "STALE"
    assert snapshot["recent_24h_entries"] == 0
    assert snapshot["recent_24h_weighted_sentiment_score"] is None


def test_snapshot_writer_stages_rolling_feature_store(tmp_path):
    log = tmp_path / "log.jsonl"
    config = tmp_path / "config.json"
    log.write_text('{"url":"https://example.com","ingested_at":"2026-11-02T07:00:00Z"}\n', encoding="utf-8")
    config.write_text('{"sources": {}}', encoding="utf-8")
    snapshot = build_snapshot(log, config, now=datetime(2026, 11, 2, 8, 0, tzinfo=timezone.utc))
    output = tmp_path / "out" / "snapshot.json"
    stage = tmp_path / "stage"
    write_snapshot(snapshot, log, config, output, stage)
    assert json.loads(output.read_text(encoding="utf-8"))["entries_total"] == 1
    assert (stage / "log.jsonl").read_text(encoding="utf-8") == log.read_text(encoding="utf-8")
    assert (stage / "config.json").exists()
    assert (stage / "xrp_feature_snapshot.json").exists()


def test_distillation_batch_limit_is_deterministic():
    entries = [
        {"url": "a", "distilled": True},
        {"url": "b", "distilled": False},
        {"url": "c", "distilled": False},
        {"url": "d", "distilled": False},
    ]
    assert [row["url"] for row in select_todo(entries, 2)] == ["b", "c"]
    assert [row["url"] for row in select_todo(entries, 0)] == ["b", "c", "d"]


def test_xrp_ingestion_workflow_is_scheduled_read_only_and_artifact_backed():
    workflow = (ROOT / ".github/workflows/xrp-intelligence-ingest.yml").read_text(encoding="utf-8")
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    lowered = workflow.lower()
    assert "schedule:" in workflow
    assert "cron: \"12 * * * *\"" in workflow
    assert "permissions:\n  actions: read\n  contents: read" in workflow
    assert "contents: write" not in workflow
    assert "git push" not in lowered
    assert "persist-credentials: false" in workflow
    assert "actions/download-artifact@v4" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "retention-days: 90" in workflow
    assert 'MAX_DISTILL_PER_RUN: "24"' in workflow
    assert "tests/test_xrp_feature_snapshot.py" in ci


def test_snapshot_rejects_non_finite_relevance_and_missing_urls(tmp_path):
    now = datetime(2026, 11, 2, 8, 0, tzinfo=timezone.utc)
    log = tmp_path / "log.jsonl"
    _write_jsonl(log, [{
        "feed": "feed-a",
        "ingested_at": (now - timedelta(minutes=5)).isoformat(),
        "distilled": True,
        "distill": {"sentiment": "bullish", "xrp_relevance": float("nan"), "entities": ["XRP"]},
    }])
    snapshot = build_snapshot(log, tmp_path / "missing-config.json", now=now)
    assert snapshot["missing_url"] == 1
    assert snapshot["missing_or_invalid_xrp_relevance"] == 1
    assert snapshot["recent_24h_weighted_sentiment_score"] is None
    assert snapshot["status"] == "DEGRADED"
