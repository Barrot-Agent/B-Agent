"""Deterministic bundle shape normalization and authorization-boundary extraction."""
import copy
import json

import pytest

from barrot_agent.orchestration.bundle_engineering import (
    BUNDLE_CREATED_BY,
    BundleEngineeringController,
    build_bundle_authoring_prompt,
    extract_authorization_boundaries,
    normalize_bundle_shapes,
    review_work_bundle,
)
from tests.test_bundle_engineering import sample_bundle

DEFAULT_CONSTRAINTS = [
    "Do not perform consequential external actions without required authorization.",
    "Never claim completion without recorded validation evidence.",
]
ISSUE_BODY = """Add a dry-run mode.

Requirements:
- Add a `dry_run` input.

Authorization boundaries:
- Authorized: create one task branch, push commits to it, and open one pull request against main for this issue.
- Not authorized: merging any pull request, pushing to main, force-pushing, deploying.

Trailing notes.
"""


def codes(review):
    return [f.code for f in review.findings]


# --- gate unchanged -------------------------------------------------------

def test_gate_still_rejects_string_list_fields_without_normalization():
    bundle = sample_bundle()
    bundle["completion_gate"] = "Completion requires test evidence."
    bundle["recovery_plan"] = "Resume from persisted state; block on exhaustion."
    bundle["created_by"] = None
    review = review_work_bundle(bundle)
    assert review.valid is False
    assert codes(review).count("REQUIRED_FIELD_INVALID") == 3


def test_gate_still_requires_explicit_authorization_boundary():
    bundle = sample_bundle()
    bundle["constraints"] = list(DEFAULT_CONSTRAINTS)  # generic "authorization" wording is not an extracted boundary
    review = review_work_bundle(bundle)
    assert "AUTHORIZATION_CONSTRAINT_MISSING" in codes(review)
    assert review.valid is False


# --- unambiguous coercions -----------------------------------------------

def test_string_list_fields_become_single_item_lists():
    bundle = sample_bundle()
    bundle["completion_gate"] = "  Completion requires test evidence.  "
    bundle["recovery_plan"] = "Resume from persisted state; block on exhaustion."
    bundle["prerequisites"] = "Inspect the repository."
    bundle["tasks"][0]["tests"] = "python -m pytest -q"
    bundle["tasks"][0]["files"] = "a.py"
    bundle["tasks"][1]["depends_on"] = "inspect"
    bundle["tasks"][1]["rollback_plan"] = "Revert the commit."
    normalized, repairs = normalize_bundle_shapes(bundle)
    assert normalized["completion_gate"] == ["Completion requires test evidence."]
    assert normalized["tasks"][1]["depends_on"] == ["inspect"]
    assert set(repairs) >= {"completion_gate", "recovery_plan", "prerequisites", "tasks[0].tests",
                            "tasks[0].files", "tasks[1].depends_on", "tasks[1].rollback_plan"}
    review = review_work_bundle(normalized)
    assert review.valid and review.quality_score == 100


@pytest.mark.parametrize("value", [None, "barrot-engineer", 7, ""])
def test_created_by_is_fixed_identifier(value):
    bundle = sample_bundle()
    if value is None:
        bundle.pop("created_by")
    else:
        bundle["created_by"] = value
    normalized, repairs = normalize_bundle_shapes(bundle)
    assert normalized["created_by"] == BUNDLE_CREATED_BY == "Barrot"
    assert "created_by" in repairs


def test_digit_revision_string_becomes_int_and_input_not_mutated():
    bundle = sample_bundle()
    bundle["revision"] = "1"
    original = copy.deepcopy(bundle)
    normalized, _ = normalize_bundle_shapes(bundle)
    assert normalized["revision"] == 1
    assert bundle == original


def test_valid_bundle_is_unchanged():
    normalized, repairs = normalize_bundle_shapes(sample_bundle())
    assert normalized == sample_bundle() and repairs == []


# --- ambiguous / invalid data still fails ----------------------------------

@pytest.mark.parametrize("field,value", [
    ("completion_gate", None),          # missing
    ("completion_gate", ""),            # empty string
    ("completion_gate", "   "),
    ("recovery_plan", {"step": "resume"}),
    ("recovery_plan", 3),
])
def test_ambiguous_top_level_values_still_fail(field, value):
    bundle = sample_bundle()
    if value is None:
        bundle.pop(field)
    else:
        bundle[field] = value
    normalized, _ = normalize_bundle_shapes(bundle)
    review = review_work_bundle(normalized)
    assert review.valid is False


def test_list_with_non_string_items_is_left_unchanged():
    bundle = sample_bundle()
    bundle["completion_gate"] = ["Completion requires test evidence.", 5]
    normalized, repairs = normalize_bundle_shapes(bundle)
    assert normalized["completion_gate"] == ["Completion requires test evidence.", 5]
    assert "completion_gate" not in repairs


@pytest.mark.parametrize("value", ["one", "1.0", "-1", 1.5])
def test_non_digit_revision_is_not_coerced(value):
    bundle = sample_bundle()
    bundle["revision"] = value
    normalized, _ = normalize_bundle_shapes(bundle)
    assert normalized["revision"] == value
    assert review_work_bundle(normalized).valid is False


def test_missing_task_field_and_non_dict_tasks_still_fail():
    bundle = sample_bundle()
    del bundle["tasks"][0]["tests"]
    bundle["tasks"].append("not a task")
    normalized, _ = normalize_bundle_shapes(bundle)
    assert review_work_bundle(normalized).valid is False


def test_non_object_bundle_passthrough():
    assert normalize_bundle_shapes(["x"]) == (["x"], [])


# --- authorization boundaries ---------------------------------------------

def test_extracts_authorization_boundaries_verbatim():
    items = extract_authorization_boundaries(ISSUE_BODY)
    assert len(items) == 2
    assert items[0].endswith("Authorized: create one task branch, push commits to it, and open one pull request against main for this issue.")
    assert items[1].endswith("Not authorized: merging any pull request, pushing to main, force-pushing, deploying.")
    bundle = sample_bundle()
    bundle["constraints"] = DEFAULT_CONSTRAINTS + items
    assert "AUTHORIZATION_CONSTRAINT_MISSING" not in codes(review_work_bundle(bundle))


@pytest.mark.parametrize("body", [
    "## Authorization Boundaries\n\n* Authorized: open one PR.\n",
    "**Authorization boundaries:**\n1. Authorized: open one PR.\n",
])
def test_heading_variants(body):
    assert len(extract_authorization_boundaries(body)) == 1


def test_extracts_safety_and_execution_constraints_verbatim():
    body = """## Safety and execution constraints

- Work only on a new branch from current main.
- Never force-push, reset, clean, stash, or discard user work.
- Never merge PRs or deploy production.

## Definition of done
A reviewable PR.
"""
    items = extract_authorization_boundaries(body)
    assert len(items) == 3
    assert items[0].endswith("Work only on a new branch from current main.")
    assert items[1].endswith("Never force-push, reset, clean, stash, or discard user work.")
    assert items[2].endswith("Never merge PRs or deploy production.")
    bundle = sample_bundle()
    bundle["constraints"] = DEFAULT_CONSTRAINTS + items
    assert "AUTHORIZATION_CONSTRAINT_MISSING" not in codes(review_work_bundle(bundle))


@pytest.mark.parametrize("body", [
    "",
    None,
    "Fix the bug. Requirements:\n- do it\n",
    "Authorization boundaries:\nPlease be careful.\n- Authorized: x\n",  # prose, not bullets
    "Mentions authorization boundaries inline: - Authorized: x",
])
def test_absent_or_ambiguous_section_keeps_gate_failing(body):
    assert extract_authorization_boundaries(body) == []
    bundle = sample_bundle()
    bundle["constraints"] = DEFAULT_CONSTRAINTS + extract_authorization_boundaries(body)
    assert "AUTHORIZATION_CONSTRAINT_MISSING" in codes(review_work_bundle(bundle))


# --- prompt and controller -------------------------------------------------

def test_authoring_prompt_states_exact_types():
    prompt = build_bundle_authoring_prompt(objective="Do X", constraints=["Require human approval."])
    assert "completion_gate: non-empty list of strings" in prompt
    assert "recovery_plan: non-empty list of strings" in prompt
    assert 'created_by: string, exactly "Barrot"' in prompt
    assert "revision: integer 1" in prompt
    json.loads(prompt.split("Shape example (types only; replace values):\n", 1)[1].split("\n\nEach task must contain", 1)[0])


class ScriptedBrain:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.prompts = []

    def think(self, prompt, system=None):
        self.prompts.append(prompt)
        return json.dumps(self.outputs.pop(0))


def test_controller_normalizes_draft_shapes_before_gate():
    draft = sample_bundle()
    draft["completion_gate"] = "Completion requires test evidence."
    draft["created_by"] = "barrot-engineer"
    brain = ScriptedBrain([draft])
    result = BundleEngineeringController(brain, max_revision_attempts=0).run(
        objective=draft["objective"], constraints=draft["constraints"])
    assert result.status == "READY_FOR_EXECUTION_REVIEW"
    assert result.bundle["created_by"] == "Barrot"
    assert set(result.attempts[0]["shape_repairs"]) == {"completion_gate", "created_by"}


def test_controller_still_blocks_missing_fields():
    draft = sample_bundle()
    del draft["completion_gate"], draft["recovery_plan"]
    brain = ScriptedBrain([draft])
    result = BundleEngineeringController(brain, max_revision_attempts=0).run(
        objective=draft["objective"], constraints=draft["constraints"])
    assert result.status == "BLOCKED_BUNDLE_QUALITY"
    assert codes(result.review).count("REQUIRED_FIELD_INVALID") == 2


def test_controller_normalizes_revision_shapes():
    draft = sample_bundle()
    del draft["completion_gate"]
    revised = copy.deepcopy(draft)
    revised["completion_gate"] = "Completion requires test evidence."  # string, fixed by normalization
    brain = ScriptedBrain([draft, revised])
    result = BundleEngineeringController(brain, max_revision_attempts=1).run(
        objective=draft["objective"], constraints=draft["constraints"])
    assert result.status == "READY_FOR_EXECUTION_REVIEW"
    assert "completion_gate" in result.attempts[1]["invariant_repairs"]
