
def test_calibration_records_trust_metadata(tmp_path, monkeypatch):
    import barrot_agent.evolution.confidence_calibration as module

    monkeypatch.setattr(
        module,
        "CALIBRATION_FILE",
        tmp_path / "confidence.json",
    )
    monkeypatch.setattr(
        module,
        "DATA_DIR",
        tmp_path,
    )

    engine = module.ConfidenceCalibrationEngine()

    trust = {
        "records_evaluated": 2,
        "authoritative_records": 2,
        "unverified_records": 0,
        "average_trust_confidence": 0.91,
    }

    record = engine.record(
        claim_id="claim-1",
        confidence=0.88,
        status="corroborated",
        trust=trust,
    )

    assert record["trust"]["authoritative_records"] == 2
    assert engine.trust_summary()["authoritative_records"] == 1
    assert engine.trust_summary()["average_trust_confidence"] == 0.91


def test_calibration_accepts_aggregate_trust_summary(tmp_path, monkeypatch):
    import barrot_agent.evolution.confidence_calibration as module

    monkeypatch.setattr(
        module,
        "CALIBRATION_FILE",
        tmp_path / "confidence.json",
    )

    engine = module.ConfidenceCalibrationEngine()

    trust = {
        "records_evaluated": 2,
        "authoritative_records": 2,
        "unverified_records": 0,
        "average_trust_confidence": 0.91,
    }

    record = engine.record(
        claim_id="aggregate-trust-1",
        confidence=0.88,
        status="corroborated",
        trust=trust,
    )

    assert record["trust"]["authoritative_records"] == 2
    assert engine.trust_summary()["authoritative_records"] == 1
    assert engine.trust_summary()["average_trust_confidence"] == 0.91
