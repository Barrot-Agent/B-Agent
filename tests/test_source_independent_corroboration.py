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


def test_same_domain_counts_as_one_independent_source(tmp_path, monkeypatch):
    _configure_storage(tmp_path, monkeypatch)

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    engine = CrossCorroborationEngine()

    engine.evidence_store.add(
        {
            "claim_id": "evidence-001",
            "claim": "Independent verification improves reliability.",
            "source": "article_one",
            "source_url": "https://example.com/article-one",
        }
    )
    engine.evidence_store.add(
        {
            "claim_id": "evidence-002",
            "claim": "Independent verification improves reliability.",
            "source": "article_two",
            "source_url": "https://example.com/article-two",
        }
    )

    result = engine.corroborate("Independent verification improves reliability.")

    assert result["status"] == "corroborated"
    assert result["independent_supporting_sources"] == 1
    assert len(result["supporting_records"]) == 1
    assert result["corroborated_confidence"] == 0.6


def test_different_domains_count_as_independent_sources(tmp_path, monkeypatch):
    _configure_storage(tmp_path, monkeypatch)

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    engine = CrossCorroborationEngine()

    engine.evidence_store.add(
        {
            "claim_id": "evidence-001",
            "claim": "Independent verification improves reliability.",
            "source": "article_one",
            "source_url": "https://example.com/article-one",
        }
    )
    engine.evidence_store.add(
        {
            "claim_id": "evidence-002",
            "claim": "Independent verification improves reliability.",
            "source": "article_two",
            "source_url": "https://independent.org/article-two",
        }
    )

    result = engine.corroborate("Independent verification improves reliability.")

    assert result["independent_supporting_sources"] == 2
    assert len(result["supporting_records"]) == 2
    assert result["corroborated_confidence"] == 0.7


def test_conflicting_domains_are_counted_independently(tmp_path, monkeypatch):
    _configure_storage(tmp_path, monkeypatch)

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    engine = CrossCorroborationEngine()

    engine.evidence_store.add(
        {
            "claim_id": "support-001",
            "claim": "The system is reliable.",
            "source": "source_a",
            "source_url": "https://source-a.example/research",
        }
    )

    engine.evidence_store.add(
        {
            "claim_id": "conflict-001",
            "claim": "The system is not reliable.",
            "source": "source_b",
            "source_url": "https://source-b.example/research",
        }
    )

    result = engine.corroborate("The system is reliable.")

    assert result["independent_supporting_sources"] == 1
    assert result["independent_conflicting_sources"] == 1
    assert result["status"] == "conflicted"
