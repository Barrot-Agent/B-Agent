from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from barrot_agent.research import (
    AdversarialReview,
    ClaimStatus,
    CrossPollinationEngine,
    IndependenceEvaluator,
    LeanVerificationGateway,
    NavierStokesProblemAdapter,
    ResearchCycleRecord,
    ResearchEvidence,
    ResearchState,
    ScientificDiscoveryController,
    StaticResearchProblemAdapter,
    VerificationIndependence,
    is_scientific_discovery_task,
)

SCRIPT_PATH = Path("/home/runner/work/B-Agent/B-Agent/scripts/barrot_agent.py")
BUNDLE_PATH = Path(
    "/home/runner/work/B-Agent/B-Agent/data/research/navier_stokes_research_bundle.json"
)


def load_script_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_bundle(path: Path, *, independent: bool, adversarial_status: str, formal_command: list[str] | None = None) -> Path:
    bundle = {
        "problem": {
            "problem_id": "generic_problem",
            "title": "Generic research problem",
            "domain": "math",
            "primary_question": "Is the claim established?",
            "primary_claims": ["claim.main"],
            "related_problems": [],
            "acceptance_requirements": {
                "formal_verification_required": True,
                "independent_verification_required": True,
                "resolved_adversarial_reviews_required": True,
            },
        },
        "sources": [
            {
                "source_id": "paper",
                "title": "Primary paper",
                "author_or_organization": "Author",
                "source_type": "paper",
                "url": "https://example.invalid/paper",
                "publication_date": "2026-01-01",
                "version": "v1",
                "source_commit": "",
                "sections": ["main theorem"],
                "equations": [],
                "theorem_names": ["main_theorem"],
                "definitions": [],
                "citations": [],
                "relationships": [],
            },
            {
                "source_id": "formal_repo",
                "title": "Formal repo",
                "author_or_organization": "Author",
                "source_type": "formal_repo",
                "url": "https://example.invalid/repo",
                "publication_date": "2026-01-01",
                "version": "lean4",
                "source_commit": "abc123",
                "sections": ["formalization"],
                "equations": [],
                "theorem_names": ["main_theorem"],
                "definitions": [],
                "citations": ["paper"],
                "relationships": [],
            },
            {
                "source_id": "independent_check",
                "title": "Independent verification",
                "author_or_organization": "Independent team",
                "source_type": "independent_report",
                "url": "https://example.invalid/check",
                "publication_date": "2026-01-02",
                "version": "v1",
                "source_commit": "",
                "sections": ["verification"],
                "equations": [],
                "theorem_names": [],
                "definitions": [],
                "citations": [],
                "relationships": [],
            },
        ],
        "claims": [
            {
                "claim_id": "claim.main",
                "statement": "Main theorem statement.",
                "domain": "math",
                "claim_type": "theorem",
                "source": "paper",
                "source_location": "section 1",
                "source_commit": "",
                "assumptions": ["A1", "A2"],
                "dependencies": [],
                "provenance": ["paper"],
            }
        ],
        "evidence": [
            {
                "evidence_id": "paper-support",
                "claim_id": "claim.main",
                "kind": "theorem",
                "summary": "Primary paper states theorem.",
                "source_id": "paper",
                "source_location": "section 1",
                "status": "SUPPORTED",
                "independence": "same_source_confirmation",
                "provenance": ["paper"],
                "details": {"ancestry": "lineage-paper"},
            },
            {
                "evidence_id": "independent-support",
                "claim_id": "claim.main",
                "kind": "independent_verification",
                "summary": "Independent team checked theorem.",
                "source_id": "independent_check",
                "source_location": "section 2",
                "status": "INDEPENDENTLY_VERIFIED",
                "independence": "independent_mathematical_derivation" if independent else "same_source_confirmation",
                "provenance": ["independent_check"],
                "details": {"ancestry": "independent-lineage" if independent else "lineage-paper"},
            },
        ],
        "tracks": [
            {
                "track_id": "proof",
                "role": "proof_construction",
                "strategy": "constructive proof",
                "hypothesis": "claim should hold",
                "assumptions": ["A1"],
                "dependencies": [],
                "focus_claims": ["claim.main"],
                "intermediate_results": [
                    {"claim_id": "claim.main", "summary": "constructed argument", "status": "SUPPORTED"}
                ],
                "evidence": ["paper-support"],
                "failed_approaches": [],
                "unresolved_objections": [],
                "confidence": 0.7,
                "provenance": ["paper"],
            },
            {
                "track_id": "formal",
                "role": "formalization",
                "strategy": "formal proof",
                "hypothesis": "formalization should compile",
                "assumptions": [],
                "dependencies": ["claim.main"],
                "focus_claims": ["claim.formal"],
                "intermediate_results": [
                    {"claim_id": "claim.main", "summary": "formal theorem registered", "status": "FORMALIZED"}
                ],
                "evidence": [],
                "failed_approaches": [],
                "unresolved_objections": [],
                "confidence": 0.8,
                "provenance": ["formal_repo"],
            },
        ],
        "adversarial_reviews": [
            {
                "review_id": "adv-1",
                "claim_id": "claim.main",
                "objections": ["Check missing assumption"],
                "responses": ["Addressed"] if adversarial_status == ClaimStatus.SUPPORTED.value else [],
                "status": adversarial_status,
                "provenance": ["adversarial"],
            }
        ],
        "formal_verification": [
            {
                "verification_id": "formal-1",
                "system": "lean",
                "claim_ids": ["claim.main"],
                "theorem_names": ["main_theorem"],
                "source_files": ["Main.lean"],
                "repository": "https://example.invalid/repo",
                "repository_path": None,
                "source_commit": "abc123",
                "toolchain_version": "lean4",
                "command": formal_command or ["lake", "build"],
                "dependencies": ["Mathlib"],
            }
        ],
        "question_map": [],
    }
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return path


def test_navier_stokes_adapter_loads_authoritative_bundle() -> None:
    adapter = NavierStokesProblemAdapter()
    summary = adapter.source_summary()

    assert summary["problem"]["problem_id"] == "navier_stokes_millennium_prize"
    assert "openai_breakdown_r3" in summary["primary_claims"]
    assert summary["source_count"] >= 5
    assert summary["question_count"] >= 10


def test_navier_stokes_comprehension_queries_are_structured() -> None:
    adapter = NavierStokesProblemAdapter()

    clay = adapter.answer_question("clay_requirements")
    alternative = adapter.answer_question("clay_alternative")
    energy = adapter.answer_question("energy_vs_velocity")
    lean = adapter.answer_question("what_does_lean_verify")

    assert clay["answer"]["alternatives"] == ["C", "D"]
    assert "∂_t u + (u · ∇)u + ∇p = νΔu + f" in clay["answer"]["equations"]
    assert alternative["answer"]["alternatives"][0]["claim_id"] == "openai_breakdown_r3"
    assert energy["answer"]["scaling"]["tau"] == "1 - t"
    assert "NavierStokes.Comparator.navier_stokes_breakdown_R3" in lean["answer"]["theorem_names"]


def test_same_source_confirmation_is_not_independent() -> None:
    evaluator = IndependenceEvaluator()
    result = evaluator.assess(
        [
            ResearchEvidence(
                evidence_id="e1",
                claim_id="c",
                kind="theorem",
                summary="same",
                source_id="s1",
                status=ClaimStatus.SUPPORTED.value,
                independence=VerificationIndependence.SAME_SOURCE.value,
                details={"ancestry": "x"},
            ),
            ResearchEvidence(
                evidence_id="e2",
                claim_id="c",
                kind="theorem",
                summary="same lineage",
                source_id="s2",
                status=ClaimStatus.INDEPENDENTLY_VERIFIED.value,
                independence=VerificationIndependence.INDEPENDENT_DERIVATION.value,
                details={"ancestry": "x"},
            ),
        ]
    )

    assert result["status"] == ClaimStatus.UNRESOLVED.value
    assert result["independent_evidence"] == []
    assert result["blocked_evidence"] == ["e1", "e2"]


def test_navier_stokes_default_cycle_refuses_solution_claim(tmp_path: Path) -> None:
    controller = ScientificDiscoveryController(workspace=tmp_path)
    cycle = controller.run(NavierStokesProblemAdapter())

    assert cycle.status == "no_solution_claim"
    assert cycle.current_state == ResearchState.NO_SOLUTION_CLAIM.value
    assert cycle.acceptance_gate_passed is False
    assert any("independent verification" in item.lower() for item in cycle.unresolved_questions)


def test_failed_lean_compilation_is_recorded(tmp_path: Path) -> None:
    bundle = write_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.SUPPORTED.value)
    controller = ScientificDiscoveryController(workspace=tmp_path)

    cycle = controller.run(
        StaticResearchProblemAdapter(bundle),
        formal_runner=lambda command, repo: {"returncode": 1, "stdout": "", "stderr": f"failed {command} {repo}"},
    )

    assert cycle.status == "no_solution_claim"
    assert cycle.formal_verifications[0]["compiled"] is False
    assert cycle.formal_verifications[0]["status"] == ClaimStatus.UNRESOLVED.value


def test_successful_formal_verification_and_independence_can_complete(tmp_path: Path) -> None:
    bundle = write_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.SUPPORTED.value)
    controller = ScientificDiscoveryController(workspace=tmp_path)

    cycle = controller.run(
        StaticResearchProblemAdapter(bundle),
        formal_runner=lambda command, repo: {
            "returncode": 0,
            "stdout": f"ok {command} {repo}",
            "stderr": "",
            "independently_verified": True,
        },
    )

    assert cycle.status == "complete"
    assert cycle.current_state == ResearchState.COMPLETE.value
    assert cycle.problem_resolution_status == ClaimStatus.INDEPENDENTLY_VERIFIED.value
    assert cycle.formal_verifications[0]["compiled"] is True


def test_adversarial_contradiction_blocks_acceptance(tmp_path: Path) -> None:
    bundle = write_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.CHALLENGED.value)
    controller = ScientificDiscoveryController(workspace=tmp_path)

    cycle = controller.run(
        StaticResearchProblemAdapter(bundle),
        formal_runner=lambda command, repo: {"returncode": 0, "stdout": "ok", "stderr": ""},
    )

    assert cycle.status == "no_solution_claim"
    assert any("adversarial mathematical objection" in item.lower() for item in cycle.unresolved_questions)


def test_cross_pollination_preserves_provenance_and_skips_duplicates() -> None:
    adapter = NavierStokesProblemAdapter()
    _, _, _, _, tracks, _, _, _ = adapter.ingest()
    transfers = CrossPollinationEngine().synthesize(tracks)

    assert transfers
    assert any(item.result == "duplicate_skipped" for item in transfers)
    assert all(item.provenance for item in transfers)


def test_unsupported_formal_command_is_rejected() -> None:
    gateway = LeanVerificationGateway()
    try:
        gateway.verify({"system": "lean", "command": ["python", "hack.py"], "theorem_names": [], "source_files": [], "repository": ""})
    except Exception as exc:  # noqa: BLE001
        assert "Unsupported formal verification command" in str(exc)
    else:
        raise AssertionError("expected unsupported command rejection")


def test_research_cycle_persists_and_is_idempotent(tmp_path: Path) -> None:
    bundle = write_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.SUPPORTED.value)
    controller = ScientificDiscoveryController(workspace=tmp_path)
    adapter = StaticResearchProblemAdapter(bundle)

    first = controller.run(adapter, formal_runner=lambda command, repo: {"returncode": 0, "stdout": "ok", "stderr": ""})
    second = controller.run(adapter, formal_runner=lambda command, repo: {"returncode": 1, "stdout": "bad", "stderr": "bad"})

    ledger = tmp_path / ".git" / "barrot_research" / "claim_ledger.json"
    assert ledger.exists()
    assert second.cycle_id == first.cycle_id
    assert second.status == first.status


def test_scientific_discovery_task_detection() -> None:
    assert is_scientific_discovery_task("Navier-Stokes review", "formal verification") is True
    assert is_scientific_discovery_task("Bugfix", "repair parser") is False


def test_script_routes_scientific_discovery_tasks(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", "Investigate the Navier-Stokes Millennium Prize claim with Lean formal verification.")
    monkeypatch.setenv("TASK_TITLE", "Navier-Stokes research")
    monkeypatch.setenv("ISSUE_NUMBER", "42")
    monkeypatch.setenv("BRANCH", "barrot/task-42")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    module = load_script_module("barrot_agent_science_script_test")
    calls: dict[str, object] = {}

    class FakeCycle:
        def __init__(self):
            self.status = "no_solution_claim"

        def to_dict(self):
            return {
                "cycle_id": "science-1",
                "problem_id": "navier_stokes_millennium_prize",
                "status": "no_solution_claim",
                "current_state": ResearchState.NO_SOLUTION_CLAIM.value,
                "state_history": [ResearchState.IDLE.value, ResearchState.NO_SOLUTION_CLAIM.value],
                "problem_resolution_status": ClaimStatus.UNRESOLVED.value,
                "acceptance_gate_passed": False,
                "sources": [],
                "claims": [],
                "tracks": [],
                "cross_pollination": [],
                "formal_verifications": [],
                "adversarial_reviews": [],
                "unresolved_questions": ["Independent verification remains incomplete."],
                "problem": {},
            }

    class FakeScientificDiscoveryController:
        def __init__(self, **kwargs):
            calls["init"] = kwargs

        def run(self, adapter):
            calls["adapter"] = adapter
            return FakeCycle()

    monkeypatch.setattr(module, "configure_git", lambda: calls.setdefault("configured", True))
    monkeypatch.setattr(module, "checkout_branch", lambda branch: calls.setdefault("branch", branch))
    monkeypatch.setattr(module, "ScientificDiscoveryController", FakeScientificDiscoveryController)
    monkeypatch.setattr(module, "write_collaboration_record", lambda cycle: calls.setdefault("record", cycle))
    monkeypatch.setattr(module, "post_issue_comment", lambda message: calls.setdefault("comment", message))
    monkeypatch.setattr(module, "NavierStokesProblemAdapter", lambda: "adapter")

    module.main()

    assert calls["adapter"] == "adapter"
    assert "record" in calls
    assert "scientific discovery recorded" in str(calls["comment"]).lower()
