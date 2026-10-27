from barrot_agent.evolution.event_bus import CognitiveEventBus
from barrot_agent.evolution.intelligence_pipeline import IntelligencePipeline


def test_new_research_emits_event(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module
    import barrot_agent.evolution.intelligence_pipeline as module

    monkeypatch.setattr(module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(module, "CORPUS_FILE", tmp_path / "corpus.json")
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

    bus.subscribe("research_acquired", observer)

    pipeline = IntelligencePipeline(event_bus=bus)

    item = {
        "source": "test_research",
        "source_url": "https://example.invalid/research",
        "type": "research",
        "content_hash": "test-hash-001",
        "retrieved_at": "2026-08-29T00:00:00+00:00",
        "content": "Agents require independent evidence verification.",
    }

    result = pipeline.synthesize([item])

    assert result["new_items"] == 1
    assert len(received) == 1
    assert received[0].event_type == "research_acquired"
    assert received[0].payload["content_hash"] == "test-hash-001"
