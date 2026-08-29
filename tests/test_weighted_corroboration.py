def _configure_storage(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as integrity_module
    import barrot_agent.evolution.confidence_calibration as calibration_module
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

    monkeypatch.setattr(calibration_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        calibration_module,
        "CALIBRATION_FILE",
        tmp_path / "calibration.json",
    )


def test_weighted_independent_support(tmp_path, monkeypatch):
    _configure_storage(tmp_path, monkeypatch)

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    engine = CrossCorroborationEngine()

    for claim_id, domain in (
        ("evidence-001", "example.com"),
        ("evidence-002", "independent.org"),
    ):
        engine.evidence_store.add(
            {
                "claim_id": claim_id,
                "claim": "Independent verification improves reliability.",
                "source": domain,
                "source_url": f"https://{domain}/research",
            }
        )

    result = engine.corroborate("Independent verification improves reliability.")

    assert result["independent_supporting_sources"] == 2
    assert result["status"] == "corroborated"
    assert result["lifecycle_status"] == "supported"
    assert result["corroborated_confidence"] == 0.7


def test_conflicting_evidence_preserves_dispute(tmp_path, monkeypatch):
    _configure_storage(tmp_path, monkeypatch)

    from barrot_agent.evolution.corroboration import (
        CrossCorroborationEngine,
    )

    engine = CrossCorroborationEngine()

    engine.evidence_store.add(
        {
            "claim_id": "support",
            "claim": "The system is reliable.",
            "source": "source_a",
            "source_url": "https://source-a.example/research",
        }
    )
    engine.evidence_store.add(
        {
            "claim_id": "conflict",
            "claim": "The system is not reliable.",
            "source": "source_b",
            "source_url": "https://source-b.example/research",
        }
    )

    result = engine.corroborate("The system is reliable.")

    assert result["status"] == "conflicted"
    assert result["lifecycle_status"] == "disputed"
    assert result["independent_supporting_sources"] == 1
    assert result["independent_conflicting_sources"] == 1
