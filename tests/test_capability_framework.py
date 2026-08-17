from __future__ import annotations

import json

import pytest

from barrot_agent.capability_framework import (
    BenchmarkCase,
    Capability,
    CapabilityRouter,
    ContinualLearningStore,
    Evaluation,
    GovernancePolicy,
    ModelCandidate,
    SafetyError,
    evaluate_benchmark,
    inventory_components,
)


def candidate(model_id: str, output: str, license: str = "MIT") -> ModelCandidate:
    return ModelCandidate(
        model_id,
        frozenset({Capability.REASONING}),
        lambda _prompt: output,
        license=license,
        provenance="model-card:test",
    )


def test_inventory_covers_all_planned_subsystems() -> None:
    assert {
        "inference",
        "orchestration",
        "ingestion",
        "memory",
        "mcp",
        "benchmarking",
        "upgrade",
    } <= inventory_components().keys()


def test_router_selects_best_evaluated_candidate() -> None:
    router = CapabilityRouter(
        [candidate("short", "x"), candidate("long", "useful answer")],
        evaluator=lambda _prompt, output: len(output),
    )
    decision = router.route(Capability.REASONING, "question")
    assert decision.selected.model_id == "long"
    assert decision.alternatives[0].model_id == "short"


def test_router_rejects_unknown_license() -> None:
    router = CapabilityRouter([candidate("x", "answer", "Proprietary")])
    with pytest.raises(SafetyError, match="license"):
        router.route(Capability.REASONING, "question")


def test_policy_blocks_untrusted_personal_data() -> None:
    with pytest.raises(SafetyError, match="personal data"):
        GovernancePolicy().validate_external_data(
            license="MIT", provenance="source:test", contains_personal_data=True
        )


def test_benchmark_requires_expected_terms() -> None:
    case = BenchmarkCase("coding-1", Capability.CODING, "write", ("python",))
    assert evaluate_benchmark(case, "python code").score == 1.0
    assert evaluate_benchmark(case, "javascript").score == 0.0


def test_learning_requires_gates_and_approval(tmp_path) -> None:
    store = ContinualLearningStore(tmp_path / "learning.jsonl")
    with pytest.raises(SafetyError):
        store.propose(
            parent_version="v1",
            changes={"policy": "unsafe"},
            evaluation=Evaluation(1.0, 0.5, 1.0),
            human_approved=True,
        )
    proposal = store.propose(
        parent_version="v1",
        changes={"policy": "safe"},
        evaluation=Evaluation(1.0, 1.0, 1.0),
        human_approved=True,
    )
    store.rollback(proposal.proposal_id, "regression detected")
    records = [json.loads(line) for line in (tmp_path / "learning.jsonl").read_text().splitlines()]
    assert [record["type"] for record in records] == ["proposal", "rollback"]


def test_resource_limit_is_enforced() -> None:
    policy = GovernancePolicy(max_prompt_chars=3)
    router = CapabilityRouter([candidate("x", "answer")], policy=policy)
    with pytest.raises(ValueError, match="resource"):
        router.route(Capability.REASONING, "long")
