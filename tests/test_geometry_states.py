"""Tests for the four-state and eight-state contracts."""
import pytest

from barrot_agent.geometry.states import (
    ConstraintResult,
    EvidenceState,
    TruthState,
    combine,
    evaluate_constraint,
    from_mmi_evidence,
    from_parse_state,
    from_stage_status,
    refuted_evidence,
    verified_evidence,
)


ALL_STATES = (
    TruthState.VALID,
    TruthState.INVALID,
    TruthState.UNRESOLVED,
    TruthState.NOT_APPLICABLE,
)


def test_combine_with_no_checks_is_not_applicable():
    assert combine() is TruthState.NOT_APPLICABLE


@pytest.mark.parametrize("state", ALL_STATES)
def test_combine_single_state_is_identity(state):
    assert combine(state) is state


def test_invalid_dominates_unresolved_and_valid():
    assert combine(TruthState.INVALID, TruthState.UNRESOLVED) is TruthState.INVALID
    assert combine(TruthState.INVALID, TruthState.VALID) is TruthState.INVALID


def test_unresolved_dominates_valid_but_not_invalid():
    assert combine(TruthState.UNRESOLVED, TruthState.VALID) is TruthState.UNRESOLVED
    assert combine(TruthState.UNRESOLVED, TruthState.INVALID) is TruthState.INVALID


def test_not_applicable_is_inert():
    assert combine(TruthState.VALID, TruthState.NOT_APPLICABLE) is TruthState.VALID
    assert (
        combine(TruthState.UNRESOLVED, TruthState.NOT_APPLICABLE)
        is TruthState.UNRESOLVED
    )
    assert (
        combine(TruthState.NOT_APPLICABLE, TruthState.NOT_APPLICABLE)
        is TruthState.NOT_APPLICABLE
    )


def test_combine_rejects_foreign_values():
    with pytest.raises(TypeError):
        combine("VALID")


def test_missing_evidence_is_unresolved_not_invalid():
    result = evaluate_constraint(satisfied=None, violated=None)
    assert isinstance(result, ConstraintResult)
    assert result.state is TruthState.UNRESOLVED
    assert result.contradictory is False


def test_satisfied_constraint_is_valid():
    result = evaluate_constraint(satisfied=True, violated=None)
    assert result.state is TruthState.VALID


def test_violated_constraint_is_invalid():
    result = evaluate_constraint(satisfied=None, violated=True)
    assert result.state is TruthState.INVALID


def test_conflicting_evidence_is_flagged_not_collapsed():
    result = evaluate_constraint(satisfied=True, violated=True)
    assert result.state is TruthState.UNRESOLVED
    assert result.contradictory is True


def test_inapplicable_constraint_is_not_applicable():
    result = evaluate_constraint(satisfied=True, violated=True, applicable=False)
    assert result.state is TruthState.NOT_APPLICABLE
    assert result.contradictory is False


def test_constraint_reason_is_preserved():
    result = evaluate_constraint(satisfied=None, violated=None, reason="no samples")
    assert result.reason == "no samples"


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("COMPLETE", TruthState.VALID),
        ("PARTIAL", TruthState.UNRESOLVED),
        ("BLOCKED", TruthState.UNRESOLVED),
        ("UNKNOWN", TruthState.UNRESOLVED),
        ("NOT_APPLICABLE", TruthState.NOT_APPLICABLE),
    ],
)
def test_stage_status_adapter(status, expected):
    assert from_stage_status(status) is expected


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("OBSERVED", EvidenceState.OBSERVED),
        ("PARSED", EvidenceState.COMPUTED),
        ("DERIVED", EvidenceState.DERIVED),
        ("INFERRED", EvidenceState.INFERRED),
        ("UNKNOWN", EvidenceState.UNRESOLVED),
        ("NOT_PARSABLE", EvidenceState.UNRESOLVED),
        ("NOT_APPLICABLE", EvidenceState.UNRESOLVED),
    ],
)
def test_mmi_evidence_adapter(state, expected):
    assert from_mmi_evidence(state) is expected


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("OBSERVED", EvidenceState.OBSERVED),
        ("PARSED", EvidenceState.COMPUTED),
        ("DERIVED", EvidenceState.DERIVED),
        ("INFERRED", EvidenceState.INFERRED),
        ("HYPOTHESIZED", EvidenceState.CONJECTURED),
        ("PROPOSED", EvidenceState.CONJECTURED),
        ("UNKNOWN", EvidenceState.UNRESOLVED),
        ("NOT_PARSABLE", EvidenceState.UNRESOLVED),
        ("NOT_PRESENT", EvidenceState.UNRESOLVED),
    ],
)
def test_parse_state_adapter(state, expected):
    assert from_parse_state(state) is expected


def test_unknown_vocabulary_fails_closed():
    with pytest.raises(ValueError):
        from_stage_status("MADE_UP")
    with pytest.raises(ValueError):
        from_mmi_evidence("MADE_UP")
    with pytest.raises(ValueError):
        from_parse_state("MADE_UP")


def test_verified_requires_a_record():
    assert verified_evidence(None) is EvidenceState.UNRESOLVED
    assert verified_evidence("") is EvidenceState.UNRESOLVED
    assert verified_evidence("sha256:abc") is EvidenceState.VERIFIED


def test_refuted_requires_evidence():
    assert refuted_evidence(None) is EvidenceState.UNRESOLVED
    assert refuted_evidence("counterexample: vertex 2 out of range") is EvidenceState.REFUTED


def test_no_adapter_can_produce_verified():
    adapted = [
        from_mmi_evidence(state)
        for state in ("OBSERVED", "PARSED", "DERIVED", "INFERRED", "UNKNOWN")
    ]
    adapted.extend(
        from_parse_state(state)
        for state in ("OBSERVED", "PARSED", "HYPOTHESIZED", "PROPOSED")
    )
    assert EvidenceState.VERIFIED not in adapted
