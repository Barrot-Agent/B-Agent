import json

from scripts import ask_barrot


def test_system_identity_uses_current_xrp_mission_without_stale_capability_claims():
    assert "highest-priority mission is XRP intelligence" in ask_barrot.SYSTEM_BASE
    assert "hourly knowledge ingestion" not in ask_barrot.SYSTEM_BASE
    assert "You do not have technical indicators" not in ask_barrot.SYSTEM_BASE


def test_xrp_mission_status_loader_injects_repository_contracts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "BARROT_XRP_MISSION_HANDOFF.md").write_text("CURRENT MISSION STATUS", encoding="utf-8")
    docs = tmp_path / "research" / "xrp_intelligence"
    docs.mkdir(parents=True)
    (docs / "feature-store-contract.md").write_text("FEATURE STORE STATUS", encoding="utf-8")
    (docs / "forecast-ledger-contract.md").write_text("FORECAST LEDGER STATUS", encoding="utf-8")
    loaded = ask_barrot.load_xrp_intelligence_status()
    assert "CURRENT MISSION STATUS" in loaded
    assert "FEATURE STORE STATUS" in loaded
    assert "FORECAST LEDGER STATUS" in loaded


def test_signal_snapshot_does_not_mislabel_legacy_signal_as_forecast(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    web = tmp_path / "web"
    web.mkdir()
    (web / "latest_signal.json").write_text(json.dumps({
        "timestamp": "2026-11-05T00:00:00Z",
        "score": 0.7,
        "confidence": 0.5,
        "source": "sentiment",
        "forecast_status": "NOT_ISSUED",
        "forecast_model_eligible": False,
    }), encoding="utf-8")
    snapshot = ask_barrot.load_signal_snapshot()
    assert "forecast_status=NOT_ISSUED" in snapshot
    assert "forecast_model_eligible=False" in snapshot
    assert "Do not treat a sentiment/signal score as a validated forecast" in snapshot


def test_answer_artifact_writer_never_overwrites_existing_user_files(tmp_path):
    existing = tmp_path / "barrot_answer.md"
    existing.write_text("user-owned answer", encoding="utf-8")
    output_dir = tmp_path / "answers"

    first = ask_barrot.write_answer_artifact("new answer one", output_dir)
    second = ask_barrot.write_answer_artifact("new answer two", output_dir)

    assert first != second
    assert first.read_text(encoding="utf-8") == "new answer one"
    assert second.read_text(encoding="utf-8") == "new answer two"
    assert existing.read_text(encoding="utf-8") == "user-owned answer"
