from barrot_agent.evolution.evidence_normalization import (
    EvidenceNormalizationEngine,
)


def test_normalizes_text_into_individual_claims():
    engine = EvidenceNormalizationEngine()

    records = engine.normalize(
        (
            "Independent verification improves reliability in complex systems. "
            "Multiple sources can reduce dependence on a single source."
        ),
        source="test_source",
        source_url="https://example.invalid",
        content_hash="abc123",
    )

    assert len(records) == 2
    assert records[0]["candidate"] is True
    assert records[0]["source"] == "test_source"
    assert records[0]["content_hash"] == "abc123"
    assert records[0]["claim_id"]
