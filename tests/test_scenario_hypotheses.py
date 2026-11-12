from __future__ import annotations

import pytest

from barrot_agent.evolution.scenario_hypotheses import (
    ScenarioHypothesisError,
    build_scenario_hypotheses,
)


CUTOFF = "2026-11-12T03:00:00Z"


def evidence(evidence_id: str, **overrides):
    record = {
        "evidence_id": evidence_id,
        "hypothesis_id": "macro-liquidity",
        "domain": "macro",
        "hypothesis": "Persistent dollar strength and higher yields constrain broad crypto risk appetite.",
        "counter_hypothesis": "The macro shock may already be priced, while asset-specific flows and liquidity can dominate.",
        "claim": f"Observation {evidence_id} supports the research hypothesis.",
        "source_id": f"source-{evidence_id}",
        "source_name": f"Publisher {evidence_id}",
        "source_url": f"https://publisher-{evidence_id}.example/research",
        "independence_group": f"publisher-{evidence_id}",
        "source_status": "verified",
        "stance": "supports",
        "event_status": "occurred",
        "event_time_utc": "2026-11-11T20:00:00Z",
        "available_at_utc": "2026-11-11T20:05:00Z",
        "raw_source_sha256": "a" * 64,
        "assumptions": ["The source timestamp is accurate."],
        "falsification_conditions": ["The dollar index reverses and real yields fall."],
    }
    record.update(overrides)
    return record


def build(records):
    return build_scenario_hypotheses(
        asset="XRP",
        data_cutoff_utc=CUTOFF,
        horizon_seconds=86_400,
        evidence_records=records,
    )


def test_assembles_hypothesis_and_counter_hypothesis_without_forecasting():
    result = build([evidence("a"), evidence("b", stance="contradicts")])
    scenario = result["scenarios"][0]

    assert scenario["hypothesis"].startswith("Persistent dollar strength")
    assert scenario["counter_hypothesis"].startswith("The macro shock may already be priced")
    assert scenario["disagreement_present"] is True
    assert scenario["minority_objection_count"] == 1
    assert scenario["minority_objections"][0]["evidence_id"] == "b"
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["directional_forecast"] is False
    assert result["probabilities"] is None
    assert result["model_eligible"] is False


def test_minorities_are_not_suppressed_when_supporting_sources_are_more_numerous():
    records = [
        evidence("s1"),
        evidence("s2"),
        evidence("s3"),
        evidence("s4", stance="contradicts"),
    ]
    scenario = build(records)["scenarios"][0]

    assert len(scenario["supporting_evidence"]) == 3
    assert len(scenario["contrary_evidence"]) == 1
    assert scenario["minority_objections"] == scenario["contrary_evidence"]


def test_provisional_and_unverified_sources_are_context_only():
    records = [
        evidence("provisional", source_status="provisional"),
        evidence("unverified", source_status="unverified", stance="contradicts"),
    ]
    scenario = build(records)["scenarios"][0]

    assert scenario["supporting_evidence"] == []
    assert scenario["contrary_evidence"] == []
    assert len(scenario["context_evidence"]) == 2
    assert {item["declared_stance"] for item in scenario["context_evidence"]} == {
        "supports",
        "contradicts",
    }


def test_future_scheduled_event_is_allowed_when_schedule_was_available_by_cutoff():
    record = evidence(
        "scheduled",
        event_status="scheduled",
        event_time_utc="2026-11-13T13:30:00Z",
        available_at_utc="2026-11-11T12:00:00Z",
    )
    scenario = build([record])["scenarios"][0]

    assert scenario["future_scheduled_event_count"] == 1
    assert scenario["supporting_evidence"][0]["event_is_future"] is True


def test_future_occurred_event_is_excluded():
    record = evidence(
        "future-outcome",
        event_time_utc="2026-11-13T13:30:00Z",
        available_at_utc="2026-11-11T12:00:00Z",
    )
    result = build([record])

    assert result["scenarios"] == []
    assert result["excluded_evidence"] == [
        {
            "evidence_id": "future-outcome",
            "reason": "occurred_event_is_after_data_cutoff",
        }
    ]


def test_evidence_captured_after_cutoff_is_excluded():
    record = evidence(
        "late-capture",
        available_at_utc="2026-11-12T03:00:01Z",
    )
    result = build([record])

    assert result["scenarios"] == []
    assert result["excluded_evidence"][0]["reason"] == "not_available_by_data_cutoff"


def test_elapsed_scheduled_event_is_excluded_until_timeline_is_reconciled():
    record = evidence(
        "stale-schedule",
        event_status="scheduled",
        event_time_utc="2026-11-12T02:59:00Z",
    )
    result = build([record])

    assert result["scenarios"] == []
    assert result["excluded_evidence"][0]["reason"] == "scheduled_event_time_has_elapsed"


def test_declared_lineage_collapses_distinct_domains():
    records = [
        evidence("one", independence_group="same-upstream"),
        evidence(
            "two",
            source_url="https://different-publisher.example/data",
            independence_group="same-upstream",
        ),
    ]
    scenario = build(records)["scenarios"][0]

    assert scenario["independent_source_groups_count"] == 1


def test_publisher_aliases_collapse_and_sbic_remains_distinct_from_sbi():
    records = [
        evidence(
            "sbi-holdings",
            source_url="https://www.sbigroup.co.jp/news/2026/example.html",
            independence_group="sbi-holdings",
        ),
        evidence(
            "sbi-vc",
            source_url="https://www.sbivc.co.jp/news/example.html",
            independence_group="sbi-vc",
        ),
        evidence(
            "tokyo-sbic",
            source_url="https://www.sbic.co.jp/news/example.html",
            independence_group="tokyo-sbic",
        ),
    ]
    scenario = build(records)["scenarios"][0]

    assert scenario["independent_source_groups_count"] == 2


def test_same_input_order_produces_same_ids_and_fingerprint():
    records = [evidence("z"), evidence("a", stance="contradicts")]
    first = build(records)
    second = build(list(reversed(records)))

    assert first["artifact_id"] == second["artifact_id"]
    assert first["evidence_fingerprint"] == second["evidence_fingerprint"]
    assert first["scenarios"][0]["scenario_id"] == second["scenarios"][0]["scenario_id"]


def test_missing_raw_hash_is_visible_and_never_model_eligible():
    record = evidence("missing-receipt", raw_source_sha256=None)
    result = build([record])
    scenario = result["scenarios"][0]

    assert scenario["receipt_complete"] is False
    assert scenario["raw_hash_present"] is False
    assert scenario["raw_hash_present_count"] == 0
    assert scenario["supporting_evidence"][0]["receipt_status"] == "MISSING_RAW_RECEIPT_HASH"
    assert result["raw_hash_present_count"] == 0
    assert result["receipt_complete"] is False
    assert result["model_eligible"] is False


def test_payload_hash_alone_does_not_claim_a_complete_source_receipt():
    result = build([evidence("hash-only")])
    scenario = result["scenarios"][0]
    item = scenario["supporting_evidence"][0]

    assert item["raw_hash_present"] is True
    assert item["receipt_status"] == "RAW_SHA256_PRESENT_UNVERIFIED"
    assert scenario["raw_hash_present_count"] == 1
    assert scenario["receipt_complete"] is False
    assert result["raw_hash_present_count"] == 1
    assert result["receipt_complete"] is False
    assert result["model_eligible"] is False


def test_invalid_raw_hash_is_rejected():
    with pytest.raises(ScenarioHypothesisError, match="64-character SHA-256"):
        build([evidence("bad-hash", raw_source_sha256="not-a-hash")])


def test_invalid_or_credential_bearing_source_url_is_rejected():
    with pytest.raises(ScenarioHypothesisError, match="HTTP\\(S\\) URL"):
        build([evidence("bad-url", source_url="file:///tmp/source.txt")])
    with pytest.raises(ScenarioHypothesisError, match="embedded credentials"):
        build([evidence("credential-url", source_url="https://user:pass@example.com/a")])


def test_timezone_is_required_for_every_timestamp():
    with pytest.raises(ScenarioHypothesisError, match="must include a timezone"):
        build([evidence("naive", available_at_utc="2026-11-12T02:00:00")])


def test_horizon_must_be_a_positive_non_boolean_integer():
    with pytest.raises(ScenarioHypothesisError, match="positive integer"):
        build_scenario_hypotheses(
            asset="XRP",
            data_cutoff_utc=CUTOFF,
            horizon_seconds=True,
            evidence_records=[],
        )
    with pytest.raises(ScenarioHypothesisError, match="positive integer"):
        build_scenario_hypotheses(
            asset="XRP",
            data_cutoff_utc=CUTOFF,
            horizon_seconds=0,
            evidence_records=[],
        )


def test_duplicate_evidence_ids_are_rejected():
    with pytest.raises(ScenarioHypothesisError, match="duplicate evidence_id"):
        build([evidence("same"), evidence("same", stance="contradicts")])


def test_conflicting_definitions_for_one_hypothesis_id_are_rejected():
    with pytest.raises(ScenarioHypothesisError, match="conflicting definitions"):
        build(
            [
                evidence("one"),
                evidence("two", counter_hypothesis="A different counter-hypothesis."),
            ]
        )


def test_falsification_conditions_are_mandatory():
    with pytest.raises(ScenarioHypothesisError, match="at least one item"):
        build([evidence("unfalsifiable", falsification_conditions=[])])


def test_empty_evidence_returns_an_explicit_non_forecast_state():
    result = build([])

    assert result["scenario_count"] == 0
    assert result["scenarios"] == []
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["directional_forecast"] is False
    assert result["probabilities"] is None
    assert result["model_eligible"] is False
