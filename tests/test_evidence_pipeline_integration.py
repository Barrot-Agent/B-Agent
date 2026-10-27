from barrot_agent.evolution.event_bus import CognitiveEventBus
from barrot_agent.evolution.intelligence_pipeline import IntelligencePipeline


def test_research_flows_through_evidence_store_and_claim_event(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module
    import barrot_agent.evolution.evidence_store as store_module
    import barrot_agent.evolution.intelligence_pipeline as pipeline_module

    monkeypatch.setattr(pipeline_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        pipeline_module,
        "CORPUS_FILE",
        tmp_path / "corpus.json",
    )

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

    bus = CognitiveEventBus()
    claims = []

    def observer(event):
        claims.append(event.payload)
        return {"status": "received"}

    bus.subscribe("claim_submitted", observer)

    pipeline = IntelligencePipeline(event_bus=bus)

    item = {
        "source": "integration_test",
        "source_url": "https://example.invalid/research",
        "type": "research",
        "content_hash": "integration-hash-001",
        "retrieved_at": "2026-08-29T00:00:00+00:00",
        "content": (
            "Independent verification improves reliability in complex systems. "
            "Multiple sources reduce dependence on a single source."
        ),
    }

    result = pipeline.synthesize([item])

    assert result["new_items"] == 1
    assert len(claims) == 2
    assert pipeline.evidence_store.summary()["records"] == 2
    assert all(claim["candidate"] is True for claim in claims)
