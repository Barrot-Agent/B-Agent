# Changelog

All notable changes to B-Agent are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Unbuildable wheel: setuptools discovery now scoped to `barrot_agent*`
  (repo root had four top-level `__init__.py` dirs, so `python -m build`
  aborted with "Multiple top-level packages discovered").
- Broken sibling imports in `mcp_orchestrator`, `orchestrator_bridge` and
  `dependency_micro_ingestion` (worked only when run as standalone scripts).
- `b_agent.py` unrunnable: undeclared `rich`/`httpx`, misplaced shebang.
- `scripts/vader_check.py` import-safe without `vaderSentiment`.
- `scripts/barrot_task_allocator.py` direct execution ImportError.
- `dependency-audit.yml`: `requirements.tx` typo pointed the supplemental
  audit at a nonexistent file (permanently red gate).
- `app.json`: wrong repository/website URLs (pointed at a different repo).
- Flaky `tests/test_transmute.py::test_cli_end_to_end` (timing-sensitive).
- `v_sync_relay.sh`: no longer auto-commits secret-like files; rebase-before-push.

### Changed
- Dependency floors raised across `requirements.txt` / `pyproject.toml`
  (torch 2.6, transformers 4.48, numpy 2.1, cryptography 44, ...);
  dev/pre-commit toolchain refreshed to current majors.
- Dockerfiles moved from EOL Python 3.10 to 3.12.
- `opencode.json` migrated to the native OpenCode V2 config shape.
- `.env.example` now documents all env vars referenced by the code.

## [0.1.0] - 2026-04-07

### Added
- Initial project structure with `barrot_agent/` package
- IBM Granite 4.0-3B Vision model integration (`models.py`, `inference.py`)
- Pydantic-based configuration management (`config.py`)
- Structured JSON logging with rotating file support (`logger.py`)
- Core application class (`core.py`)
- Comprehensive test suite with pytest (`tests/`)
- GitHub Actions CI/CD pipeline (`ci.yml`, `release.yml`)
- Dockerfile and docker-compose for containerized deployment
- Pre-commit hooks for code quality enforcement
- Dependabot for automated dependency updates
- Documentation: README, ARCHITECTURE, DEVELOPMENT, CONTRIBUTING, API
- `.env.example` for environment variable templates
- Makefile for common development tasks
- `requirements.txt` with pinned versions
- `requirements-dev.txt` with development tooling
