from barrot_agent.structural_analysis import ConstraintResult, EvidenceStage, InvariantResult, StructuralAnalyzer, StructuralInput, StructuralRelation, RelationType, VerificationStatus


def test_deterministic_and_order_independent_signature():
    a = StructuralInput([[1,0],[0,1]], "matrix", constraints=(ConstraintResult("det", "satisfied"), ConstraintResult("rank", "satisfied")), invariants=(InvariantResult("rank",2),), dimension=2)
    b = StructuralInput([[1,0],[0,1]], "matrix", constraints=tuple(reversed(a.constraints)), invariants=tuple(reversed(a.invariants)), dimension=2)
    assert StructuralAnalyzer().analyze(a).identity_hash == StructuralAnalyzer().analyze(b).identity_hash


def test_regions_remain_distinct():
    assert StructuralAnalyzer().analyze(StructuralInput(0,"scalar",constraints=(ConstraintResult("p","violated"),))).valid_region == "invalid"
    assert StructuralAnalyzer().analyze(StructuralInput(None,"scalar",constraints=(ConstraintResult("p","unknown"),))).valid_region == "unresolved"


def test_evaluator_budget_and_type_safety():
    try: StructuralAnalyzer(max_evaluations=0)
    except ValueError: pass
    else: raise AssertionError
    a=StructuralAnalyzer(constraint_evaluators=[lambda x: ConstraintResult("ok","satisfied")])
    assert a.analyze(StructuralInput(1,"scalar")).constraints[0].evidence_stage == EvidenceStage.COMPUTED


def test_invariant_similarity_is_not_equivalence():
    s=StructuralAnalyzer()
    a=s.analyze(StructuralInput(1,"a",invariants=(InvariantResult("rank",2),)))
    b=s.analyze(StructuralInput(2,"b",invariants=(InvariantResult("rank",2),)))
    c=s.compare_invariants(a,b)
    assert c["descriptor_match"] is True and c["equivalence_claim"] is None and c["verification"] == "unverified"


def test_relations_are_explicit_and_typed():
    r=StructuralRelation("A","B",RelationType.BOUNDARY_OF,criterion="closure witness")
    s=StructuralAnalyzer().analyze(StructuralInput("x","region",relations=(r,)))
    assert s.relations[0].relation == RelationType.BOUNDARY_OF
    assert s.relations[0].verification == VerificationStatus.UNVERIFIED


def test_invalid_dimension_rejected():
    try: StructuralInput(1,"scalar",dimension=-1)
    except ValueError: pass
    else: raise AssertionError
