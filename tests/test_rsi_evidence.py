import pytest

from barrot_agent.rsi.evidence import EvaluationSnapshot, assess_improvement


def test_measured_improvement_requires_paired_runs():
    baseline = EvaluationSnapshot("b1", "sha-a", {"accuracy": 0.7, "latency_ms": 100})
    candidate = EvaluationSnapshot("c1", "sha-b", {"accuracy": 0.8, "latency_ms": 90})
    result = assess_improvement(baseline, candidate, lower_is_better=frozenset({"latency_ms"}))
    assert result.eligible and result.improved
    assert result.metric_deltas["accuracy"] == pytest.approx(0.1)
    assert result.metric_deltas["latency_ms"] == 10 and result.score > 0


def test_regression_blocks_candidate_promotion():
    baseline = EvaluationSnapshot("b1", "sha-a", {"accuracy": 0.8, "safety": 0.99})
    candidate = EvaluationSnapshot("c1", "sha-b", {"accuracy": 0.9, "safety": 0.90})
    result = assess_improvement(baseline, candidate)
    assert not result.eligible and not result.improved
    assert result.regressions == ("safety",) and result.score == 0


def test_incompatible_or_unmeasured_runs_are_rejected():
    baseline = EvaluationSnapshot("b1", "sha-a", {"accuracy": 0.8})
    with pytest.raises(ValueError):
        assess_improvement(baseline, EvaluationSnapshot("b2", "sha-b", {"loss": 0.2}))
    with pytest.raises(ValueError):
        EvaluationSnapshot("b3", "sha-c", {"accuracy": float("nan")})


def test_snapshot_freezes_caller_metrics():
    metrics = {"accuracy": 0.8, "safety": 0.99}
    snapshot = EvaluationSnapshot("b1", "sha-a", metrics)
    metrics["safety"] = float("nan")
    assert snapshot.metrics["safety"] == 0.99
    with pytest.raises(TypeError):
        snapshot.metrics["safety"] = 0.1


def test_non_finite_derived_delta_is_rejected():
    baseline = EvaluationSnapshot("b1", "sha-a", {"metric": -1e308})
    candidate = EvaluationSnapshot("c1", "sha-b", {"metric": 1e308})
    with pytest.raises(ValueError, match="non-finite"):
        assess_improvement(baseline, candidate)


def test_non_positive_aggregate_and_unchanged_runs_are_ineligible():
    baseline = EvaluationSnapshot("b1", "sha-a", {"a": 1.0, "b": 1.0})
    tolerated_decline = EvaluationSnapshot("c1", "sha-b", {"a": 0.91, "b": 1.01})
    result = assess_improvement(baseline, tolerated_decline, tolerances={"a": 0.1})
    assert not result.eligible and not result.improved
    unchanged = EvaluationSnapshot("c2", "sha-c", {"a": 1.0, "b": 1.0})
    result = assess_improvement(baseline, unchanged)
    assert not result.eligible and not result.improved
    assert result.to_dict()["eligible"] is False

def test_aggregate_score_overflow_is_rejected():
    baseline = EvaluationSnapshot("b1", "sha-a", {"a": 1.0, "b": 1.0})
    candidate = EvaluationSnapshot("c1", "sha-b", {"a": 1e308, "b": 1e308})
    with pytest.raises(ValueError, match="aggregate"):
        assess_improvement(baseline, candidate)

def test_same_revision_cannot_be_claimed_as_candidate_change():
    baseline = EvaluationSnapshot("b1", "same-sha", {"accuracy": 0.8})
    candidate = EvaluationSnapshot("c1", "same-sha", {"accuracy": 0.9})
    with pytest.raises(ValueError, match="distinct revisions"):
        assess_improvement(baseline, candidate)
