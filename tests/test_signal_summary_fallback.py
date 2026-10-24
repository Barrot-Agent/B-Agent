from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_summary_script():
    path = REPO_ROOT / "scripts" / "signal_summary.py"
    spec = importlib.util.spec_from_file_location("test_signal_summary_fallback_module", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_paths(module, tmp_path: Path, monkeypatch, signal: dict) -> Path:
    web_dir = tmp_path / "web"
    web_dir.mkdir(parents=True, exist_ok=True)
    signal_file = web_dir / "latest_signal.json"
    summary_file = web_dir / "latest_signal_summary.json"
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "SIGNAL_FILE", signal_file)
    monkeypatch.setattr(module, "SUMMARY_FILE", summary_file)
    monkeypatch.setattr(module, "AUDIO_DIR", web_dir / "generated_audio")
    monkeypatch.setattr(module, "AUDIO_FILE", web_dir / "generated_audio" / "latest_signal_summary.wav")
    signal_file.write_text(json.dumps(signal), encoding="utf-8")
    return summary_file


def test_missing_key_writes_deterministic_news_only_summary(tmp_path: Path, monkeypatch, capsys):
    module = load_summary_script()
    signal = {
        "score": 88,
        "confidence": 0.0,
        "model_available": False,
        "score_basis": "news_only",
        "source": "news_only_fallback(model_unavailable; provider unavailable)+news(11)",
        "news_score": 88,
        "news_entries": 11,
    }
    summary_file = prepare_paths(module, tmp_path, monkeypatch, signal)
    monkeypatch.setattr(module, "KEY", "")
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("chat must not be called")))
    monkeypatch.setattr(module, "speak", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("TTS must not be called without a key")))

    module.main()

    capsys.readouterr()
    output = json.loads(summary_file.read_text(encoding="utf-8"))
    assert output["summary_source"] == "deterministic_fallback"
    assert output["deterministic_fallback_used"] is True
    assert "news-only sentiment score" in output["summary"]
    assert "not a price forecast" in output["summary"]
    assert "news-only sentiment score" in output["spoken_line"]
    assert output["audio"] is None
    assert output["tts_error"] == "GROQ_API_KEY not set; TTS skipped"
    assert output["source_signal"] == signal


def test_provider_failure_writes_fallback_instead_of_leaving_stale_summary(tmp_path: Path, monkeypatch, capsys):
    module = load_summary_script()
    signal = {
        "score": 50,
        "confidence": 0.0,
        "model_available": False,
        "score_basis": "unavailable_neutral_placeholder",
        "source": "sentiment unavailable (provider unavailable)",
        "news_score": None,
        "news_entries": 0,
    }
    summary_file = prepare_paths(module, tmp_path, monkeypatch, signal)
    monkeypatch.setattr(module, "KEY", "test-key")
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: "")
    monkeypatch.setattr(module, "speak", lambda _line: (None, "HTTP 429 simulated"))

    module.main()

    capsys.readouterr()
    output = json.loads(summary_file.read_text(encoding="utf-8"))
    assert output["summary_source"] == "deterministic_fallback"
    assert "neutral placeholder" in output["summary"]
    assert "not a market signal or price forecast" in output["summary"]
    assert output["audio"] is None
    assert output["tts_error"] == "HTTP 429 simulated"


def test_successful_model_summary_is_marked_as_model_generated(tmp_path: Path, monkeypatch, capsys):
    module = load_summary_script()
    signal = {
        "score": 74,
        "confidence": 0.8,
        "model_available": True,
        "score_basis": "model_and_news_blend",
        "source": "groq:neutral+news(11)",
        "news_score": 88,
        "news_entries": 11,
    }
    summary_file = prepare_paths(module, tmp_path, monkeypatch, signal)
    monkeypatch.setattr(module, "KEY", "test-key")
    responses = iter([
        "The score blends model sentiment with news sentiment. This is not a price forecast.",
        "XRP sentiment score 74. Not a price forecast.",
    ])
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: next(responses))
    monkeypatch.setattr(module, "speak", lambda _line: (None, None))

    module.main()

    capsys.readouterr()
    output = json.loads(summary_file.read_text(encoding="utf-8"))
    assert output["summary_source"] == "groq"
    assert output["deterministic_fallback_used"] is False
    assert output["summary"].startswith("The score blends")
    assert output["spoken_line"].startswith("XRP sentiment score 74.")
    assert output["source_signal"] == signal
