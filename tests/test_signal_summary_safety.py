from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "signal_summary.py"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "signal-summary.yml"


def load_summary_script():
    spec = importlib.util.spec_from_file_location("signal_summary_safety_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configure_paths(module, tmp_path: Path, monkeypatch, signal_text: str | None):
    signal_file = tmp_path / "latest_signal.json"
    summary_file = tmp_path / "latest_signal_summary.json"
    audio_dir = tmp_path / "generated_audio"
    audio_file = audio_dir / "latest_signal_summary.wav"
    if signal_text is not None:
        signal_file.write_text(signal_text, encoding="utf-8")
    audio_dir.mkdir()
    audio_file.write_bytes(b"stale audio")
    monkeypatch.setattr(module, "SIGNAL_FILE", signal_file)
    monkeypatch.setattr(module, "SUMMARY_FILE", summary_file)
    monkeypatch.setattr(module, "AUDIO_DIR", audio_dir)
    monkeypatch.setattr(module, "AUDIO_FILE", audio_file)
    return summary_file, audio_file


def test_invalid_zero_confidence_signal_persists_not_issued_without_provider(tmp_path, monkeypatch):
    module = load_summary_script()
    summary_file, audio_file = configure_paths(
        module,
        tmp_path,
        monkeypatch,
        json.dumps({
            "timestamp": "2026-10-28T07:23:52Z",
            "score": 44,
            "confidence": 0.0,
            "source": "sentiment unavailable: missing token; provider failed: HTTP 429",
            "news_score": 88,
            "news_entries": 11,
        }),
    )
    monkeypatch.setattr(module, "KEY", "")
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider must not be called")))
    monkeypatch.setattr(module, "speak", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("TTS must not be called")))

    module.main()

    result = json.loads(summary_file.read_text(encoding="utf-8"))
    assert result["status"] == "NOT_ISSUED"
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["summary_only"] is True
    assert "no directional conclusion is supported" in result["summary"].lower()
    assert result["audio"] is None
    assert not audio_file.exists()


def test_missing_signal_still_writes_explicit_not_issued_status(tmp_path, monkeypatch):
    module = load_summary_script()
    summary_file, _ = configure_paths(module, tmp_path, monkeypatch, None)
    monkeypatch.setattr(module, "KEY", "")
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider must not be called")))

    module.main()

    result = json.loads(summary_file.read_text(encoding="utf-8"))
    assert result["status"] == "NOT_ISSUED"
    assert result["forecast_status"] == "NOT_ISSUED"
    assert "signal artifact is missing" in result["summary"]
    assert result["input_error"].startswith("FileNotFoundError")


def test_missing_provider_key_uses_summary_fallback_and_persists(tmp_path, monkeypatch):
    module = load_summary_script()
    summary_file, _ = configure_paths(
        module,
        tmp_path,
        monkeypatch,
        json.dumps({"score": 12, "confidence": 0.7, "source": "local_observation"}),
    )
    monkeypatch.setattr(module, "KEY", "")
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider must not be called")))
    monkeypatch.setattr(module, "speak", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("TTS must not be called")))

    module.main()

    result = json.loads(summary_file.read_text(encoding="utf-8"))
    assert result["status"] == "SUMMARY_FALLBACK_NOT_A_FORECAST"
    assert result["forecast_status"] == "NOT_ISSUED"
    assert "model-generated summarization is unavailable" in result["summary"]
    assert result["audio"] is None


def test_provider_summary_failure_does_not_discard_output(tmp_path, monkeypatch):
    module = load_summary_script()
    summary_file, _ = configure_paths(
        module,
        tmp_path,
        monkeypatch,
        json.dumps({"score": 12, "confidence": 0.7, "source": "local_observation"}),
    )
    monkeypatch.setattr(module, "KEY", "test-key")
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: "")
    monkeypatch.setattr(module, "speak", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("TTS must not be called")))

    module.main()

    result = json.loads(summary_file.read_text(encoding="utf-8"))
    assert result["status"] == "SUMMARY_FALLBACK_NOT_A_FORECAST"
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["source_signal"]["confidence"] == 0.7
    assert result["audio"] is None


def test_summary_workflow_is_read_only_and_artifact_based():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "permissions:" in workflow
    assert "contents: read" in workflow
    assert "actions/upload-artifact@" in workflow
    assert "retention-days: 30" in workflow
    assert "git commit" not in workflow
    assert "git push" not in workflow
    assert "contents: write" not in workflow
