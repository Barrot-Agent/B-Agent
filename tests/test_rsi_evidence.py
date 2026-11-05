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
    with pytest.raises(ValueError): assess_improvement(baseline, EvaluationSnapshot("b2", "sha-b", {"loss": 0.2}))
    with pytest.raises(ValueError): EvaluationSnapshot("b3", "sha-c", {"accuracy": float("nan")})
