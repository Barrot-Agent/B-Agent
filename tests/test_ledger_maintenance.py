def test_compact_ledger_retains_limit(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module
    import barrot_agent.evolution.ledger_maintenance as maintenance

    ledger_file = tmp_path / "outcomes.json"
    monkeypatch.setattr(integrity_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(integrity_module, "LEDGER_FILE", ledger_file)
    monkeypatch.setattr(maintenance, "LEDGER_FILE", ledger_file)

    from barrot_agent.evolution.cognitive_integrity import CognitiveIntegrityLoop

    loop = CognitiveIntegrityLoop()
    for number in range(5):
        loop.record_outcome("test", {"claim": f"event {number}"})

    result = maintenance.compact_ledger(max_records=3)

    assert result["after"] == 3
    assert result["removed"] == 2
