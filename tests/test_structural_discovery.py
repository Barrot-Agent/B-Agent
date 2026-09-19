from barrot_agent.geometry.structural_discovery import (
    StructuralDiscoveryCore, Constraint, CorrespondenceType,
)


def det2x2(rep):
    m = rep.data
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def rank2x2(rep):
    d = det2x2(rep)
    if d != 0:
        return 2
    if any(any(x != 0 for x in row) for row in rep.data):
        return 1
    return 0


def test_rank_stratification_distinguishes_matrices():
    core = StructuralDiscoveryCore()
    rep_full_rank = core.register_representation(
        domain="linear_algebra", kind="matrix", data=[[1, 0], [0, 1]],
        transformation_group="GL(2,R)",
    )
    rep_rank1 = core.register_representation(
        domain="linear_algebra", kind="matrix", data=[[1, 2], [2, 4]],
        transformation_group="GL(2,R)",
    )
    full_rank_constraint = Constraint("is_invertible", lambda r: det2x2(r) != 0)
    sig_a = core.compute_signature(
        rep_full_rank, {"determinant": det2x2, "rank": rank2x2}, [full_rank_constraint]
    )
    sig_b = core.compute_signature(
        rep_rank1, {"determinant": det2x2, "rank": rank2x2}, [full_rank_constraint]
    )
    assert sig_a.invariants["rank"] == 2
    assert sig_b.invariants["rank"] == 1
    assert sig_a.feasibility["is_invertible"].value == "valid"
    assert sig_b.feasibility["is_invertible"].value == "invalid"


def test_unsupported_equivalence_claim_forced_to_unresolved():
    core = StructuralDiscoveryCore()
    rep_a = core.register_representation(domain="linear_algebra", kind="matrix", data=[[1, 0], [0, 1]])
    rep_b = core.register_representation(domain="linear_algebra", kind="matrix", data=[[1, 2], [2, 4]])

    def no_real_test(a, b):
        return None

    claim = core.claim_correspondence(
        rep_a, rep_b, CorrespondenceType.ISOMORPHISM,
        criterion="none supplied", test_fn=no_real_test,
    )
    assert claim.correspondence_type.value == "unresolved"
