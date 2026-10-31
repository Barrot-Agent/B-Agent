from barrot_agent.evolution.evidence_quality import EvidenceQualityEngine


def test_complete_evidence_scores_higher_than_incomplete():
    engine = EvidenceQualityEngine()

    complete = engine.score(
        {
            "claim_id": "one",
            "claim": "Testing improves reliability.",
            "source": "research",
            "source_url": "https://example.com/research",
        }
    )

    incomplete = engine.score(
        {
            "claim": "Testing improves reliability.",
        }
    )

    assert complete["quality_score"] > incomplete["quality_score"]


def test_quality_score_is_bounded():
    score = EvidenceQualityEngine().score({"claim_id": "one", "claim": "A", "source": "B"})

    assert 0.0 <= score["quality_score"] <= 1.0
