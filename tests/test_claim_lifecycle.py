from barrot_agent.evolution.claim_lifecycle import ClaimLifecycleEngine


def test_multiple_supporting_sources_becomes_supported():
    result = ClaimLifecycleEngine().determine(2, 0, 0.8)
    assert result["status"] == "supported"


def test_support_and_conflict_becomes_disputed():
    result = ClaimLifecycleEngine().determine(1, 1, 0.5)
    assert result["status"] == "disputed"


def test_no_evidence_is_unverified():
    result = ClaimLifecycleEngine().determine(0, 0, 0.5)
    assert result["status"] == "unverified"
