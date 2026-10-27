from barrot_agent.evolution.event_bus import CognitiveEvent, CognitiveEventBus


def test_event_bus_dispatches_event(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module

    monkeypatch.setattr(integrity_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(integrity_module, "LEDGER_FILE", tmp_path / "outcomes.json")

    bus = CognitiveEventBus()
    received = []

    def observer(event):
        received.append(event.payload["claim"])
        return {"status": "observed"}

    bus.subscribe("research_acquired", observer)

    results = bus.publish(
        CognitiveEvent(
            event_type="research_acquired",
            payload={"claim": "Evidence requires corroboration"},
            source="research_engine",
        )
    )

    assert received == ["Evidence requires corroboration"]
    assert results == [{"status": "observed"}]


def test_event_bus_blocks_nested_dispatch(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module

    monkeypatch.setattr(integrity_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(integrity_module, "LEDGER_FILE", tmp_path / "outcomes.json")

    bus = CognitiveEventBus()
    calls = []

    def observer(event):
        calls.append(event.event_type)
        nested = bus.publish(
            CognitiveEvent(
                event_type="nested",
                payload={},
                source="observer",
            )
        )
        assert nested == []

    bus.subscribe("primary", observer)
    bus.publish(
        CognitiveEvent(
            event_type="primary",
            payload={},
            source="test",
        )
    )

    assert calls == ["primary"]
