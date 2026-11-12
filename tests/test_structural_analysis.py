import json
import pytest

from barrot_agent.structural_analysis import (
    ConstraintResult, EvidenceStage, InvariantResult, StructuralAnalyzer,
    StructuralInput, StructuralRelation, RelationType, VerificationStatus,
)


def test_deterministic_and_order_independent_signature():
    a = StructuralInput([[1, 0], [0, 1]], "matrix", constraints=(ConstraintResult("det", "satisfied"), ConstraintResult("rank", "satisfied")), invariants=(InvariantResult("rank", 2),), dimension=2)
    b = StructuralInput([[1, 0], [0, 1]], "matrix", constraints=tuple(reversed(a.constraints)), invariants=tuple(reversed(a.invariants)), dimension=2)
    assert StructuralAnalyzer().analyze(a).identity_hash == StructuralAnalyzer().analyze(b).identity_hash


def test_regions_remain_distinct():
    analyzer = StructuralAnalyzer()
    assert analyzer.analyze(StructuralInput(0, "scalar", constraints=(ConstraintResult("p", "violated"),))).valid_region == "invalid"
    assert analyzer.analyze(StructuralInput(None, "scalar", constraints=(ConstraintResult("p", "unknown"),))).valid_region == "unresolved"


def test_evaluator_budget_and_type_safety():
    with pytest.raises(ValueError):
        StructuralAnalyzer(max_evaluations=0)
    with pytest.raises(ValueError):
        StructuralAnalyzer(max_evaluations=True)
    analyzer = StructuralAnalyzer(constraint_evaluators=[lambda x: ConstraintResult("ok", "satisfied")])
    assert analyzer.analyze(StructuralInput(1, "scalar")).constraints[0].evidence_stage == EvidenceStage.COMPUTED
    with pytest.raises(TypeError):
        StructuralAnalyzer(constraint_evaluators=[lambda x: "not evidence"]).analyze(StructuralInput(1, "scalar"))


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
    with pytest.raises(ValueError):
        StructuralInput(1, "scalar", dimension=-1)
    with pytest.raises(ValueError):
        StructuralInput(1, "scalar", dimension=True)


def test_signature_serializes_to_json_with_enum_values():
    signature = StructuralAnalyzer().analyze(StructuralInput(
        "x", "scalar", constraints=(ConstraintResult("positive", "satisfied"),),
        invariants=(InvariantResult("value", 2.0),),
    ))
    decoded = json.loads(signature.to_json())
    assert decoded["constraints"][0]["evidence_stage"] == "computed"
    assert decoded["invariants"][0]["verification"] == "unverified"


def test_full_descriptor_metadata_affects_deterministic_hash():
    a = StructuralAnalyzer().analyze(StructuralInput(1, "scalar", constraints=(ConstraintResult("c", "satisfied", detail="one"),)))
    b = StructuralAnalyzer().analyze(StructuralInput(1, "scalar", constraints=(ConstraintResult("c", "satisfied", detail="two"),)))
    assert a.identity_hash != b.identity_hash


def test_duplicate_invariant_names_are_compared_without_data_loss():
    analyzer = StructuralAnalyzer()
    a = analyzer.analyze(StructuralInput(1, "scalar", invariants=(InvariantResult("rank", 1), InvariantResult("rank", 2))))
    b = analyzer.analyze(StructuralInput(2, "scalar", invariants=(InvariantResult("rank", 1), InvariantResult("rank", 3))))
    comparison = analyzer.compare_invariants(a, b)
    assert comparison["common_invariants"] == ["rank"]
    assert comparison["matching_invariants"] == []
    assert comparison["descriptor_match"] is False


def test_provenance_is_part_of_identity():
    analyzer = StructuralAnalyzer()
    a = analyzer.analyze(StructuralInput("x", "scalar", provenance={"source": "a"}))
    b = analyzer.analyze(StructuralInput("x", "scalar", provenance={"source": "b"}))
    assert a.identity_hash != b.identity_hash


def test_non_finite_or_unsupported_values_are_rejected():
    with pytest.raises(ValueError):
        InvariantResult("bad", float("nan"))
    with pytest.raises(TypeError):
        StructuralInput(object(), "opaque", provenance={"bad": object()})


def test_relation_endpoints_are_required():
    with pytest.raises(ValueError):
        StructuralRelation("", "B", RelationType.EQUAL)
