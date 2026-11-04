from barrot_agent.structural_analysis import (
    ConstraintResult, EvidenceStage, InvariantResult, RelationType,
    StructuralAnalyzer, StructuralInput, StructuralRelation, VerificationStatus,
)


def test_deterministic_and_order_independent_signature():
    a = StructuralInput(
        [[1, 0], [0, 1]], "matrix",
        constraints=(ConstraintResult("det", "satisfied"), ConstraintResult("rank", "satisfied")),
        invariants=(InvariantResult("rank", 2),), dimension=2,
    )
    b = StructuralInput(
        [[1, 0], [0, 1]], "matrix",
        constraints=tuple(reversed(a.constraints)),
        invariants=tuple(reversed(a.invariants)), dimension=2,
    )
    assert StructuralAnalyzer().analyze(a).identity_hash == StructuralAnalyzer().analyze(b).identity_hash


def test_regions_remain_distinct():
    analyzer = StructuralAnalyzer()
    assert analyzer.analyze(StructuralInput(0, "scalar", constraints=(ConstraintResult("p", "violated"),))).valid_region == "invalid"
    assert analyzer.analyze(StructuralInput(None, "scalar", constraints=(ConstraintResult("p", "unknown"),))).valid_region == "unresolved"


def test_evaluator_budget_and_type_safety():
    try:
        StructuralAnalyzer(max_evaluations=0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero evaluator budget must be rejected")
    analyzer = StructuralAnalyzer(constraint_evaluators=[lambda value: ConstraintResult("ok", "satisfied")])
    assert analyzer.analyze(StructuralInput(1, "scalar")).constraints[0].evidence_stage == EvidenceStage.COMPUTED
    try:
        StructuralAnalyzer(constraint_evaluators=[lambda value: "not a result"]).analyze(StructuralInput(1, "scalar"))
    except TypeError:
        pass
    else:
        raise AssertionError("invalid evaluator return must be rejected")


def test_invariant_similarity_is_not_equivalence():
    analyzer = StructuralAnalyzer()
    a = analyzer.analyze(StructuralInput(1, "a", invariants=(InvariantResult("rank", 2),)))
    b = analyzer.analyze(StructuralInput(2, "b", invariants=(InvariantResult("rank", 2),)))
    result = analyzer.compare_invariants(a, b)
    assert result["descriptor_match"] is True
    assert result["equivalence_claim"] is None
    assert result["verification"] == "unverified"


def test_relations_are_explicit_and_typed():
    relation = StructuralRelation("A", "B", RelationType.BOUNDARY_OF, criterion="closure witness")
    signature = StructuralAnalyzer().analyze(StructuralInput("x", "region", relations=(relation,)))
    assert signature.relations[0].relation == RelationType.BOUNDARY_OF
    assert signature.relations[0].verification == VerificationStatus.UNVERIFIED


def test_invalid_dimension_rejected():
    try:
        StructuralInput(1, "scalar", dimension=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative dimension must be rejected")


def test_signature_json_is_serializable_and_provenance_bound():
    base = StructuralInput(1, "scalar", provenance={"source": "unit-test"})
    changed = StructuralInput(1, "scalar", provenance={"source": "different-source"})
    signature = StructuralAnalyzer().analyze(base)
    assert signature.to_dict()["provenance"]["source"] == "unit-test"
    assert signature.identity_hash != StructuralAnalyzer().analyze(changed).identity_hash



def test_empty_constraint_set_is_unresolved_not_valid():
    signature = StructuralAnalyzer().analyze(StructuralInput({"x": 1}, "mapping"))
    assert signature.valid_region == "unresolved"

def test_complete_descriptor_records_are_used_as_deterministic_sort_tiebreakers():
    constraints = (
        ConstraintResult(
            "same", "satisfied",
            verification=VerificationStatus.VERIFIED,
        ),
        ConstraintResult(
            "same", "satisfied",
            verification=VerificationStatus.FAILED,
        ),
    )
    invariants = (
        InvariantResult("same", 1, method="method-a"),
        InvariantResult("same", 1, method="method-b"),
    )
    relations = (
        StructuralRelation("A", "B", RelationType.EQUAL, witness="witness-a"),
        StructuralRelation("A", "B", RelationType.EQUAL, witness="witness-b"),
    )
    first = StructuralInput(
        "representation", "test",
        constraints=constraints, invariants=invariants, relations=relations,
    )
    second = StructuralInput(
        "representation", "test",
        constraints=tuple(reversed(constraints)),
        invariants=tuple(reversed(invariants)),
        relations=tuple(reversed(relations)),
    )

    assert StructuralAnalyzer().analyze(first).identity_hash == (
        StructuralAnalyzer().analyze(second).identity_hash
    )


def test_inexact_numeric_invariants_use_declared_tolerance():
    analyzer = StructuralAnalyzer()
    left = analyzer.analyze(StructuralInput(
        1, "scalar",
        invariants=(InvariantResult("measurement", 1.0, exact=False, tolerance=0.001),),
    ))
    right = analyzer.analyze(StructuralInput(
        1, "scalar",
        invariants=(InvariantResult("measurement", 1.0005, exact=False, tolerance=0.001),),
    ))

    result = analyzer.compare_invariants(left, right)
    assert result["matching_invariants"] == ["measurement"]


def test_signature_snapshots_and_recursively_freezes_nested_inputs():
    provenance = {"origin": {"labels": ["original"]}}
    invariant_value = {"measurements": [{"value": 1}]}
    signature = StructuralAnalyzer().analyze(StructuralInput(
        1, "scalar",
        provenance=provenance,
        invariants=(InvariantResult("nested", invariant_value),),
    ))
    original_hash = signature.identity_hash

    provenance["origin"]["labels"].append("mutated")
    invariant_value["measurements"][0]["value"] = 99

    rendered = signature.to_dict()
    assert signature.identity_hash == original_hash
    assert rendered["provenance"]["origin"]["labels"] == ["original"]
    assert rendered["invariants"][0]["value"]["measurements"][0]["value"] == 1

    try:
        signature.provenance["origin"]["new"] = "blocked"
    except TypeError:
        pass
    else:
        raise AssertionError("signature provenance must be immutable")


def test_non_finite_float_values_are_rejected_not_string_coerced():
    for value in (float("nan"), float("inf"), float("-inf")):
        try:
            StructuralAnalyzer().analyze(StructuralInput(
                1, "scalar",
                invariants=(InvariantResult("value", value),),
            ))
        except ValueError:
            continue
        raise AssertionError("non-finite descriptor floats must be rejected")
