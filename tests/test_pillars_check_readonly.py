import base64
from pathlib import Path
from unittest.mock import Mock

import jwt

from scripts import pillars_check


WORKFLOW = Path(".github/workflows/pillars-check.yml").read_text(encoding="utf-8")


def test_pillars_check_github_probe_uses_read_only_installation_get(monkeypatch):
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", "test-private-key")
    monkeypatch.setenv("GITHUB_INSTALLATION_ID", "67890")
    monkeypatch.setattr(jwt, "encode", lambda payload, key, algorithm: "test-app-jwt")
    response = Mock(status_code=200)
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    def fail_post(*args, **kwargs):
        raise AssertionError("GitHub App installation probe must not mint an installation token")

    monkeypatch.setattr(pillars_check.requests, "get", fake_get)
    monkeypatch.setattr(pillars_check.requests, "post", fail_post)
    ok, detail = pillars_check.check_github()

    assert ok is True
    assert detail == "HTTP 200"
    assert calls[0][0] == "https://api.github.com/app/installations/67890"
    assert "access_tokens" not in calls[0][0]
    assert calls[0][1]["headers"]["Authorization"] == "Bearer test-app-jwt"


def test_pillars_check_workflow_is_read_only_and_does_not_persist_checkout_credentials():
    assert "permissions:\n  contents: read" in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "contents: write" not in WORKFLOW
    assert "actions: write" not in WORKFLOW
    assert "git push" not in WORKFLOW
    assert "workflow_dispatch:" in WORKFLOW
    assert "schedule:" in WORKFLOW


def test_pillars_source_checks_do_not_claim_deployed_runtime_verification(monkeypatch):
    response = Mock(status_code=200)
    response.json.return_value = {
        "content": base64.b64encode("Barrot-Ω".encode("utf-8")).decode("ascii")
    }
    response.text = "clean source"
    monkeypatch.setattr(pillars_check.requests, "get", lambda url, **kwargs: response)

    ok, detail = pillars_check.check_repo_source_marker()
    assert ok is True
    assert "GitHub main source marker present" in detail
    assert "deployed Space revision not checked" in detail

    ok, detail = pillars_check.check_repo_source_fiction()
    assert ok is True
    assert "GitHub main source clean" in detail
    assert "deployed runtime not inspected" in detail


def test_pillars_check_labels_source_checks_without_runtime_claims():
    names = [name for name, _ in pillars_check.CHECKS]
    assert "repo_source_marker" in names
    assert "repo_source_fiction" in names
    assert "deploy_sync" not in names
    assert "system_prompt_fiction" not in names


def test_hf_runtime_probe_rejects_non_200_even_if_payload_claims_running(monkeypatch):
    response = Mock(status_code=503)
    response.json.return_value = {"stage": "RUNNING"}
    monkeypatch.setattr(pillars_check.requests, "get", lambda url, **kwargs: response)

    ok, detail = pillars_check.check_hf_space()

    assert ok is False
    assert detail == "HTTP 503"


def test_hf_runtime_probe_rejects_non_object_json(monkeypatch):
    response = Mock(status_code=200)
    response.json.return_value = ["RUNNING"]
    monkeypatch.setattr(pillars_check.requests, "get", lambda url, **kwargs: response)

    ok, detail = pillars_check.check_hf_space()

    assert ok is False
    assert detail == "invalid runtime response: expected object"
