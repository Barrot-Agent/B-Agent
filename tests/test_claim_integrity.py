from barrot_agent.evolution.claim_integrity import ClaimIntegrityEngine


def test_detects_explicit_contradiction():
    engine = ClaimIntegrityEngine()

    result = engine.compare(
        "Barrot uses evidence verification",
        "Barrot does not use evidence verification",
    )

    assert result["status"] == "contradiction"


def test_detects_agreement():
    engine = ClaimIntegrityEngine()

    result = engine.compare(
        "Agents require evidence verification",
        "Agents require evidence verification",
    )

    assert result["status"] == "agreement"
