from __future__ import annotations

import json

import pytest

from barrot_agent.orchestration.capability_cycle import (
    CapabilityCycleController,
    CapabilityCycleError,
    CapabilityCycleLedger,
)


def adapters(*, gaps=None, execution=None, verification=None, authorization=None, promotion=None):
    calls = {"mmi": 0, "run": 0, "promote": 0}
    def mmi(request):
        calls["mmi"] += 1
        return {"complete": True, "source_refs": ["mmi:source:1"], "request": request}
    def analyze(ingestion):
        return list(gaps if gaps is not None else [{"gap_id": "gap-1", "description": "missing capability"}])
    def plan(gap, ingestion):
        return {
            "hypothesis": "the candidate improves the measured baseline",
            "acceptance_criteria": ["all regression tests pass"],
            "estimated_cost_units": 2,
        }
    def run(plan):
        calls["run"] += 1
        return execution or {
            "sandboxed": True, "baseline_hash": "sha256:baseline",
            "artifact_refs": ["artifact:candidate"],
        }
    def verify(plan, result):
        return verification or {"passed": True, "evidence": ["test-report:1"]}
    def authorize(plan):
        return authorization or {"approved": False, "reason": "human approval pending"}
    def promote(plan, result):
        calls["promote"] += 1
        return promotion or {"promoted": True, "artifact_ref": "artifact:promoted"}
    return calls, mmi, analyze, plan, run, verify, authorize, promote


def build(tmp_path, **kwargs):
    values = adapters(**kwargs)
    calls, mmi, analyze, plan, run, verify, authorize, promote = values
    controller = CapabilityCycleController(
        workspace=tmp_path, mmi_ingest=mmi, gap_analyzer=analyze,
        experiment_planner=plan, sandbox_runner=run, verifier=verify,
        promoter=promote, authorizer=authorize,
    )
    return controller, calls


def test_cycle_records_mmi_gap_experiment_verification_and_approval_gate(tmp_path):
    controller, calls = build(tmp_path)
    result = controller.run("discover a missing capability", cycle_id="cycle-001")
    assert result.status == "verified_pending_promotion"
    assert result.gaps_found == 1
    assert result.experiments_run == 1
    assert result.experiments_verified == 1
    assert result.promoted == 0
    assert calls["promote"] == 0
    events = CapabilityCycleLedger(tmp_path).read_events()
    kinds = [event["event_type"] for event in events]
    assert kinds == [
        "cycle_started", "mmi_ingested", "gaps_identified", "experiment_planned",
        "experiment_executed", "experiment_verified", "promotion_blocked", "cycle_finished",
    ]


def test_promotion_requires_explicit_authorization_and_verified_artifact(tmp_path):
    controller, calls = build(tmp_path, authorization={"approved": True})
    result = controller.run("build capability", cycle_id="cycle-002")
    assert result.status == "complete"
    assert result.promoted == 1
    assert calls["promote"] == 1


def test_partial_mmi_blocks_experiments_and_promotion(tmp_path):
    controller, calls = build(tmp_path)
    controller.mmi_ingest = lambda request: {
        "complete": False, "source_refs": ["mmi:partial:1"]
    }
    with pytest.raises(CapabilityCycleError, match="partial or unverified"):
        controller.run("inspect source", cycle_id="cycle-003")
    assert calls["run"] == 0


def test_unsandboxed_execution_is_rejected(tmp_path):
    controller, calls = build(tmp_path, execution={
        "sandboxed": False, "baseline_hash": "sha256:base",
        "artifact_refs": ["artifact:1"],
    })
    with pytest.raises(CapabilityCycleError, match="sandbox evidence"):
        controller.run("test candidate", cycle_id="cycle-004")


def test_missing_baseline_or_artifact_is_rejected(tmp_path):
    controller, _ = build(tmp_path, execution={"sandboxed": True, "artifact_refs": ["artifact:1"]})
    with pytest.raises(CapabilityCycleError, match="baseline"):
        controller.run("test candidate", cycle_id="cycle-005")


def test_failed_verification_never_promotes(tmp_path):
    controller, calls = build(tmp_path, verification={"passed": False, "evidence": ["failed-test"]},
                              authorization={"approved": True})
    result = controller.run("try repair", cycle_id="cycle-006")
    assert result.promoted == 0
    assert result.status == "experiments_inconclusive"
    assert calls["promote"] == 0


def test_experiment_budget_is_enforced(tmp_path):
    controller, calls = build(tmp_path)
    controller.gap_analyzer = lambda ingestion: [
        {"gap_id": "gap-a"}, {"gap_id": "gap-b"}
    ]
    controller.max_cost_units = 1
    result = controller.run("find capabilities", cycle_id="cycle-007")
    assert result.experiments_run == 0
    assert result.status == "blocked_or_budget_exhausted"
    assert calls["run"] == 0


def test_duplicate_cycle_id_cannot_replay_side_effects(tmp_path):
    controller, calls = build(tmp_path)
    controller.run("same objective", cycle_id="cycle-008")
    before = calls["run"]
    with pytest.raises(CapabilityCycleError, match="already exists"):
        controller.run("same objective", cycle_id="cycle-008")
    assert calls["run"] == before


def test_ledger_detects_tampering(tmp_path):
    ledger = CapabilityCycleLedger(tmp_path)
    ledger.append("cycle-009", "started", {"x": 1})
    path = ledger.path
    event = json.loads(path.read_text().strip())
    event["payload"]["x"] = 2
    path.write_text(json.dumps(event) + "\n")
    with pytest.raises(CapabilityCycleError, match="hash mismatch"):
        ledger.read_events()



@pytest.mark.parametrize("budget", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_max_cost_budget_is_rejected(tmp_path, budget):
    _, mmi, analyze, plan, run, verify, authorize, promote = adapters()
    with pytest.raises(ValueError, match="finite positive"):
        CapabilityCycleController(
            workspace=tmp_path,
            mmi_ingest=mmi,
            gap_analyzer=analyze,
            experiment_planner=plan,
            sandbox_runner=run,
            verifier=verify,
            promoter=promote,
            authorizer=authorize,
            max_cost_units=budget,
        )


@pytest.mark.parametrize("cost", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_experiment_cost_is_rejected(tmp_path, cost):
    controller, _ = build(tmp_path)
    controller.experiment_planner = lambda gap, ingestion: {
        "hypothesis": "the candidate improves the measured baseline",
        "acceptance_criteria": ["all regression tests pass"],
        "estimated_cost_units": cost,
    }
    with pytest.raises(CapabilityCycleError, match="finite non-negative"):
        controller.run("reject non-finite cost", cycle_id="cycle-nonfinite-cost")

def test_no_gap_is_a_valid_terminal_outcome(tmp_path):
    controller, calls = build(tmp_path, gaps=[])
    result = controller.run("audit current capability", cycle_id="cycle-010")
    assert result.status == "no_gap_found"
    assert result.experiments_run == 0
    assert calls["run"] == 0
