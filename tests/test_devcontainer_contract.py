from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_devcontainer_references_existing_python_311_build_and_lifecycle_files() -> None:
    config = json.loads(_read(".devcontainer/devcontainer.json"))
    dockerfile = ROOT / ".devcontainer" / config["build"]["dockerfile"]
    assert dockerfile.is_file()
    assert "python:1-3.11-bookworm" in dockerfile.read_text(encoding="utf-8")
    assert "ghcr.io/devcontainers/features/github-cli:1" in config["features"]
    assert ".devcontainer/post-create.sh" in config["onCreateCommand"]
    assert ".devcontainer/health-check.sh" in config["postStartCommand"]


def test_default_codespaces_setup_is_core_only_and_non_destructive() -> None:
    script = _read(".devcontainer/post-create.sh")
    assert "requirements-dev-codespaces.txt" in script
    assert "requirements-dev.txt" not in script
    assert "requirements.txt" not in script
    for forbidden in ("git clean", "git reset", "git stash", "git restore", "rm -rf"):
        assert forbidden not in script


def test_health_check_uses_tools_without_printing_or_loading_secrets() -> None:
    script = _read(".devcontainer/health-check.sh")
    assert "sys.version_info[:2] != (3, 11)" in script
    assert "git --version" in script
    assert "gh --version" in script
    assert "make --version" in script
    assert "SERP_API_KEY=" not in script
    assert "gh auth status" not in script


def test_optional_dependencies_are_not_in_the_default_codespaces_prebuild() -> None:
    codespaces = _read("requirements-dev-codespaces.txt").lower()
    ml = _read("requirements-ml.txt").lower()
    ui = _read("requirements-ui.txt").lower()
    for heavy in ("torch", "transformers", "accelerate", "bitsandbytes", "safetensors", "streamlit"):
        assert heavy not in codespaces
    for heavy in ("torch", "transformers", "accelerate", "bitsandbytes", "safetensors"):
        assert heavy in ml
    assert "streamlit" in ui


def test_makefile_and_ci_share_core_and_full_test_commands() -> None:
    makefile = _read("Makefile")
    workflow = _read(".github/workflows/ci.yml")
    assert "install-dev-core:" in makefile
    assert "install-dev-full:" in makefile
    assert "install-ml:" in makefile
    assert "install-ui:" in makefile
    assert "test-core:" in makefile
    assert "test-full:" in makefile
    assert "run: make test-core" in workflow
    assert "run: make test-full" in workflow


def test_secret_documentation_distinguishes_codespaces_and_actions_scopes() -> None:
    docs = _read("docs/CODESPACES.md")
    assert "Codespaces secrets" in docs
    assert "Actions secrets" in docs
    assert "`SERP_API_KEY`" in docs
    assert "not automatically available" in docs
    assert "does not read, request, print, copy, or change" in docs
