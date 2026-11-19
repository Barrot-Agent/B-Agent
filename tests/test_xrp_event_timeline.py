
from __future__ import annotations

import pytest

from barrot_agent.evolution.event_timeline import (
    EventTimelineError,
    build_event_timeline,
)


CUTOFF = "2026-11-12T03:00:00Z"


def event(event_id: str, **overrides):
    record = {
        "event_id": event_id,
        "event_type": "macro",
        "event_name": f"Macro event {event_id}",
        "hypothesis_id": "macro-liquidity",
        "domain": "macro",
        "hypothesis": "Persistent dollar strength and higher yields constrain broad crypto risk appetite.",
        "counter_hypothesis": "The macro shock may already be priced while asset-specific flows dominate.",
        "claim": f"Event evidence {event_id}.",
        "source_id": f"source-{event_id}",
        "source_name": f"Publisher {event_id}",
        "source_url": f"https://publisher-{event_id}.example/research",
        "independence_group": f"publisher-{event_id}",
        "source_status": "verified",
        "stance": "supports",
        "event_status": "occurred",
        "event_time_utc": "2026-11-11T20:00:00Z",
        "source_published_at_utc": "2026-11-11T20:01:00Z",
        "available_at_utc": "2026-11-11T20:02:00Z",
        "captured_at_utc": "2026-11-11T20:03:00Z",
        "raw_source_sha256": "a" * 64,
        "assumptions": ["The source timestamps are accurate."],
        "falsification_conditions": ["The dollar and real yields reverse lower."],
        "related_entities": ["Federal Reserve"],
        "tags": ["rates", "macro"],
    }
    record.update(overrides)
    return record


def build(records, **overrides):
    args = {
        "asset": "XRP",
        "data_cutoff_utc": CUTOFF,
        "horizon_seconds": 86_400,
        "event_records": records,
    }
    args.update(overrides)
    return build_event_timeline(**args)


def test_builds_deterministic_timeline_and_research_only_scenarios():
    records = [event("b"), event("a", stance="contradicts")]
    first = build(records)
    second = build(list(reversed(records)))

    assert [item["event_id"] for item in first["event_timeline"]] == ["a", "b"]
    assert first["artifact_id"] == second["artifact_id"]
    assert first["timeline_fingerprint"] == second["timeline_fingerprint"]
    assert first["forecast_status"] == "NOT_ISSUED"
    assert first["directional_forecast"] is False
    assert first["probabilities"] is None
    assert first["model_eligible"] is False
    assert first["receipt_complete"] is False
    assert first["raw_hash_present_count"] == 2
    assert first["event_timeline"][0]["receipt_status"] == "RAW_SHA256_PRESENT_UNVERIFIED"
    assert first["scenario_set"]["scenarios"][0]["disagreement_present"] is True
    assert first["scenario_set"]["scenarios"][0]["minority_objection_count"] == 1


def test_future_scheduled_event_is_included_only_when_known_by_cutoff():
    item = event(
        "scheduled",
        event_type="regulatory",
        event_status="scheduled",
        event_time_utc="2026-11-12T13:30:00Z",
        source_published_at_utc="2026-11-11T10:00:00Z",
        available_at_utc="2026-11-11T10:01:00Z",
        captured_at_utc="2026-11-11T10:02:00Z",
    )
    result = build([item])

    assert result["event_count"] == 1
    assert result["event_timeline"][0]["event_status"] == "scheduled"
    assert result["scenario_set"]["scenarios"][0]["future_scheduled_event_count"] == 1


def test_future_scheduled_event_outside_horizon_is_excluded():
    item = event(
        "far-future",
        event_status="scheduled",
        event_time_utc="2026-11-14T13:30:00Z",
        source_published_at_utc="2026-11-11T10:00:00Z",
        available_at_utc="2026-11-11T10:01:00Z",
        captured_at_utc="2026-11-11T10:02:00Z",
    )
    result = build([item])

    assert result["event_timeline"] == []
    excluded = result["excluded_events"][0]
    assert excluded["event_id"] == "far-future"
    assert excluded["reason"] == "scheduled_event_outside_forecast_horizon"
    assert excluded["source_id"] == "source-far-future"
    assert excluded["raw_source_sha256"] == "a" * 64
    assert excluded["model_eligible"] is False


def test_future_occurred_event_is_excluded():
    item = event(
        "future-outcome",
        event_time_utc="2026-11-13T13:30:00Z",
        source_published_at_utc="2026-11-11T10:00:00Z",
        available_at_utc="2026-11-11T10:01:00Z",
        captured_at_utc="2026-11-11T10:02:00Z",
    )
    result = build([item])

    assert result["event_timeline"] == []
    assert result["excluded_events"][0]["reason"] == "occurred_event_is_after_data_cutoff"


def test_historical_event_captured_after_cutoff_is_excluded():
    item = event(
        "late-backfill",
        event_time_utc="2026-11-10T10:00:00Z",
        source_published_at_utc="2026-11-10T10:01:00Z",
        available_at_utc="2026-11-12T03:00:01Z",
        captured_at_utc="2026-11-12T03:00:02Z",
    )
    result = build([item])

    assert result["event_timeline"] == []
    assert result["excluded_events"][0]["reason"] == "not_captured_by_data_cutoff"


def test_capture_time_cannot_precede_availability_or_publication():
    with pytest.raises(EventTimelineError, match="cannot precede available_at"):
        build([event("bad-capture", captured_at_utc="2026-11-11T20:01:00Z")])
    with pytest.raises(EventTimelineError, match="cannot follow captured_at"):
        build([event("bad-publication", source_published_at_utc="2026-11-11T20:04:00Z")])


def test_elapsed_scheduled_event_is_excluded_until_reconciled():
    item = event(
        "elapsed",
        event_status="scheduled",
        event_time_utc="2026-11-12T02:59:00Z",
    )
    result = build([item])

    assert result["event_timeline"] == []
    assert result["excluded_events"][0]["reason"] == "scheduled_event_time_has_elapsed"


def test_unverified_evidence_is_context_only_and_not_support():
    item = event("unverified", source_status="unverified", stance="contradicts")
    result = build([item])
    scenario = result["scenario_set"]["scenarios"][0]

    assert scenario["supporting_evidence"] == []
    assert scenario["contrary_evidence"] == []
    assert len(scenario["context_evidence"]) == 1
    assert result["model_eligible"] is False


def test_missing_raw_hash_is_visible_and_receipt_incomplete():
    result = build([event("missing-receipt", raw_source_sha256=None)])

    assert result["receipt_complete"] is False
    assert result["raw_hash_present_count"] == 0
    assert result["event_timeline"][0]["raw_hash_present"] is False
    assert result["event_timeline"][0]["receipt_status"] == "MISSING_RAW_RECEIPT_HASH"
    assert result["model_eligible"] is False


def test_invalid_raw_hash_is_rejected():
    with pytest.raises(EventTimelineError, match="64-character SHA-256"):
        build([event("bad-hash", raw_source_sha256="not-a-hash")])


def test_duplicate_event_ids_are_rejected():
    with pytest.raises(EventTimelineError, match="duplicate event_id"):
        build([event("duplicate"), event("duplicate", stance="contradicts")])


def test_timezone_is_required_for_all_timeline_timestamps():
    with pytest.raises(EventTimelineError, match="must include a timezone"):
        build([event("naive", captured_at_utc="2026-11-12T03:00:00")])


def test_source_lineage_and_publisher_aliases_are_conservatively_collapsed():
    records = [
        event(
            "sbi",
            source_url="https://www.sbigroup.co.jp/news/example.html",
            independence_group="sbi-holdings",
        ),
        event(
            "sbi-vc",
            source_url="https://www.sbivc.co.jp/news/example.html",
            independence_group="sbi-vc",
        ),
        event(
            "tokyo-sbic",
            source_url="https://www.sbic.co.jp/news/example.html",
            independence_group="tokyo-sbic",
        ),
    ]
    result = build(records)

    assert result["independent_source_group_count"] == 2


def test_invalid_event_type_is_rejected():
    with pytest.raises(EventTimelineError, match="event_type"):
        build([event("bad-type", event_type="rumor")])


def test_empty_timeline_is_explicitly_not_forecast():
    result = build([])

    assert result["event_count"] == 0
    assert result["event_timeline"] == []
    assert result["scenario_set"]["scenarios"] == []
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["probabilities"] is None
    assert result["model_eligible"] is False


def test_event_horizon_must_be_a_positive_non_boolean_integer():
    with pytest.raises(EventTimelineError, match="positive integer"):
        build([], horizon_seconds=True)
    with pytest.raises(EventTimelineError, match="positive integer"):
        build([], horizon_seconds=0)


def test_excluded_events_retain_source_timestamps_lineage_and_receipt():
    item = event(
        "late-evidence",
        event_time_utc="2026-11-10T10:00:00Z",
        source_published_at_utc="2026-11-10T10:01:00Z",
        available_at_utc="2026-11-12T03:00:01Z",
        captured_at_utc="2026-11-12T03:00:02Z",
    )
    excluded = build([item])["excluded_events"][0]

    assert excluded["reason"] == "not_captured_by_data_cutoff"
    assert excluded["source_id"] == "source-late-evidence"
    assert excluded["source_url"] == "https://publisher-late-evidence.example/research"
    assert excluded["source_published_at_utc"] == "2026-11-10T10:01:00Z"
    assert excluded["captured_at_utc"] == "2026-11-12T03:00:02Z"
    assert excluded["raw_source_sha256"] == "a" * 64
    assert excluded["raw_hash_present"] is True
    assert excluded["receipt_status"] == "RAW_SHA256_PRESENT_UNVERIFIED"
    assert excluded["model_eligible"] is False


def test_invalid_statuses_are_rejected_even_when_record_is_after_cutoff():
    late = {
        "available_at_utc": "2026-11-12T03:00:01Z",
        "captured_at_utc": "2026-11-12T03:00:02Z",
    }
    with pytest.raises(EventTimelineError, match="event_status"):
        build([event("bad-event-status", event_status="rumor", **late)])
    with pytest.raises(EventTimelineError, match="source_status"):
        build([event("bad-source-status", source_status="trusted-ish", **late)])
    with pytest.raises(EventTimelineError, match="stance"):
        build([event("bad-stance", stance="probably", **late)])


def test_invalid_or_credential_bearing_urls_are_rejected_even_when_record_is_excluded():
    late = {
        "available_at_utc": "2026-11-12T03:00:01Z",
        "captured_at_utc": "2026-11-12T03:00:02Z",
    }
    with pytest.raises(EventTimelineError, match="valid HTTP"):
        build([event("bad-scheme", source_url="file:///tmp/source", **late)])
    with pytest.raises(EventTimelineError, match="embedded credentials"):
        build([event("credential-url", source_url="https://user:pass@example.com/a", **late)])


def test_invalid_raw_hash_is_rejected_even_when_record_is_excluded():
    late = {
        "available_at_utc": "2026-11-12T03:00:01Z",
        "captured_at_utc": "2026-11-12T03:00:02Z",
    }
    with pytest.raises(EventTimelineError, match="64-character SHA-256"):
        build([event("bad-late-hash", raw_source_sha256="bad", **late)])


def test_source_name_must_be_text():
    with pytest.raises(EventTimelineError, match="source_name"):
        build([event("bad-source-name", source_name=17)])
