from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from barrot_agent.orchestration.repository_repair import (
    CommandEvidence,
    ProjectIdentity,
    RepairError,
    RepairState,
    RepositoryRepairController,
    SyncController,
    WorkQueueController,
)
from barrot_agent.orchestration.shared_runtime import ControlledToolExecutor, ToolRequest
from barrot_agent.research import (
    ClaimStatus,
    ConvergenceScenarioEngine,
    ConvergenceStatus,
    NavierStokesProblemAdapter,
    ScenarioRelationshipType,
    ScientificDiscoveryController,
    StaticResearchProblemAdapter,
)
from tests.v3_test_harness import (
    FakeBrain,
    defect_command,
    failure_command,
    git,
    init_repo,
    repair_payload,
    run_cycle,
    success_command,
    timeout_command,
    write_science_bundle,
)

REPO_ROOT = Path("/home/runner/work/B-Agent/B-Agent")
ARTIFACT_DIR = REPO_ROOT / ".barrot" / "collaboration_records" / "v3_acceptance_matrix"
SUMMARY_PATH = REPO_ROOT / ".barrot" / "collaboration_records" / "barrot_v3_acceptance_matrix.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def record_case(case_id: str, description: str, command: str, components: list[str], fn=None, *, execute: bool = True, reason: str = "") -> dict[str, object]:
    timestamp = now_iso()
    evidence_path = ARTIFACT_DIR / f"{case_id}.json"
    if not execute:
        record = {
            "TEST_ID": case_id,
            "DESCRIPTION": description,
            "STATUS": "DESIGNED — NOT EXECUTED",
            "COMMAND": command,
            "RESULT": reason,
            "EVIDENCE_PATH": str(evidence_path),
            "EXECUTION_TIMESTAMP": timestamp,
            "COMPONENTS_TESTED": components,
        }
        evidence_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return record
    result = fn()
    record = {
        "TEST_ID": case_id,
        "DESCRIPTION": description,
        "STATUS": "VERIFIED",
        "COMMAND": command,
        "RESULT": result,
        "EVIDENCE_PATH": str(evidence_path),
        "EXECUTION_TIMESTAMP": timestamp,
        "COMPONENTS_TESTED": components,
    }
    evidence_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return record


def test_v3_acceptance_matrix(tmp_path: Path) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    for path in ARTIFACT_DIR.glob("case-*.json"):
        path.unlink()
    records: list[dict[str, object]] = []

    records.append(
        record_case(
            "case-01",
            "healthy repository returns NO_REPAIR_REQUIRED",
            "RepositoryRepairController.run(no defect)",
            ["RepositoryRepairController", "Validator", "CompletionGate"],
            lambda: _case_healthy_repository(tmp_path / "case01"),
        )
    )
    records.append(
        record_case(
            "case-02",
            "real defect enters deterministic repair lifecycle",
            "RepositoryRepairController.run(repair defect)",
            ["RepositoryRepairController", "PatchExecutor", "Validator"],
            lambda: _case_real_defect(tmp_path / "case02"),
        )
    )
    records.append(
        record_case(
            "case-03",
            "model success text without concrete change cannot complete repair",
            "RepositoryRepairController.run(no-op patch)",
            ["RepositoryRepairController", "PatchExecutor", "CompletionGate"],
            lambda: _case_model_claims_success_without_change(tmp_path / "case03"),
        )
    )
    records.append(record_case("case-04", "invalid JSON fails safely", "RepositoryRepairController.run(invalid JSON)", ["RepairPlanner"], lambda: _case_invalid_json(tmp_path / "case04")))
    records.append(record_case("case-05", "tool-call conflict is normalized", "RepositoryRepairController.run(tool conflict)", ["RepairPlanner"], lambda: _case_tool_conflict(tmp_path / "case05")))
    records.append(record_case("case-06", "unsupported tool is rejected", "ControlledToolExecutor.execute(unsupported)", ["ControlledToolExecutor"], lambda: _case_unsupported_tool(tmp_path / "case06")))
    records.append(record_case("case-07", "unsafe path is blocked", "RepositoryRepairController.run(unsafe patch path)", ["PatchExecutor"], lambda: _case_unsafe_path(tmp_path / "case07")))
    records.append(record_case("case-08", "missing precondition blocks patch", "RepositoryRepairController.run(missing old text)", ["PatchExecutor"], lambda: _case_missing_precondition(tmp_path / "case08")))
    records.append(record_case("case-09", "validation failure rolls back", "RepositoryRepairController.run(validation failure)", ["Validator", "RepositoryRepairController"], lambda: _case_validation_failure(tmp_path / "case09")))
    records.append(record_case("case-10", "resolution failure blocks COMPLETE", "RepositoryRepairController.run(resolution failure)", ["Validator", "CompletionGate"], lambda: _case_resolution_failure(tmp_path / "case10")))
    records.append(record_case("case-11", "commit failure blocks lifecycle", "RepositoryRepairController.run(commit failure)", ["GitGateway", "RepositoryRepairController"], lambda: _case_commit_failure(tmp_path / "case11")))
    records.append(record_case("case-12", "remote verification failure blocks COMPLETE", "RepositoryRepairController.run(remote verification failure)", ["RemoteVerifier", "CompletionGate"], lambda: _case_remote_verification_failure(tmp_path / "case12")))
    records.append(record_case("case-13", "duplicate repair attempt is idempotent and blocks repeated false progress", "RepositoryRepairController.run(duplicate attempt)", ["DurableCycleStore", "RepositoryRepairController"], lambda: _case_duplicate_repair(tmp_path / "case13")))
    records.append(record_case("case-14", "empty namespace cannot overwrite valid identity", "SyncController.run(empty namespace)", ["SyncController", "ProjectIdentity"], lambda: _case_empty_namespace(tmp_path / "case14")))
    records.append(record_case("case-15", "repeated identical API response hits bounded retry exhaustion", "SyncController.run(unchanged observation)", ["SyncController"], lambda: _case_repeated_api_response(tmp_path / "case15")))
    records.append(record_case("case-16", "API outage is classified without false completion", "RepositoryRepairController.run(provider unavailable)", ["RepairPlanner"], lambda: _case_api_outage(tmp_path / "case16")))
    records.append(record_case("case-17", "interruption and resume preserve durable work state", "WorkQueueController.run(resume)", ["WorkQueueController", "DurableWorkStore"], lambda: _case_interruption_resume(tmp_path / "case17")))
    records.append(record_case("case-18", "retry exhaustion blocks repeated unchanged repair plans", "RepositoryRepairController.run(retry exhaustion)", ["RepositoryRepairController", "DurableCycleStore"], lambda: _case_retry_exhaustion(tmp_path / "case18")))
    records.append(record_case("case-19", "false mathematical proof does not satisfy acceptance", "ScientificDiscoveryController.run(source-team only)", ["ScientificDiscoveryController", "CompletionGate"], lambda: _case_false_mathematical_proof(tmp_path / "case19")))
    records.append(record_case("case-20", "missing mathematical assumptions remain unresolved", "ScientificDiscoveryController.run(adversarial challenge)", ["ScientificDiscoveryController", "AdversarialReview"], lambda: _case_missing_math_assumptions(tmp_path / "case20")))
    records.append(record_case("case-21", "failed formalization is recorded without verification", "ScientificDiscoveryController.run(unsupported formal command)", ["LeanVerificationGateway"], lambda: _case_failed_formalization(tmp_path / "case21")))
    records.append(record_case("case-22", "Lean failure remains unresolved", "ScientificDiscoveryController.run(formal runner failure)", ["LeanVerificationGateway", "ScientificDiscoveryController"], lambda: _case_lean_failure(tmp_path / "case22")))
    records.append(record_case("case-23", "adversarial contradiction blocks acceptance", "ScientificDiscoveryController.run(challenged review)", ["ScientificDiscoveryController", "AdversarialReview"], lambda: _case_adversarial_contradiction(tmp_path / "case23")))
    records.append(record_case("case-24", "conflicting research groups are preserved as contradiction", "ConvergenceScenarioEngine.analyze_observations(conflict)", ["ConvergenceScenarioEngine"], lambda: _case_conflicting_research_groups()))
    records.append(record_case("case-25", "invalid cross-pollination is preserved and blocked", "CrossPollinationEngine.synthesize(invalid transfer)", ["CrossPollinationEngine"], lambda: _case_invalid_cross_pollination()))
    records.append(record_case("case-26", "provenance collision does not create false independence", "ConvergenceScenarioEngine.analyze_observations(shared ancestry)", ["ConvergenceScenarioEngine"], lambda: _case_provenance_collision()))
    records.append(record_case("case-27", "fake independent verification from inherited evidence is rejected", "ScientificDiscoveryController.run(non-independent evidence)", ["ScientificDiscoveryController", "IndependenceEvaluator"], lambda: _case_fake_independent_verification(tmp_path / "case27")))
    records.append(record_case("case-28", "successful formal verification is recorded but not conflated with independence", "ScientificDiscoveryController.run(formal success)", ["ScientificDiscoveryController", "LeanVerificationGateway"], lambda: _case_successful_formal_verification(tmp_path / "case28")))
    records.append(record_case("case-29", "genuine independent mathematical verification requires external evidence", "External independent mathematical verification", ["ScientificDiscoveryController", "IndependenceEvaluator"], execute=False, reason="Genuine third-party independent mathematical evidence is not available in this environment; Barrot can verify the NOT_AVAILABLE/UNRESOLVED path but must not fabricate independent verification."))
    records.append(record_case("case-30", "scientific UNRESOLVED path remains explicit", "ScientificDiscoveryController.run(default unresolved)", ["ScientificDiscoveryController", "CompletionGate"], lambda: _case_unresolved(tmp_path / "case30")))

    summary = {
        "generated_at": now_iso(),
        "records": records,
        "verified_count": sum(1 for item in records if item["STATUS"] == "VERIFIED"),
        "designed_not_executed_count": sum(1 for item in records if item["STATUS"] == "DESIGNED — NOT EXECUTED"),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    assert len(records) == 30
    assert summary["verified_count"] == 29
    assert summary["designed_not_executed_count"] == 1


def _case_healthy_repository(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path)
    (workspace / path).write_text('FLAG = "FIXED"\n', encoding="utf-8")
    cycle = run_cycle(workspace, FakeBrain(repair_payload(path)))
    assert cycle.status == "no_repair_required"
    assert cycle.current_state == RepairState.NO_REPAIR_REQUIRED.value
    return {"status": cycle.status, "state": cycle.current_state}


def _case_real_defect(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path, origin=True)
    cycle = run_cycle(workspace, FakeBrain(repair_payload(path)))
    assert cycle.issue_identified is True
    assert cycle.issue_reproduced is True
    assert RepairState.PATCHING.value in cycle.state_history
    return {"status": cycle.status, "states": cycle.state_history}


def _case_model_claims_success_without_change(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path)
    cycle = run_cycle(workspace, FakeBrain(repair_payload(path, old='FLAG = "UNCHANGED"')))
    assert cycle.status in {"failed", "rolled_back"}
    assert cycle.current_state != RepairState.COMPLETE.value
    return {"status": cycle.status, "failure": cycle.failure.code if cycle.failure else ""}


def _case_invalid_json(tmp_path: Path) -> dict[str, object]:
    workspace, _ = init_repo(tmp_path)
    cycle = run_cycle(workspace, FakeBrain("{not-json"))
    assert cycle.failure is not None and cycle.failure.code == "LLM_INVALID_JSON"
    return {"status": cycle.status, "failure": cycle.failure.code}


def _case_tool_conflict(tmp_path: Path) -> dict[str, object]:
    workspace, _ = init_repo(tmp_path)
    cycle = run_cycle(workspace, FakeBrain(RuntimeError("Tool choice is none, but model called a tool")))
    assert cycle.failure is not None and cycle.failure.code == "LLM_TOOL_CONFLICT"
    return {"status": cycle.status, "failure": cycle.failure.code}


def _case_unsupported_tool(tmp_path: Path) -> dict[str, object]:
    executor = ControlledToolExecutor(workspace=tmp_path, tool_map={"ok": lambda args: args})
    result = executor.execute(ToolRequest(tool_name="missing", arguments={}))
    assert result.success is False
    assert result.failure is not None and result.failure.code == "UNSUPPORTED_TOOL"
    return result.to_dict()


def _case_unsafe_path(tmp_path: Path) -> dict[str, object]:
    workspace, _ = init_repo(tmp_path)
    cycle = run_cycle(workspace, FakeBrain(repair_payload("../outside.py")))
    assert cycle.status == "failed"
    assert cycle.failure is not None
    return {"status": cycle.status, "failure": cycle.failure.code}


def _case_missing_precondition(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path)
    cycle = run_cycle(workspace, FakeBrain(repair_payload(path, old='FLAG = "MISSING"')))
    assert cycle.status in {"rolled_back", "failed"}
    return {"status": cycle.status, "failure": cycle.failure.code if cycle.failure else ""}


def _case_validation_failure(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path)
    cycle = run_cycle(workspace, FakeBrain(repair_payload(path, validation_commands=[failure_command()], resolution_commands=[success_command()])))
    assert cycle.status == "rolled_back"
    assert (workspace / path).read_text(encoding="utf-8").strip() == 'FLAG = "BROKEN"'
    return {"status": cycle.status, "rollback": cycle.failure.rollback_succeeded if cycle.failure else False}


def _case_resolution_failure(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path)
    cycle = run_cycle(workspace, FakeBrain(repair_payload(path, resolution_commands=[defect_command(path, token="FIXED")], validation_commands=[success_command()])))
    assert cycle.resolution_verified is False
    assert cycle.current_state != RepairState.COMPLETE.value
    return {"status": cycle.status, "resolution_verified": cycle.resolution_verified}


def _case_commit_failure(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path)
    controller = RepositoryRepairController(brain=FakeBrain(repair_payload(path, validation_commands=[success_command()], resolution_commands=[success_command()])), workspace=workspace, planner_attempts=3)
    controller.git_gateway.commit = lambda message, expected_paths: (_ for _ in ()).throw(RepairError("git commit failed"))
    cycle = controller.run(task_title="Repair target", task_body="Fix target", issue_number="123", repo="Barrot-Agent/B-Agent", branch="repair/test", audit_context={"inventory": path})
    assert cycle.status == "failed"
    assert cycle.current_state != RepairState.COMPLETE.value
    return {"status": cycle.status, "failure": cycle.failure.message if cycle.failure else ""}


def _case_remote_verification_failure(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path, origin=True)
    controller = RepositoryRepairController(brain=FakeBrain(repair_payload(path, validation_commands=[success_command()], resolution_commands=[success_command()])), workspace=workspace, planner_attempts=3)
    controller.git_gateway.remote_head = lambda remote, branch: CommandEvidence(command={}, success=True, returncode=0, stdout="deadbeef", stderr="")
    cycle = controller.run(task_title="Repair target", task_body="Fix target", issue_number="123", repo="Barrot-Agent/B-Agent", branch="repair/test", audit_context={"inventory": path})
    assert cycle.status == "failed"
    assert cycle.commit.remote_verified is False
    return {"status": cycle.status, "remote_verified": cycle.commit.remote_verified}


def _case_duplicate_repair(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path, origin=True)
    first = run_cycle(workspace, FakeBrain(repair_payload(path)))
    second = run_cycle(workspace, FakeBrain(repair_payload(path)))
    assert first.status == "complete"
    assert second.status == "no_repair_required"
    return {"first": first.status, "second": second.status}


def _case_empty_namespace(tmp_path: Path) -> dict[str, object]:
    init_repo(tmp_path)
    sync = SyncController(max_attempts=1, backoff_seconds=1, sleep_fn=lambda _: None)
    result = sync.run(
        work_id="case14",
        operation="transfer_project",
        project_identity={"id": 1, "path_with_namespace": "Barrot-Agent/B-Agent", "namespace_id": 2, "namespace_path": "Barrot-Agent", "namespace_kind": "user"},
        submit_operation=lambda identity: {"submitted": identity["path_with_namespace"]},
        observe_state=lambda: {"path": "Barrot-Agent/B-Agent", "namespace": ""},
        is_complete=lambda state, _: bool(state.get("transfer_completed")),
    )
    assert result.status == RepairState.BLOCKED.value
    return {"status": result.status, "last_valid_project": result.last_valid_project}


def _case_repeated_api_response(tmp_path: Path) -> dict[str, object]:
    init_repo(tmp_path)
    observation = {"id": 1, "path_with_namespace": "Barrot-Agent/B-Agent", "namespace_id": 2, "namespace_path": "Barrot-Agent", "namespace_kind": "user", "transfer_completed": False}
    sync = SyncController(max_attempts=3, backoff_seconds=1, sleep_fn=lambda _: None)
    submits: list[dict[str, object]] = []
    result = sync.run(
        work_id="case15",
        operation="transfer_project",
        project_identity=observation,
        submit_operation=lambda identity: submits.append(identity) or {"submitted": True},
        observe_state=lambda: dict(observation),
        is_complete=lambda state, _: bool(state.get("transfer_completed")),
    )
    assert result.status == RepairState.BLOCKED.value
    assert len(submits) == 1
    return {"status": result.status, "attempts": result.attempt_count}


def _case_api_outage(tmp_path: Path) -> dict[str, object]:
    workspace, _ = init_repo(tmp_path)
    cycle = run_cycle(workspace, FakeBrain(RuntimeError("503 service unavailable"), RuntimeError("503 service unavailable"), RuntimeError("503 service unavailable")))
    assert cycle.status == "failed"
    assert cycle.failure is not None and cycle.failure.code in {"LLM_UNAVAILABLE", "LLM_API_ERROR"}
    return {"status": cycle.status, "failure": cycle.failure.code}


def _case_interruption_resume(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path)
    queue = WorkQueueController(repair_controller=RepositoryRepairController(brain=FakeBrain(json.dumps({"mode": "no_repair_required", "report": "healthy"})), workspace=workspace))
    first = queue.run(work_id="resume", project_identity=ProjectIdentity.from_seed("Barrot-Agent/B-Agent").to_dict(), task_title="Repair target", task_body="Check target", issue_number="123", repo="Barrot-Agent/B-Agent", branch="repair/test", audit_context={"inventory": path})
    second = WorkQueueController(repair_controller=RepositoryRepairController(brain=FakeBrain(json.dumps({"mode": "no_repair_required", "report": "healthy"})), workspace=workspace)).run(work_id="resume", project_identity=ProjectIdentity.from_seed("Barrot-Agent/B-Agent").to_dict(), task_title="Repair target", task_body="Check target", issue_number="123", repo="", branch="", audit_context={"inventory": path})
    assert first.project_identity["path_with_namespace"] == "Barrot-Agent/B-Agent"
    assert second.attempt_count == 2
    return {"first": first.status, "second": second.status, "attempt_count": second.attempt_count}


def _case_retry_exhaustion(tmp_path: Path) -> dict[str, object]:
    workspace, path = init_repo(tmp_path)
    payload = repair_payload(path, validation_commands=[failure_command()], resolution_commands=[success_command()])
    first = RepositoryRepairController(brain=FakeBrain(payload), workspace=workspace, planner_attempts=3, max_unchanged_attempts=1).run(task_title="Repair target", task_body="Fix target", issue_number="123", repo="Barrot-Agent/B-Agent", branch="repair/test", audit_context={"inventory": path})
    second = RepositoryRepairController(brain=FakeBrain(payload), workspace=workspace, planner_attempts=3, max_unchanged_attempts=1).run(task_title="Repair target", task_body="Fix target", issue_number="123", repo="Barrot-Agent/B-Agent", branch="repair/test", audit_context={"inventory": path})
    assert first.status == "rolled_back"
    assert second.status == "blocked"
    return {"first": first.status, "second": second.status, "failure": second.failure.code if second.failure else ""}


def _case_false_mathematical_proof(tmp_path: Path) -> dict[str, object]:
    bundle = write_science_bundle(tmp_path / "bundle.json", independent=False, adversarial_status=ClaimStatus.SUPPORTED.value)
    cycle = ScientificDiscoveryController(workspace=tmp_path).run(StaticResearchProblemAdapter(bundle), formal_runner=lambda command, repo: {"returncode": 0, "stdout": "ok", "stderr": ""})
    assert cycle.status == "no_solution_claim"
    return {"status": cycle.status, "independent": cycle.problem_resolution_status}


def _case_missing_math_assumptions(tmp_path: Path) -> dict[str, object]:
    bundle = write_science_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.CHALLENGED.value)
    cycle = ScientificDiscoveryController(workspace=tmp_path).run(StaticResearchProblemAdapter(bundle), formal_runner=lambda command, repo: {"returncode": 0, "stdout": "ok", "stderr": ""})
    assert any("adversarial" in item.lower() for item in cycle.unresolved_questions)
    return {"status": cycle.status, "unresolved": cycle.unresolved_questions}


def _case_failed_formalization(tmp_path: Path) -> dict[str, object]:
    bundle = write_science_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.SUPPORTED.value, formal_command=["python", "hack.py"])
    cycle = ScientificDiscoveryController(workspace=tmp_path).run(StaticResearchProblemAdapter(bundle))
    assert cycle.status == "failed"
    return {"status": cycle.status, "failure": cycle.failure.code if cycle.failure else ""}


def _case_lean_failure(tmp_path: Path) -> dict[str, object]:
    bundle = write_science_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.SUPPORTED.value)
    cycle = ScientificDiscoveryController(workspace=tmp_path).run(StaticResearchProblemAdapter(bundle), formal_runner=lambda command, repo: {"returncode": 1, "stdout": "", "stderr": "lean failed"})
    assert cycle.status == "no_solution_claim"
    assert cycle.formal_verifications[0]["compiled"] is False
    return {"status": cycle.status, "formal": cycle.formal_verifications[0]}


def _case_adversarial_contradiction(tmp_path: Path) -> dict[str, object]:
    bundle = write_science_bundle(tmp_path / "bundle.json", independent=True, adversarial_status=ClaimStatus.CHALLENGED.value)
    cycle = ScientificDiscoveryController(workspace=tmp_path).run(StaticResearchProblemAdapter(bundle), formal_runner=lambda command, repo: {"returncode": 0, "stdout": "ok", "stderr": "", "independently_verified": True})
    assert cycle.status == "no_solution_claim"
    return {"status": cycle.status, "unresolved": cycle.unresolved_questions}


def _case_conflicting_research_groups() -> dict[str, object]:
    from barrot_agent.research import ConvergenceObservation

    analysis = ConvergenceScenarioEngine().analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            ConvergenceObservation(
                observation_id="a",
                track_id="group_a",
                research_problem_id="problem",
                statement="velocity remains bounded",
                features=["claim:c1", "assumption:A1"],
                source="group_a_paper",
                evidence_ids=["e1"],
                provenance_id="p1",
            ),
            ConvergenceObservation(
                observation_id="b",
                track_id="group_b",
                research_problem_id="problem",
                statement="velocity is not bounded",
                features=["claim:c1", "assumption:A2"],
                source="group_b_paper",
                evidence_ids=["e2"],
                provenance_id="p2",
            ),
        ],
    )
    assert analysis.contradictions
    assert analysis.patterns[0]["status"] == ConvergenceStatus.CONTRADICTION.value
    return {"contradictions": analysis.contradictions}


def _case_invalid_cross_pollination() -> dict[str, object]:
    from barrot_agent.research import CrossPollinationEngine, ResearchTrack

    transfers = CrossPollinationEngine().synthesize([
        ResearchTrack(track_id="a", role="proof", strategy="derive", hypothesis="claim", intermediate_results=[{"claim_id": "c1", "summary": "lemma", "status": "SUPPORTED"}], provenance=[]),
        ResearchTrack(track_id="b", role="formal", strategy="compile", hypothesis="claim", dependencies=["c1"], provenance=["p2"]),
    ])
    assert any(item.result == "invalid_transfer" for item in transfers)
    return {"results": [item.result for item in transfers]}


def _case_provenance_collision() -> dict[str, object]:
    from barrot_agent.research import ConvergenceObservation

    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(research_problem_id="problem", domain="technology", observations=[
        ConvergenceObservation(observation_id="a", track_id="t1", research_problem_id="problem", statement="shared ancestry", features=["claim:c1", "ancestry:x"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
        ConvergenceObservation(observation_id="b", track_id="t2", research_problem_id="problem", statement="shared ancestry", features=["claim:c1", "ancestry:x"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
    ])
    assert analysis.patterns[0]["independence_analysis"]["status"] == "DEPENDENT"
    return {"pattern": analysis.patterns[0]}


def _case_fake_independent_verification(tmp_path: Path) -> dict[str, object]:
    bundle = write_science_bundle(tmp_path / "bundle.json", independent=False, adversarial_status=ClaimStatus.SUPPORTED.value)
    cycle = ScientificDiscoveryController(workspace=tmp_path).run(StaticResearchProblemAdapter(bundle), formal_runner=lambda command, repo: {"returncode": 0, "stdout": "ok", "stderr": "", "independently_verified": False})
    assert cycle.problem_resolution_status == ClaimStatus.UNRESOLVED.value
    return {"status": cycle.status, "problem_resolution_status": cycle.problem_resolution_status}


def _case_successful_formal_verification(tmp_path: Path) -> dict[str, object]:
    bundle = write_science_bundle(tmp_path / "bundle.json", independent=False, adversarial_status=ClaimStatus.SUPPORTED.value)
    cycle = ScientificDiscoveryController(workspace=tmp_path).run(StaticResearchProblemAdapter(bundle), formal_runner=lambda command, repo: {"returncode": 0, "stdout": "ok", "stderr": ""})
    assert cycle.formal_verifications[0]["compiled"] is True
    assert cycle.status == "no_solution_claim"
    return {"status": cycle.status, "formal": cycle.formal_verifications[0]}


def _case_unresolved(tmp_path: Path) -> dict[str, object]:
    cycle = ScientificDiscoveryController(workspace=tmp_path).run(NavierStokesProblemAdapter())
    assert cycle.status == "no_solution_claim"
    assert cycle.acceptance_gate_passed is False
    return {"status": cycle.status, "convergence": bool(cycle.convergence_analysis)}
