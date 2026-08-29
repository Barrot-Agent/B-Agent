from barrot_agent.evolution.event_bus import CognitiveEventBus


def _configure_storage(tmp_path, monkeypatch):
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


def test_corroborated_claim_emits_event(tmp_path, monkeypatch):
    _configure_storage(tmp_path, monkeypatch)

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    bus = CognitiveEventBus()
    received = []
    bus.subscribe("claim_corroborated", lambda event: received.append(event))

    engine = CrossCorroborationEngine(event_bus=bus)
    engine.evidence_store.add(
        {
            "claim_id": "evidence-001",
            "claim": "Independent verification improves reliability.",
            "source": "independent_source",
            "source_url": "https://independent.example/research",
        }
    )

    result = engine.corroborate("Independent verification improves reliability.")

    assert result["status"] == "corroborated"
    assert len(received) == 1
    assert received[0].event_type == "claim_corroborated"


def test_conflicted_claim_emits_event(tmp_path, monkeypatch):
    _configure_storage(tmp_path, monkeypatch)

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    bus = CognitiveEventBus()
    received = []
    bus.subscribe("claim_conflicted", lambda event: received.append(event))

    engine = CrossCorroborationEngine(event_bus=bus)
    engine.evidence_store.add(
        {
            "claim_id": "conflict-001",
            "claim": "The system is not reliable.",
            "source": "independent_source",
            "source_url": "https://independent.example/research",
        }
    )

    result = engine.corroborate("The system is reliable.")

    assert result["status"] == "conflicted"
    assert len(received) == 1
    assert received[0].event_type == "claim_conflicted"


def test_insufficient_evidence_emits_event(tmp_path, monkeypatch):
    _configure_storage(tmp_path, monkeypatch)

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    bus = CognitiveEventBus()
    received = []
    bus.subscribe(
        "claim_insufficient_evidence",
        lambda event: received.append(event),
    )

    engine = CrossCorroborationEngine(event_bus=bus)
    result = engine.corroborate("Independent verification improves reliability.")

    assert result["status"] == "insufficient_evidence"
    assert len(received) == 1
    assert received[0].event_type == "claim_insufficient_evidence"
