from __future__ import annotations

import json
from pathlib import Path

import pytest

from barrot_agent.research.millennium_claim_registry import (
    ClaimLedger,
    ClaimRecord,
    EvidenceGrade,
    MILLENNIUM_PROBLEMS,
)


def sample_claim(**overrides):
    payload = dict(
        claim_id="navier-ai-claim-2026-01",
        problem_id="navier_stokes",
        statement="The source claims a finite-time breakdown construction for a specified formulation.",
        source_url="https://example.org/paper",
        source_title="Research claim",
        source_publisher="Research group",
        publication_date="2026-09-08",
        theorem_scope="Claimed theorem only; equivalence to the full Clay statement not yet established.",
        evidence_grade=EvidenceGrade.CLAIMED.value,
        unresolved_obligations=["Compare assumptions and conclusion with the official Clay statement."],
    )
    payload.update(overrides)
    return ClaimRecord(**payload)


def test_registry_contains_all_seven_with_official_sources_and_baselines():
    assert len(MILLENNIUM_PROBLEMS) == 7
    assert all(item["official_source"].startswith("https://www.claymath.org/") for item in MILLENNIUM_PROBLEMS.values())
    assert sum(item["baseline_status"] == "OPEN" for item in MILLENNIUM_PROBLEMS.values()) == 6
    assert MILLENNIUM_PROBLEMS["poincare_conjecture"]["baseline_status"] == "SOLVED_HISTORICAL"


def test_claim_requires_source_and_known_problem():
    with pytest.raises(ValueError, match="source_url"):
        sample_claim(source_url="paper.pdf").validate()
    with pytest.raises(ValueError, match="unknown Millennium problem"):
        sample_claim(problem_id="unknown").validate()


def test_unreviewed_claim_cannot_be_marked_accepted():
    with pytest.raises(ValueError, match="independent review"):
        sample_claim(evidence_grade=EvidenceGrade.ACCEPTED_RECOGNIZED.value).validate()


def test_poincare_historical_baseline_cannot_be_reset_by_new_claim():
    with pytest.raises(ValueError, match="solved historically"):
        sample_claim(problem_id="poincare_conjecture").validate()


def test_ledger_survives_recreation_and_keeps_status_history(tmp_path: Path):
    path = tmp_path / "claims.jsonl"
    first = ClaimLedger(path)
    first.record(sample_claim())
    second = ClaimLedger(path)
    loaded = second.list_claims()
    assert len(loaded) == 1
    assert loaded[0]["claim_id"] == "navier-ai-claim-2026-01"
    assert loaded[0]["status_history"][0]["grade"] == EvidenceGrade.CLAIMED.value
    second.record(sample_claim(evidence_grade=EvidenceGrade.FORMALIZED.value, formalization_scope="Only named theorem; full Clay equivalence unverified."))
    reopened = ClaimLedger(path).list_claims()
    assert len(reopened) == 2
    assert [item["evidence_grade"] for item in reopened] == [EvidenceGrade.CLAIMED.value, EvidenceGrade.FORMALIZED.value]
    assert all(item["source_url"] == "https://example.org/paper" for item in reopened)


def test_seed_claim_is_provenance_bound_and_not_marked_solved():
    seed = Path(__file__).resolve().parents[1] / "data" / "research" / "millennium_claims_seed.jsonl"
    record = json.loads(seed.read_text(encoding="utf-8").splitlines()[0])
    assert record["problem_id"] == "navier_stokes"
    assert record["evidence_grade"] == EvidenceGrade.UNRESOLVED.value
    assert record["source_url"].startswith("https://")
    assert record["counterevidence"]
    assert record["unresolved_obligations"]
    assert not record["independent_review"]


def test_claim_id_cannot_be_reassigned_to_another_problem(tmp_path: Path):
    ledger = ClaimLedger(tmp_path / "claims.jsonl")
    ledger.record(sample_claim())
    with pytest.raises(ValueError, match="reassigned"):
        ledger.record(sample_claim(problem_id="riemann_hypothesis"))
