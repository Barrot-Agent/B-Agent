from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_CASES = [
    ("emit_signal.py", "latest_signal.json", "signal_history.jsonl", "ripple"),
    ("emit_signal_btc.py", "latest_signal_btc.json", "signal_history_btc.jsonl", "bitcoin"),
]


def load_script(filename: str):
    path = REPO_ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(f"test_{path.stem}_{filename}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakePriceResponse:
    def json(self):
        return {"ripple": {"usd": 1.29}, "bitcoin": {"usd": 80000.0}}


@pytest.mark.parametrize("script_name,output_name,history_name,asset_id", SCRIPT_CASES)
def test_provider_failure_uses_news_score_without_halving(
    tmp_path: Path, monkeypatch, capsys, script_name, output_name, history_name, asset_id
):
    module = load_script(script_name)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "_news_score", lambda: (88, 11, ["[bullish] test headline"]))
    monkeypatch.setattr(
        module,
        "analyze_signal",
        lambda _text: (0, 0.0, "sentiment unavailable (provider unavailable)"),
    )
    monkeypatch.setattr(module.requests, "get", lambda *args, **kwargs: FakePriceResponse())

    module.main()

    output = json.loads(capsys.readouterr().out.strip())
    assert output["score"] == 88
    assert output["news_score"] == 88
    assert output["confidence"] == 0.0
    assert output["model_available"] is False
    assert output["score_basis"] == "news_only"
    assert "news_only_fallback" in output["source"]
    assert (tmp_path / "web" / output_name).is_file()
    history = json.loads((tmp_path / "web" / history_name).read_text(encoding="utf-8").splitlines()[-1])
    assert history["price_at_emission"] == (1.29 if asset_id == "ripple" else 80000.0)


@pytest.mark.parametrize("script_name,output_name,history_name,asset_id", SCRIPT_CASES)
def test_missing_model_and_missing_news_uses_neutral_unavailable_placeholder(
    tmp_path: Path, monkeypatch, capsys, script_name, output_name, history_name, asset_id
):
    del asset_id
    module = load_script(script_name)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "_news_score", lambda: (None, 0, []))
    monkeypatch.setattr(
        module,
        "analyze_signal",
        lambda _text: (0, 0.0, "sentiment unavailable (provider unavailable)"),
    )
    monkeypatch.setattr(module.requests, "get", lambda *args, **kwargs: FakePriceResponse())

    module.main()

    output = json.loads(capsys.readouterr().out.strip())
    assert output["score"] == 50
    assert output["confidence"] == 0.0
    assert output["model_available"] is False
    assert output["score_basis"] == "unavailable_neutral_placeholder"
    assert output["news_score"] is None
    assert (tmp_path / "web" / output_name).is_file()
    assert (tmp_path / "web" / history_name).is_file()


@pytest.mark.parametrize("script_name,output_name,history_name,asset_id", SCRIPT_CASES)
def test_available_model_keeps_weighted_blend(
    tmp_path: Path, monkeypatch, capsys, script_name, output_name, history_name, asset_id
):
    del asset_id
    module = load_script(script_name)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "_news_score", lambda: (88, 11, ["[bullish] test headline"]))
    monkeypatch.setattr(module, "analyze_signal", lambda _text: (60, 0.8, "groq:neutral"))
    monkeypatch.setattr(module.requests, "get", lambda *args, **kwargs: FakePriceResponse())

    module.main()

    output = json.loads(capsys.readouterr().out.strip())
    assert output["score"] == 74
    assert output["confidence"] == 0.8
    assert output["model_available"] is True
    assert output["score_basis"] == "model_and_news_blend"
    assert output["source"] == "groq:neutral+news(11)"
    assert (tmp_path / "web" / output_name).is_file()
    assert (tmp_path / "web" / history_name).is_file()
