from __future__ import annotations

import json

import pytest

from barrot_agent.orchestration import shared_inference


class FakeResponse:
    def __init__(self, body: dict):
        self.body = json.dumps(body).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


def test_local_llama_provider_uses_loopback_endpoint_without_api_key(monkeypatch):
    monkeypatch.setenv("BARROT_INFERENCE_PROVIDER", "local_llama")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("FIREWORKS_API_KEY", raising=False)
    monkeypatch.delenv("LOCAL_LLAMA_MODEL", raising=False)
    provider = shared_inference.get_provider()
    assert provider == {
        "name": "local_llama",
        "api_key": "",
        "base_url": "http://127.0.0.1:8081/v1",
        "default_model": "local",
    }


def test_local_llama_chat_sends_openai_compatible_request_without_auth(monkeypatch):
    monkeypatch.setenv("BARROT_INFERENCE_PROVIDER", "local_llama")
    monkeypatch.setenv("LOCAL_LLAMA_BASE_URL", "http://127.0.0.1:8081/v1")
    monkeypatch.setenv("LOCAL_LLAMA_MODEL", "llama-3.2-1b-q4km")
    captured = {}

    def fake_urlopen(request, timeout=0):
        captured["url"] = request.full_url
        captured["headers"] = {k.lower(): v for k, v in request.header_items()}
        captured["timeout"] = timeout
        captured["payload"] = json.loads(request.data.decode())
        return FakeResponse({
            "choices": [{"message": {"role": "assistant", "content": "BARROT LOCAL LLAMA ONLINE"}}]
        })

    monkeypatch.setattr(shared_inference.urllib.request, "urlopen", fake_urlopen)
    result = shared_inference.ask(
        "Reply exactly: BARROT LOCAL LLAMA ONLINE",
        model=shared_inference.get_provider()["default_model"],
        max_tokens=32,
        temperature=0,
        timeout=180,
    )

    assert result == "BARROT LOCAL LLAMA ONLINE"
    assert captured["url"] == "http://127.0.0.1:8081/v1/chat/completions"
    assert "authorization" not in captured["headers"]
    assert captured["timeout"] == 180
    assert captured["payload"]["model"] == "llama-3.2-1b-q4km"
    assert captured["payload"]["max_tokens"] == 32


def test_auto_provider_preserves_existing_groq_priority(monkeypatch):
    monkeypatch.delenv("BARROT_INFERENCE_PROVIDER", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("FIREWORKS_API_KEY", "test-fireworks-key")
    provider = shared_inference.get_provider()
    assert provider["name"] == "groq"
    assert provider["api_key"] == "test-groq-key"


def test_explicit_local_selection_does_not_silently_fallback_to_cloud(monkeypatch):
    monkeypatch.setenv("BARROT_INFERENCE_PROVIDER", "local_llama")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("FIREWORKS_API_KEY", "test-fireworks-key")

    def fail_urlopen(request, timeout=0):
        raise OSError("connection refused")

    monkeypatch.setattr(shared_inference.urllib.request, "urlopen", fail_urlopen)
    with pytest.raises(shared_inference.InferenceError, match="local_llama request failed"):
        shared_inference.ask("hello")
