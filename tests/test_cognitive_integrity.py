from barrot_agent.evolution.cognitive_integrity import CognitiveIntegrityLoop


def test_integrity_loop_records_outcome(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as module

    monkeypatch.setattr(module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(module, "LEDGER_FILE", tmp_path / "outcomes.json")

    loop = CognitiveIntegrityLoop()
    record = loop.record_outcome(
        "test",
        {"result": "verified"},
        sources=["internal_test"],
        confidence=0.9,
    )

    assert record["operation"] == "test"
    assert loop.evaluate_integrity()["records"] == 1
