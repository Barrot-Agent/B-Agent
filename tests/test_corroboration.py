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
