import json

from scripts.model_runtime_inventory import inspect_runtime


def test_inventory_reports_provider_surfaces_without_secret_values(tmp_path):
    (tmp_path / "opencode.json").write_text(json.dumps({
        "default_agent": "barrot",
        "model": "opencode/deepseek-v4.1-flash-free",
        "mcp": {"servers": {"lunaroute": {"disabled": True}}},
        "provider": {"lunaroute": {"models": {"example": {"name": "Example"}}}},
    }), encoding="utf-8")

    report = inspect_runtime(tmp_path, {
        "GROQ_API_KEY": "never-serialize-this",
        "FIREWORKS_API_KEY": "",
        "BARROT_LLM_PROVIDER": "groq",
    })

    assert report["active_worker_snapshot"]["provider"] == "groq"
    assert report["active_worker_snapshot"]["credential_presence"]["GROQ_API_KEY"] is True
    assert report["opencode_snapshot"]["model"] == "opencode/deepseek-v4.1-flash-free"
    assert report["opencode_snapshot"]["lunaroute_mcp_disabled"] is True
    rendered = json.dumps(report)
    assert "never-serialize-this" not in rendered
    assert report["safety"]["network_requests_made"] is False
    assert report["safety"]["model_weights_read_or_modified"] is False


def test_local_provider_is_reported_as_configuration_not_connectivity(tmp_path):
    report = inspect_runtime(tmp_path, {
        "BARROT_LLM_PROVIDER": "local",
        "BARROT_LLM_BASE_URL": "http://127.0.0.1:8081/v1/chat/completions",
        "BARROT_LLM_MODEL": "local-model",
        "BARROT_LLM_API_KEY": "local-secret",
    })

    active = report["active_worker_snapshot"]
    assert active["provider"] == "local"
    assert active["model"] == "local-model"
    assert active["local_endpoint_loopback_allowed"] is True
    assert active["connectivity_tested"] is False
    assert active["inference_executed"] is False
    assert "local-secret" not in json.dumps(report)


def test_non_loopback_local_endpoint_is_flagged(tmp_path):
    report = inspect_runtime(tmp_path, {
        "BARROT_LLM_PROVIDER": "local",
        "BARROT_LLM_BASE_URL": "http://0.0.0.0:8081/v1/chat/completions",
        "BARROT_LLM_MODEL": "local-model",
    })

    assert report["active_worker_snapshot"]["local_endpoint_loopback_allowed"] is False


def test_environment_scope_is_explicit(tmp_path):
    report = inspect_runtime(tmp_path, {})
    assert "This process only" in report["execution_context"]["environment_scope"]
    assert report["safety"]["inference_executed"] is False
