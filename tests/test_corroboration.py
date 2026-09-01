def test_corroboration_returns_structure(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module
    from barrot_agent.evolution.cognitive_integrity import CognitiveIntegrityLoop
    from barrot_agent.evolution.corroboration import CrossCorroborationEngine

    monkeypatch.setattr(integrity_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(integrity_module, "LEDGER_FILE", tmp_path / "outcomes.json")

    loop = CognitiveIntegrityLoop()
    loop.record_outcome(
        "research",
        {"claim": "agents require evidence verification"},
        sources=["research_source"],
        confidence=0.8,
    )

    result = CrossCorroborationEngine().corroborate(
        {"claim": "agents require evidence verification"},
        sources=["new_source"],
    )

    assert "status" in result
    assert "corroborated_confidence" in result


def test_corroboration_exposes_trust_adjusted_confidence(tmp_path, monkeypatch):
    import barrot_agent.evolution.corroboration as module
    import barrot_agent.evolution.evidence_store as store_module

    monkeypatch.setattr(
        store_module,
        "STORE_FILE",
        tmp_path / "evidence.json",
    )

    evidence = {
        "claim_id": "claim-1",
        "claim": "Independent verification improves system reliability.",
        "source": "trusted_source",
        "source_url": "https://example.invalid",
        "content_hash": "hash-1",
        "candidate": True,
        "trust": {
            "authoritative": True,
            "confidence": {
                "lower_bound": 0.9,
            },
            "certificate": {
                "certificate_type": "BVC-1",
            },
        },
    }

    store_module.EvidenceStore().save([evidence])

    engine = module.CrossCorroborationEngine()
    result = engine.corroborate(
        "Independent verification improves system reliability."
    )

    assert "trust" in result
    assert result["trust"]["records_evaluated"] == 1
    assert result["trust"]["authoritative_records"] == 1
    assert result["trust"]["unverified_records"] == 0
    assert result["trust_adjusted_confidence"] > 0
