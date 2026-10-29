from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from barrot_agent.creative import ProductionDirector
from barrot_agent.research import (
    AnthropicFermatBenchmarkAdapter,
    AdversarialReview,
    ClaimStatus,
    CrossPollinationEngine,
    FormalVerificationStatus,
    IndependenceEvaluator,
    LeanVerificationGateway,
    NavierStokesProblemAdapter,
    ResearchCycleRecord,
    ResearchEvidence,
    ResearchState,
    ScientificDiscoveryController,
    StaticResearchProblemAdapter,
    ResearchTrack,
    VerificationIndependence,
    is_scientific_discovery_task,
    should_route_scientific_discovery,
    select_scientific_problem_adapter,
)

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "barrot_agent.py"
BUNDLE_PATH = Path(
    str(Path(__file__).resolve().parents[1] / "data" / "research" / "navier_stokes_research_bundle.json")
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
    assert cycle.formal_verifications[0]["status"] == FormalVerificationStatus.BUILD_ATTEMPTED.value


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
    assert cycle.formal_verifications[0]["status"] == FormalVerificationStatus.INDEPENDENTLY_CHECKED.value


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


def test_research_cycle_persists_and_starts_new_cycle_after_terminal_completion(tmp_path: Path) -> None:
    bundle = write_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.SUPPORTED.value)
    controller = ScientificDiscoveryController(workspace=tmp_path)
    adapter = StaticResearchProblemAdapter(bundle)

    first = controller.run(adapter, formal_runner=lambda command, repo: {"returncode": 0, "stdout": "ok", "stderr": ""})
    second = controller.run(adapter, formal_runner=lambda command, repo: {"returncode": 1, "stdout": "bad", "stderr": "bad"})

    ledger = tmp_path / ".git" / "barrot_research" / "claim_ledger.json"
    assert ledger.exists()
    assert second.cycle_id != first.cycle_id
    assert second.status in {"complete", "no_solution_claim", "failed", "blocked"}


def test_research_cycle_can_resume_from_checkpoint(tmp_path: Path) -> None:
    bundle = write_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.SUPPORTED.value)
    controller = ScientificDiscoveryController(workspace=tmp_path)
    adapter = StaticResearchProblemAdapter(bundle)

    first = controller.run(adapter, stop_after_state=ResearchState.SYNTHESIS)
    resumed = controller.run(
        adapter,
        formal_runner=lambda command, repo: {
            "returncode": 0,
            "stdout": "ok",
            "stderr": "",
            "independently_verified": True,
        },
    )

    assert first.status == "checkpointed"
    assert resumed.resumed_from_cycle_id == first.cycle_id
    assert resumed.status == "complete"
    assert resumed.checkpoints


def test_cross_pollination_blocks_invalid_circular_and_contradictory_transfers() -> None:
    engine = CrossPollinationEngine()
    transfers = engine.synthesize(
        [
            ResearchTrack(
                track_id="circular-source",
                role="proof_construction",
                strategy="derive estimate",
                hypothesis="velocity remains bounded",
                dependencies=["recipient"],
                focus_claims=["claim.main"],
                intermediate_results=[{"claim_id": "claim.main", "summary": "lemma A", "status": "SUPPORTED"}],
                provenance=["paper"],
            ),
            ResearchTrack(
                track_id="recipient",
                role="counterexample_search",
                strategy="seek blowup",
                hypothesis="velocity is not bounded",
                dependencies=["claim.main"],
                focus_claims=["claim.alt"],
                provenance=["counterexample"],
            ),
            ResearchTrack(
                track_id="missing-provenance",
                role="literature_research",
                strategy="survey",
                hypothesis="collect references",
                focus_claims=["claim.side"],
                intermediate_results=[{"claim_id": "claim.side", "summary": "lemma B", "status": "SUPPORTED"}],
                provenance=[],
            ),
            ResearchTrack(
                track_id="contradiction-source",
                role="alternative_derivation",
                strategy="derive boundedness",
                hypothesis="velocity remains bounded",
                focus_claims=["claim.bound"],
                intermediate_results=[{"claim_id": "claim.main", "summary": "lemma C", "status": "SUPPORTED"}],
                provenance=["paper-2"],
            ),
        ]
    )

    assert any(item.result == "circular_blocked" for item in transfers)
    assert any(item.result == "contradictory_transfer" for item in transfers)
    assert any(item.result == "invalid_transfer" for item in transfers)


def test_source_team_formal_verification_does_not_imply_independence() -> None:
    evaluator = IndependenceEvaluator()
    result = evaluator.assess(
        [
            ResearchEvidence(
                evidence_id="team-formal",
                claim_id="claim.main",
                kind="formalization",
                summary="source team proved theorem in Lean",
                source_id="formal_repo",
                status=ClaimStatus.FORMALLY_VERIFIED.value,
                independence=VerificationIndependence.SOURCE_TEAM_FORMAL.value,
                details={"ancestry": "source-team"},
            )
        ]
    )

    assert result["status"] == ClaimStatus.UNRESOLVED.value
    assert result["independent_evidence"] == []


def test_creative_engine_records_pending_media_without_claiming_generation(tmp_path: Path) -> None:
    record = ProductionDirector(tmp_path).run()

    assert record.status == "PENDING"
    assert len(record.artists) == 3
    assert len(record.songs) == 3
    assert any(asset["status"] == "PENDING" for asset in record.assets)
    assert record.completion_gate["satisfied"] is False


def test_scientific_discovery_task_detection() -> None:
    assert is_scientific_discovery_task("Navier-Stokes review", "formal verification") is True
    assert is_scientific_discovery_task("FLT benchmark", "Fermat theorem import") is True
    assert is_scientific_discovery_task("Bugfix", "repair parser") is False


def test_scientific_route_requires_explicit_mode() -> None:
    title = "Add evidence-graded Millennium Problems research and AI-claim registry"
    body = "Track Navier-Stokes, Lean formalizations, and the seven Millennium Prize problems."

    assert should_route_scientific_discovery("engineering", title, body) is False
    assert should_route_scientific_discovery("scientific_discovery", title, body) is True


def test_scientific_problem_selection_chooses_flt_adapter() -> None:
    adapter = select_scientific_problem_adapter("Formalizing Fermat's Last Theorem", "lean theorem benchmark")

    assert isinstance(adapter, AnthropicFermatBenchmarkAdapter)


def test_script_routes_scientific_discovery_tasks(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", "Investigate the Navier-Stokes Millennium Prize claim with Lean formal verification.")
    monkeypatch.setenv("TASK_TITLE", "Navier-Stokes research")
    monkeypatch.setenv("TASK_MODE", "scientific_discovery")
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
    monkeypatch.setattr(module, "persist_scientific_discovery", lambda cycle: calls.setdefault("persistence", {"remote_persisted": True}))
    monkeypatch.setattr(module, "post_issue_comment", lambda message: calls.setdefault("comment", message))
    monkeypatch.setattr(module, "select_scientific_problem_adapter", lambda title, body: "adapter")

    module.main()

    assert calls["adapter"] == "adapter"
    assert "persistence" in calls
    assert "persisted to the task branch" in str(calls["comment"]).lower()
    assert "scientific discovery recorded" in str(calls["comment"]).lower()


def test_checkout_branch_resumes_remote_branch_and_rejects_unsafe_names(monkeypatch) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    module = load_script_module("barrot_agent_resume_branch_test")
    calls: list[list[str]] = []

    def fake_run(args, *, check=True, quiet=False):
        calls.append(args)
        return module.subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(module, "run", fake_run)
    module.checkout_branch("barrot/task-42")
    assert calls[0][1] == "fetch"
    assert "refs/remotes/origin/barrot/task-42" in calls[0][3]
    assert calls[1] == ["git", "checkout", "-B", "barrot/task-42", "origin/barrot/task-42"]

    import pytest
    with pytest.raises(ValueError, match="Invalid Barrot task branch"):
        module.checkout_branch("../main")


def test_scientific_discovery_persistence_commits_pushes_and_opens_draft_pr(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("ISSUE_NUMBER", "42")
    monkeypatch.setenv("BRANCH", "barrot/task-42")
    monkeypatch.setenv("TASK_TITLE", "Navier-Stokes research")
    module = load_script_module("barrot_agent_persist_science_test")
    module.ROOT = tmp_path
    calls: list[list[str]] = []
    pr_calls: list[list[str]] = []

    def write_record(cycle):
        record_dir = tmp_path / ".barrot" / "collaboration_records"
        record_dir.mkdir(parents=True, exist_ok=True)
        latest = record_dir / "latest_scientific_discovery.json"
        latest.write_text(json.dumps(cycle), encoding="utf-8")
        (record_dir / "cycle-42.json").write_text(json.dumps(cycle), encoding="utf-8")
        return latest

    def fake_run(args, *, check=True, quiet=False):
        calls.append(args)
        if args[1:4] == ["diff", "--cached", "--quiet"]:
            return module.subprocess.CompletedProcess(args, 1, stdout="", stderr="")
        if args[1:3] == ["rev-parse", "HEAD"]:
            return module.subprocess.CompletedProcess(args, 0, stdout="abc123\\n", stderr="")
        return module.subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    def fake_run_gh(args):
        pr_calls.append(args)
        return module.subprocess.CompletedProcess(args, 0, stdout="draft PR created", stderr="")

    monkeypatch.setattr(module, "write_collaboration_record", write_record)
    monkeypatch.setattr(module, "run", fake_run)
    monkeypatch.setattr(module, "run_gh", fake_run_gh)
    cycle = {
        "cycle_id": "cycle-42",
        "problem_id": "navier_stokes_millennium_prize",
        "status": "no_solution_claim",
        "acceptance_gate_passed": False,
        "unresolved_questions": ["Independent verification remains incomplete."],
    }

    result = module.persist_scientific_discovery(cycle)

    assert result["remote_persisted"] is True
    assert any(args[:3] == ["git", "push", "--set-upstream"] for args in calls)
    assert "--draft" in pr_calls[0]
    assert "--head" in pr_calls[0] and "barrot/task-42" in pr_calls[0]
    saved = json.loads((tmp_path / ".barrot" / "collaboration_records" / "latest_scientific_discovery.json").read_text(encoding="utf-8"))
    assert saved["cycle_id"] == "cycle-42"
    assert saved["acceptance_gate_passed"] is False


def test_scientific_evidence_survives_real_git_push_and_fresh_clone(tmp_path: Path, monkeypatch) -> None:
    import subprocess

    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("ISSUE_NUMBER", "42")
    monkeypatch.setenv("BRANCH", "barrot/task-42")
    monkeypatch.setenv("TASK_TITLE", "Navier-Stokes research")
    module = load_script_module("barrot_agent_real_git_persistence_test")
    remote = tmp_path / "origin.git"
    workspace = tmp_path / "workspace"
    resumed = tmp_path / "resumed"

    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True, text=True)
    workspace.mkdir()
    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "tests@barrot.invalid"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "Barrot Test"], cwd=workspace, check=True)
    (workspace / "README.md").write_text("test repository\\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=workspace, check=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=workspace, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=workspace, check=True, capture_output=True, text=True)

    module.ROOT = workspace
    module.BRANCH = "barrot/task-42"
    module.REPO = "Barrot-Agent/B-Agent"
    module.ISSUE = "42"
    module.TITLE = "Navier-Stokes research"
    module.checkout_branch(module.BRANCH)

    pr_calls: list[list[str]] = []

    def fake_run_gh(args):
        pr_calls.append(args)
        return module.subprocess.CompletedProcess(args, 0, stdout="draft PR created", stderr="")

    monkeypatch.setattr(module, "run_gh", fake_run_gh)
    cycle = {
        "cycle_id": "cycle-42",
        "problem_id": "navier_stokes_millennium_prize",
        "status": "no_solution_claim",
        "acceptance_gate_passed": False,
        "state_history": ["IDLE", "NO_SOLUTION_CLAIM"],
        "sources": [{"source_id": "clay", "url": "https://www.claymath.org/"}],
        "claims": [],
        "unresolved_questions": ["Independent verification remains incomplete."],
    }
    persisted = module.persist_scientific_discovery(cycle)
    assert persisted["remote_persisted"] is True
    assert "--draft" in pr_calls[0]

    subprocess.run(["git", "clone", str(remote), str(resumed)], check=True, capture_output=True, text=True)
    module.ROOT = resumed
    module.checkout_branch("barrot/task-42")
    saved_path = resumed / ".barrot" / "collaboration_records" / "latest_scientific_discovery.json"
    saved = json.loads(saved_path.read_text(encoding="utf-8"))
    assert saved["cycle_id"] == "cycle-42"
    assert saved["problem_id"] == "navier_stokes_millennium_prize"
    assert saved["remaining_blockers"] == ["Independent verification remains incomplete."]


def test_new_research_cycle_imports_prior_committed_evidence_and_restarts_terminal_cycle(tmp_path: Path) -> None:
    bundle = write_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.SUPPORTED.value)
    record_dir = tmp_path / ".barrot" / "collaboration_records"
    record_dir.mkdir(parents=True)
    prior = {
        "cycle_id": "prior-cycle",
        "problem_id": "generic_problem",
        "evidence": {
            "sources": [{
                "source_id": "prior.source", "title": "Prior source",
                "author_or_organization": "Barrot", "source_type": "prior_cycle",
                "url": "https://example.org/prior"
            }],
            "claims": [{
                "claim_id": "prior.claim", "statement": "Prior scoped claim",
                "domain": "math", "claim_type": "theorem", "source": "prior.source",
                "provenance": ["prior-cycle"]
            }],
            "evidence": [{
                "evidence_id": "prior.evidence", "claim_id": "prior.claim",
                "kind": "unresolved_question", "summary": "Prior evidence remains incomplete.",
                "source_id": "prior.source", "provenance": ["prior-cycle"]
            }],
            "tracks": [{
                "track_id": "prior.track", "failed_approaches": ["Do not repeat failed approach X."],
                "unresolved_objections": ["Assumption Y still needs proof."]
            }],
            "unresolved_questions": ["Prior verification is incomplete."]
        }
    }
    (record_dir / "prior-cycle.json").write_text(json.dumps(prior), encoding="utf-8")
    adapter = StaticResearchProblemAdapter(bundle)
    controller = ScientificDiscoveryController(workspace=tmp_path)

    first = controller.run(adapter)
    assert any(item["source_id"] == "prior.source" for item in first.sources)
    assert any(item["claim_id"] == "prior.claim" for item in first.claims)
    assert any(item["evidence_id"] == "prior.evidence" for item in first.evidence)
    assert any("Prior verification is incomplete." in item.get("prompt", "") for item in first.questions)
    assert any("Do not repeat failed approach X." in item.get("prompt", "") for item in first.questions)

    second = controller.run(adapter)
    assert second.cycle_id != first.cycle_id
    assert any(item["claim_id"] == "prior.claim" for item in second.claims)


def test_provider_backed_track_execution_is_recorded_without_promoting_claims(tmp_path: Path) -> None:
    bundle = write_bundle(tmp_path / "bundle.json", independent=False, adversarial_status=ClaimStatus.CHALLENGED.value)
    adapter = StaticResearchProblemAdapter(bundle)
    controller = ScientificDiscoveryController(workspace=tmp_path)
    calls: list[str] = []

    def execute(track):
        calls.append(track.track_id)
        return {
            "provider": "test-provider/model-v1",
            "result": {
                "findings": [f"Provisional finding for {track.track_id}"],
                "open_questions": ["What assumption remains unproven?"],
                "counterarguments": ["The supplied evidence may not imply the full theorem."],
                "recommended_checks": ["Run an independent derivation."],
            },
        }

    cycle = controller.run(adapter, track_executor=execute)
    assert calls
    for track in cycle.tracks:
        record = track["execution_records"][-1]
        assert record["provider"] == "test-provider/model-v1"
        assert record["duration_ms"] >= 0
        assert record["response"]["provider_backed"] is True
        assert record["response"]["intermediate_results"][-1]["status"] == "MODEL_GENERATED_UNVERIFIED"
        assert any("Model-generated counterargument" in item for item in track["unresolved_objections"])
    assert all(claim["acceptance_status"] == ClaimStatus.UNRESOLVED.value for claim in cycle.claims)
