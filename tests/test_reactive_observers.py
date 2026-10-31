from barrot_agent.evolution.event_bus import CognitiveEvent, CognitiveEventBus
from barrot_agent.evolution.reactive_observers import ReactiveCorroborationObserver


def test_reactive_observer_handles_claim(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module

    monkeypatch.setattr(integrity_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        integrity_module,
        "LEDGER_FILE",
        tmp_path / "outcomes.json",
    )

    bus = CognitiveEventBus()
    observer = ReactiveCorroborationObserver()
    observer.register(bus)

    results = bus.publish(
        CognitiveEvent(
            event_type="claim_submitted",
            payload={"claim": "Evidence should be independently verified"},
            source="test_engine",
        )
    )

    assert len(results) == 1
    assert "status" in results[0]
