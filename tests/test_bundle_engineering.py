import copy

import pytest

from barrot_agent.orchestration.bundle_engineering import (
    BundleEngineeringError,
    build_bundle_authoring_prompt,
    build_bundle_improvement_prompt,
    bundle_fingerprint,
    review_work_bundle,
    validate_bundle_revision,
)


def sample_bundle():
    return {
        "schema_version": "1.0",
        "bundle_id": "autonomy-foundation",
        "objective": "Teach Barrot to author and improve work bundles.",
        "revision": 1,
        "constraints": [
            "Require human authorization for consequential external changes.",
            "Never claim completion without evidence.",
        ],
        "prerequisites": ["Inspect the actual repository and current tests."],
        "tasks": [
            {
                "id": "inspect",
                "title": "Inspect current bundle infrastructure",
                "description": "Map existing bundle generation, validation, and delivery code.",
                "files": ["barrot_agent/orchestration/bundle_validation.py"],
                "acceptance_criteria": ["Existing capability map cites current repository files."],
                "tests": ["python -m pytest -q tests/test_bundle_validation.py"],
                "depends_on": [],
                "risk_level": "low",
                "rollback_plan": ["Revert this documentation-only task if its assertions are stale."],
            },
            {
                "id": "validate",
                "title": "Validate generated bundles",
                "description": "Reject missing evidence gates and invalid task dependencies.",
                "files": ["barrot_agent/orchestration/bundle_engineering.py"],
                "acceptance_criteria": ["Malformed bundles produce explicit findings."],
                "tests": ["python -m pytest -q tests/test_bundle_engineering.py"],
                "depends_on": ["inspect"],
                "risk_level": "medium",
                "rollback_plan": ["Disable the new validator entrypoint while preserving prior bundle files."],
            },
        ],
        "completion_gate": ["Completion requires test evidence and independent verification."],
        "recovery_plan": ["On interruption, resume from persisted state; bound retries and block on exhaustion."],
        "created_by": "Barrot",
    }


def test_complete_bundle_passes_deterministic_review():
    result = review_work_bundle(sample_bundle())
    assert result.valid is True
    assert result.quality_score == 100
    assert result.findings == ()
    assert result.fingerprint.startswith("sha256:")


def test_missing_test_and_evidence_gate_are_reported():
    bundle = sample_bundle()
    bundle["tasks"][0]["tests"] = []
    bundle["completion_gate"] = ["Finish all steps."]
    result = review_work_bundle(bundle)
    codes = {finding.code for finding in result.findings}
    assert "TASK_FIELD_EMPTY" in codes
    assert "EVIDENCE_GATE_MISSING" in codes
    assert result.valid is False


def test_unknown_dependency_and_dependency_cycle_are_rejected():
    bundle = sample_bundle()
    bundle["tasks"][0]["depends_on"] = ["missing"]
    bundle["tasks"][1]["depends_on"] = ["inspect"]
    result = review_work_bundle(bundle)
    assert "UNKNOWN_DEPENDENCY" in {finding.code for finding in result.findings}

    bundle = sample_bundle()
    bundle["tasks"][0]["depends_on"] = ["validate"]
    result = review_work_bundle(bundle)
    assert "DEPENDENCY_CYCLE" in {finding.code for finding in result.findings}


def test_duplicate_task_ids_are_rejected():
    bundle = sample_bundle()
    bundle["tasks"][1]["id"] = bundle["tasks"][0]["id"]
    result = review_work_bundle(bundle)
    assert "DUPLICATE_TASK_ID" in {finding.code for finding in result.findings}


def test_non_object_bundle_fails_closed():
    result = review_work_bundle("not-json-object")
    assert result.valid is False
    assert result.quality_score == 75
    assert result.findings[0].code == "BUNDLE_NOT_OBJECT"


def test_authoring_prompt_requires_objective_and_constraints():
    prompt = build_bundle_authoring_prompt(
        objective="Build a tested bundle authoring loop.",
        constraints=["Preserve human authorization."],
        repository_context="bundle_engineering.py exists",
    )
    assert "acceptance_criteria" in prompt
    assert "completion gate" in prompt.lower()
    assert "bundle_engineering.py exists" in prompt

    with pytest.raises(BundleEngineeringError):
        build_bundle_authoring_prompt(objective=" ", constraints=[])


def test_improvement_prompt_contains_findings_and_parent_fingerprint():
    bundle = sample_bundle()
    bundle["tasks"][0]["tests"] = []
    review = review_work_bundle(bundle)
    prompt = build_bundle_improvement_prompt(bundle, review)
    assert review.fingerprint in prompt
    assert "improve" in prompt.lower()
    assert "Do not execute it" in prompt


def test_revision_must_preserve_objective_constraints_and_improve_quality():
    original = sample_bundle()
    original["tasks"][0]["tests"] = []
    revised = copy.deepcopy(original)
    revised["revision"] = 2
    revised["parent_fingerprint"] = bundle_fingerprint(original)
    revised["tasks"][0]["tests"] = ["python -m pytest -q tests/test_bundle_engineering.py"]

    result = validate_bundle_revision(original, revised)
    assert result.valid is True
    assert result.quality_score > review_work_bundle(original).quality_score

    changed_objective = copy.deepcopy(revised)
    changed_objective["objective"] = "A different objective."
    with pytest.raises(BundleEngineeringError, match="objective"):
        validate_bundle_revision(original, changed_objective)

    weakened_constraints = copy.deepcopy(revised)
    weakened_constraints["constraints"] = []
    with pytest.raises(BundleEngineeringError, match="constraints"):
        validate_bundle_revision(original, weakened_constraints)


def test_revision_requires_correct_parent_and_exact_revision_increment():
    original = sample_bundle()
    original["tasks"][0]["tests"] = []
    revised = copy.deepcopy(original)
    revised["revision"] = 2
    revised["parent_fingerprint"] = "sha256:wrong"
    with pytest.raises(BundleEngineeringError, match="parent_fingerprint"):
        validate_bundle_revision(original, revised)

    revised["parent_fingerprint"] = bundle_fingerprint(original)
    revised["revision"] = 3
    with pytest.raises(BundleEngineeringError, match="increase by exactly one"):
        validate_bundle_revision(original, revised)


def test_controller_authors_and_returns_ready_bundle():
    import json

    from barrot_agent.orchestration.bundle_engineering import BundleEngineeringController

    bundle = sample_bundle()

    class FakeBrain:
        def think(self, prompt, system=None):
            assert "work-bundle engineer" in system
            assert "Create an executable" in prompt
            return json.dumps(bundle)

    result = BundleEngineeringController(FakeBrain()).run(
        objective=bundle["objective"],
        constraints=bundle["constraints"],
        repository_context="verified repository context",
    )
    assert result.status == "READY_FOR_EXECUTION_REVIEW"
    assert result.review.valid is True
    assert result.attempts[0]["kind"] == "draft"


def test_controller_revises_a_deficient_bundle_before_ready():
    import json

    from barrot_agent.orchestration.bundle_engineering import BundleEngineeringController

    original = sample_bundle()
    original["tasks"][0]["tests"] = []
    revised = copy.deepcopy(original)
    revised["revision"] = 2
    revised["parent_fingerprint"] = bundle_fingerprint(original)
    revised["tasks"][0]["tests"] = ["python -m pytest -q tests/test_bundle_engineering.py"]
    responses = iter([json.dumps(original), json.dumps(revised)])

    class FakeBrain:
        def think(self, prompt, system=None):
            return next(responses)

    result = BundleEngineeringController(FakeBrain(), max_revision_attempts=1).run(
        objective=original["objective"],
        constraints=original["constraints"],
    )
    assert result.status == "READY_FOR_EXECUTION_REVIEW"
    assert result.review.valid is True
    assert len(result.attempts) == 2
    assert result.attempts[1]["accepted"] is True


def test_controller_blocks_when_quality_does_not_reach_gate():
    import json

    from barrot_agent.orchestration.bundle_engineering import BundleEngineeringController

    bundle = sample_bundle()
    bundle["tasks"][0]["tests"] = []

    class FakeBrain:
        def think(self, prompt, system=None):
            return json.dumps(bundle)

    result = BundleEngineeringController(FakeBrain(), max_revision_attempts=0).run(
        objective=bundle["objective"],
        constraints=bundle["constraints"],
    )
    assert result.status == "BLOCKED_BUNDLE_QUALITY"
    assert result.review.valid is False


def test_controller_rejects_objective_or_constraint_drift():
    import json

    from barrot_agent.orchestration.bundle_engineering import BundleEngineeringController

    bundle = sample_bundle()
    bundle["objective"] = "Quietly change the goal."

    class FakeBrain:
        def think(self, prompt, system=None):
            return json.dumps(bundle)

    with pytest.raises(BundleEngineeringError, match="objective"):
        BundleEngineeringController(FakeBrain()).run(
            objective="Teach Barrot to author and improve work bundles.",
            constraints=bundle["constraints"],
        )


def test_revision_cannot_change_bundle_identity():
    original = sample_bundle()
    original["tasks"][0]["tests"] = []
    revised = copy.deepcopy(original)
    revised["revision"] = 2
    revised["parent_fingerprint"] = bundle_fingerprint(original)
    revised["bundle_id"] = "different-bundle"
    revised["tasks"][0]["tests"] = ["python -m pytest -q tests/test_bundle_engineering.py"]
    with pytest.raises(BundleEngineeringError, match="identity"):
        validate_bundle_revision(original, revised)
