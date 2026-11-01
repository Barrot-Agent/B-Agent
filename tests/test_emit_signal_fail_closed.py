import json
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

import pytest

from scripts import emit_signal, knowledge_ingest


def test_score_parser_rejects_malformed_or_incomplete_provider_output():
    with pytest.raises(ValueError):
        emit_signal._score_from_text("not-json")
    with pytest.raises(ValueError):
        emit_signal._score_from_text('{"score": 50, "confidence": 0.5}')
    with pytest.raises(ValueError):
        emit_signal._score_from_text('{"score": 50, "confidence": 0.5, "label": "unknown"}')


def test_score_parser_accepts_only_complete_bounded_output():
    assert emit_signal._score_from_text(
        '{"score": 82, "confidence": 0.75, "label": "bullish"}'
    ) == (82, 0.75, "bullish")


def test_both_provider_failures_return_no_numeric_signal(monkeypatch):
    def fail_github(_):
        raise RuntimeError("missing token")

    def fail_groq(_):
        raise RuntimeError("HTTP 429")

    monkeypatch.setattr(emit_signal, "_call_github_models", fail_github)
    monkeypatch.setattr(emit_signal, "_call_groq", fail_groq)

    score, confidence, source = emit_signal.analyze_signal("recent XRP headlines")

    assert score is None
    assert confidence is None
    assert "sentiment unavailable" in source
    assert "missing token" in source
    assert "HTTP 429" in source


def test_no_qualifying_input_writes_unavailable_without_history(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BARROT_SIGNAL_TEXT", raising=False)
    monkeypatch.setattr(emit_signal, "_news_score", lambda: (None, 0, []))
    monkeypatch.setattr(
        emit_signal,
        "analyze_signal",
        lambda *_: (_ for _ in ()).throw(AssertionError("no input must not call a provider")),
    )

    emit_signal.main()

    latest = json.loads(Path("web/latest_signal.json").read_text(encoding="utf-8"))
    assert latest["status"] == "UNAVAILABLE"
    assert latest["forecast_status"] == "NOT_ISSUED"
    assert latest["score"] is None
    assert latest["confidence"] is None
    assert latest["history_appended"] is False
    assert not Path("web/signal_history.jsonl").exists()


def test_provider_failure_does_not_append_zero_confidence_history(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BARROT_SIGNAL_TEXT", raising=False)
    monkeypatch.setattr(
        emit_signal,
        "_news_score",
        lambda: (61, 2, ["[bullish] recent XRP headline"]),
    )
    monkeypatch.setattr(
        emit_signal,
        "analyze_signal",
        lambda *_: (None, None, "sentiment unavailable (GitHub missing token; Groq 429)"),
    )

    emit_signal.main()

    latest = json.loads(Path("web/latest_signal.json").read_text(encoding="utf-8"))
    assert latest["status"] == "UNAVAILABLE"
    assert latest["score"] is None
    assert latest["confidence"] is None
    assert latest["news_score"] == 61
    assert latest["history_appended"] is False
    assert not Path("web/signal_history.jsonl").exists()


def test_zero_confidence_is_not_persisted_as_a_signal(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        emit_signal,
        "_news_score",
        lambda: (None, 0, ["[neutral] one headline"]),
    )
    monkeypatch.setattr(emit_signal, "analyze_signal", lambda *_: (44, 0.0, "sentiment unavailable"))

    emit_signal.main()

    latest = json.loads(Path("web/latest_signal.json").read_text(encoding="utf-8"))
    assert latest["status"] == "UNAVAILABLE"
    assert latest["score"] is None
    assert latest["confidence"] is None
    assert not Path("web/signal_history.jsonl").exists()


def test_price_lookup_failure_is_null_not_zero(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        emit_signal,
        "_news_score",
        lambda: (70, 2, ["[bullish] recent XRP headline"]),
    )
    monkeypatch.setattr(emit_signal, "analyze_signal", lambda *_: (80, 0.8, "groq:bullish"))

    def fail_price(*args, **kwargs):
        raise RuntimeError("price provider unavailable")

    monkeypatch.setattr(emit_signal.requests, "get", fail_price)
    emit_signal.main()

    latest = json.loads(Path("web/latest_signal.json").read_text(encoding="utf-8"))
    history = Path("web/signal_history.jsonl").read_text(encoding="utf-8").splitlines()
    row = json.loads(history[0])

    assert latest["status"] == "SENTIMENT_OBSERVATION"
    assert latest["forecast_status"] == "NOT_ISSUED"
    assert latest["score"] == 75
    assert latest["confidence"] == 0.8
    assert latest["history_appended"] is True
    assert row["price_at_emission"] is None


def test_knowledge_signal_cycle_is_manual_read_only_and_artifact_based():
    workflow = Path(".github/workflows/knowledge-signal-cycle.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow
    assert "permissions:" in workflow
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "retention-days: 30" in workflow
    assert "git commit" not in workflow
    assert "git push" not in workflow


def test_ci_registers_fail_closed_signal_regression_suite():
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "tests/test_emit_signal_fail_closed.py" in workflow



def test_rss_ingestion_preserves_raw_date_and_adds_normalized_publication_time():
    raw = b"""<rss><channel><item>
      <title>XRP source timestamp test</title>
      <link>https://example.invalid/xrp-item</link>
      <description>Test summary</description>
      <pubDate>Sat, 31 Oct 2026 23:00:00 GMT</pubDate>
    </item></channel></rss>"""
    rows = knowledge_ingest.parse_rss(raw, "test", "https://example.invalid/feed")

    assert len(rows) == 1
    assert rows[0]["published"] == "Sat, 31 Oct 2026 23:00:00 GMT"
    assert rows[0]["published_at"] == "2026-10-31T23:00:00+00:00"
    assert rows[0]["ingested_at"]


def test_news_score_uses_publication_time_and_rejects_bad_or_future_rows(tmp_path):
    now = datetime.now(timezone.utc)
    recent = now - timedelta(hours=1)
    old = now - timedelta(hours=100)
    future = now + timedelta(hours=1)

    def row(title, published, sentiment="bullish", weight=0.8, ingested=None, url=None):
        value = {
            "title": title,
            "ingested_at": (ingested or now).isoformat(),
            "published": format_datetime(published),
            "distilled": True,
            "distill": {"sentiment": sentiment, "xrp_relevance": weight},
        }
        if url:
            value["url"] = url
        return value

    rows = [
        row("valid RSS timestamp", recent, url="https://example.invalid/1"),
        {
            "title": "valid normalized timestamp",
            "ingested_at": now.isoformat(),
            "published_at": recent.isoformat(),
            "distilled": True,
            "distill": {"sentiment": "bearish", "xrp_relevance": 0.2},
            "url": "https://example.invalid/2",
        },
        row("old story re-ingested now", old, url="https://example.invalid/3"),
        {
            "title": "missing publication time",
            "ingested_at": now.isoformat(),
            "distilled": True,
            "distill": {"sentiment": "bullish", "xrp_relevance": 1.0},
        },
        {
            "title": "future publication time",
            "ingested_at": now.isoformat(),
            "published_at": future.isoformat(),
            "distilled": True,
            "distill": {"sentiment": "bullish", "xrp_relevance": 1.0},
        },
        row("naive ingestion timestamp", recent, ingested=now.replace(tzinfo=None)),
        row("invalid sentiment", recent, sentiment="maybe"),
        row("non-finite weight", recent, weight="NaN"),
        row("future ingestion timestamp", recent, ingested=future),
    ]
    path = tmp_path / "log.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in rows) + "\n", encoding="utf-8")

    score, count, headlines = emit_signal._news_score(hours=72, path=str(path))

    assert score == 80
    assert count == 2
    assert any("valid RSS timestamp" in headline for headline in headlines)


def test_news_score_deduplicates_urls_and_ignores_missing_or_malformed_timestamps(tmp_path):
    now = datetime.now(timezone.utc)
    published = now - timedelta(minutes=30)
    base = {
        "ingested_at": now.isoformat(),
        "published_at": published.isoformat(),
        "distilled": True,
        "distill": {"sentiment": "bullish", "xrp_relevance": 0.9},
        "url": "https://example.invalid/duplicate",
    }
    duplicate = dict(base, title="duplicate")
    first = dict(base, title="first")
    malformed = dict(base, title="malformed", ingested_at="not-a-timestamp")
    path = tmp_path / "log.jsonl"
    path.write_text(
        "\n".join(json.dumps(item) for item in (first, duplicate, malformed)) + "\n",
        encoding="utf-8",
    )

    score, count, headlines = emit_signal._news_score(hours=72, path=str(path))

    assert score == 100
    assert count == 1
    assert len(headlines) == 1
