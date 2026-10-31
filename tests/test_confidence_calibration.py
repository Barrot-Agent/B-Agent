def test_calibration_records_and_resolves(tmp_path, monkeypatch):
    import barrot_agent.evolution.confidence_calibration as module

    monkeypatch.setattr(module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        module,
        "CALIBRATION_FILE",
        tmp_path / "calibration.json",
    )

    engine = module.ConfidenceCalibrationEngine()

    engine.record("claim-001", 0.8, "supported")

    assert engine.resolve("claim-001", True) is True

    summary = engine.summary()

    assert summary["records"] == 1
    assert summary["resolved"] == 1
    assert summary["accuracy"] == 1.0


def test_calibration_does_not_invent_outcomes(tmp_path, monkeypatch):
    import barrot_agent.evolution.confidence_calibration as module

    monkeypatch.setattr(module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        module,
        "CALIBRATION_FILE",
        tmp_path / "calibration.json",
    )

    engine = module.ConfidenceCalibrationEngine()
    engine.record("claim-001", 0.8, "supported")

    summary = engine.summary()

    assert summary["resolved"] == 0
    assert summary["accuracy"] is None
