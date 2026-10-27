def test_evidence_store_preserves_provenance(tmp_path, monkeypatch):
    import barrot_agent.evolution.evidence_store as module

    monkeypatch.setattr(module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(module, "STORE_FILE", tmp_path / "evidence.json")

    store = module.EvidenceStore()

    evidence = {
        "claim_id": "claim-001",
        "claim": "Independent verification improves reliability.",
        "source": "source_a",
        "source_url": "https://example.invalid/a",
    }

    result = store.add(evidence)

    assert result["status"] == "stored"
    assert len(store.get("claim-001")) == 1
    assert store.summary()["sources"] == 1


def test_evidence_store_allows_multiple_sources(tmp_path, monkeypatch):
    import barrot_agent.evolution.evidence_store as module

    monkeypatch.setattr(module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(module, "STORE_FILE", tmp_path / "evidence.json")

    store = module.EvidenceStore()

    store.add(
        {
            "claim_id": "claim-001",
            "claim": "Verification improves reliability.",
            "source": "source_a",
        }
    )
    store.add(
        {
            "claim_id": "claim-001",
            "claim": "Verification improves reliability.",
            "source": "source_b",
        }
    )

    assert len(store.get("claim-001")) == 2
    assert store.summary()["sources"] == 2
