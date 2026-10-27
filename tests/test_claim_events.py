from barrot_agent.evolution.event_bus import CognitiveEventBus
from barrot_agent.evolution.evidence_normalization import EvidenceNormalizationEngine


def test_normalized_claim_can_emit_event(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module

    monkeypatch.setattr(integrity_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        integrity_module,
        "LEDGER_FILE",
        tmp_path / "outcomes.json",
    )

    bus = CognitiveEventBus()
    received = []

    def observer(event):
        received.append(event)
        return {"status": "received"}

    bus.subscribe("claim_submitted", observer)

    evidence = EvidenceNormalizationEngine().normalize(
        "Independent verification improves reliability in complex systems.",
        source="test_source",
    )[0]

    from barrot_agent.evolution.event_bus import CognitiveEvent

    results = bus.publish(
        CognitiveEvent(
            event_type="claim_submitted",
            payload=evidence,
            source=evidence["source"],
        )
    )

    assert len(received) == 1
    assert received[0].payload["claim"] == evidence["claim"]
    assert results == [{"status": "received"}]
