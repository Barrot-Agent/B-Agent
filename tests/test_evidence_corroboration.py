def test_corroboration_uses_independent_evidence(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module
    import barrot_agent.evolution.evidence_store as store_module

    monkeypatch.setattr(integrity_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        integrity_module,
        "LEDGER_FILE",
        tmp_path / "outcomes.json",
    )
    monkeypatch.setattr(store_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        store_module,
        "STORE_FILE",
        tmp_path / "evidence.json",
    )

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    engine = CrossCorroborationEngine()

    engine.evidence_store.add(
        {
            "claim_id": "evidence-001",
            "claim": "Independent verification improves reliability.",
            "source": "source_a",
        }
    )

    result = engine.corroborate(
        "Independent verification improves reliability.",
        sources=["source_b"],
    )

    assert result["status"] == "corroborated"
    assert result["supporting_records"] == ["evidence-001"]


def test_corroboration_excludes_originating_source(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module
    import barrot_agent.evolution.evidence_store as store_module

    monkeypatch.setattr(integrity_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        integrity_module,
        "LEDGER_FILE",
        tmp_path / "outcomes.json",
    )
    monkeypatch.setattr(store_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        store_module,
        "STORE_FILE",
        tmp_path / "evidence.json",
    )

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    engine = CrossCorroborationEngine()

    engine.evidence_store.add(
        {
            "claim_id": "evidence-001",
            "claim": "Independent verification improves reliability.",
            "source": "source_a",
        }
    )

    result = engine.corroborate(
        "Independent verification improves reliability.",
        sources=["source_a"],
    )

    assert result["status"] == "insufficient_evidence"
    assert result["supporting_records"] == []
