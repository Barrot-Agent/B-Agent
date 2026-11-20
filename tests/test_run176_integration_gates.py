from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dependency_audit_runs_on_every_main_and_integration_push() -> None:
    workflow = (ROOT / ".github/workflows/dependency-audit.yml").read_text(encoding="utf-8")
    trigger_section = workflow.split("permissions:", 1)[0]
    assert 'branches: [main, "integration/**"]' in trigger_section
    assert "pull_request:\n    branches: [main]" in trigger_section
    assert "paths:" not in trigger_section
    assert "contents: read" in workflow
    assert "Audit PEP 621 project dependencies" in workflow


def test_pages_build_is_build_only_on_integration_push() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    start = workflow.index("  pages-build:")
    rest = workflow[start:]
    next_job = re.search(r"\n  [a-zA-Z0-9_-]+:", rest[1:])
    job = rest[: next_job.start() + 1] if next_job else rest
    assert "github.event_name == 'pull_request'" in job
    assert "startsWith(github.ref, 'refs/heads/integration/')" in job
    assert re.search(r"(?m)^\s+uses: actions/jekyll-build-pages@[0-9a-f]{40} # v1\s*$", job)
    assert "actions/deploy-pages" not in job
    assert "contents: read" in job


def test_opencode_mcp_configuration_preserves_least_privilege() -> None:
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    servers = config["mcp"]["servers"]
    assert config["default_agent"] == "barrot"
    assert {"github", "docling", "searxng", "lunaroute"} <= set(servers)
    assert "GITHUB_MCP_TOKEN" in servers["github"]["headers"]["Authorization"]
    assert servers["lunaroute"]["disabled"] is True
    assert config["permission"]["edit"] == "ask"
    assert config["permission"]["bash"] == "ask"
    assert config["agent"]["barrot"]["permission"]["*"] == "ask"


def test_local_searxng_launcher_binds_only_to_loopback() -> None:
    script = (ROOT / "scripts/start_searxng.sh").read_text(encoding="utf-8")
    assert 'bind_address: "127.0.0.1"' in script
    assert "public_instance: false" in script
    assert "limiter: false" in script
    assert 'exec .venv/bin/python -m searx.webapp' in script
    assert "0.0.0.0" not in script


def test_docs_do_not_claim_github_mcp_is_already_authenticated() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    memory = (ROOT / "MEMORY.md").read_text(encoding="utf-8")
    assert "already stored in the OpenCode service environment" not in readme
    assert "authentication is not yet verified" in readme
    assert "not yet verified" in memory
