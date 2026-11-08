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



def test_pillars_check_fiction_scan_rejects_non_200(monkeypatch):
    for status in (404, 500):
        response = Mock(status_code=status, text="clean-looking error body")
        monkeypatch.setattr(pillars_check.requests, "get", lambda *args, **kwargs: response)
        ok, detail = pillars_check.check_system_prompt_fiction()
        assert ok is False
        assert detail == f"HTTP {status}"


def test_pillars_check_fiction_scan_reports_http_200_and_scans_body(monkeypatch):
    response = Mock(status_code=200, text="")
    monkeypatch.setattr(pillars_check.requests, "get", lambda *args, **kwargs: response)
    ok, detail = pillars_check.check_system_prompt_fiction()
    assert ok is True
    assert detail == "HTTP 200; clean"

    fiction_term = next(iter(pillars_check.FICTION_TERMS))
    response = Mock(status_code=200, text=fiction_term)
    monkeypatch.setattr(pillars_check.requests, "get", lambda *args, **kwargs: response)
    ok, detail = pillars_check.check_system_prompt_fiction()
    assert ok is False
    assert detail.startswith("HTTP 200; fiction terms present")
