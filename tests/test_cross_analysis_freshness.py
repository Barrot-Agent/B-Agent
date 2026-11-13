from datetime import datetime, timedelta, timezone

from scripts import entity_sentiment_profile, sentiment_shift


NOW = datetime(2026, 11, 13, 19, 0, tzinfo=timezone.utc)


def _entry(ts, sentiment="bullish", relevance=0.8, *, naive=False):
    if naive:
        ts_value = ts.replace(tzinfo=None).isoformat()
    else:
        ts_value = ts.isoformat()
    return {
        "ingested_at": ts_value,
        "distilled": True,
        "title": "XRP market evidence",
        "distill": {
            "sentiment": sentiment,
            "xrp_relevance": relevance,
            "btc_relevance": relevance,
            "entities": ["XRP"],
        },
    }


def test_entity_profile_marks_old_corpus_stale_and_non_forecast_eligible():
    entries = [_entry(datetime(2026, 10, 29, 13, 23, tzinfo=timezone.utc))]

    result = entity_sentiment_profile.build_data_freshness(entries, NOW)

    assert result["status"] == "STALE"
    assert result["recent_24h_sentiment_entries"] == 0
    assert result["latest_sentiment_age_hours"] > 48
    assert result["forecast_eligible"] is False
    assert "Historical corpus aggregate" in result["interpretation"]


def test_entity_profile_rejects_naive_and_missing_timestamps():
    entries = [
        _entry(NOW - timedelta(hours=1), naive=True),
        {"distill": {"sentiment": "bullish", "entities": ["XRP"]}},
    ]

    result = entity_sentiment_profile.build_data_freshness(entries, NOW)

    assert result["status"] == "NO_VALID_DISTILLED_TIMESTAMP"
    assert result["invalid_timestamp_entries"] == 2
    assert result["forecast_eligible"] is False


def test_sentiment_shift_requires_minimum_sample_in_both_windows():
    recent = [_entry(NOW - timedelta(hours=i + 1)) for i in range(4)]
    prior = [_entry(NOW - timedelta(hours=25 + i), sentiment="bearish") for i in range(5)]

    result = sentiment_shift.build_asset_result(recent + prior, "xrp_relevance", NOW)

    assert result["status"] == "INSUFFICIENT_SAMPLE"
    assert result["recent_24h_entries"] == 4
    assert result["prior_24h_entries"] == 5
    assert result["shift"] is None
    assert result["significant_shift"] is False
    assert result["forecast_eligible"] is False


def test_sentiment_shift_rejects_stale_input_even_when_historical_scores_exist():
    old = [
        _entry(NOW - timedelta(days=3, hours=i), sentiment="bullish" if i % 2 else "bearish")
        for i in range(12)
    ]

    result = sentiment_shift.build_asset_result(old, "xrp_relevance", NOW)

    assert result["status"] == "STALE_INPUT"
    assert result["shift"] is None
    assert result["significant_shift"] is False


def test_sentiment_shift_rejects_naive_timestamps_without_comparing_them():
    entries = [_entry(NOW - timedelta(hours=1), naive=True)]

    score, count = sentiment_shift.window_score(
        entries,
        "xrp_relevance",
        NOW - timedelta(hours=24),
        NOW,
    )

    assert score is None
    assert count == 0


def test_sentiment_shift_comparison_ready_is_still_not_a_forecast():
    recent = [_entry(NOW - timedelta(hours=i + 1), sentiment="bullish") for i in range(5)]
    prior = [_entry(NOW - timedelta(hours=25 + i), sentiment="bearish") for i in range(5)]

    result = sentiment_shift.build_asset_result(recent + prior, "xrp_relevance", NOW)

    assert result["status"] == "COMPARISON_READY"
    assert result["shift"] is not None
    assert result["significant_shift"] is True
    assert result["forecast_eligible"] is False

def test_cross_analysis_downloads_exact_upstream_artifact_with_read_only_permissions():
    from pathlib import Path

    workflow = Path(".github/workflows/cross-analysis.yml").read_text(encoding="utf-8")
    assert "actions: read" in workflow
    assert "contents: read" in workflow
    assert "actions/download-artifact@v8" in workflow
    assert "github.event.workflow_run.run_number" in workflow
    assert "github.event.workflow_run.id" in workflow
    assert "if: github.event_name == 'workflow_run'" in workflow
    assert "contents: write" not in workflow
    assert "git push" not in workflow
    assert "schedule:" in workflow


def test_legacy_knowledge_cycle_keeps_explicit_external_research_gate():
    from pathlib import Path

    workflow = Path(".github/workflows/knowledge-signal-cycle.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "confirm_external_research" in workflow
    assert "default: NO" in workflow
    assert "inputs.confirm_external_research == 'YES'" in workflow
    assert "schedule:" not in workflow

