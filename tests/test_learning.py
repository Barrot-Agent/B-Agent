"""Tests for the durable Barrot learning ledger."""

import json

import pytest

from barrot_agent.learning import Experience, ExperienceLedger


def test_records_and_reads_experience(tmp_path):
    ledger = ExperienceLedger(tmp_path / "experiences.jsonl")
    original = Experience(
        task="reverse a list",
        success=True,
        score=1.0,
        feedback="passed deterministic test",
        metadata={"benchmark": "smoke"},
    )

    ledger.record(original)

    assert ledger.read() == [original]
    assert ledger.recent(1)[0].metadata["benchmark"] == "smoke"


def test_summary_and_comparison_require_scored_evidence(tmp_path):
    ledger = ExperienceLedger(tmp_path / "experiences.jsonl")
    baseline = [Experience("task", True, score=0.5)]
    candidate = [Experience("task", True, score=0.8)]

    summary = ledger.summarize(candidate)
    comparison = ledger.compare(baseline, candidate, minimum_delta=0.2)

    assert summary == {
        "count": 1,
        "successes": 1,
        "success_rate": 1.0,
        "mean_score": 0.8,
    }
    assert comparison["score_delta"] == pytest.approx(0.3)
    assert comparison["eligible"] is True
    assert ledger.compare(baseline, [Experience("task", True)], 0)["eligible"] is False


def test_rejects_invalid_scores_and_corrupt_records(tmp_path):
    with pytest.raises(ValueError):
        Experience("task", True, score=1.1)

    path = tmp_path / "experiences.jsonl"
    path.write_text(json.dumps({"task": "", "success": True}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid experience at line 1"):
        ExperienceLedger(path).read()
