import base64
from pathlib import Path
from unittest.mock import Mock

import jwt

from scripts import pillars_check


WORKFLOW = Path(".github/workflows/pillars-check.yml").read_text(encoding="utf-8")


def test_pillars_check_github_probe_uses_read_only_installation_get(monkeypatch):
    monkeypatch.setenv("GITHUB_APP_PROBE_ENABLED", "true")
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



def test_repo_source_fiction_rejects_non_200(monkeypatch):
    for status in (404, 500):
        response = Mock(status_code=status, text="clean-looking error body")
        monkeypatch.setattr(pillars_check.requests, "get", lambda *args, **kwargs: response)
        ok, detail = pillars_check.check_repo_source_fiction()
        assert ok is False
        assert detail == f"HTTP {status}"


def test_repo_source_fiction_reports_http_200_and_scans_body(monkeypatch):
    response = Mock(status_code=200, text="")
    monkeypatch.setattr(pillars_check.requests, "get", lambda *args, **kwargs: response)
    ok, detail = pillars_check.check_repo_source_fiction()
    assert ok is True
    assert detail == "GitHub main source clean; deployed runtime not inspected"

    fiction_term = next(iter(pillars_check.FICTION_TERMS))
    response = Mock(status_code=200, text=fiction_term)
    monkeypatch.setattr(pillars_check.requests, "get", lambda *args, **kwargs: response)
    ok, detail = pillars_check.check_repo_source_fiction()
    assert ok is False
    assert detail.startswith("fiction terms present in GitHub main hf_space/app.py")



def test_github_probe_skips_without_explicit_opt_in(monkeypatch):
    for name in ("GITHUB_APP_PROBE_ENABLED", "GITHUB_APP_ID", "GITHUB_APP_PRIVATE_KEY", "GITHUB_INSTALLATION_ID"):
        monkeypatch.delenv(name, raising=False)

    def fail_get(*args, **kwargs):
        raise AssertionError("GitHub App credentials must not be used without explicit opt-in")

    monkeypatch.setattr(pillars_check.requests, "get", fail_get)
    ok, detail = pillars_check.check_github()

    assert ok is None
    assert "manual workflow_dispatch opt-in" in detail


def test_databricks_probe_skips_without_explicit_opt_in(monkeypatch):
    for name in ("DATABRICKS_PROBE_ENABLED", "DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_WAREHOUSE_ID"):
        monkeypatch.delenv(name, raising=False)

    def fail_post(*args, **kwargs):
        raise AssertionError("Databricks credentials must not be used without explicit opt-in")

    monkeypatch.setattr(pillars_check.requests, "post", fail_post)
    ok, detail = pillars_check.check_databricks()

    assert ok is None
    assert "manual workflow_dispatch opt-in" in detail


def test_explicit_databricks_probe_is_select_one_and_surfaces_forbidden(monkeypatch):
    monkeypatch.setenv("DATABRICKS_PROBE_ENABLED", "true")
    monkeypatch.setenv("DATABRICKS_HOST", "workspace.example")
    monkeypatch.setenv("DATABRICKS_TOKEN", "test-token")
    monkeypatch.setenv("DATABRICKS_WAREHOUSE_ID", "warehouse-123")
    calls = []
    response = Mock(status_code=403)

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return response

    monkeypatch.setattr(pillars_check.requests, "post", fake_post)
    ok, detail = pillars_check.check_databricks()

    assert ok is False
    assert detail == "HTTP 403"
    assert calls[0][0] == "https://workspace.example/api/2.0/sql/statements"
    assert calls[0][1]["json"]["statement"] == "SELECT 1"
    assert calls[0][1]["json"]["warehouse_id"] == "warehouse-123"


def test_workflow_withholds_platform_credentials_from_scheduled_check():
    default_step = WORKFLOW.split("- name: Run public/read-only pillars checks", 1)[1].split(
        "- name: Install PyJWT for the explicitly approved GitHub App probe", 1
    )[0]
    assert "GITHUB_APP_PRIVATE_KEY" not in default_step
    assert "DATABRICKS_TOKEN" not in default_step
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in WORKFLOW
    assert "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0" in WORKFLOW
    assert "confirm_read_only_github_app_probe" in WORKFLOW
    assert "confirm_read_only_databricks_probe" in WORKFLOW
    assert "default: NO" in WORKFLOW

def test_manual_credential_probes_are_restricted_to_main():
    assert "if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main' && inputs.confirm_read_only_github_app_probe == 'YES'" in WORKFLOW
    assert "if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main' && inputs.confirm_read_only_databricks_probe == 'YES'" in WORKFLOW
    assert "GITHUB_APP_PRIVATE_KEY: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}" in WORKFLOW
    assert "DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}" in WORKFLOW
